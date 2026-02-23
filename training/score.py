#!/usr/bin/env python3
"""Phase 4.2-4.3: Score and compare baseline vs fine-tuned outputs."""

import json
import ast
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BASELINE_PATH = ROOT / "results" / "baseline_outputs.jsonl"
FINETUNED_PATH = ROOT / "results" / "finetuned_outputs.jsonl"

RHINO_MARKERS = [
    "rhinoscriptsyntax", "Rhino.", "rhino3dm",
    "scriptcontext", "ghpythonlib", "Grasshopper",
]


def extract_code(text: str) -> str:
    """Extract code from markdown code blocks if present, otherwise return as-is."""
    # Try to find ```python ... ``` blocks
    blocks = re.findall(r"```(?:python)?\s*\n(.*?)```", text, re.DOTALL)
    if blocks:
        return "\n\n".join(blocks)
    return text


def check_syntax(code: str) -> bool:
    try:
        ast.parse(code)
        return True
    except SyntaxError:
        return False


def has_rhino_import(code: str) -> bool:
    return any(m in code for m in RHINO_MARKERS)


def code_lines(code: str) -> int:
    return len([l for l in code.strip().splitlines() if l.strip()])


def score_outputs(entries: list, output_key: str) -> dict:
    n = len(entries)
    syntax_ok = 0
    has_import = 0
    total_lines = 0
    total_chars = 0

    for e in entries:
        raw = e[output_key]
        code = extract_code(raw)
        if check_syntax(code):
            syntax_ok += 1
        if has_rhino_import(code):
            has_import += 1
        total_lines += code_lines(code)
        total_chars += len(code)

    return {
        "syntax_valid": syntax_ok,
        "syntax_pct": 100 * syntax_ok / n,
        "has_rhino_import": has_import,
        "import_pct": 100 * has_import / n,
        "avg_lines": total_lines / n,
        "avg_chars": total_chars / n,
    }


def main():
    with open(BASELINE_PATH) as f:
        baseline = [json.loads(l) for l in f if l.strip()]
    with open(FINETUNED_PATH) as f:
        finetuned = [json.loads(l) for l in f if l.strip()]

    n = len(baseline)
    bs = score_outputs(baseline, "baseline_output")
    ft = score_outputs(finetuned, "finetuned_output")

    print("=" * 62)
    print(f"  BASELINE vs FINE-TUNED COMPARISON  ({n} samples)")
    print("=" * 62)
    print(f"{'Metric':<25} {'Baseline':>12} {'Fine-tuned':>12} {'Delta':>10}")
    print("-" * 62)
    print(f"{'Syntax valid':<25} {bs['syntax_pct']:>11.0f}% {ft['syntax_pct']:>11.0f}% {ft['syntax_pct']-bs['syntax_pct']:>+9.0f}%")
    print(f"{'Has Rhino imports':<25} {bs['import_pct']:>11.0f}% {ft['import_pct']:>11.0f}% {ft['import_pct']-bs['import_pct']:>+9.0f}%")
    print(f"{'Avg code lines':<25} {bs['avg_lines']:>12.1f} {ft['avg_lines']:>12.1f} {ft['avg_lines']-bs['avg_lines']:>+10.1f}")
    print(f"{'Avg code chars':<25} {bs['avg_chars']:>12.0f} {ft['avg_chars']:>12.0f} {ft['avg_chars']-bs['avg_chars']:>+10.0f}")
    print("=" * 62)

    # Side-by-side examples
    print("\n\nSAMPLE COMPARISONS")
    print("=" * 62)
    for i, (b, f_) in enumerate(zip(baseline, finetuned)):
        print(f"\n--- Sample {i+1}: {b['instruction'][:70]}...")
        print(f"\n  REFERENCE ({code_lines(b['reference'])} lines):")
        for line in b["reference"].splitlines()[:8]:
            print(f"    {line}")
        if code_lines(b["reference"]) > 8:
            print(f"    ... ({code_lines(b['reference'])-8} more lines)")

        b_code = extract_code(b["baseline_output"])
        print(f"\n  BASELINE ({code_lines(b_code)} lines):")
        for line in b_code.splitlines()[:8]:
            print(f"    {line}")
        if code_lines(b_code) > 8:
            print(f"    ... ({code_lines(b_code)-8} more lines)")

        f_code = extract_code(f_["finetuned_output"])
        print(f"\n  FINE-TUNED ({code_lines(f_code)} lines):")
        for line in f_code.splitlines()[:8]:
            print(f"    {line}")
        if code_lines(f_code) > 8:
            print(f"    ... ({code_lines(f_code)-8} more lines)")


if __name__ == "__main__":
    main()
