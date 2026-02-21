#!/usr/bin/env python3
"""
Dataset cleaning script for Rhino3D fine-tuning dataset.

Reads all raw data sources, applies quality filters, rewrites weak instructions,
deduplicates, and outputs:
  - data/processed/cleaned_pairs.jsonl  (kept entries)
  - data/excluded/                       (removed entries, by reason)
  - data/processed/cleaning_stats.json   (statistics)
"""

import json
import os
import re
import hashlib
from pathlib import Path
from collections import defaultdict

BASE = Path(__file__).resolve().parent.parent  # data/
RAW = BASE / "raw"
PROCESSED = BASE / "processed"
EXCLUDED = BASE / "excluded"

PROCESSED.mkdir(exist_ok=True)
EXCLUDED.mkdir(exist_ok=True)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def load_jsonl(path):
    """Load a JSONL file, returning list of dicts."""
    entries = []
    with open(path) as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                entries.append(json.loads(line))
            except json.JSONDecodeError:
                print(f"  WARNING: bad JSON at {path.name}:{line_num}")
    return entries


def write_jsonl(path, entries):
    with open(path, "w") as f:
        for e in entries:
            f.write(json.dumps(e, ensure_ascii=False) + "\n")


def code_hash(code):
    """Normalize whitespace and hash code for dedup."""
    normalized = re.sub(r'\s+', ' ', code.strip())
    return hashlib.md5(normalized.encode()).hexdigest()


def instruction_hash(instr):
    """Normalize instruction for dedup."""
    normalized = re.sub(r'\s+', ' ', instr.strip().lower())
    return hashlib.md5(normalized.encode()).hexdigest()


# ---------------------------------------------------------------------------
# Sample pairs: instruction rewriting map
# ---------------------------------------------------------------------------

