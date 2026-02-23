#!/usr/bin/env python3
"""Generate synthetic_v2 dataset for Rhino3D fine-tuning.

Generates 2500+ validated (instruction, code) pairs across 6 categories:
1. Multi-step geometry workflows
2. "How do I..." user questions
3. Grasshopper Python component patterns
4. rhino3dm standalone scripts
5. Code fixing/debugging
6. Common design workflows

All code validated with ast.parse() and import checking.
Output: data/raw/synthetic_v2/*.jsonl
"""

import json
import ast
import os
import sys
import re
from pathlib import Path
from collections import Counter

OUTPUT_DIR = Path("data/raw/synthetic_v2")
VALID_IMPORTS = {
    "rhinoscriptsyntax", "Rhino", "Rhino.Geometry", "Rhino.Input",
    "Rhino.DocObjects", "Rhino.Commands", "scriptcontext", "rhino3dm",
    "ghpythonlib", "ghpythonlib.components", "ghpythonlib.treehelpers",
    "Grasshopper", "Grasshopper.Kernel", "Grasshopper.DataTree",
    "System", "System.Collections.Generic", "Rhino.Collections",
    "Rhino.Display", "Rhino.Render",
}


def make(instruction, code, category, difficulty, api, tags):
    """Create a standardized pair dict."""
    return {
        "instruction": instruction,
        "code": code,
        "source": "synthetic",
        "category": category,
        "difficulty": difficulty,
        "api": api,
        "tags": tags,
    }


def validate_syntax(code):
    """Check Python syntax via ast.parse(). Returns (valid, error_msg)."""
    try:
        ast.parse(code)
        return True, ""
    except SyntaxError as e:
        return False, f"SyntaxError: {e.msg} (line {e.lineno})"


def check_imports(code):
    """Check code has at least one Rhino-related import."""
    rhino_patterns = [
        r"import\s+rhinoscriptsyntax",
        r"import\s+Rhino",
        r"import\s+scriptcontext",
        r"import\s+rhino3dm",
        r"import\s+ghpythonlib",
        r"from\s+Grasshopper",
        r"from\s+Rhino",
        r"import\s+Grasshopper",
        r"from\s+ghpythonlib",
        r"from\s+scriptcontext",
        r"from\s+rhino3dm",
        r"from\s+System",
    ]
    for pat in rhino_patterns:
        if re.search(pat, code):
            return True
    return False


def validate_pair(pair):
    """Full validation of a pair. Returns (valid_syntax, valid_imports)."""
    code = pair["code"]
    # For code_fixing category, the "code" is the FIXED version — validate that
    syn_ok, syn_err = validate_syntax(code)
    imp_ok = check_imports(code)
    return syn_ok, imp_ok, syn_err


# ============================================================
# Import category generators (loaded dynamically)
# ============================================================

def load_category(name):
    """Import a category generator module."""
    import importlib.util
    script_dir = Path(__file__).parent
    mod_path = script_dir / "synth_v2" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, mod_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.generate()


CATEGORIES = [
    "multi_step_workflows",
    "how_do_i_questions",
    "grasshopper_python",
    "rhino3dm_standalone",
    "code_fixing",
    "design_workflows",
    "template_expander",
    "expanded_patterns",
    "expanded_patterns_2",
    "expanded_patterns_3",
]


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    total_pairs = 0
    total_valid_syntax = 0
    total_valid_imports = 0
    total_invalid = []
    category_stats = {}

    for cat_name in CATEGORIES:
        print(f"\n{'='*60}")
        print(f"Generating: {cat_name}")
        print(f"{'='*60}")

        pairs = load_category(cat_name)
        valid_count = 0
        import_count = 0
        invalid_entries = []

        for i, pair in enumerate(pairs):
            syn_ok, imp_ok, syn_err = validate_pair(pair)
            if syn_ok:
                valid_count += 1
            else:
                invalid_entries.append({
                    "index": i,
                    "instruction": pair["instruction"][:80],
                    "error": syn_err,
                })
            if imp_ok:
                import_count += 1

        # Write JSONL
        out_file = OUTPUT_DIR / f"{cat_name}.jsonl"
        with open(out_file, "w") as f:
            for pair in pairs:
                f.write(json.dumps(pair, ensure_ascii=False) + "\n")

        print(f"  Total pairs: {len(pairs)}")
        print(f"  Valid syntax: {valid_count}/{len(pairs)} ({100*valid_count/max(len(pairs),1):.1f}%)")
        print(f"  Valid imports: {import_count}/{len(pairs)} ({100*import_count/max(len(pairs),1):.1f}%)")
        if invalid_entries:
            print(f"  INVALID entries ({len(invalid_entries)}):")
            for inv in invalid_entries[:5]:
                print(f"    [{inv['index']}] {inv['error']} - {inv['instruction']}")

        category_stats[cat_name] = {
            "total": len(pairs),
            "valid_syntax": valid_count,
            "valid_imports": import_count,
            "invalid_count": len(invalid_entries),
        }
        total_pairs += len(pairs)
        total_valid_syntax += valid_count
        total_valid_imports += import_count
        total_invalid.extend(invalid_entries)

    # Write validation report
    report = {
        "total_pairs": total_pairs,
        "total_valid_syntax": total_valid_syntax,
        "total_valid_imports": total_valid_imports,
        "syntax_pass_rate": round(100 * total_valid_syntax / max(total_pairs, 1), 2),
        "import_pass_rate": round(100 * total_valid_imports / max(total_pairs, 1), 2),
        "invalid_entries": total_invalid,
        "category_stats": category_stats,
    }
    with open(OUTPUT_DIR / "validation_report.json", "w") as f:
        json.dump(report, f, indent=2)

    # Write summary
    summary = {
        "total_pairs": total_pairs,
        "categories": {k: v["total"] for k, v in category_stats.items()},
        "validation": {
            "syntax_pass_rate": report["syntax_pass_rate"],
            "import_pass_rate": report["import_pass_rate"],
        },
    }
    with open(OUTPUT_DIR / "summary.json", "w") as f:
        json.dump(summary, f, indent=2)

    print(f"\n{'='*60}")
    print(f"SUMMARY")
    print(f"{'='*60}")
    print(f"Total pairs generated: {total_pairs}")
    print(f"Syntax valid: {total_valid_syntax}/{total_pairs} ({report['syntax_pass_rate']}%)")
    print(f"Import valid: {total_valid_imports}/{total_pairs} ({report['import_pass_rate']}%)")
    print(f"Output directory: {OUTPUT_DIR}")
    for cat, stats in category_stats.items():
        print(f"  {cat}: {stats['total']} pairs")


if __name__ == "__main__":
    main()
