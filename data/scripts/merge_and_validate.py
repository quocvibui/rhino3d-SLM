#!/usr/bin/env python3
"""Merge cleaned_pairs.jsonl + synthetic_v2/*.jsonl → pairs.jsonl
Deduplicates on (instruction, code), validates JSON syntax, prints stats.
"""

import json
import ast
import os
import hashlib
from pathlib import Path
from collections import Counter

ROOT = Path(__file__).resolve().parents[1]  # data/
CLEANED = ROOT / "processed" / "cleaned_pairs.jsonl"
SYNTH_DIR = ROOT / "raw" / "synthetic_v2"
OUTPUT = ROOT / "processed" / "pairs.jsonl"


def dedup_key(entry: dict) -> str:
    """Hash on normalised instruction + code to catch exact duplicates."""
    inst = entry.get("instruction", "").strip().lower()
    code = entry.get("code", "").strip()
    return hashlib.sha256(f"{inst}||{code}".encode()).hexdigest()


def validate_json_line(line: str, filepath: str, lineno: int):
    """Parse a single JSONL line. Returns (entry, error_msg | None)."""
    try:
        entry = json.loads(line)
    except json.JSONDecodeError as e:
        return None, f"{filepath}:{lineno} — bad JSON: {e}"
    if not isinstance(entry, dict):
        return None, f"{filepath}:{lineno} — not a JSON object"
    if not entry.get("instruction", "").strip():
        return None, f"{filepath}:{lineno} — empty instruction"
    if not entry.get("code", "").strip():
        return None, f"{filepath}:{lineno} — empty code"
    return entry, None


def check_python_syntax(code: str) -> bool:
    """Return True if code parses as valid Python."""
    try:
        ast.parse(code)
        return True
    except SyntaxError:
        return False


def has_rhino_import(code: str) -> bool:
    """Check whether the code references a known Rhino module."""
    markers = [
        "rhinoscriptsyntax", "Rhino.", "rhino3dm",
        "scriptcontext", "ghpythonlib", "Grasshopper",
    ]
    return any(m in code for m in markers)


def load_jsonl(filepath: Path):
    """Yield (entry, error) tuples from a JSONL file."""
    with open(filepath, "r", encoding="utf-8") as f:
        for lineno, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            entry, err = validate_json_line(line, filepath.name, lineno)
            yield entry, err


def main():
    all_entries = []
    errors = []
    source_counts = Counter()

    # --- Load cleaned_pairs ---
    print(f"Loading {CLEANED.name} ...")
    for entry, err in load_jsonl(CLEANED):
        if err:
            errors.append(err)
        else:
            entry.setdefault("origin_file", CLEANED.name)
            all_entries.append(entry)
            source_counts[CLEANED.name] += 1

    # --- Load synthetic_v2 ---
    synth_files = sorted(SYNTH_DIR.glob("*.jsonl"))
    for sf in synth_files:
        print(f"Loading {sf.name} ...")
        for entry, err in load_jsonl(sf):
            if err:
                errors.append(err)
            else:
                entry.setdefault("origin_file", sf.name)
                all_entries.append(entry)
                source_counts[sf.name] += 1

    total_before = len(all_entries)
    print(f"\nTotal entries loaded: {total_before}")

    # --- Deduplicate ---
    seen = {}
    unique = []
    dupe_count = 0
    for entry in all_entries:
        key = dedup_key(entry)
        if key not in seen:
            seen[key] = True
            unique.append(entry)
        else:
            dupe_count += 1
    all_entries = unique

    # --- Python syntax check ---
    syntax_ok = 0
    syntax_fail = 0
    syntax_fail_examples = []
    for entry in all_entries:
        if check_python_syntax(entry["code"]):
            syntax_ok += 1
        else:
            syntax_fail += 1
            if len(syntax_fail_examples) < 5:
                syntax_fail_examples.append(
                    (entry.get("origin_file", "?"), entry["instruction"][:80])
                )

    # --- Rhino import check ---
    has_import = sum(1 for e in all_entries if has_rhino_import(e["code"]))

    # --- Write output ---
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT, "w", encoding="utf-8") as f:
        for entry in all_entries:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    # --- Stats ---
    avg_inst = sum(len(e["instruction"]) for e in all_entries) / len(all_entries)
    avg_code = sum(len(e["code"]) for e in all_entries) / len(all_entries)
    code_lines = [e["code"].count("\n") + 1 for e in all_entries]
    avg_lines = sum(code_lines) / len(code_lines)

    # Source breakdown
    api_counts = Counter(e.get("api", "unknown") for e in all_entries)
    cat_counts = Counter(e.get("category", e.get("source", "unknown")) for e in all_entries)

    print("\n" + "=" * 60)
    print("MERGE & VALIDATION REPORT")
    print("=" * 60)
    print(f"Files loaded:           {1 + len(synth_files)}")
    print(f"  cleaned_pairs.jsonl:  {source_counts[CLEANED.name]}")
    for sf in synth_files:
        print(f"  {sf.name}: {source_counts[sf.name]}")
    print(f"\nTotal before dedup:     {total_before}")
    print(f"Duplicates removed:     {dupe_count}")
    print(f"Final unique pairs:     {len(all_entries)}")
    print(f"\nJSON parse errors:      {len(errors)}")
    print(f"Python syntax valid:    {syntax_ok} ({100*syntax_ok/len(all_entries):.1f}%)")
    print(f"Python syntax invalid:  {syntax_fail} ({100*syntax_fail/len(all_entries):.1f}%)")
    if syntax_fail_examples:
        print("  Examples of syntax failures:")
        for origin, inst in syntax_fail_examples:
            print(f"    [{origin}] {inst}")
    print(f"Has Rhino imports:      {has_import} ({100*has_import/len(all_entries):.1f}%)")
    print(f"\nAvg instruction length: {avg_inst:.0f} chars")
    print(f"Avg code length:        {avg_code:.0f} chars")
    print(f"Avg code lines:         {avg_lines:.1f}")
    print(f"\nAPI distribution:")
    for api, cnt in api_counts.most_common():
        print(f"  {api}: {cnt}")
    print(f"\nCategory / source distribution:")
    for cat, cnt in cat_counts.most_common():
        print(f"  {cat}: {cnt}")
    print(f"\nOutput written to: {OUTPUT}")
    print("=" * 60)

    if errors:
        print(f"\n⚠ {len(errors)} JSON errors encountered:")
        for e in errors[:10]:
            print(f"  {e}")


if __name__ == "__main__":
    main()