SAMPLE_INSTRUCTION_REWRITES = {
    "SampleBlockLeader.py":
        "Create a leader annotation that labels a block instance with its definition name",
    "SampleArrayCrv.py":
        "Array selected objects along a curve, orienting each copy to follow the curve's frame",
    "SampleSynchronizeRenderColors.py":
        "Synchronize all objects' render material colors to match their display colors",
    "SampleRebuildSrfDeviation.py":
        "Rebuild a surface to a target point count and report the maximum deviation from the original",
    "SampleGetLiteralString.py":
        "Prompt the user for a literal string input using a custom GetString command",
    "SampleTraverseBrepFace.py":
        "Traverse the faces of a Brep and print info about each face's underlying surface type",
    "SampleCircleRadius.py":
        "Interactively draw a circle by picking center and radius with dynamic preview",
    "SampleAddRenderMaterials.py":
        "Add physically-based render materials (PBR) to objects in the document",
    "SampleShowToolbarGroup.py":
        "Show or toggle a named toolbar group in the Rhino UI",
    "SampleDrawExtrudedCurves.py":
        "Use a display conduit to draw curves as extruded shapes in the viewport",
    "SampleDrawBrepEdges.py":
        "Use a display conduit to draw Brep edges with custom colors in the viewport",
    "SampleEtoPushPickButtonDialog.py":
        "Create an Eto dialog with a button that lets the user pick a point in the viewport",
    "SampleGetArc.py":
        "Interactively get an arc from the user with start, end, and point on arc",
    "SampleSphereStyles.py":
        "Create spheres using different RhinoCommon construction methods (center+radius, 2pt, 3pt, 4pt, fit)",
    "SampleDupSeam.py":
        "Duplicate the seam edge curve of a closed surface",
    "SampleEtoListBoxDialog.py":
        "Create an Eto dialog with a list box for the user to select from multiple items",
    "SampleNonRationalNurbsSurface.py":
        "Create a non-rational NURBS surface by specifying control points and knot vectors",
    "SampleRationalNurbsSurface.py":
        "Create a rational NURBS surface with weighted control points and knot vectors",
    "SampleAddRadialDimension.py":
        "Add a radial dimension annotation to a circle or arc in the document",
    "SampleCurveDirConduit.py":
        "Display curve direction arrows using a custom display conduit",
    "SampleMake2dSnapshots.py":
        "Generate Make2D drawings from multiple named view snapshots and export them",
    "SampleExportUTF8.py":
        "Export object names and attributes to a UTF-8 encoded text file",
    "SampleGetPolyline.py":
        "Interactively get a polyline from the user by picking points sequentially",
    "SampleCurvature.py":
        "Display an interactive curvature circle on a curve using a custom GetPoint and conduit",
    "SampleTextBox.py":
        "Create a text object and compute its bounding box as a rectangle curve",
    "SampleSetCameraTarget.py":
        "Set the active viewport camera location and target point programmatically",
    "SamplePointsOnSphere.py":
        "Generate evenly distributed points on a sphere surface and add them to the document",
    "SampleEtoDialog.py":
        "Create a basic Eto modal dialog with text input, checkboxes, and OK/Cancel buttons",
    "SampleEtoRebuildCurve.py":
        "Create an Eto dialog that lets the user rebuild a curve with interactive point count control",
    "SampleViewCaptureToFile.py":
        "Capture the current viewport to an image file (PNG, JPG, BMP, or TIF)",
    "SampleEtoCollapsibleDialog.py":
        "Create an Eto dialog with collapsible/expandable sections",
    "SampleEtoModelessForm.py":
        "Create a modeless (non-blocking) Eto form that stays open while the user works",
    "SampleExportCurvesAsJSON.py":
        "Export selected curves as JSON with their control point coordinates",
    "SampleCreateFromLoftRebuild.py":
        "Create a lofted surface from multiple curves, then rebuild it to a target degree and point count",
    "SampleFibonacciSphere.py":
        "Generate points on a sphere using the Fibonacci spiral distribution algorithm",
    "SampleEventHandler.py":
        "Set up event handlers that respond to Rhino document events (add, delete, modify objects)",
    "SampleDescribeObject.py":
        "Print a detailed description of a selected object's geometry type and properties",
    "SampleSerialization.py":
        "Serialize and deserialize Rhino geometry objects to/from JSON strings",
    "SamplePlaneSurfaceHoleMaker.py":
        "Create a planar surface with circular holes cut out at specified locations",
    "SampleTextDotConduit.py":
        "Display temporary text dots in the viewport using a custom display conduit",
    "SampleObjectDescription.py":
        "Get and display a human-readable description of any selected Rhino object",
    "SampleNurbsCurves.py":
        "Create various NURBS curve types: line, arc, circle, ellipse from control points and knots",
    "SampleExportStep.py":
        "Export selected Brep objects to a STEP file format",
    "SampleMultiplePointsConduit.py":
        "Display a collection of transient points in the viewport using a display conduit",
    "SampleParseTextFields.py":
        "Parse and evaluate text field expressions (like %<Date>%) in text objects",
    "SampleDrawMeshConduit.py":
        "Draw a custom colored mesh overlay in the viewport using a display conduit",
    "SampleEtoTabbedDialog.py":
        "Create an Eto dialog with multiple tabbed pages for organizing controls",
    "SampleGetSpecificObjectGrip.py":
        "Select a specific grip point on a curve or surface by grip index",
    "SampleEtoViewports.py":
        "Create an Eto panel that displays viewport thumbnails and allows viewport switching",
    "SampleSetCPlaneToView.py":
        "Set the construction plane to match the current view orientation",
    "SampleTextDot.py":
        "Add text dot annotations at specified 3D points in the document",
    "SampleSphere.py":
        "Create a sphere with interactive radius preview using a custom GetPoint class",
    "SampleGridViewDialog.py":
        "Create an Eto dialog with a data grid view showing tabular data",
    "SampleSetCurveWeight.py":
        "Modify the weight of a specific NURBS curve control point",
    "SampleGardenPath.py":
        "Generate a garden path pattern: array rectangular pavers along a curve with spacing",
    "SampleDeselectObjects.py":
        "Deselect specific objects by type or property while keeping others selected",
    "SampleModifyInstanceDef.py":
        "Modify an existing block instance definition by updating its geometry objects",
    "SampleRibbonOffsetCurve.py":
        "Create a ribbon surface by offsetting a curve on both sides and lofting between them",
    "SampleMouseCallback.py":
        "Set up a mouse callback to respond to mouse clicks and movement in the viewport",
    "SampleQuadRemesh.py":
        "Convert a mesh to a clean quad-dominant mesh using QuadRemesh with target face count",
    "SampleAppearanceColors.py":
        "Get and modify Rhino application appearance colors (background, grid, axes, etc.)",
    "SampleDraftAngleCurves.py":
        "Analyze draft angles on a surface and extract curves at a specified draft angle",
    "SampleSetDetailsToWireframe.py":
        "Set all detail viewports on a layout page to wireframe display mode",
    "SampleImportNamedViews.py":
        "Import named views from another 3dm file into the current document",
    "SampleMoveBrepEdge.py":
        "Move a specific edge of a Brep by a translation vector",
    "SampleDumpInstanceDefinition.py":
        "Print a hierarchical dump of all block instance definitions and their nested structure",
    "SampleEditPoints.py":
        "Display and edit Greville (edit) points on a curve",
    "SampleUnroller.py":
        "Unroll a developable surface (or polysurface) flat with its curves and dots",
    "SamplePointCloudColors.py":
        "Add colored point cloud objects to the document with per-point colors",
    "SampleEtoColorDropDown.py":
        "Create an Eto dialog with a color picker dropdown control",
    "SampleMirrorWithHistory.py":
        "Mirror objects across a plane while preserving construction history",
    "SampleBoxSpaceMorph.py":
        "Deform geometry using a box morph (map from one box shape to another)",
    "SampleEtoViewCaptureDialog.py":
        "Create an Eto dialog for configuring and executing viewport captures with resolution options",
    "SampleCurveDivideByCount.py":
        "Divide a curve into equal segments by count and place point objects at division points",
    "makemesh.py":
        "Create a mesh from scratch by defining vertices and faces programmatically",
    # rhino3dm samples
    "SampleSun.py":
        "Configure sun settings (location, date, time, intensity) in a 3dm file using rhino3dm",
    "SampleRequestBoundingBox.py":
        "Get the bounding box of objects in a remote 3dm file using rhino3dm",
    "SampleGetMeshes.py":
        "Read render meshes from Brep faces in a 3dm file using rhino3dm",
    "SampleSafeFrame.py":
        "Configure safe frame rendering settings in a 3dm file using rhino3dm",
    "SamplePointCloud.py":
        "Create and manipulate point cloud objects using rhino3dm",
    "SamplePolyCurve.py":
        "Build a polycurve by appending arcs and lines using rhino3dm",
    "SampleViewports.py":
        "Configure viewport settings (camera, projection, display mode) using rhino3dm",
    "SampleBrepSetMesh.py":
        "Assign custom render meshes to Brep faces using rhino3dm",
    "SampleNurbsSurfaceProperties.py":
        "Read and display NURBS surface properties (degree, knots, control points) using rhino3dm",
    "SampleSimple.py":
        "Create a simple 3dm file with basic geometry objects using rhino3dm",
    "SampleSphereLines.py":
        "Generate random lines distributed on a sphere surface and save to a 3dm file using rhino3dm",
    "SampleCreateCircleAndWriteTo3dmFile.py":
        "Create a circle and write it to a 3dm file using rhino3dm",
    "SampleReadTextEntities.py":
        "Read and extract text entity content from a 3dm file using rhino3dm",
    "SampleAddMaterial.py":
        "Add render materials with diffuse colors to a 3dm file using rhino3dm",
    "SampleExtrusionSetMesh.py":
        "Set custom render meshes on extrusion objects using rhino3dm",
    "SampleDecals.py":
        "Add and configure decal textures on objects using rhino3dm",
    "SampleSkylight.py":
        "Configure skylight rendering settings in a 3dm file using rhino3dm",
    "SampleAddInstanceDefinition.py":
        "Create a block instance definition and insert instances of it in the document",
}


