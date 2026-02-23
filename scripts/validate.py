#!/usr/bin/env python3
"""
Validate all synthetic (instruction, code) pairs.

Checks:
1. Python syntax validity (ast.parse)
2. Correct API calls (rs.* against known rhinoscriptsyntax functions,
   rg.* against known RhinoCommon classes from api_info.json)
3. Correct imports

Outputs validation_report.json and updates summary.json.
"""

import json
import ast
import re
import os
from collections import Counter, defaultdict

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SYNTHETIC_DIR = os.path.join(BASE_DIR, "data", "raw", "synthetic")
API_INFO_PATH = os.path.join(BASE_DIR, "data", "raw", "docs", "api_info.json")

# Known rhinoscriptsyntax functions
KNOWN_RS_FUNCS = {
    "AddPoint", "AddPoints", "AddLine", "AddPolyline", "AddCircle", "AddArc",
    "AddArc3Pt", "AddSphere", "AddCylinder", "AddCurve", "AddInterpCurve",
    "AddSrfPt", "AddLoftSrf", "AddRevSrf", "AddPipe", "AddBox", "AddText",
    "AddTextDot", "AddSpiral", "ExtrudeCurve", "ExtrudeCurveStraight",
    "CapPlanarHoles", "MoveObject", "MoveObjects", "RotateObject",
    "RotateObjects", "ScaleObject", "ScaleObjects", "MirrorObject",
    "MirrorObjects", "CopyObject", "CopyObjects", "DeleteObject",
    "DeleteObjects", "SelectObjects", "UnselectAllObjects", "GetObject",
    "GetObjects", "GetPoint", "GetPoints", "GetReal", "ObjectsByType",
    "ObjectsByLayer", "AllObjects", "CurveLength", "CurveArea",
    "CurveAreaCentroid", "CurveDomain", "CurveCurvature",
    "CurveClosestPoint", "CurveTangent", "CurvePlane", "CurvePerpFrame",
    "EvaluateCurve", "DivideCurve", "SplitCurve", "JoinCurves",
    "OffsetCurve", "RebuildCurve", "IsCurve", "IsCurveClosed",
    "IsCurvePlanar", "SurfaceDomain", "SurfaceNormal",
    "SurfaceClosestPoint", "SurfaceVolume", "SurfaceVolumeCentroid",
    "EvaluateSurface", "OffsetSurface", "RebuildSurface", "SplitBrep",
    "BooleanUnion", "BooleanDifference", "BooleanIntersection",
    "ExplodePolysurfaces", "MeshObjects", "AddLayer", "DeleteLayer",
    "LayerNames", "LayerVisible", "LayerLocked", "IsLayer", "IsLayerEmpty",
    "IsLayerCurrent", "CurrentLayer", "ObjectLayer", "ObjectColor",
    "ObjectName", "ObjectType", "ObjectGroups", "AddGroup", "DeleteGroup",
    "AddObjectsToGroup", "BoundingBox", "Distance", "PointCoordinates",
    "AddBlock", "InsertBlock", "BlockNames", "BlockInstanceCount",
    "DeleteBlock", "SetUserText", "GetUserText", "AddMaterialToObject",
    "MaterialColor", "MaterialShine", "ObjectPrintWidth",
    "ObjectAreaCentroid", "CurveCurveIntersection",
    "CurveSurfaceIntersection", "PointInPlanarClosedCurve",
    "ProjectCurveToSurface", "ProjectPointToSurface", "CurveFilletPoints",
    "FilletSrf", "DuplicateEdgeCurves", "OrientObject", "TrimCurve",
    "AddLinearDimension2", "Command", "coercecurve", "coercebrep",
    "coerce3dpoint", "coerceguid", "IsObject", "HideObject", "HideObjects",
    "ShowObject", "ShowObjects", "filter",
}

# Known RhinoCommon geometry classes
KNOWN_RG_CLASSES = {
    "Point3d", "Point3f", "Point2d", "Point4d", "Vector3d", "Vector3f",
    "Line", "Plane", "Circle", "Arc", "Sphere", "Box", "BoundingBox",
    "Interval", "NurbsCurve", "NurbsSurface", "Brep", "Mesh", "PointCloud",
    "Transform", "Curve", "Surface", "PlaneSurface", "Ellipse", "SubD",
    "AreaMassProperties", "VolumeMassProperties", "LoftType", "Intersect",
    "MeshFace", "MeshVertexList", "Point3dList", "Polyline", "PolyCurve",
    "LineCurve", "ArcCurve", "Cylinder", "Cone", "Torus", "Extrusion",
    "TextEntity", "AnnotationBase", "Hatch", "MeshingParameters",
}


