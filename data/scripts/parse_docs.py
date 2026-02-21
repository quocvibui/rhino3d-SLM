#!/usr/bin/env python3
"""Agent 3 — Parse Official Docs + Samples into (instruction, code) pairs.

Reads from data/raw/docs/ and outputs JSONL files:
  - api_pairs.jsonl          (from api_info.json)
  - sample_pairs.jsonl       (from rhino-developer-samples)
  - rs_mapping_pairs.jsonl   (from rhinoscriptsyntax source)
  - reference_pairs.jsonl    (command reference Q&A)
  - summary.json             (stats)
"""

import json
import os
import re
import ast
import textwrap
from pathlib import Path
from collections import defaultdict

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
BASE = Path(__file__).resolve().parent.parent  # data/
RAW_DOCS = BASE / "raw" / "docs"
API_JSON = RAW_DOCS / "api_info.json"
SAMPLES_DIR = RAW_DOCS / "samples"
RS_SRC_DIR = RAW_DOCS / "rhinoscriptsyntax_src" / "Scripts" / "rhinoscript"
STUBS_DIR = RAW_DOCS / "stubs"

OUT_API = RAW_DOCS / "api_pairs.jsonl"
OUT_SAMPLES = RAW_DOCS / "sample_pairs.jsonl"
OUT_RS = RAW_DOCS / "rs_mapping_pairs.jsonl"
OUT_REF = RAW_DOCS / "reference_pairs.jsonl"
OUT_SUMMARY = RAW_DOCS / "summary.json"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def write_jsonl(path: Path, records: list[dict]):
    with open(path, "w", encoding="utf-8") as f:
        for rec in records:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    print(f"  Wrote {len(records)} pairs → {path.name}")


def clean_summary(text: str | None) -> str:
    if not text:
        return ""
    text = re.sub(r"<[^>]+>", "", text)  # strip HTML tags
    text = re.sub(r"\s+", " ", text).strip()
    return text


def parse_csharp_type(sig: str) -> str:
    """Extract the return type and method name from a C#-style signature."""
    return sig.strip()


def csharp_type_to_python(t: str) -> str:
    """Very rough C# → Python type hint mapping."""
    mapping = {
        "void": "None",
        "bool": "bool",
        "Boolean": "bool",
        "System.Boolean": "bool",
        "int": "int",
        "Int32": "int",
        "System.Int32": "int",
        "double": "float",
        "Double": "float",
        "System.Double": "float",
        "float": "float",
        "Single": "float",
        "string": "str",
        "String": "str",
        "System.String": "str",
        "object": "object",
        "System.Object": "object",
    }
    t = t.strip().rstrip("[]")
    return mapping.get(t, t)


def param_default(ptype: str) -> str:
    """Generate a plausible default value placeholder for a parameter type."""
    ptype_lower = ptype.lower()
    if "point3d" in ptype_lower:
        return "rg.Point3d(0, 0, 0)"
    if "vector3d" in ptype_lower:
        return "rg.Vector3d(0, 0, 1)"
    if "plane" in ptype_lower:
        return "rg.Plane.WorldXY"
    if "interval" in ptype_lower:
        return "rg.Interval(0, 1)"
    if "bool" in ptype_lower:
        return "True"
    if "int" in ptype_lower:
        return "3"
    if "double" in ptype_lower or "float" in ptype_lower or "single" in ptype_lower:
        return "1.0"
    if "string" in ptype_lower or "str" in ptype_lower:
        return '"value"'
    if "color" in ptype_lower:
        return "System.Drawing.Color.Black"
    if "brep" in ptype_lower:
        return "brep"
    if "curve" in ptype_lower:
        return "curve"
    if "surface" in ptype_lower:
        return "surface"
    if "mesh" in ptype_lower:
        return "mesh"
    if "guid" in ptype_lower:
        return "System.Guid.Empty"
    if "ienumerable" in ptype_lower or "list" in ptype_lower or "[]" in ptype:
        return "[]"
    return "None"


