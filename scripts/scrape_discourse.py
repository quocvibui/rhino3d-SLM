#!/usr/bin/env python3
"""
Agent 1: Scrape McNeel Discourse forum for Rhino scripting (instruction, code) pairs.

Searches discourse.mcneel.com for threads where users ask scripting questions
and receive working code answers. Extracts code blocks and pairs them with
the original question as training data.

Output: data/raw/discourse/{topic_id}.json + summary.json
"""

import json
import logging
import os
import re
import sys
import time
from html.parser import HTMLParser
from pathlib import Path

import requests
from bs4 import BeautifulSoup

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
BASE_URL = "https://discourse.mcneel.com"
OUTPUT_DIR = Path(__file__).resolve().parent.parent / "data" / "raw" / "discourse"
ERROR_LOG = OUTPUT_DIR / "errors.log"
SUMMARY_FILE = OUTPUT_DIR / "summary.json"

SEARCH_QUERIES = [
    "rhinoscriptsyntax",
    "rhinocommon python",
    "python script rhino",
    "ghpython",
    "import Rhino.Geometry",
    "rs.Add",
    "scriptcontext",
    "RhinoCommon C#",
    "Rhino.Geometry python",
    "rhinoscriptsyntax rs.",
]

CATEGORY_IDS = [
    3,   # Rhino Developer
    11,  # Scripting
    8,   # Grasshopper Developer
]

# Rate limiting
REQUEST_DELAY = 1.0          # seconds between requests
BACKOFF_BASE = 2.0           # base for exponential backoff
MAX_RETRIES = 5

# Search pagination
MAX_SEARCH_PAGES = 10        # per query

# Category pagination
MAX_CATEGORY_PAGES = 15      # per category

# Minimum code block length (lines)
MIN_CODE_LINES = 3

# Rhino-related keywords to identify relevant code
RHINO_KEYWORDS = [
    "rhinoscriptsyntax", "rhino.geometry", "rhinocommon", "scriptcontext",
    "rs.", "import Rhino", "import rhino3dm", "RhinoDoc", "RhinoApp",
    "Rhino.Commands", "Rhino.Input", "Rhino.DocObjects",
    "ghpythonlib", "Grasshopper", "ghdoc",
    "AddLine", "AddCircle", "AddSphere", "AddCurve", "AddSurface",
    "AddPoint", "AddMesh", "AddBrep", "AddBox", "AddCylinder",
    "GetObject", "GetObjects", "GetPoint", "GetPoints",
    "ObjectName", "ObjectLayer", "ObjectColor",
    "coerce", "scriptcontext.doc",
    # C# Rhino
    "RhinoCommon", "Rhino.Geometry.", "RhinoDoc.ActiveDoc",
    "Rhino.Commands.Result", "using Rhino",
]

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(ERROR_LOG, mode="a"),
    ],
)
log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# HTTP helpers
# ---------------------------------------------------------------------------
session = requests.Session()
session.headers.update({
    "User-Agent": "RhinoICL-DataCollector/1.0 (research; polite-scraper)",
    "Accept": "application/json",
})


def api_get(url: str, params: dict = None) -> dict | None:
    """GET with rate limiting, retries, and exponential backoff."""
    for attempt in range(MAX_RETRIES):
        try:
            time.sleep(REQUEST_DELAY)
            resp = session.get(url, params=params, timeout=30)
            if resp.status_code == 200:
                return resp.json()
            elif resp.status_code == 429:
                wait = BACKOFF_BASE ** (attempt + 1)
                log.warning("Rate limited (429). Waiting %.1fs ...", wait)
                time.sleep(wait)
                continue
            else:
                log.warning("HTTP %d for %s", resp.status_code, url)
                if attempt < MAX_RETRIES - 1:
                    time.sleep(BACKOFF_BASE ** attempt)
                    continue
                return None
        except requests.RequestException as e:
            log.error("Request error for %s: %s", url, e)
            if attempt < MAX_RETRIES - 1:
                time.sleep(BACKOFF_BASE ** attempt)
                continue
            return None
    return None