# ---------------------------------------------------------------------------
# API Pairs filtering
# ---------------------------------------------------------------------------

def is_trivial_getter(entry):
    """Detect trivial property getter: just obj.Prop + print."""
    code = entry.get("code", "")
    lines = [l.strip() for l in code.strip().splitlines() if l.strip() and not l.strip().startswith("#")]
    # Pattern: import, value = obj.X, print(value)
    if len(lines) <= 3 and "value = obj." in code and "print(value)" in code:
        return True
    return False


def has_assume_boilerplate(entry):
    """Detect 'Assume obj is an existing' placeholder pattern."""
    code = entry.get("code", "")
    return "# Assume 'obj' is an existing" in code


def has_csharp_system_types(entry):
    """Detect C# System types used as Python arguments."""
    code = entry.get("code", "")
    # System.Guid.Empty, System.UInt32, etc. but allow System.Drawing (used in color)
    if re.search(r'System\.(?!Drawing)', code):
        return True
    return False


def has_placeholder_none_args(entry):
    """Detect passing None as placeholder arguments."""
    code = entry.get("code", "")
    # Pattern: method(None, ...) or method(..., None) — likely placeholder
    if re.search(r'\(\s*None\s*,', code) or re.search(r',\s*None\s*\)', code):
        return True
    return False