def extract_method_name(sig: str) -> str:
    """Extract method name from C# signature like 'Point3d ClosestPoint(Point3d testPoint)'."""
    m = re.match(r"[\w\.\[\]<>,\s]+?\s+(\w+)\s*\(", sig)
    if m:
        return m.group(1)
    m = re.match(r"(\w+)\s*\(", sig)
    if m:
        return m.group(1)
    return sig.split("(")[0].strip().split()[-1] if "(" in sig else sig.strip()


def extract_return_type(sig: str) -> str:
    """Extract return type from signature."""
    parts = sig.split("(")[0].strip().split()
    if len(parts) >= 2:
        return parts[0]
    return "void"


# ---------------------------------------------------------------------------
# 1. Parse API JSON → api_pairs.jsonl
# ---------------------------------------------------------------------------
def parse_api_json() -> list[dict]:
    print("Parsing api_info.json ...")
    with open(API_JSON, encoding="utf-8") as f:
        data = json.load(f)

    pairs = []
    class_names = set()
    geometry_classes = set()

    for item in data:
        dtype = item.get("dataType")
        if dtype not in ("class", "struct"):
            continue

        ns = item.get("namespace", "")
        name = item.get("name", "")
        fqn = f"{ns}.{name}" if ns else name
        summary = clean_summary(item.get("summary", ""))
        class_names.add(fqn)
        if "Geometry" in ns:
            geometry_classes.add(fqn)

        is_geometry = "Geometry" in ns

        # --- Constructors ---
        for ctor in item.get("constructors", []):
            if ctor.get("protected"):
                continue
            ctor_summary = clean_summary(ctor.get("summary", ""))
            params = ctor.get("parameters", [])
            if not ctor_summary and not params:
                continue

            instruction = f"Create a new {name} object"
            if ctor_summary:
                instruction += f": {ctor_summary}"

            # Build code
            param_strs = []
            for p in params:
                pt = p.get("type", "object")
                param_strs.append(param_default(pt))

            import_line = f"import Rhino.Geometry as rg" if is_geometry else f"import {ns}"
            code_lines = [import_line, ""]
            if is_geometry:
                code_lines.append(f"obj = rg.{name}({', '.join(param_strs)})")
            else:
                code_lines.append(f"obj = {fqn}({', '.join(param_strs)})")

            pairs.append({
                "instruction": instruction,
                "code": "\n".join(code_lines),
                "source": "api_docs",
                "api": "RhinoCommon",
                "class": fqn,
                "method": "__init__",
                "synthetic_from_docs": True,
                "tags": _tags_for_class(ns, name),
            })

        # --- Static Methods ---
        for method in item.get("methods", []):
            mods = method.get("modifiers", [])
            if method.get("protected") or "private" in mods:
                continue
            is_static = "static" in mods
            method_name = extract_method_name(method.get("signature", ""))
            method_summary = clean_summary(method.get("summary", ""))
            ret_type = extract_return_type(method.get("signature", ""))
            params = method.get("parameters", [])

            if not method_summary:
                continue

            instruction = f"Use RhinoCommon {name}.{method_name} to {method_summary}"
            if len(instruction) > 300:
                instruction = instruction[:297] + "..."

            # Build code
            param_strs = []
            for p in params:
                pt = p.get("type", "object")
                param_strs.append(param_default(pt))

            import_line = f"import Rhino.Geometry as rg" if is_geometry else f"import {ns}"
            code_lines = [import_line, ""]

            if is_static:
                if is_geometry:
                    call = f"result = rg.{name}.{method_name}({', '.join(param_strs)})"
                else:
                    call = f"result = {fqn}.{method_name}({', '.join(param_strs)})"
            else:
                if is_geometry:
                    code_lines.append(f"# Assume 'obj' is an existing {name} instance")
                    call = f"result = obj.{method_name}({', '.join(param_strs)})"
                else:
                    code_lines.append(f"# Assume 'obj' is an existing {fqn} instance")
                    call = f"result = obj.{method_name}({', '.join(param_strs)})"

            code_lines.append(call)

            if ret_type != "void":
                code_lines.append(f"# Returns: {csharp_type_to_python(ret_type)}")

            pairs.append({
                "instruction": instruction,
                "code": "\n".join(code_lines),
                "source": "api_docs",
                "api": "RhinoCommon",
                "class": fqn,
                "method": method_name,
                "synthetic_from_docs": True,
                "tags": _tags_for_class(ns, name) + [method_name],
            })

        # --- Properties ---
        for prop in item.get("properties", []):
            if prop.get("protected"):
                continue
            prop_sig = prop.get("signature", "")
            prop_summary = clean_summary(prop.get("summary", ""))
            prop_access = prop.get("property", [])

            if not prop_summary:
                continue

            prop_name = prop_sig.strip().split()[-1] if prop_sig else ""
            if not prop_name:
                continue

            if "get" in prop_access:
                instruction = f"Get the {prop_name} property of a {name} object in RhinoCommon: {prop_summary}"
                if len(instruction) > 300:
                    instruction = instruction[:297] + "..."

                import_line = f"import Rhino.Geometry as rg" if is_geometry else f"import {ns}"
                code_lines = [
                    import_line,
                    "",
                    f"# Assume 'obj' is an existing {name} instance",
                    f"value = obj.{prop_name}",
                    f"print(value)",
                ]

                pairs.append({
                    "instruction": instruction,
                    "code": "\n".join(code_lines),
                    "source": "api_docs",
                    "api": "RhinoCommon",
                    "class": fqn,
                    "method": prop_name,
                    "synthetic_from_docs": True,
                    "tags": _tags_for_class(ns, name) + ["property", prop_name],
                })

    return pairs, class_names, geometry_classes