# ---------------------------------------------------------------------------
# HTML -> text helpers
# ---------------------------------------------------------------------------
def html_to_text(html: str) -> str:
    """Strip HTML tags and return plain text, preserving newlines."""
    soup = BeautifulSoup(html, "html.parser")
    return soup.get_text(separator="\n").strip()


def extract_code_blocks(html: str) -> list[str]:
    """Extract code blocks from Discourse post HTML.

    Discourse wraps code in:
      <pre><code class="lang-python">...</code></pre>
    or just <pre><code>...</code></pre>
    """
    soup = BeautifulSoup(html, "html.parser")
    blocks = []

    # <pre><code> blocks (fenced code)
    for pre in soup.find_all("pre"):
        code_tag = pre.find("code")
        if code_tag:
            text = code_tag.get_text()
        else:
            text = pre.get_text()
        text = text.strip()
        if text:
            blocks.append(text)

    # Inline <code> that might be multi-line (rare but possible)
    for code in soup.find_all("code"):
        # Skip if already captured inside a <pre>
        if code.parent and code.parent.name == "pre":
            continue
        text = code.get_text().strip()
        if "\n" in text and len(text.split("\n")) >= MIN_CODE_LINES:
            blocks.append(text)

    return blocks


def detect_language(code: str) -> str:
    """Heuristic language detection for code blocks."""
    lower = code.lower()
    # Python signals
    py_signals = ["import ", "def ", "print(", "for ", "rhinoscriptsyntax", "rs.", "scriptcontext", "ghpythonlib"]
    cs_signals = ["using ", "void ", "public ", "private ", "static ", "namespace ", "var ", "{", "};", "//"]

    py_score = sum(1 for s in py_signals if s in lower)
    cs_score = sum(1 for s in cs_signals if s in lower)

    if py_score > cs_score:
        return "python"
    elif cs_score > py_score:
        return "csharp"
    else:
        return "unknown"


def is_rhino_code(code: str) -> bool:
    """Check if a code block contains Rhino-related content."""
    lower = code.lower()
    return any(kw.lower() in lower for kw in RHINO_KEYWORDS)


def code_lang_from_html(pre_tag) -> str | None:
    """Try to detect language from HTML class attributes."""
    code_tag = pre_tag.find("code") if pre_tag else None
    if code_tag:
        classes = code_tag.get("class", [])
        for cls in classes:
            if "python" in cls.lower():
                return "python"
            if "csharp" in cls.lower() or "cs" in cls.lower():
                return "csharp"
    return None


def extract_code_blocks_with_meta(html: str) -> list[dict]:
    """Extract code blocks with language metadata."""
    soup = BeautifulSoup(html, "html.parser")
    blocks = []

    for pre in soup.find_all("pre"):
        code_tag = pre.find("code")
        if code_tag:
            text = code_tag.get_text().strip()
        else:
            text = pre.get_text().strip()

        if not text:
            continue

        # Try HTML class first, fall back to heuristic
        lang = code_lang_from_html(pre)
        if not lang:
            lang = detect_language(text)

        blocks.append({"code": text, "language": lang})

    return blocks


