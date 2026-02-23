#!/usr/bin/env python3
"""Agent 2: Scrape GitHub repos for Rhino3D Python scripts.

Collects Python files using RhinoCommon/rhinoscriptsyntax/rhino3dm from GitHub.
Outputs individual JSON files to data/raw/github/.
"""

import os
import sys
import json
import time
import hashlib
import base64
import re
import subprocess
from pathlib import Path
from urllib.parse import quote

import requests

# --- Configuration ---
BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "data" / "raw" / "github"
SCRAPED_URLS_FILE = RAW_DIR / "scraped_urls.txt"
SUMMARY_FILE = RAW_DIR / "summary.json"

SEARCH_QUERIES = [
    '"import rhinoscriptsyntax" language:python',
    '"import Rhino.Geometry" language:python',
    '"import Rhino" language:python',
    '"import rhino3dm" language:python',
    '"import scriptcontext" language:python',
    '"from Rhino.Geometry import" language:python',
    '"rs.AddSurface" language:python',
    '"rs.AddCurve" language:python',
    '"RhinoCommon" language:python',
    '"ghpythonlib" language:python',
]

KNOWN_REPOS = [
    "mcneel/rhino-developer-samples",
    "mcneel/rhinoscriptsyntax",
    "mcneel/rhino3dm",
    "compas-dev/compas",
]

RHINO_PATTERNS = [
    "import rhinoscriptsyntax",
    "import Rhino",
    "from Rhino",
    "import rhino3dm",
    "from rhino3dm",
    "import scriptcontext",
    "from scriptcontext",
    "ghpythonlib",
    "RhinoCommon",
    "rs.Add",
]


# --- GitHub API ---
class GitHubAPI:
    def __init__(self, token):
        self.token = token
        self.headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json",
        }
        self.search_count = 0
        self.api_count = 0

    def _request(self, url, is_search=False):
        if is_search:
            self.search_count += 1
            if self.search_count % 28 == 0:
                print(f"  [Rate limit] Pausing 65s after {self.search_count} search requests...")
                time.sleep(65)
        else:
            self.api_count += 1
            if self.api_count % 100 == 0:
                print(f"  [API count: {self.api_count}]")
                time.sleep(1)

        for attempt in range(5):
            try:
                resp = requests.get(url, headers=self.headers, timeout=30)

                if resp.status_code == 200:
                    return resp.json()
                elif resp.status_code == 403:
                    retry_after = int(resp.headers.get("Retry-After", 60))
                    reset_time = resp.headers.get("X-RateLimit-Reset")
                    if reset_time:
                        wait = max(int(reset_time) - int(time.time()), 10)
                        retry_after = min(wait, 120)
                    print(f"  [Rate limited] Waiting {retry_after}s (attempt {attempt+1}/5)...")
                    time.sleep(retry_after + 1)
                elif resp.status_code == 404:
                    return None
                elif resp.status_code == 422:
                    print(f"  [Validation error] {url[:100]}: {resp.text[:200]}")
                    return None
                else:
                    print(f"  [HTTP {resp.status_code}] {url[:100]}: {resp.text[:200]}")
                    time.sleep(5)
            except Exception as e:
                print(f"  [Error] {e}, retrying in 10s...")
                time.sleep(10)
        return None

    def search_code(self, query, page=1, per_page=100):
        encoded_q = quote(query)
        url = f"https://api.github.com/search/code?q={encoded_q}&per_page={per_page}&page={page}"
        return self._request(url, is_search=True)

    def get_file_content(self, owner, repo, path):
        encoded_path = quote(path, safe="/")
        url = f"https://api.github.com/repos/{owner}/{repo}/contents/{encoded_path}"
        return self._request(url)

    def get_repo_info(self, owner, repo):
        url = f"https://api.github.com/repos/{owner}/{repo}"
        return self._request(url)

    def get_repo_tree(self, owner, repo, branch="main"):
        url = f"https://api.github.com/repos/{owner}/{repo}/git/trees/{branch}?recursive=1"
        result = self._request(url)
        if result is None:
            url = f"https://api.github.com/repos/{owner}/{repo}/git/trees/master?recursive=1"
            result = self._request(url)
        return result