def _tags_for_class(ns: str, name: str) -> list[str]:
    tags = ["RhinoCommon"]
    name_lower = name.lower()
    if "Geometry" in ns:
        tags.append("geometry")
    if any(k in name_lower for k in ("curve", "line", "arc", "circle", "polyline", "nurbs")):
        tags.append("curve")
    if any(k in name_lower for k in ("surface", "brep", "nurbs")):
        tags.append("surface")
    if "mesh" in name_lower:
        tags.append("mesh")
    if "point" in name_lower:
        tags.append("point")
    if "vector" in name_lower:
        tags.append("vector")
    if "transform" in name_lower:
        tags.append("transform")
    if "display" in ns.lower():
        tags.append("display")
    return tags


# ---------------------------------------------------------------------------
# 2. Parse Official Samples → sample_pairs.jsonl
# ---------------------------------------------------------------------------
def parse_samples() -> list[dict]:
    print("Parsing official samples ...")
    pairs = []

    sample_dirs = [
        (SAMPLES_DIR / "rhinocommon" / "py", "RhinoCommon"),
        (SAMPLES_DIR / "rhinopython", "rhinoscriptsyntax"),
        (SAMPLES_DIR / "compute" / "py", "compute"),
        (SAMPLES_DIR / "rhino3dm" / "py", "rhino3dm"),
    ]

    for sdir, api in sample_dirs:
        if not sdir.exists():
            print(f"  Skipping {sdir} (not found)")
            continue

        py_files = list(sdir.rglob("*.py"))
        print(f"  Found {len(py_files)} .py files in {sdir.name}/")

        for pyf in py_files:
            try:
                code = pyf.read_text(encoding="utf-8", errors="replace")
            except Exception:
                continue

            if len(code.strip()) < 20:
                continue

            instruction = _extract_instruction_from_sample(pyf.name, code)
            if not instruction:
                continue

            tags = {api}
            if "rhinoscriptsyntax" in code or "import rs" in code:
                tags.add("rhinoscriptsyntax")
            if "Rhino.Geometry" in code or "import rg" in code:
                tags.add("geometry")
            if "RhinoCommon" not in tags and "Rhino." in code:
                tags.add("RhinoCommon")
            tags = sorted(tags)

            pairs.append({
                "instruction": instruction,
                "code": code.strip(),
                "source": "official_samples",
                "api": api,
                "file": pyf.name,
                "tags": tags,
            })

    return pairs