# ---------------------------------------------------------------------------
# Tag inference
# ---------------------------------------------------------------------------
def infer_tags(title: str, question: str, code_blocks: list[dict]) -> list[str]:
    """Infer tags from content."""
    combined = (title + " " + question + " " + " ".join(b["code"] for b in code_blocks)).lower()
    tags = set()

    tag_keywords = {
        "python": ["python", "rhinoscriptsyntax", "rs.", "ghpython", "scriptcontext"],
        "csharp": ["c#", "csharp", "using rhino", "rhinocommon"],
        "rhinoscriptsyntax": ["rhinoscriptsyntax", "import rhinoscriptsyntax"],
        "rhinocommon": ["rhinocommon", "rhino.geometry", "rhino.commands"],
        "grasshopper": ["grasshopper", "ghpython", "ghdoc", "ghpythonlib"],
        "geometry": ["curve", "surface", "mesh", "brep", "point", "line", "circle", "sphere", "box", "cylinder"],
        "selection": ["getobject", "getobjects", "selectedobjects"],
        "layers": ["layer", "objectlayer", "addlayer", "currentlayer"],
        "materials": ["material", "render", "texture"],
        "transformation": ["move", "rotate", "scale", "transform", "mirror", "orient"],
        "boolean": ["boolean", "booleanunion", "booleandifference", "booleanintersection"],
        "mesh": ["mesh", "addmesh", "meshface", "meshvertex"],
        "nurbs": ["nurbs", "nurbscurve", "nurbssurface", "controlpoint"],
        "file-io": ["import ", "export", "open ", "save", "readfile", "writefile"],
        "ui": ["getstring", "getinteger", "getreal", "messagebox", "listbox"],
    }

    for tag, keywords in tag_keywords.items():
        if any(kw in combined for kw in keywords):
            tags.add(tag)

    return sorted(tags)


# ---------------------------------------------------------------------------
# Discourse API wrappers
# ---------------------------------------------------------------------------
def search_topics(query: str, max_pages: int = MAX_SEARCH_PAGES) -> list[dict]:
    """Search Discourse and return list of topic stubs."""
    topics = {}
    for page in range(1, max_pages + 1):
        data = api_get(f"{BASE_URL}/search.json", params={"q": query, "page": page})
        if not data:
            break

        for t in data.get("topics", []):
            tid = t["id"]
            if tid not in topics:
                topics[tid] = {
                    "id": tid,
                    "title": t.get("title", ""),
                    "slug": t.get("slug", ""),
                    "has_accepted_answer": t.get("has_accepted_answer", False),
                    "tags": t.get("tags", []),
                    "category_id": t.get("category_id"),
                }

        more = data.get("grouped_search_result", {}).get("more_full_page_results", False)
        if not more:
            break

    return list(topics.values())


def list_category_topics(category_id: int, max_pages: int = MAX_CATEGORY_PAGES) -> list[dict]:
    """List topics from a category."""
    topics = {}
    url = f"{BASE_URL}/c/{category_id}.json"

    for page in range(max_pages):
        data = api_get(url)
        if not data:
            break

        topic_list = data.get("topic_list", {})
        for t in topic_list.get("topics", []):
            tid = t["id"]
            if tid not in topics:
                topics[tid] = {
                    "id": tid,
                    "title": t.get("title", ""),
                    "slug": t.get("slug", ""),
                    "has_accepted_answer": t.get("has_accepted_answer", False),
                    "tags": t.get("tags", []),
                    "category_id": t.get("category_id"),
                }

        more_url = topic_list.get("more_topics_url")
        if not more_url:
            break
        url = f"{BASE_URL}{more_url}"

    return list(topics.values())


def fetch_topic_posts(topic_id: int) -> dict | None:
    """Fetch full topic with all posts.

    Discourse may paginate posts for large threads. We fetch additional
    chunks via the post stream IDs.
    """
    data = api_get(f"{BASE_URL}/t/{topic_id}.json")
    if not data:
        return None

    post_stream = data.get("post_stream", {})
    posts = post_stream.get("posts", [])
    all_stream_ids = set(post_stream.get("stream", []))
    fetched_ids = {p["id"] for p in posts}

    # Fetch remaining posts in chunks of 20
    missing = list(all_stream_ids - fetched_ids)
    for i in range(0, len(missing), 20):
        chunk = missing[i:i + 20]
        ids_param = "&".join(f"post_ids[]={pid}" for pid in chunk)
        extra = api_get(f"{BASE_URL}/t/{topic_id}/posts.json?{ids_param}")
        if extra and "post_stream" in extra:
            posts.extend(extra["post_stream"].get("posts", []))

    data["_all_posts"] = posts
    return data