# --- Helpers ---
def get_github_token():
    try:
        result = subprocess.run(["gh", "auth", "token"], capture_output=True, text=True)
        if result.returncode == 0:
            return result.stdout.strip()
    except FileNotFoundError:
        pass
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        return token
    print("ERROR: No GitHub token found. Run 'gh auth login' or set GITHUB_TOKEN.")
    sys.exit(1)


def load_scraped_urls():
    if SCRAPED_URLS_FILE.exists():
        text = SCRAPED_URLS_FILE.read_text().strip()
        if text:
            return set(text.split("\n"))
    return set()


def save_scraped_url(url):
    with open(SCRAPED_URLS_FILE, "a") as f:
        f.write(url + "\n")


def make_filename(repo, filepath):
    owner, name = repo.split("/", 1)
    path_hash = hashlib.md5(filepath.encode()).hexdigest()[:10]
    safe_owner = re.sub(r'[^\w\-]', '_', owner)
    safe_name = re.sub(r'[^\w\-]', '_', name)
    return f"{safe_owner}_{safe_name}_{path_hash}.json"


def is_meaningful_script(code, filepath):
    basename = os.path.basename(filepath).lower()
    skip_names = {"__init__.py", "setup.py", "conftest.py", "conf.py", "__main__.py"}
    if basename in skip_names:
        return False
    if basename.startswith("test_") or basename.endswith("_test.py"):
        return False
    real_lines = 0
    for line in code.split("\n"):
        stripped = line.strip()
        if stripped and not stripped.startswith("#") and not stripped.startswith("import ") and not stripped.startswith("from "):
            real_lines += 1
    return real_lines >= 5


def has_rhino_content(code):
    code_lower = code.lower()
    for pattern in RHINO_PATTERNS:
        if pattern.lower() in code_lower:
            return True
    return False


def extract_docstring(code):
    lines = code.strip().split("\n")
    start = 0
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("#") or stripped == "":
            start = i + 1
        else:
            break
    if start >= len(lines):
        return None
    rest = "\n".join(lines[start:])
    for q in ['"""', "'''"]:
        if rest.strip().startswith(q):
            end_idx = rest.find(q, rest.index(q) + len(q))
            if end_idx > 0:
                return rest[rest.index(q) + len(q):end_idx].strip()
    return None


def extract_top_comments(code):
    lines = code.strip().split("\n")
    comments = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("#!") or stripped.startswith("# -*-"):
            continue
        if stripped.startswith("#"):
            comment_text = stripped.lstrip("#").strip()
            if comment_text:
                comments.append(comment_text)
        elif stripped == "":
            if comments:
                break
        else:
            break
    return " ".join(comments) if comments else None


def extract_instruction(code, filepath):
    docstring = extract_docstring(code)
    if docstring and len(docstring) > 10:
        instruction = docstring.strip().split("\n\n")[0].strip()
        if len(instruction) > 200:
            instruction = instruction[:200].rsplit(" ", 1)[0] + "..."
        return instruction, True

    top_comment = extract_top_comments(code)
    if top_comment and len(top_comment) > 10:
        return top_comment.strip(), True

    basename = os.path.splitext(os.path.basename(filepath))[0]
    instruction = basename.replace("_", " ").replace("-", " ")
    instruction = re.sub(r'([a-z])([A-Z])', r'\1 \2', instruction)
    instruction = instruction.strip().capitalize()
    if len(instruction) > 5:
        return instruction, False

    return None, False


def extract_imports(code):
    imports = set()
    for line in code.split("\n"):
        stripped = line.strip()
        if "rhinoscriptsyntax" in stripped:
            imports.add("rhinoscriptsyntax")
        if "Rhino.Geometry" in stripped:
            imports.add("Rhino.Geometry")
        if "rhino3dm" in stripped:
            imports.add("rhino3dm")
        if "scriptcontext" in stripped:
            imports.add("scriptcontext")
        if "ghpythonlib" in stripped:
            imports.add("ghpythonlib")
        if "RhinoCommon" in stripped:
            imports.add("RhinoCommon")
        if re.match(r'^\s*(import|from)\s+Rhino\b', stripped):
            imports.add("Rhino")
    return sorted(imports)


