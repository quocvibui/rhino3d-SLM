#!/usr/bin/env python3
"""
Agent 4: Generate synthetic (instruction, code) pairs for Rhino3D scripting.

This script generates diverse, validated pairs across multiple categories:
- geometry_creation, geometry_manipulation, geometry_analysis
- scene_management, advanced_sculptural
- code_fixing, code_explanation, api_conversion
- backlabeled (instructions for GitHub code with null instructions)

All output goes to data/raw/synthetic/*.jsonl
Uses data/raw/docs/api_info.json for API validation.
Uses data/raw/github/ for backlabeling.
"""

import json
import os
import re
import ast
from collections import Counter, defaultdict

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SYNTHETIC_DIR = os.path.join(BASE_DIR, "data", "raw", "synthetic")
API_INFO_PATH = os.path.join(BASE_DIR, "data", "raw", "docs", "api_info.json")
GITHUB_DIR = os.path.join(BASE_DIR, "data", "raw", "github")


def build_api_lookup():
    """Parse api_info.json and build validation lookup tables."""
    with open(API_INFO_PATH) as f:
        data = json.load(f)

    classes = {}
    enums = {}

    for entry in data:
        ns = entry.get("namespace", "")
        name = entry.get("name", "")
        dtype = entry.get("dataType", "")
        fqn = f"{ns}.{name}" if ns else name

        if dtype in ("class", "struct"):
            methods = []
            for m in entry.get("methods", []):
                sig = m.get("signature", "")
                parts = sig.split("(")[0].strip().split()
                if len(parts) >= 2:
                    methods.append(parts[-1])

            properties = []
            for p in entry.get("properties", []):
                sig = p.get("signature", "")
                parts = sig.split()
                if len(parts) >= 2:
                    properties.append(parts[-1])

            classes[fqn] = {
                "methods": list(set(methods)),
                "properties": list(set(properties)),
                "has_constructors": len(entry.get("constructors", [])) > 0,
            }
            classes[name] = classes[fqn]

        elif dtype == "enum":
            values = [v.get("name", "") for v in entry.get("values", [])]
            enums[fqn] = values
            enums[name] = values

    return {"classes": classes, "enums": enums}


def backlabel_github_files():
    """Generate instructions for GitHub files with null instructions."""
    results = []
    for f in sorted(os.listdir(GITHUB_DIR)):
        if not f.endswith(".json"):
            continue
        with open(os.path.join(GITHUB_DIR, f)) as fp:
            d = json.load(fp)
        if d.get("instruction") is not None:
            continue

        code = d.get("code", "")
        if not code or len(code.strip()) < 20:
            continue

        func_names = re.findall(r"def (\w+)\s*\(", code)
        class_names = re.findall(r"class (\w+)", code)
        code_lower = code.lower()

        has_rs = "rhinoscriptsyntax" in code or "import rs" in code_lower
        has_rc = "rhino.geometry" in code_lower
        has_rhino3dm = "rhino3dm" in code_lower
        api = "rhinoscriptsyntax" if has_rs else ("RhinoCommon" if has_rc else ("rhino3dm" if has_rhino3dm else "rhinoscriptsyntax"))

        instruction = None
        docstring_match = re.search(r'"""(.+?)"""', code, re.DOTALL)
        if not docstring_match:
            docstring_match = re.search(r"'''(.+?)'''", code, re.DOTALL)
        if docstring_match:
            doc = docstring_match.group(1).strip().split("\n")[0].strip()
            if 10 < len(doc) < 200:
                instruction = doc

        if not instruction and func_names:
            main_func = func_names[0]
            readable = re.sub(r"([A-Z])", r" \1", main_func).replace("_", " ").strip().lower()
            instruction = f"Implement the function '{main_func}' for Rhino scripting"

        if not instruction and class_names:
            instruction = f"Implement the class '{class_names[0]}' for Rhino scripting"

        if not instruction:
            fp_name = d.get("filepath", "")
            base = os.path.splitext(os.path.basename(fp_name))[0]
            readable = re.sub(r"([A-Z])", r" \1", base).replace("_", " ").replace("-", " ").strip()
            instruction = f"Implement a Rhino Python script for: {readable}" if readable else "Write a Rhino Python script"

        tags = []
        if has_rs: tags.append("rhinoscriptsyntax")
        if has_rc: tags.append("RhinoCommon")
        for kw in ["curve", "surface", "mesh", "point", "line", "brep", "layer"]:
            if kw in code_lower:
                tags.append(kw)

        results.append({
            "instruction": instruction,
            "code": code,
            "source": "backlabeled",
            "category": "backlabeled",
            "difficulty": "medium",
            "api": api,
            "tags": list(set(tags)),
            "original_file": f,
            "repo": d.get("repo", ""),
        })

    out_path = os.path.join(SYNTHETIC_DIR, "backlabeled.jsonl")
    with open(out_path, "w") as fp:
        for r in results:
            fp.write(json.dumps(r) + "\n")
    print(f"Wrote {len(results)} backlabeled pairs")
    return len(results)


def generate_summary():
    """Generate summary.json from all JSONL files in synthetic dir."""
    stats = {"total": 0, "by_category": Counter(), "by_difficulty": Counter(), "by_api": Counter(), "by_file": {}}
    for jf in sorted(os.listdir(SYNTHETIC_DIR)):
        if not jf.endswith(".jsonl"):
            continue
        count = 0
        with open(os.path.join(SYNTHETIC_DIR, jf)) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    pair = json.loads(line)
                except json.JSONDecodeError:
                    continue
                count += 1
                stats["total"] += 1
                stats["by_category"][pair.get("category", "unknown")] += 1
                stats["by_difficulty"][pair.get("difficulty", "unknown")] += 1
                stats["by_api"][pair.get("api", "unknown")] += 1
        stats["by_file"][jf] = count

    summary = {
        "total_pairs": stats["total"],
        "by_category": dict(stats["by_category"]),
        "by_difficulty": dict(stats["by_difficulty"]),
        "by_api": dict(stats["by_api"]),
        "by_file": stats["by_file"],
    }
    with open(os.path.join(SYNTHETIC_DIR, "summary.json"), "w") as f:
        json.dump(summary, f, indent=2)
    print(f"Summary: {stats['total']} total pairs")
    return summary


if __name__ == "__main__":
    os.makedirs(SYNTHETIC_DIR, exist_ok=True)
    print("=== Backlabeling GitHub files ===")
    backlabel_github_files()
    print("\n=== Generating summary ===")
    generate_summary()
    print("\nDone. Run scripts/validate.py for validation.")