# ---------------------------------------------------------------------------
# Core extraction
# ---------------------------------------------------------------------------
def process_topic(topic_meta: dict) -> dict | None:
    """Fetch a topic, extract code blocks, and return structured data.

    Returns None if no relevant code blocks found.
    """
    topic_id = topic_meta["id"]
    out_file = OUTPUT_DIR / f"{topic_id}.json"

    # Skip already-scraped topics
    if out_file.exists():
        return None

    data = fetch_topic_posts(topic_id)
    if not data:
        log.warning("Could not fetch topic %d", topic_id)
        return None

    posts = data.get("_all_posts", [])
    if not posts:
        return None

    title = data.get("title", topic_meta.get("title", ""))

    # First post = the question
    first_post = posts[0]
    question_html = first_post.get("cooked", "")
    question_text = html_to_text(question_html)

    # Truncate very long questions
    if len(question_text) > 2000:
        question_text = question_text[:2000] + "..."

    # Collect code blocks from reply posts
    code_blocks = []
    for post in posts[1:]:  # skip first post (question)
        cooked = post.get("cooked", "")
        blocks_with_meta = extract_code_blocks_with_meta(cooked)

        for block in blocks_with_meta:
            code = block["code"]
            # Filter: too short
            if len(code.strip().split("\n")) < MIN_CODE_LINES:
                continue
            # Filter: must be Rhino-related
            if not is_rhino_code(code):
                continue

            code_blocks.append({
                "code": code,
                "language": block["language"],
                "author": post.get("username", "unknown"),
                "post_number": post.get("post_number"),
                "is_solution": bool(post.get("accepted_answer", False)),
            })

    # Also check first post for self-answered threads
    first_blocks = extract_code_blocks_with_meta(question_html)
    for block in first_blocks:
        code = block["code"]
        if len(code.strip().split("\n")) >= MIN_CODE_LINES and is_rhino_code(code):
            code_blocks.append({
                "code": code,
                "language": block["language"],
                "author": first_post.get("username", "unknown"),
                "post_number": 1,
                "is_solution": False,
            })

    if not code_blocks:
        return None

    # Build tags
    tags = infer_tags(title, question_text, code_blocks)

    result = {
        "source_url": f"{BASE_URL}/t/{data.get('slug', '')}/{topic_id}",
        "topic_id": topic_id,
        "title": title,
        "question": question_text,
        "code_blocks": code_blocks,
        "tags": tags,
        "has_accepted_answer": data.get("has_accepted_answer", False)
                               or topic_meta.get("has_accepted_answer", False),
        "category_id": data.get("category_id"),
        "posts_count": data.get("posts_count", len(posts)),
        "views": data.get("views", 0),
    }

    # Save immediately
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    return result


# ---------------------------------------------------------------------------
# Main collection loop
# ---------------------------------------------------------------------------
def collect_all_topic_ids() -> dict[int, dict]:
    """Gather unique topic IDs from search queries + category listings."""
    all_topics: dict[int, dict] = {}

    # 1. Search queries
    for query in SEARCH_QUERIES:
        log.info("Searching: %s", query)
        results = search_topics(query)
        for t in results:
            all_topics.setdefault(t["id"], t)
        log.info("  Found %d topics (total unique: %d)", len(results), len(all_topics))

    # 2. Category listings
    for cat_id in CATEGORY_IDS:
        log.info("Listing category %d", cat_id)
        results = list_category_topics(cat_id)
        for t in results:
            all_topics.setdefault(t["id"], t)
        log.info("  Found %d topics (total unique: %d)", len(results), len(all_topics))

    return all_topics


def already_scraped() -> set[int]:
    """Return set of topic IDs already saved to disk."""
    scraped = set()
    for f in OUTPUT_DIR.glob("*.json"):
        if f.name in ("summary.json",):
            continue
        try:
            scraped.add(int(f.stem))
        except ValueError:
            pass
    return scraped