def _extract_instruction_from_sample(filename: str, code: str) -> str:
    """Try to extract a human-readable instruction from a sample script."""
    # Try docstring
    try:
        tree = ast.parse(code)
        ds = ast.get_docstring(tree)
        if ds and len(ds) > 10:
            return ds.split("\n")[0].strip()
    except SyntaxError:
        pass

    # Try top comment block (skip boilerplate lines like filenames, copyrights, licenses)
    lines = code.split("\n")
    comment_lines = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("#") and not stripped.startswith("#!"):
            text = stripped.lstrip("# ").strip()
            # Skip boilerplate
            if any(kw in text.lower() for kw in ("copyright", "license", ".py", "########", "see license")):
                continue
            if text:
                comment_lines.append(text)
        elif stripped and not stripped.startswith("#"):
            break

    if comment_lines:
        first_meaningful = " ".join(comment_lines[:3])
        if len(first_meaningful) > 10:
            return first_meaningful[:300]

    # Fall back to filename
    name = filename.replace(".py", "").replace("Sample", "").replace("_", " ")
    # CamelCase → words
    name = re.sub(r"([a-z])([A-Z])", r"\1 \2", name).strip()
    if len(name) > 5:
        return f"Rhino sample: {name}"

    return ""


# ---------------------------------------------------------------------------
# 3. Parse rhinoscriptsyntax Source → rs_mapping_pairs.jsonl
# ---------------------------------------------------------------------------
def parse_rhinoscriptsyntax() -> list[dict]:
    print("Parsing rhinoscriptsyntax source ...")
    pairs = []

    if not RS_SRC_DIR.exists():
        print(f"  WARNING: {RS_SRC_DIR} not found")
        return pairs

    py_files = sorted(RS_SRC_DIR.glob("*.py"))
    print(f"  Found {len(py_files)} source files")

    for pyf in py_files:
        if pyf.name.startswith("__"):
            continue
        try:
            source = pyf.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue

        module_name = pyf.stem  # e.g. "curve", "surface", "mesh"

        try:
            tree = ast.parse(source)
        except SyntaxError:
            print(f"  Skipping {pyf.name} (syntax error)")
            continue

        for node in ast.walk(tree):
            if not isinstance(node, ast.FunctionDef):
                continue

            func_name = node.name
            if func_name.startswith("_"):
                continue

            docstring = ast.get_docstring(node) or ""
            first_line = docstring.split("\n")[0].strip() if docstring else ""

            # Extract function body source
            try:
                func_source = ast.get_source_segment(source, node)
            except Exception:
                start = node.lineno - 1
                end = node.end_lineno if hasattr(node, "end_lineno") and node.end_lineno else start + 20
                func_source = "\n".join(source.split("\n")[start:end])

            if not func_source or len(func_source) < 30:
                continue

            # Build instruction
            if first_line and len(first_line) > 10:
                instruction = f"rhinoscriptsyntax rs.{func_name}: {first_line}"
            else:
                readable = func_name.replace("_", " ")
                instruction = f"Use rhinoscriptsyntax rs.{func_name} to {readable}"

            # Build code showing usage
            args = []
            for arg in node.args.args:
                arg_name = arg.arg
                if arg_name == "self":
                    continue
                args.append(arg_name)

            usage_code = f"import rhinoscriptsyntax as rs\n\nresult = rs.{func_name}({', '.join(args)})"

            # Also include the implementation for mapping understanding
            full_code = f"# Usage:\n{usage_code}\n\n# Implementation (shows RhinoCommon mapping):\n{func_source}"

            tags = ["rhinoscriptsyntax", module_name]
            if "Rhino.Geometry" in func_source or "scriptcontext" in func_source:
                tags.append("RhinoCommon")

            pairs.append({
                "instruction": instruction,
                "code": full_code,
                "source": "rhinoscriptsyntax_source",
                "api": "rhinoscriptsyntax",
                "function": f"rs.{func_name}",
                "module": module_name,
                "tags": tags,
            })

    return pairs