def has_truncated_instruction(entry):
    """Detect instructions truncated mid-sentence."""
    instr = entry.get("instruction", "")
    # If instruction is long and ends with a short word fragment (likely truncated)
    if len(instr) > 150 and not instr.endswith(('.', ')', '"', "'", '!', '?')):
        # Check if last word is very short (likely cut off)
        last_word = instr.rstrip().split()[-1] if instr.strip() else ""
        if len(last_word) <= 3 and last_word.islower():
            return True
    return False


def is_interesting_api_pair(entry):
    """
    Keep API pairs that demonstrate meaningful usage:
    - Constructor calls (creating objects)
    - Methods with multiple real arguments
    - Static factory methods
    """
    code = entry.get("code", "")
    method = entry.get("method", "")

    # Always exclude trivial getters and assume-obj boilerplate
    if is_trivial_getter(entry):
        return False
    if has_assume_boilerplate(entry):
        return False
    if has_csharp_system_types(entry):
        return False
    if has_placeholder_none_args(entry):
        return False
    if has_truncated_instruction(entry):
        return False

    # Keep constructors
    if method == "__init__":
        return True

    # Keep static methods (no "obj." pattern)
    if "obj." not in code and "result = " in code:
        return True

    # Keep if code has meaningful length (not just a one-liner call)
    real_lines = [l for l in code.splitlines()
                  if l.strip() and not l.strip().startswith("#") and not l.strip().startswith("import")]
    if len(real_lines) >= 3:
        return True

    return False


# ---------------------------------------------------------------------------
# Backlabeled filtering and instruction rewriting
# ---------------------------------------------------------------------------

def is_genuine_rhino_backlabeled(entry):
    """Check if backlabeled entry has genuine Rhino-specific code."""
    code = entry.get("code", "")
    instr = entry.get("instruction", "")

    # Code length check
    if len(code) > 2000:
        return False

    # Must reference Rhino APIs
    rhino_markers = [
        "rhinoscriptsyntax", "rs.", "Rhino.Geometry", "Rhino.Input",
        "Rhino.DocObjects", "rhino3dm", "scriptcontext", "RhinoCommon",
        "Rhino.Display", "Rhino.FileIO", "rg.", "sc.doc",
    ]
    has_rhino = any(m in code for m in rhino_markers)
    if not has_rhino:
        return False

    # Reject generic "Implement the function X" instructions
    if instr.startswith("Implement the function"):
        return False

    # Reject vague "Implement a Rhino Python script for: X" instructions
    if re.match(r"Implement a Rhino Python script for:\s*\w+$", instr):
        return False

    # Reject pure class stubs (just pass statements)
    if code.count("pass") > 3:
        return False

    # Reject if contains hardcoded credentials or license keys
    credential_markers = ["license", "api_key", "apiKey", "password", "token",
                          "secret", "credential"]
    code_lower = code.lower()
    if any(m in code_lower for m in credential_markers):
        # Allow if it's just a comment about licensing
        non_comment_lines = [l for l in code.splitlines()
                             if l.strip() and not l.strip().startswith("#")]
        if any(any(m in l.lower() for m in credential_markers) for l in non_comment_lines):
            return False

    # Reject if mostly non-Rhino imports (Flask, Django, etc.)
    non_rhino_imports = ["flask", "django", "redis", "fastapi", "pydantic",
                         "livestock", "pymesh", "viktor", "compute_rhino3d"]
    if any(imp in code_lower for imp in non_rhino_imports):
        return False

    # Reject code that references undefined variables (sign of incomplete snippet)
    # Simple heuristic: if code uses a variable that's never assigned/imported
    if _has_undefined_variable_smell(code):
        return False

    # Reject code with more than 1 function def (probably a full file dump or mixed code)
    func_defs = re.findall(r'^def \w+\(', code, re.MULTILINE)
    if len(func_defs) > 1:
        return False

    # Reject Grasshopper component dumps (single-letter output vars: a = ..., b = ...)
    single_letter_assigns = re.findall(r'^[a-c]\s*=\s*', code, re.MULTILINE)
    if len(single_letter_assigns) >= 2:
        return False

    # Reject vague "Write a ... script" instructions under 40 chars
    if instr.startswith("Write a") and len(instr) < 40:
        return False

    return True