def save_summary(stats: dict):
    """Save collection summary."""
    with open(SUMMARY_FILE, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2, ensure_ascii=False)


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    log.info("=" * 60)
    log.info("Starting McNeel Discourse scraper")
    log.info("Output: %s", OUTPUT_DIR)
    log.info("=" * 60)

    # Phase 1: Collect topic IDs
    log.info("Phase 1: Collecting topic IDs from search + categories ...")
    all_topics = collect_all_topic_ids()
    log.info("Total unique topics found: %d", len(all_topics))

    # Phase 2: Filter out already-scraped
    done = already_scraped()
    to_scrape = {tid: t for tid, t in all_topics.items() if tid not in done}
    log.info("Already scraped: %d, remaining: %d", len(done), len(to_scrape))

    # Phase 3: Fetch & extract
    log.info("Phase 2: Fetching topics and extracting code blocks ...")
    scraped_count = 0
    with_code_count = 0
    total_code_blocks = 0
    errors = 0

    for i, (tid, meta) in enumerate(to_scrape.items(), 1):
        try:
            result = process_topic(meta)
            scraped_count += 1
            if result:
                with_code_count += 1
                n_blocks = len(result["code_blocks"])
                total_code_blocks += n_blocks
                log.info(
                    "[%d/%d] Topic %d: %d code blocks — %s",
                    i, len(to_scrape), tid, n_blocks, meta.get("title", "")[:60],
                )
            else:
                log.info(
                    "[%d/%d] Topic %d: no relevant code — %s",
                    i, len(to_scrape), tid, meta.get("title", "")[:60],
                )
        except Exception as e:
            errors += 1
            log.error("Error processing topic %d: %s", tid, e, exc_info=True)

        # Progress save every 50 topics
        if i % 50 == 0:
            save_summary({
                "status": "in_progress",
                "topics_discovered": len(all_topics),
                "topics_scraped": scraped_count + len(done),
                "topics_with_code": with_code_count,
                "total_code_blocks": total_code_blocks,
                "errors": errors,
            })

    # Final summary (include previously scraped files)
    final_files = list(OUTPUT_DIR.glob("*.json"))
    final_files = [f for f in final_files if f.name != "summary.json"]

    # Recount from disk for accuracy
    disk_with_code = 0
    disk_total_blocks = 0
    disk_solution_blocks = 0
    language_counts = {"python": 0, "csharp": 0, "unknown": 0}

    for f in final_files:
        try:
            d = json.loads(f.read_text())
            blocks = d.get("code_blocks", [])
            if blocks:
                disk_with_code += 1
                disk_total_blocks += len(blocks)
                for b in blocks:
                    lang = b.get("language", "unknown")
                    language_counts[lang] = language_counts.get(lang, 0) + 1
                    if b.get("is_solution"):
                        disk_solution_blocks += 1
        except Exception:
            pass

    stats = {
        "status": "complete",
        "topics_discovered": len(all_topics),
        "topics_scraped_total": len(final_files),
        "topics_with_code": disk_with_code,
        "total_code_blocks": disk_total_blocks,
        "solution_code_blocks": disk_solution_blocks,
        "language_counts": language_counts,
        "errors": errors,
        "search_queries_used": SEARCH_QUERIES,
        "categories_scraped": CATEGORY_IDS,
    }

    save_summary(stats)

    log.info("=" * 60)
    log.info("DONE")
    log.info("Topics discovered: %d", stats["topics_discovered"])
    log.info("Topics scraped (on disk): %d", stats["topics_scraped_total"])
    log.info("Topics with code: %d", stats["topics_with_code"])
    log.info("Total code blocks: %d", stats["total_code_blocks"])
    log.info("Solution blocks: %d", stats["solution_code_blocks"])
    log.info("Language breakdown: %s", stats["language_counts"])
    log.info("Errors: %d", errors)
    log.info("Output: %s", OUTPUT_DIR)
    log.info("=" * 60)


if __name__ == "__main__":
    main()