# ---------------------------------------------------------------------------
# 4. Build Command Reference Pairs → reference_pairs.jsonl
# ---------------------------------------------------------------------------
TASK_CATEGORIES = {
    "creating_curves": {
        "keywords": ["curve", "line", "arc", "circle", "polyline", "ellipse", "helix", "spiral", "nurbs"],
        "question": "List all methods to create curves in RhinoCommon",
    },
    "creating_surfaces": {
        "keywords": ["surface", "brep", "loft", "sweep", "extrude", "revolve", "planar"],
        "question": "List all methods to create surfaces in RhinoCommon",
    },
    "creating_meshes": {
        "keywords": ["mesh", "triangulate", "quad"],
        "question": "List all methods to create meshes in RhinoCommon",
    },
    "transformations": {
        "keywords": ["transform", "move", "rotate", "scale", "mirror", "orient", "shear", "project"],
        "question": "List all transformation methods in RhinoCommon",
    },
    "analysis": {
        "keywords": ["area", "volume", "length", "closest", "distance", "intersect", "contains", "bounds"],
        "question": "List all geometry analysis methods in RhinoCommon",
    },
    "boolean_operations": {
        "keywords": ["boolean", "union", "difference", "intersection", "split", "trim"],
        "question": "List all boolean and splitting operations in RhinoCommon",
    },
    "points_vectors": {
        "keywords": ["point", "vector", "plane", "coordinate"],
        "question": "List all point and vector operations in RhinoCommon",
    },
}


def build_reference_pairs(api_data: list[dict]) -> list[dict]:
    print("Building command reference pairs ...")
    pairs = []

    # Group methods by class for method listing pairs
    classes_with_methods = defaultdict(list)
    method_by_task = defaultdict(list)

    # Only include Geometry-related namespaces for task categorization
    RELEVANT_NS = {"Rhino.Geometry", "Rhino.Geometry.Intersect", "Rhino.Geometry.Collections",
                    "Rhino.Geometry.Morphs", "Rhino.Geometry.MeshingParameters"}

    for item in api_data:
        if item.get("dataType") not in ("class", "struct"):
            continue
        ns = item.get("namespace", "")
        name = item.get("name", "")
        fqn = f"{ns}.{name}" if ns else name

        for method in item.get("methods", []):
            if method.get("protected"):
                continue
            sig = method.get("signature", "")
            summary = clean_summary(method.get("summary", ""))
            method_name = extract_method_name(sig)
            entry = f"  {name}.{method_name}: {summary}" if summary else f"  {name}.{method_name}"

            classes_with_methods[fqn].append((method_name, summary, sig))

            # Only categorize methods from Geometry-related namespaces
            if ns not in RELEVANT_NS and not ns.startswith("Rhino.Geometry"):
                continue
            combined = f"{name} {method_name} {summary}".lower()
            for task, info in TASK_CATEGORIES.items():
                if any(kw in combined for kw in info["keywords"]):
                    method_by_task[task].append(entry)

    # Task-based reference pairs
    for task, info in TASK_CATEGORIES.items():
        methods = method_by_task.get(task, [])
        if not methods:
            continue
        code = "\n".join(methods[:50])  # cap at 50
        pairs.append({
            "instruction": info["question"],
            "code": f"# RhinoCommon methods for {task.replace('_', ' ')}:\n{code}",
            "source": "reference",
            "api": "RhinoCommon",
            "tags": ["reference", task],
        })

    # Per-class method listing pairs (for Geometry classes with 3+ methods)
    for fqn, methods in classes_with_methods.items():
        if "Geometry" not in fqn:
            continue
        if len(methods) < 3:
            continue
        class_name = fqn.split(".")[-1]
        method_list = "\n".join(
            f"  - {m[0]}({_sig_params(m[2])}): {m[1]}" for m in methods[:30]
        )
        pairs.append({
            "instruction": f"What methods are available on RhinoCommon {class_name}?",
            "code": f"# {fqn} methods:\n{method_list}",
            "source": "reference",
            "api": "RhinoCommon",
            "class": fqn,
            "tags": ["reference", "method_list", class_name],
        })

    # Parameter signature pairs for common rs.* functions
    pairs.extend(_build_rs_signature_pairs())

    return pairs


def _sig_params(sig: str) -> str:
    """Extract just the parameter names from a signature."""
    m = re.search(r"\((.+)\)", sig)
    if not m:
        return ""
    params = m.group(1)
    # Extract param names (last word before comma or end)
    names = []
    for part in params.split(","):
        part = part.strip()
        tokens = part.split()
        if tokens:
            names.append(tokens[-1])
    return ", ".join(names)