def _has_undefined_variable_smell(code):
    """Heuristic: detect code that uses variables never defined in the snippet."""
    lines = code.splitlines()
    # Look for function calls using variables that aren't defined anywhere
    # Common pattern: listPoints2, myObject, etc. used but never assigned
    all_text = code
    # Check for common undefined variable patterns
    for pattern in [r'\blistPoints\d*\b', r'\bmyObject\b', r'\bsurface\b(?!s)']:
        if re.search(pattern, all_text):
            # Check if it's defined (assigned, in function args, or imported)
            var_match = re.search(pattern, all_text)
            if var_match:
                var_name = var_match.group()
                # Is it assigned somewhere? (var = ...) or in function def args
                if not re.search(rf'{var_name}\s*=', all_text) and \
                   not re.search(rf'def \w+\([^)]*{var_name}', all_text) and \
                   not re.search(rf'for {var_name} in', all_text) and \
                   not re.search(rf'import.*{var_name}', all_text):
                    return True
    return False


def rewrite_backlabeled_instruction(entry):
    """Rewrite vague backlabeled instructions to be task-oriented."""
    instr = entry.get("instruction", "")
    code = entry.get("code", "")

    # If instruction is already decent (describes a task), keep it
    if len(instr) > 30 and not instr.startswith("Implement") and not instr.startswith("Represents"):
        return instr

    # Try to extract from docstring in code
    docstring_match = re.search(r'"""(.*?)"""', code, re.DOTALL)
    if docstring_match:
        doc = docstring_match.group(1).strip().split("\n")[0].strip()
        if len(doc) > 15 and not doc.startswith("Represents"):
            return doc

    # Try to extract from function name
    func_match = re.search(r'def (\w+)\(', code)
    if func_match:
        func_name = func_match.group(1)
        # Convert camelCase/snake_case to words
        words = re.sub(r'([A-Z])', r' \1', func_name)
        words = words.replace('_', ' ').strip()
        return f"Write a Rhino script function to {words.lower()}"

    # Fallback: generic but better than original
    return instr


# ---------------------------------------------------------------------------
# Main cleaning pipeline
# ---------------------------------------------------------------------------