def save_file_data(data):
    filename = make_filename(data["repo"], data["filepath"])
    outpath = RAW_DIR / filename
    with open(outpath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    return outpath


# --- Main Scraping Logic ---

def scrape_search_results(api, scraped_urls):
    all_items = {}

    for i, query in enumerate(SEARCH_QUERIES):
        print(f"\n[Search {i+1}/{len(SEARCH_QUERIES)}] {query}")
        page = 1
        total_for_query = 0

        while page <= 10:
            result = api.search_code(query, page=page, per_page=100)
            if result is None:
                print(f"  Page {page}: failed, stopping pagination")
                break

            total_count = result.get("total_count", 0)
            items = result.get("items", [])

            if page == 1:
                print(f"  Total results: {total_count}")

            if not items:
                break

            for item in items:
                html_url = item.get("html_url", "")
                if html_url and html_url not in all_items and html_url not in scraped_urls:
                    all_items[html_url] = item
                    total_for_query += 1

            print(f"  Page {page}: {len(items)} results ({total_for_query} new cumulative)")

            if len(items) < 100:
                break

            page += 1
            time.sleep(3)

        print(f"  Subtotal new items from this query: {total_for_query}")

    print(f"\nTotal unique files from search: {len(all_items)}")
    return all_items


def scrape_known_repos(api, scraped_urls):
    all_items = {}

    for repo_full in KNOWN_REPOS:
        owner, repo = repo_full.split("/")
        print(f"\n[Known repo] {repo_full}")

        tree = api.get_repo_tree(owner, repo)
        if tree is None:
            print(f"  Could not get tree for {repo_full}")
            continue

        tree_items = tree.get("tree", [])
        py_files = [t for t in tree_items if t["path"].endswith(".py") and t["type"] == "blob"]
        print(f"  Found {len(py_files)} Python files")

        count = 0
        for t in py_files:
            html_url = f"https://github.com/{repo_full}/blob/HEAD/{t['path']}"
            if html_url not in scraped_urls and html_url not in all_items:
                all_items[html_url] = {
                    "html_url": html_url,
                    "path": t["path"],
                    "repository": {
                        "full_name": repo_full,
                        "owner": {"login": owner},
                        "name": repo,
                    },
                    "_known_repo": True,
                }
                count += 1
        print(f"  New files to process: {count}")

    print(f"\nTotal files from known repos: {len(all_items)}")
    return all_items


def process_file(api, html_url, item, repo_info_cache):
    repo_data = item.get("repository", {})
    repo_full = repo_data.get("full_name", "")
    if not repo_full:
        return None

    owner, repo = repo_full.split("/", 1)
    filepath = item.get("path", "")
    if not filepath:
        return None

    # Get repo info (cached)
    if repo_full not in repo_info_cache:
        info = api.get_repo_info(owner, repo)
        repo_info_cache[repo_full] = info or {}

    repo_info = repo_info_cache[repo_full]
    stars = repo_info.get("stargazers_count", 0)
    repo_description = repo_info.get("description", "")
    repo_license = repo_info.get("license", {})
    license_name = repo_license.get("spdx_id", "unknown") if repo_license else "unknown"

    # Get file content
    content_data = api.get_file_content(owner, repo, filepath)
    if content_data is None:
        return None

    content_b64 = content_data.get("content", "")
    encoding = content_data.get("encoding", "")

    if encoding == "base64":
        try:
            code = base64.b64decode(content_b64).decode("utf-8", errors="replace")
        except Exception:
            return None
    else:
        code = content_b64

    if not code or len(code.strip()) < 20:
        return None

    # Check Rhino content
    if not has_rhino_content(code):
        return None

    # Check meaningful
    if not is_meaningful_script(code, filepath):
        return None

    # Extract instruction
    instruction, has_docstring = extract_instruction(code, filepath)

    # Extract imports
    imports = extract_imports(code)

    # Language
    language = "csharp" if filepath.endswith(".cs") else "python"

    return {
        "source_url": html_url,
        "repo": repo_full,
        "repo_stars": stars,
        "repo_description": repo_description,
        "license": license_name,
        "filepath": filepath,
        "instruction": instruction,
        "code": code,
        "language": language,
        "imports": imports,
        "has_docstring": has_docstring,
    }


def generate_summary(saved_files):
    total = len(saved_files)
    with_docstring = sum(1 for f in saved_files if f.get("has_docstring"))
    with_instruction = sum(1 for f in saved_files if f.get("instruction"))

    languages = {}
    for f in saved_files:
        lang = f.get("language", "unknown")
        languages[lang] = languages.get(lang, 0) + 1

    import_counts = {}
    for f in saved_files:
        for imp in f.get("imports", []):
            import_counts[imp] = import_counts.get(imp, 0) + 1

    repo_counts = {}
    for f in saved_files:
        r = f.get("repo", "unknown")
        repo_counts[r] = repo_counts.get(r, 0) + 1
    top_repos = sorted(repo_counts.items(), key=lambda x: -x[1])[:20]

    return {
        "total_files": total,
        "files_with_docstrings": with_docstring,
        "files_with_instructions": with_instruction,
        "files_without_instructions": total - with_instruction,
        "language_breakdown": languages,
        "import_breakdown": import_counts,
        "top_repos": dict(top_repos),
    }


def main():
    print("=" * 60)
    print("Agent 2: GitHub Rhino3D Script Scraper")
    print("=" * 60)

    RAW_DIR.mkdir(parents=True, exist_ok=True)
    token = get_github_token()
    api = GitHubAPI(token)
    scraped_urls = load_scraped_urls()
    print(f"Already scraped: {len(scraped_urls)} URLs")

    # Phase 1: Search API
    print("\n--- Phase 1: GitHub Code Search ---")
    search_items = scrape_search_results(api, scraped_urls)

    # Phase 2: Known repos
    print("\n--- Phase 2: Known Repos ---")
    known_items = scrape_known_repos(api, scraped_urls)

    # Merge (search items take priority for richer metadata)
    all_items = {**known_items, **search_items}
    print(f"\nTotal unique files to process: {len(all_items)}")

    # Phase 3: Download and process
    print("\n--- Phase 3: Download & Process ---")
    saved_files = []
    repo_info_cache = {}
    skipped = 0
    errors = 0

    sorted_items = sorted(all_items.items())

    for idx, (url, item) in enumerate(sorted_items):
        if (idx + 1) % 50 == 0 or idx == 0:
            print(f"\nProcessing {idx+1}/{len(sorted_items)} (saved: {len(saved_files)}, skipped: {skipped}, errors: {errors})")

        try:
            data = process_file(api, url, item, repo_info_cache)
            if data is None:
                skipped += 1
                continue

            save_file_data(data)
            save_scraped_url(url)
            saved_files.append(data)

        except Exception as e:
            errors += 1
            print(f"  Error processing {url}: {e}")

    # Phase 4: Summary
    print("\n--- Phase 4: Summary ---")
    summary = generate_summary(saved_files)
    summary["total_processed"] = len(all_items)
    summary["skipped"] = skipped
    summary["errors"] = errors

    with open(SUMMARY_FILE, "w") as f:
        json.dump(summary, f, indent=2)

    print(f"\nResults:")
    print(f"  Total files processed: {len(all_items)}")
    print(f"  Files saved: {len(saved_files)}")
    print(f"  Skipped (not meaningful/Rhino): {skipped}")
    print(f"  Errors: {errors}")
    print(f"  Files with docstrings: {summary['files_with_docstrings']}")
    print(f"  Files with instructions: {summary['files_with_instructions']}")
    print(f"  Language breakdown: {summary['language_breakdown']}")
    print(f"  Import breakdown: {summary['import_breakdown']}")
    print(f"  Top repos: {json.dumps(summary['top_repos'], indent=2)}")
    print(f"\nSummary saved to: {SUMMARY_FILE}")
    print(f"Data saved to: {RAW_DIR}/")
    print("Done!")


if __name__ == "__main__":
    main()