def _build_rs_signature_pairs() -> list[dict]:
    """Build 'what parameters does rs.X take?' pairs from rhinoscriptsyntax source."""
    pairs = []
    if not RS_SRC_DIR.exists():
        return pairs

    for pyf in sorted(RS_SRC_DIR.glob("*.py")):
        if pyf.name.startswith("__"):
            continue
        try:
            source = pyf.read_text(encoding="utf-8", errors="replace")
            tree = ast.parse(source)
        except Exception:
            continue

        for node in ast.walk(tree):
            if not isinstance(node, ast.FunctionDef):
                continue
            if node.name.startswith("_"):
                continue

            docstring = ast.get_docstring(node) or ""
            if len(docstring) < 20:
                continue

            # Build parameter info
            args_info = []
            for arg in node.args.args:
                if arg.arg == "self":
                    continue
                args_info.append(arg.arg)

            defaults = node.args.defaults
            # Pair defaults with the last N args
            num_defaults = len(defaults)
            for i, d in enumerate(defaults):
                idx = len(args_info) - num_defaults + i
                if 0 <= idx < len(args_info):
                    try:
                        args_info[idx] = f"{args_info[idx]}=<optional>"
                    except Exception:
                        pass

            instruction = f"What parameters does rs.{node.name} take?"
            first_para = docstring.split("\n\n")[0].strip()
            code = f"# rs.{node.name}({', '.join(args_info)})\n# {first_para}"

            pairs.append({
                "instruction": instruction,
                "code": code,
                "source": "reference",
                "api": "rhinoscriptsyntax",
                "function": f"rs.{node.name}",
                "tags": ["reference", "signature", "rhinoscriptsyntax"],
            })

    return pairs


# ---------------------------------------------------------------------------
# 5. Summary stats
# ---------------------------------------------------------------------------
def build_summary(api_pairs, sample_pairs, rs_pairs, ref_pairs, class_names, geometry_classes):
    classes_with_examples = set()
    for p in api_pairs:
        c = p.get("class", "")
        if c:
            classes_with_examples.add(c)

    geo_with_examples = classes_with_examples & geometry_classes

    summary = {
        "total_pairs": len(api_pairs) + len(sample_pairs) + len(rs_pairs) + len(ref_pairs),
        "api_pairs": len(api_pairs),
        "sample_pairs": len(sample_pairs),
        "rs_mapping_pairs": len(rs_pairs),
        "reference_pairs": len(ref_pairs),
        "total_classes_in_api": len(class_names),
        "classes_with_examples": len(classes_with_examples),
        "geometry_classes_total": len(geometry_classes),
        "geometry_classes_with_examples": len(geo_with_examples),
        "api_coverage_pct": round(len(classes_with_examples) / max(len(class_names), 1) * 100, 1),
        "geometry_coverage_pct": round(len(geo_with_examples) / max(len(geometry_classes), 1) * 100, 1),
    }
    return summary


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    print("=" * 60)
    print("Agent 3: Parse Official Docs + Samples")
    print("=" * 60)

    # Step 1: Parse API JSON
    api_pairs, class_names, geometry_classes = parse_api_json()
    write_jsonl(OUT_API, api_pairs)

    # Step 2: Parse samples
    sample_pairs = parse_samples()
    write_jsonl(OUT_SAMPLES, sample_pairs)

    # Step 3: Parse rhinoscriptsyntax
    rs_pairs = parse_rhinoscriptsyntax()
    write_jsonl(OUT_RS, rs_pairs)

    # Step 4: Build reference pairs
    with open(API_JSON, encoding="utf-8") as f:
        raw_api = json.load(f)
    ref_pairs = build_reference_pairs(raw_api)
    write_jsonl(OUT_REF, ref_pairs)

    # Step 5: Summary
    summary = build_summary(api_pairs, sample_pairs, rs_pairs, ref_pairs, class_names, geometry_classes)
    with open(OUT_SUMMARY, "w") as f:
        json.dump(summary, f, indent=2)

    print("\n" + "=" * 60)
    print("Summary:")
    for k, v in summary.items():
        print(f"  {k}: {v}")
    print("=" * 60)
    print("Done!")


if __name__ == "__main__":
    main()