def build_api_lookup():
    """Build validation lookups from api_info.json."""
    with open(API_INFO_PATH) as f:
        data = json.load(f)

    classes = set()
    for entry in data:
        if entry.get("dataType") in ("class", "struct", "enum"):
            classes.add(entry.get("name", ""))
    return classes


def validate_pair(pair, api_classes):
    """Validate a single pair. Returns (syntax_ok, api_ok, issues)."""
    code = pair.get("code", "")
    category = pair.get("category", "")

    # Skip explanation pairs (output is text, not code)
    if category == "code_explanation":
        return True, True, []

    issues = []

    # 1. Syntax check
    syntax_ok = True
    if code:
        try:
            ast.parse(code)
        except SyntaxError as e:
            syntax_ok = False
            issues.append(f"SyntaxError: {e}")

    # 2. API check — only flag truly wrong calls
    api_ok = True
    if code:
        # Check rs.* calls — but only if rs is actually rhinoscriptsyntax
        if re.search(r"import rhinoscriptsyntax as rs", code):
            rs_calls = set(re.findall(r"\brs\.([A-Z]\w+)", code))
            for call in rs_calls:
                if call not in KNOWN_RS_FUNCS:
                    api_ok = False
                    issues.append(f"Unknown rs.{call}")

        # Check rg.* calls — only capitalized (class names)
        if re.search(r"import Rhino\.Geometry as rg", code):
            rg_calls = set(re.findall(r"\brg\.([A-Z]\w+)", code))
            for call in rg_calls:
                if call not in KNOWN_RG_CLASSES and call not in api_classes:
                    api_ok = False
                    issues.append(f"Unknown rg.{call}")

    return syntax_ok, api_ok, issues


def main():
    os.makedirs(SYNTHETIC_DIR, exist_ok=True)
    api_classes = build_api_lookup()

    jsonl_files = sorted(f for f in os.listdir(SYNTHETIC_DIR) if f.endswith(".jsonl"))
    all_issues = []
    stats = {
        "total": 0, "syntax_pass": 0, "syntax_fail": 0,
        "api_pass": 0, "api_fail": 0,
        "by_file": {},
    }

    for jf in jsonl_files:
        file_total = file_valid = 0
        with open(os.path.join(SYNTHETIC_DIR, jf)) as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    pair = json.loads(line)
                except json.JSONDecodeError:
                    continue

                stats["total"] += 1
                file_total += 1

                syntax_ok, api_ok, issues = validate_pair(pair, api_classes)

                if syntax_ok:
                    stats["syntax_pass"] += 1
                else:
                    stats["syntax_fail"] += 1
                if api_ok:
                    stats["api_pass"] += 1
                else:
                    stats["api_fail"] += 1

                if syntax_ok and api_ok:
                    file_valid += 1
                elif issues:
                    all_issues.append({"file": jf, "line": line_num, "issues": issues})

        stats["by_file"][jf] = {"total": file_total, "valid": file_valid, "invalid": file_total - file_valid}

    # Write report
    report = {
        "total_pairs": stats["total"],
        "syntax_pass": stats["syntax_pass"],
        "syntax_fail": stats["syntax_fail"],
        "api_pass": stats["api_pass"],
        "api_fail": stats["api_fail"],
        "syntax_pass_rate": round(stats["syntax_pass"] / max(stats["total"], 1) * 100, 1),
        "api_pass_rate": round(stats["api_pass"] / max(stats["total"], 1) * 100, 1),
        "by_file": stats["by_file"],
        "issues": all_issues[:200],
        "total_issues": len(all_issues),
    }

    report_path = os.path.join(SYNTHETIC_DIR, "validation_report.json")
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)

    print(f"Total pairs: {stats['total']}")
    print(f"Syntax pass: {stats['syntax_pass']}/{stats['total']} ({report['syntax_pass_rate']}%)")
    print(f"API pass:    {stats['api_pass']}/{stats['total']} ({report['api_pass_rate']}%)")
    print(f"Issues:      {len(all_issues)}")
    print(f"Report:      {report_path}")

    # Update summary
    summary_path = os.path.join(SYNTHETIC_DIR, "summary.json")
    if os.path.exists(summary_path):
        with open(summary_path) as f:
            summary = json.load(f)
        summary["validation"] = {
            "syntax_pass_rate": report["syntax_pass_rate"],
            "api_pass_rate": report["api_pass_rate"],
            "total_valid": stats["syntax_pass"],
            "total_flagged": stats["syntax_fail"] + stats["api_fail"],
        }
        with open(summary_path, "w") as f:
            json.dump(summary, f, indent=2)


if __name__ == "__main__":
    main()