def main():
    stats = defaultdict(int)
    kept = []
    excluded_by_reason = defaultdict(list)
    seen_code_hashes = set()
    seen_instr_hashes = set()

    # -----------------------------------------------------------------------
    # 1. API Pairs — heavy filtering
    # -----------------------------------------------------------------------
    print("Processing API Pairs...")
    api_pairs = load_jsonl(RAW / "docs" / "api_pairs.jsonl")
    stats["api_pairs_total"] = len(api_pairs)

    for entry in api_pairs:
        if is_trivial_getter(entry):
            excluded_by_reason["api_trivial_getter"].append(entry)
            stats["api_excluded_trivial_getter"] += 1
        elif has_assume_boilerplate(entry):
            excluded_by_reason["api_assume_boilerplate"].append(entry)
            stats["api_excluded_assume_boilerplate"] += 1
        elif has_csharp_system_types(entry):
            excluded_by_reason["api_csharp_types"].append(entry)
            stats["api_excluded_csharp_types"] += 1
        elif has_placeholder_none_args(entry):
            excluded_by_reason["api_placeholder_none"].append(entry)
            stats["api_excluded_placeholder_none"] += 1
        elif has_truncated_instruction(entry):
            excluded_by_reason["api_truncated_instruction"].append(entry)
            stats["api_excluded_truncated"] += 1
        elif not is_interesting_api_pair(entry):
            excluded_by_reason["api_not_interesting"].append(entry)
            stats["api_excluded_not_interesting"] += 1
        else:
            entry["_source_file"] = "api_pairs"
            kept.append(entry)
            stats["api_kept"] += 1

    print(f"  API Pairs: {stats['api_kept']} kept / {stats['api_pairs_total']} total")

    # -----------------------------------------------------------------------
    # 2. RS Mapping Pairs — keep as-is (good quality)
    # -----------------------------------------------------------------------
    print("Processing RS Mapping Pairs...")
    rs_pairs = load_jsonl(RAW / "docs" / "rs_mapping_pairs.jsonl")
    stats["rs_mapping_total"] = len(rs_pairs)

    for entry in rs_pairs:
        entry["_source_file"] = "rs_mapping_pairs"
        kept.append(entry)
        stats["rs_mapping_kept"] += 1

    print(f"  RS Mapping: {stats['rs_mapping_kept']} kept / {stats['rs_mapping_total']} total")

    # -----------------------------------------------------------------------
    # 3. Reference Pairs — EXCLUDE ALL (wrong format for code-gen)
    # -----------------------------------------------------------------------
    print("Processing Reference Pairs...")
    ref_pairs = load_jsonl(RAW / "docs" / "reference_pairs.jsonl")
    stats["reference_total"] = len(ref_pairs)

    for entry in ref_pairs:
        excluded_by_reason["reference_wrong_format"].append(entry)
        stats["reference_excluded"] += 1

    print(f"  Reference: 0 kept / {stats['reference_total']} total (all excluded: wrong format)")

    # -----------------------------------------------------------------------
    # 4. Sample Pairs — keep all, rewrite instructions
    # -----------------------------------------------------------------------
    print("Processing Sample Pairs...")
    sample_pairs = load_jsonl(RAW / "docs" / "sample_pairs.jsonl")
    stats["sample_total"] = len(sample_pairs)

    for entry in sample_pairs:
        filename = entry.get("file", "")
        if filename in SAMPLE_INSTRUCTION_REWRITES:
            entry["instruction_original"] = entry["instruction"]
            entry["instruction"] = SAMPLE_INSTRUCTION_REWRITES[filename]
            stats["sample_instruction_rewritten"] += 1
        entry["_source_file"] = "sample_pairs"
        kept.append(entry)
        stats["sample_kept"] += 1

    print(f"  Sample Pairs: {stats['sample_kept']} kept / {stats['sample_total']} total"
          f" ({stats.get('sample_instruction_rewritten', 0)} instructions rewritten)")

    # -----------------------------------------------------------------------
    # 5. Backlabeled — keep only genuine Rhino code <2000 chars, rewrite
    # -----------------------------------------------------------------------
    print("Processing Backlabeled...")
    backlabeled = load_jsonl(RAW / "synthetic" / "backlabeled.jsonl")
    stats["backlabeled_total"] = len(backlabeled)

    for entry in backlabeled:
        if is_genuine_rhino_backlabeled(entry):
            entry["instruction_original"] = entry["instruction"]
            entry["instruction"] = rewrite_backlabeled_instruction(entry)
            entry["_source_file"] = "backlabeled"
            kept.append(entry)
            stats["backlabeled_kept"] += 1
        else:
            reason = "backlabeled_"
            code = entry.get("code", "")
            instr = entry.get("instruction", "")
            if len(code) > 2000:
                reason += "too_long"
            elif instr.startswith("Implement the function"):
                reason += "generic_instruction"
            elif any(m in code.lower() for m in ["flask", "django", "redis", "fastapi"]):
                reason += "non_rhino_code"
            else:
                reason += "no_rhino_markers"
            excluded_by_reason[reason].append(entry)
            stats[f"backlabeled_excluded_{reason.split('_', 1)[1]}"] += 1

    print(f"  Backlabeled: {stats['backlabeled_kept']} kept / {stats['backlabeled_total']} total")

    # -----------------------------------------------------------------------
    # 6. Small Synthetic files — keep all (best quality)
    # -----------------------------------------------------------------------
    print("Processing Small Synthetic files...")
    synth_files = [
        "geometry_creation.jsonl", "geometry_manipulation.jsonl",
        "geometry_analysis.jsonl", "advanced_sculptural.jsonl",
        "scene_management.jsonl", "code_explanation.jsonl",
        "code_fixing.jsonl", "api_conversion.jsonl",
    ]
    for fname in synth_files:
        path = RAW / "synthetic" / fname
        if not path.exists():
            continue
        entries = load_jsonl(path)
        stats[f"synthetic_{fname}_total"] = len(entries)
        for entry in entries:
            entry["_source_file"] = f"synthetic_{fname}"
            kept.append(entry)
            stats[f"synthetic_{fname}_kept"] = stats.get(f"synthetic_{fname}_kept", 0) + 1

    synth_total = sum(v for k, v in stats.items() if k.startswith("synthetic_") and k.endswith("_total"))
    synth_kept = sum(v for k, v in stats.items() if k.startswith("synthetic_") and k.endswith("_kept"))
    print(f"  Small Synthetic: {synth_kept} kept / {synth_total} total")

    # -----------------------------------------------------------------------
    # 7. Deduplication
    # -----------------------------------------------------------------------
    print("\nDeduplicating...")
    pre_dedup = len(kept)
    deduped = []

    for entry in kept:
        code = entry.get("code", "")
        instr = entry.get("instruction", "")

        c_hash = code_hash(code)
        i_hash = instruction_hash(instr)

        # Check for exact duplicate code
        if c_hash in seen_code_hashes:
            excluded_by_reason["duplicate_code"].append(entry)
            stats["dedup_code"] += 1
            continue

        # Check for exact duplicate instruction
        if i_hash in seen_instr_hashes:
            excluded_by_reason["duplicate_instruction"].append(entry)
            stats["dedup_instruction"] += 1
            continue

        seen_code_hashes.add(c_hash)
        seen_instr_hashes.add(i_hash)
        deduped.append(entry)

    stats["dedup_removed"] = pre_dedup - len(deduped)
    print(f"  Removed {stats['dedup_removed']} duplicates ({pre_dedup} -> {len(deduped)})")

    # -----------------------------------------------------------------------
    # 8. Clean up internal fields and write output
    # -----------------------------------------------------------------------
    print("\nWriting output...")

    # Remove internal tracking field
    for entry in deduped:
        entry.pop("_source_file", None)

    # Write cleaned pairs
    output_path = PROCESSED / "cleaned_pairs.jsonl"
    write_jsonl(output_path, deduped)
    print(f"  Wrote {len(deduped)} entries to {output_path}")

    # Write excluded entries by reason
    for reason, entries in excluded_by_reason.items():
        exc_path = EXCLUDED / f"{reason}.jsonl"
        write_jsonl(exc_path, entries)
        print(f"  Wrote {len(entries)} excluded entries to {exc_path.name}")

    # -----------------------------------------------------------------------
    # 9. Summary stats
    # -----------------------------------------------------------------------
    stats["final_kept"] = len(deduped)
    stats["total_excluded"] = sum(len(v) for v in excluded_by_reason.values())
    stats["total_input"] = (stats["api_pairs_total"] + stats["rs_mapping_total"] +
                            stats["reference_total"] + stats["sample_total"] +
                            stats["backlabeled_total"] + synth_total)

    # Source breakdown of final kept
    source_counts = defaultdict(int)
    for entry in deduped:
        source = entry.get("source", "unknown")
        source_counts[source] += 1
    stats["final_by_source"] = dict(source_counts)

    # API breakdown of final kept
    api_counts = defaultdict(int)
    for entry in deduped:
        api = entry.get("api", "unknown")
        api_counts[api] += 1
    stats["final_by_api"] = dict(api_counts)

    stats_path = PROCESSED / "cleaning_stats.json"
    with open(stats_path, "w") as f:
        json.dump(dict(stats), f, indent=2)
    print(f"  Wrote stats to {stats_path}")

    # Print summary
    print("\n" + "=" * 60)
    print("  CLEANING SUMMARY")
    print("=" * 60)
    print(f"  Total input entries:    {stats['total_input']:,}")
    print(f"  Total excluded:         {stats['total_excluded']:,}")
    print(f"  Total kept (deduped):   {stats['final_kept']:,}")
    print(f"  Keep rate:              {stats['final_kept']/stats['total_input']*100:.1f}%")
    print()
    print("  Kept by source:")
    for source, count in sorted(source_counts.items()):
        print(f"    {source}: {count}")
    print()
    print("  Excluded breakdown:")
    for reason, entries in sorted(excluded_by_reason.items(), key=lambda x: -len(x[1])):
        print(f"    {reason}: {len(entries):,}")
    print("=" * 60)


if __name__ == "__main__":
    main()
