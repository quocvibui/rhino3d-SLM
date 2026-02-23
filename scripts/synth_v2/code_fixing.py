"""Code fixing/debugging pairs (~400+)."""

def m(instruction, code, difficulty, api, tags):
    return {"instruction": instruction, "code": code, "source": "synthetic",
            "category": "code_fixing", "difficulty": difficulty, "api": api, "tags": tags}

def generate():
    pairs = []

    # ── 1) Wrong import patterns ──
    wrong_imports = [
        ("import RhinoGeometry as rg", "import Rhino.Geometry as rg", "misspelled module"),
        ("import rhinoscript as rs", "import rhinoscriptsyntax as rs", "wrong module name"),
        ("import Rhino_Geometry as rg", "import Rhino.Geometry as rg", "underscore instead of dot"),
        ("from Rhino import Geometry", "import Rhino.Geometry as rg", "wrong import style"),
        ("import script_context as sc", "import scriptcontext as sc", "wrong scriptcontext name"),
        ("import RhinoCommon as rc", "import Rhino.Geometry as rg\nimport scriptcontext as sc", "RhinoCommon is not a module"),
        ("import rs", "import rhinoscriptsyntax as rs", "missing full module path"),
        ("from rhinoscriptsyntax import *", "import rhinoscriptsyntax as rs", "star import not recommended"),
        ("import Rhino.geometry as rg", "import Rhino.Geometry as rg", "wrong capitalization"),
        ("import rhino3d", "import rhino3dm", "wrong package name"),
        ("import GHPython", "import ghpythonlib.components as ghcomp", "wrong GH module"),
        ("from Grasshopper.DataTree import *", "import Grasshopper as gh", "wrong Grasshopper import"),
    ]
    for buggy, fixed, desc in wrong_imports:
        pairs.append(m(
            f"Fix the import error in this script:\n```python\n{buggy}\npt = rg.Point3d(0, 0, 0) if 'rg' in '{fixed}' else None\n```",
            f"{fixed}\npt = rg.Point3d(0, 0, 0)" if "rg" in fixed else fixed,
            "easy", "RhinoCommon" if "Rhino" in fixed else ("rhinoscriptsyntax" if "rs" in fixed else "rhino3dm"),
            ["fix", "import"]))

    # ── 2) Wrong arguments to rs functions ──
    wrong_args_rs = [
        ("rs.AddSphere(0, 0, 0, 5)", "rs.AddSphere((0, 0, 0), 5)", "sphere needs tuple center"),
        ("rs.AddLine([0,0,0], 10, 5, 0)", "rs.AddLine([0,0,0], [10,5,0])", "line needs two point args"),
        ("rs.AddCircle(0, 0, 0, 5)", "rs.AddCircle((0,0,0), 5)", "circle args need tuple"),
        ("rs.AddCylinder(0, 10, 3)", "rs.AddCylinder((0,0,0), 10, 3)", "cylinder needs tuple base"),
        ("rs.AddCone(0, 8, 4)", "rs.AddCone((0,0,0), 8, 4)", "cone needs tuple base"),
        ("rs.AddBox(0,0,0, 10,10,10)", "rs.AddBox([(0,0,0),(10,0,0),(10,10,0),(0,10,0),(0,0,10),(10,0,10),(10,10,10),(0,10,10)])", "box needs 8 corner points"),
        ("rs.MoveObject(obj, 10, 0, 0)", "rs.MoveObject(obj, (10, 0, 0))", "move needs vector tuple"),
        ("rs.RotateObject(obj, 0, 0, 0, 45)", "rs.RotateObject(obj, (0,0,0), 45)", "rotate needs tuple center"),
        ("rs.ScaleObject(obj, 2)", "rs.ScaleObject(obj, (0,0,0), (2,2,2))", "scale needs center and factors"),
        ("rs.AddPoint(1, 2)", "rs.AddPoint(1, 2, 0)", "AddPoint needs 3 coordinates"),
        ("rs.AddSrfPt((0,0,0), (10,0,0), (10,10,0), (0,10,0))", "rs.AddSrfPt([(0,0,0),(10,0,0),(10,10,0),(0,10,0)])", "SrfPt needs list of points"),
        ("rs.AddLoftSrf(c1, c2)", "rs.AddLoftSrf([c1, c2])", "LoftSrf needs list of curves"),
        ("rs.BooleanUnion(a, b)", "rs.BooleanUnion([a, b])", "BooleanUnion needs list"),
        ("rs.BooleanDifference([a, b])", "rs.BooleanDifference(a, b)", "BooleanDifference takes two args"),
        ("rs.AddPipe(rail, 2)", "rs.AddPipe(rail, 0, 2)", "AddPipe needs parameter and radius"),
    ]
    for buggy, fixed, desc in wrong_args_rs:
        pairs.append(m(
            f"Fix the incorrect arguments in this code:\n```python\nimport rhinoscriptsyntax as rs\n{buggy}\n```",
            f"import rhinoscriptsyntax as rs\n{fixed}",
            "easy", "rhinoscriptsyntax", ["fix", "arguments"]))

    # ── 3) Missing null checks ──
    null_check_patterns = [
        ("obj = rs.GetObject('Select')\nrs.DeleteObject(obj)",
         "obj = rs.GetObject('Select')\nif obj:\n    rs.DeleteObject(obj)",
         "no null check after GetObject"),
        ("obj = rs.GetObject('Select curve')\nlength = rs.CurveLength(obj)\nprint(length)",
         "obj = rs.GetObject('Select curve', 4)\nif obj:\n    length = rs.CurveLength(obj)\n    print(length)",
         "no filter type and no null check"),
        ("pt = rs.GetPoint('Pick')\nrs.AddSphere(pt, 5)",
         "pt = rs.GetPoint('Pick')\nif pt:\n    rs.AddSphere(pt, 5)",
         "no null check after GetPoint"),
        ("val = rs.GetReal('Enter radius')\nrs.AddCircle((0,0,0), val)",
         "val = rs.GetReal('Enter radius')\nif val is not None:\n    rs.AddCircle((0,0,0), val)",
         "GetReal can return None"),
        ("objs = rs.GetObjects('Select')\nfor obj in objs:\n    rs.DeleteObject(obj)",
         "objs = rs.GetObjects('Select')\nif objs:\n    for obj in objs:\n        rs.DeleteObject(obj)",
         "GetObjects can return None"),
        ("srf = rs.GetObject('Select surface')\narea = rs.SurfaceArea(srf)\nprint(area[0])",
         "srf = rs.GetObject('Select surface', 8)\nif srf:\n    area = rs.SurfaceArea(srf)\n    if area:\n        print(area[0])",
         "double null check needed"),
        ("crv = rs.GetObject('Select')\nresult = rs.OffsetCurve(crv, (0,0,0), 2)\nrs.DeleteObject(crv)",
         "crv = rs.GetObject('Select', 4)\nif crv:\n    result = rs.OffsetCurve(crv, (0,0,0), 2)\n    if result:\n        rs.DeleteObject(crv)",
         "offset can fail"),
        ("c1 = rs.GetObject('First curve')\nc2 = rs.GetObject('Second curve')\nrs.BooleanUnion([c1, c2])",
         "c1 = rs.GetObject('First curve', 4)\nc2 = rs.GetObject('Second curve', 4)\nif c1 and c2:\n    result = rs.BooleanUnion([c1, c2])",
         "both selections need checking"),
    ]
    for buggy, fixed, desc in null_check_patterns:
        pairs.append(m(
            f"Fix the missing null check in this code:\n```python\nimport rhinoscriptsyntax as rs\n{buggy}\n```",
            f"import rhinoscriptsyntax as rs\n{fixed}",
            "easy", "rhinoscriptsyntax", ["fix", "null-check"]))

    # ── 4) Missing Redraw ──
    missing_redraw = [
        ("pt = rg.Point3d(5, 5, 5)\nsc.doc.Objects.AddPoint(pt)",
         "pt = rg.Point3d(5, 5, 5)\nsc.doc.Objects.AddPoint(pt)\nsc.doc.Views.Redraw()", "point"),
        ("circle = rg.Circle(rg.Plane.WorldXY, 5)\nsc.doc.Objects.AddCircle(circle)",
         "circle = rg.Circle(rg.Plane.WorldXY, 5)\nsc.doc.Objects.AddCircle(circle)\nsc.doc.Views.Redraw()", "circle"),
        ("line = rg.Line(rg.Point3d(0,0,0), rg.Point3d(10,0,0))\nsc.doc.Objects.AddLine(line)",
         "line = rg.Line(rg.Point3d(0,0,0), rg.Point3d(10,0,0))\nsc.doc.Objects.AddLine(line)\nsc.doc.Views.Redraw()", "line"),
        ("sphere = rg.Sphere(rg.Point3d.Origin, 5)\nbrep = sphere.ToBrep()\nsc.doc.Objects.AddBrep(brep)",
         "sphere = rg.Sphere(rg.Point3d.Origin, 5)\nbrep = sphere.ToBrep()\nsc.doc.Objects.AddBrep(brep)\nsc.doc.Views.Redraw()", "sphere brep"),
        ("mesh = rg.Mesh()\nmesh.Vertices.Add(0,0,0)\nmesh.Vertices.Add(10,0,0)\nmesh.Vertices.Add(5,10,0)\nmesh.Faces.AddFace(0,1,2)\nsc.doc.Objects.AddMesh(mesh)",
         "mesh = rg.Mesh()\nmesh.Vertices.Add(0,0,0)\nmesh.Vertices.Add(10,0,0)\nmesh.Vertices.Add(5,10,0)\nmesh.Faces.AddFace(0,1,2)\nmesh.Normals.ComputeNormals()\nsc.doc.Objects.AddMesh(mesh)\nsc.doc.Views.Redraw()", "mesh"),
    ]
    RC = "import Rhino.Geometry as rg\nimport scriptcontext as sc"
    for buggy, fixed, desc in missing_redraw:
        pairs.append(m(
            f"Fix this RhinoCommon code that doesn't update the viewport:\n```python\n{RC}\n{buggy}\n```",
            f"{RC}\n{fixed}",
            "easy", "RhinoCommon", ["fix", "redraw"]))

    # ── 5) Type errors (tuple vs Point3d) ──
    type_errors = [
        ("pts = [(0,0,0), (5,5,0), (10,0,0)]\ncurve = rg.NurbsCurve.Create(False, 3, pts)",
         "pts = [rg.Point3d(0,0,0), rg.Point3d(5,5,0), rg.Point3d(10,0,0)]\ncurve = rg.NurbsCurve.Create(False, 2, pts)",
         "tuples instead of Point3d, wrong degree"),
        ("plane = rg.Plane((0,0,0), (0,0,1))",
         "plane = rg.Plane(rg.Point3d(0,0,0), rg.Vector3d(0,0,1))",
         "tuples instead of Point3d/Vector3d"),
        ("line = rg.Line((0,0,0), (10,0,0))",
         "line = rg.Line(rg.Point3d(0,0,0), rg.Point3d(10,0,0))",
         "tuples instead of Point3d"),
        ("circle = rg.Circle((0,0,0), 5)",
         "circle = rg.Circle(rg.Plane(rg.Point3d(0,0,0), rg.Vector3d(0,0,1)), 5)",
         "Circle needs Plane not tuple"),
        ("xform = rg.Transform.Translation(10, 0, 0)",
         "xform = rg.Transform.Translation(rg.Vector3d(10, 0, 0))",
         "Translation needs Vector3d"),
        ("vec = rg.Vector3d(10)\nvec.Unitize()",
         "vec = rg.Vector3d(10, 0, 0)\nvec.Unitize()",
         "Vector3d needs 3 args"),
        ("sphere = rg.Sphere(0, 0, 0, 5)",
         "sphere = rg.Sphere(rg.Point3d(0, 0, 0), 5)",
         "Sphere needs Point3d center"),
    ]
    for buggy, fixed, desc in type_errors:
        pairs.append(m(
            f"Fix the type error in this RhinoCommon code:\n```python\n{RC}\n{buggy}\n```",
            f"{RC}\n{fixed}",
            "medium", "RhinoCommon", ["fix", "type-error"]))

    # ── 6) Logic bugs (degrees vs radians) ──
    logic_bugs = [
        ("xform = rg.Transform.Rotation(45, rg.Vector3d.ZAxis, rg.Point3d.Origin)",
         "import math\nxform = rg.Transform.Rotation(math.radians(45), rg.Vector3d.ZAxis, rg.Point3d.Origin)",
         "Rotation takes radians not degrees"),
        ("import math\nfor i in range(36):\n    x = 5 * math.cos(i * 10)\n    y = 5 * math.sin(i * 10)",
         "import math\nfor i in range(36):\n    x = 5 * math.cos(math.radians(i * 10))\n    y = 5 * math.sin(math.radians(i * 10))",
         "cos/sin need radians"),
        ("pts = []\nfor i in range(10):\n    pts.append((i, 0, 0))\nrs.AddPolyline(pts)",
         "pts = []\nfor i in range(10):\n    pts.append((i, 0, 0))\npts.append(pts[0])\nrs.AddPolyline(pts)",
         "polyline not closed"),
        ("for i in range(5):\n    rs.AddCircle((i*3, 0, 0), 0)",
         "for i in range(5):\n    rs.AddCircle((i*3, 0, 0), 1)",
         "radius of 0 is invalid"),
        ("pts = [(0,0,0), (10,0,0)]\nrs.AddCurve(pts, 3)",
         "pts = [(0,0,0), (10,0,0)]\nrs.AddCurve(pts, 1)",
         "degree must be < point count"),
        ("rs.RotateObject(obj, (0,0,0), 3.14159)",
         "rs.RotateObject(obj, (0,0,0), 180)",
         "rs.RotateObject uses degrees, not radians"),
    ]
    for buggy, fixed, desc in logic_bugs:
        imp = RC if "rg." in buggy else "import rhinoscriptsyntax as rs"
        imp_fix = RC if "rg." in fixed else "import rhinoscriptsyntax as rs"
        if "import math" in fixed and "import math" not in imp_fix:
            imp_fix = imp_fix
        api = "RhinoCommon" if "rg." in buggy else "rhinoscriptsyntax"
        pairs.append(m(
            f"Fix the logic bug in this code ({desc}):\n```python\n{imp}\n{buggy}\n```",
            f"{imp_fix}\n{fixed}",
            "medium", api, ["fix", "logic"]))

    # ── 7) Wrong method names ──
    wrong_methods = [
        ("rs.Length(crv)", "rs.CurveLength(crv)", "Length -> CurveLength"),
        ("rs.Area(srf)", "rs.SurfaceArea(srf)", "Area -> SurfaceArea"),
        ("rs.AddSurface(pts)", "rs.AddSrfPt(pts)", "AddSurface -> AddSrfPt"),
        ("rs.CurvePoint(crv, 0.5)", "rs.EvaluateCurve(crv, 0.5)", "CurvePoint -> EvaluateCurve"),
        ("rs.SurfacePoint(srf, 0.5, 0.5)", "rs.EvaluateSurface(srf, 0.5, 0.5)", "SurfacePoint -> EvaluateSurface"),
        ("rs.CreateLayer('Test')", "rs.AddLayer('Test')", "CreateLayer -> AddLayer"),
        ("rs.SetLayer(obj, 'Test')", "rs.ObjectLayer(obj, 'Test')", "SetLayer -> ObjectLayer"),
        ("rs.SetColor(obj, (255,0,0))", "rs.ObjectColor(obj, (255,0,0))", "SetColor -> ObjectColor"),
        ("rs.SetName(obj, 'MyObj')", "rs.ObjectName(obj, 'MyObj')", "SetName -> ObjectName"),
        ("rs.Explode(brep)", "rs.ExplodePolysurfaces(brep)", "Explode -> ExplodePolysurfaces"),
        ("rs.Offset(crv, 2)", "rs.OffsetCurve(crv, (0,0,0), 2)", "Offset -> OffsetCurve with direction"),
        ("rs.GetCurve('Select')", "rs.GetObject('Select', 4)", "GetCurve -> GetObject with filter"),
        ("rs.GetSurface('Select')", "rs.GetObject('Select', 8)", "GetSurface -> GetObject with filter"),
        ("rs.AddNurbsCurve(pts, 3)", "rs.AddCurve(pts, 3)", "AddNurbsCurve -> AddCurve"),
        ("rs.CurveMidpoint(crv)", "rs.CurveMidPoint(crv)", "wrong capitalization"),
    ]
    for buggy, fixed, desc in wrong_methods:
        pairs.append(m(
            f"Fix the wrong method name ({desc}):\n```python\nimport rhinoscriptsyntax as rs\n{buggy}\n```",
            f"import rhinoscriptsyntax as rs\n{fixed}",
            "easy", "rhinoscriptsyntax", ["fix", "method-name"]))

    # ── 8) Collection/format errors ──
    collection_errors = [
        ("rs.AddLoftSrf(crv1, crv2)", "rs.AddLoftSrf([crv1, crv2])", "loft needs list"),
        ("rs.BooleanUnion(box, sphere)", "rs.BooleanUnion([box, sphere])", "union needs list"),
        ("rs.JoinCurves(crv1, crv2)", "rs.JoinCurves([crv1, crv2])", "join needs list"),
        ("rs.AddPolyline((0,0,0), (10,0,0), (10,10,0))", "rs.AddPolyline([(0,0,0), (10,0,0), (10,10,0)])", "polyline needs list of points"),
        ("rs.DeleteObjects(obj1, obj2, obj3)", "rs.DeleteObjects([obj1, obj2, obj3])", "delete needs list"),
        ("rs.SelectObjects(obj1, obj2)", "rs.SelectObjects([obj1, obj2])", "select needs list"),
        ("rs.AddSrfPt((0,0,0), (10,0,0), (10,10,0), (0,10,0))", "rs.AddSrfPt([(0,0,0), (10,0,0), (10,10,0), (0,10,0)])", "SrfPt needs list"),
    ]
    for buggy, fixed, desc in collection_errors:
        pairs.append(m(
            f"Fix the collection error ({desc}):\n```python\nimport rhinoscriptsyntax as rs\n{buggy}\n```",
            f"import rhinoscriptsyntax as rs\n{fixed}",
            "easy", "rhinoscriptsyntax", ["fix", "collection"]))

    # ── 9) Missing operations ──
    missing_ops = [
        ("mesh = rg.Mesh()\nmesh.Vertices.Add(0,0,0)\nmesh.Vertices.Add(10,0,0)\nmesh.Vertices.Add(5,10,0)\nmesh.Faces.AddFace(0,1,2)\nsc.doc.Objects.AddMesh(mesh)",
         "mesh = rg.Mesh()\nmesh.Vertices.Add(0,0,0)\nmesh.Vertices.Add(10,0,0)\nmesh.Vertices.Add(5,10,0)\nmesh.Faces.AddFace(0,1,2)\nmesh.Normals.ComputeNormals()\nmesh.Compact()\nsc.doc.Objects.AddMesh(mesh)\nsc.doc.Views.Redraw()",
         "mesh missing ComputeNormals and Redraw"),
        ("pts = [(0,0,0),(10,0,0),(10,10,0),(0,10,0)]\nrs.AddPolyline(pts)",
         "pts = [(0,0,0),(10,0,0),(10,10,0),(0,10,0),(0,0,0)]\nrs.AddPolyline(pts)",
         "polyline not closing back to start"),
        ("crv = rs.AddCircle((0,0,0), 5)\npath = rs.AddLine((0,0,0),(0,0,10))\nrs.ExtrudeCurve(crv, path)",
         "crv = rs.AddCircle((0,0,0), 5)\npath = rs.AddLine((0,0,0),(0,0,10))\nsrf = rs.ExtrudeCurve(crv, path)\nrs.CapPlanarHoles(srf)\nrs.DeleteObject(path)",
         "extrusion not capped, path not cleaned up"),
        ("srf = rs.AddSphere((0,0,0), 5)\nmesh = rg.Mesh()\nsc.doc.Objects.AddMesh(mesh)",
         "import Rhino.Geometry as rg\nimport scriptcontext as sc\nsphere = rg.Sphere(rg.Point3d(0,0,0), 5)\nmesh = rg.Mesh.CreateFromSphere(sphere, 20, 20)\nsc.doc.Objects.AddMesh(mesh)\nsc.doc.Views.Redraw()",
         "empty mesh, wrong API mix"),
    ]
    for buggy, fixed, desc in missing_ops:
        imp = RC if "rg." in buggy else "import rhinoscriptsyntax as rs"
        imp_fix = RC if "rg." in fixed else "import rhinoscriptsyntax as rs"
        if fixed.startswith("import"):
            code_fix = fixed
        else:
            code_fix = f"{imp_fix}\n{fixed}"
        api = "RhinoCommon" if "rg." in fixed else "rhinoscriptsyntax"
        pairs.append(m(
            f"Fix the missing operation ({desc}):\n```python\n{imp}\n{buggy}\n```",
            code_fix,
            "medium", api, ["fix", "missing-operation"]))

    # ── 10) Scope/variable errors ──
    scope_errors = [
        ("for i in range(5):\n    pt = rs.AddPoint(i, 0, 0)\nrs.DeleteObject(pt)",
         "pts = []\nfor i in range(5):\n    pts.append(rs.AddPoint(i, 0, 0))\nfor pt in pts:\n    rs.DeleteObject(pt)",
         "pt only holds last point, need list"),
        ("obj = rs.GetObject('Select')\nrs.MoveObject(obj, vec)",
         "obj = rs.GetObject('Select')\nif obj:\n    vec = (10, 0, 0)\n    rs.MoveObject(obj, vec)",
         "vec undefined"),
        ("crv = rs.AddCircle((0,0,0), 5)\nprint(crv_length)",
         "crv = rs.AddCircle((0,0,0), 5)\ncrv_length = rs.CurveLength(crv)\nprint(crv_length)",
         "crv_length undefined"),
        ("result = []\nfor i in range(10):\n    rs.AddPoint(i, 0, 0)\nrs.DeleteObjects(result)",
         "result = []\nfor i in range(10):\n    pt = rs.AddPoint(i, 0, 0)\n    result.append(pt)\nrs.DeleteObjects(result)",
         "result is always empty"),
        ("layers = rs.LayerNames()\nfor l in layers:\n    count = rs.ObjectsByLayer(l)\n    print(l, len(count))",
         "layers = rs.LayerNames()\nif layers:\n    for l in layers:\n        objs = rs.ObjectsByLayer(l)\n        count = len(objs) if objs else 0\n        print(l, count)",
         "ObjectsByLayer can return None"),
    ]
    for buggy, fixed, desc in scope_errors:
        pairs.append(m(
            f"Fix the variable/scope error ({desc}):\n```python\nimport rhinoscriptsyntax as rs\n{buggy}\n```",
            f"import rhinoscriptsyntax as rs\n{fixed}",
            "medium", "rhinoscriptsyntax", ["fix", "scope", "variable"]))

    # ── 11) Python 2 vs 3 issues ──
    py23_issues = [
        ("print 'Hello'", "print('Hello')", "print statement vs function"),
        ("for i in xrange(10):\n    rs.AddPoint(i, 0, 0)", "for i in range(10):\n    rs.AddPoint(i, 0, 0)", "xrange removed in Python 3"),
        ("if rs.GetObject('Select').has_key('id'):", "obj = rs.GetObject('Select')\nif obj:\n    print('Object selected')", "has_key removed in Python 3"),
        ("pts = rs.GetObjects('Select')\npts.sort(lambda a,b: cmp(a,b))", "pts = rs.GetObjects('Select')\nif pts:\n    pts = sorted(pts)", "cmp removed in Python 3"),
        ("length = rs.CurveLength(crv)\nprint \"Length: %s\" % length", "length = rs.CurveLength(crv)\nprint('Length: {}'.format(length))", "print and string formatting"),
    ]
    for buggy, fixed, desc in py23_issues:
        pairs.append(m(
            f"Fix this Python 2 code for Python 3 ({desc}):\n```python\nimport rhinoscriptsyntax as rs\n{buggy}\n```",
            f"import rhinoscriptsyntax as rs\n{fixed}",
            "easy", "rhinoscriptsyntax", ["fix", "python3"]))

    # ── 12) GhPython-specific bugs ──
    gh_bugs = [
        ("import ghpythonlib.components as ghcomp\nresult = ghcomp.Move(geo, (10,0,0))",
         "import ghpythonlib.components as ghcomp\nimport Rhino.Geometry as rg\nresult = ghcomp.Move(geo, rg.Vector3d(10,0,0))",
         "tuple instead of Vector3d"),
        ("import Grasshopper\ntree = Grasshopper.DataTree()\ntree.Add(1, Grasshopper.GH_Path(0))",
         "import Grasshopper as gh\ntree = gh.DataTree[object]()\ntree.Add(1, gh.Kernel.Data.GH_Path(0))",
         "wrong DataTree creation and path"),
        ("import Rhino.Geometry as rg\na = []\nfor pt in x:\n    a.append(rg.Circle(pt, r))",
         "import Rhino.Geometry as rg\na = []\nfor pt in x:\n    plane = rg.Plane(pt, rg.Vector3d.ZAxis)\n    a.append(rg.Circle(plane, r).ToNurbsCurve())",
         "Circle needs Plane not Point, needs ToNurbsCurve"),
        ("import ghpythonlib.treehelpers as th\nresult = th.list_to_tree(data)\na = result.Branch(0)",
         "import ghpythonlib.treehelpers as th\nimport Rhino.Geometry as rg\nresult = th.list_to_tree(data)\nif result.BranchCount > 0:\n    a = list(result.Branch(0))\nelse:\n    a = []",
         "missing branch count check, needs list()"),
    ]
    for buggy, fixed, desc in gh_bugs:
        pairs.append(m(
            f"Fix this GhPython component ({desc}):\n```python\n{buggy}\n```",
            fixed,
            "medium", "grasshopper", ["fix", "grasshopper"]))

    # ── 13) rhino3dm bugs ──
    r3dm_bugs = [
        ("import rhino3dm\nmodel = rhino3dm.File3dm()\nmodel.Objects.AddPoint(0, 0, 0)",
         "import rhino3dm\nmodel = rhino3dm.File3dm()\nmodel.Objects.AddPoint(rhino3dm.Point3d(0, 0, 0))",
         "AddPoint needs Point3d not raw coords"),
        ("import rhino3dm\nmodel = rhino3dm.File3dm()\nmodel.Write('output.3dm')",
         "import rhino3dm\nmodel = rhino3dm.File3dm()\nmodel.Write('output.3dm', 7)",
         "Write needs version number"),
        ("import rhino3dm\nmodel = rhino3dm.File3dm.Read('input.3dm')\nfor obj in model:\n    print(obj)",
         "import rhino3dm\nmodel = rhino3dm.File3dm.Read('input.3dm')\nfor obj in model.Objects:\n    print(type(obj.Geometry).__name__)",
         "iterate model.Objects not model"),
        ("import rhino3dm\nmodel = rhino3dm.File3dm()\nlayer = rhino3dm.Layer()\nlayer.name = 'Test'\nmodel.Layers.Add(layer)",
         "import rhino3dm\nmodel = rhino3dm.File3dm()\nlayer = rhino3dm.Layer()\nlayer.Name = 'Test'\nmodel.Layers.Add(layer)",
         "Name property is capitalized"),
    ]
    for buggy, fixed, desc in r3dm_bugs:
        pairs.append(m(
            f"Fix this rhino3dm code ({desc}):\n```python\n{buggy}\n```",
            fixed,
            "medium", "rhino3dm", ["fix", "rhino3dm"]))

    # ── 14) Performance/best practices ──
    perf_fixes = [
        ("for i in range(1000):\n    rs.AddPoint(i, 0, 0)\n    rs.Redraw()",
         "rs.EnableRedraw(False)\nfor i in range(1000):\n    rs.AddPoint(i, 0, 0)\nrs.EnableRedraw(True)",
         "redraw inside loop kills performance"),
        ("objs = rs.AllObjects()\nfor obj in objs:\n    if rs.ObjectLayer(obj) == 'Delete':\n        rs.DeleteObject(obj)",
         "objs = rs.ObjectsByLayer('Delete')\nif objs:\n    rs.DeleteObjects(objs)",
         "use ObjectsByLayer instead of filtering all"),
        ("for i in range(100):\n    for j in range(100):\n        rs.AddPoint(i, j, 0)",
         "rs.EnableRedraw(False)\nfor i in range(100):\n    for j in range(100):\n        rs.AddPoint(i, j, 0)\nrs.EnableRedraw(True)",
         "disable redraw for bulk operations"),
    ]
    for buggy, fixed, desc in perf_fixes:
        pairs.append(m(
            f"Optimize this slow script ({desc}):\n```python\nimport rhinoscriptsyntax as rs\n{buggy}\n```",
            f"import rhinoscriptsyntax as rs\n{fixed}",
            "medium", "rhinoscriptsyntax", ["fix", "performance"]))

    # ── 15) Template expansion: common bug patterns × shapes ──
    shapes = ["sphere", "cylinder", "cone", "box"]
    for shape in shapes:
        # Missing import
        pairs.append(m(
            f"Fix this script that's missing the import:\n```python\nrs.Add{shape.capitalize()}((0,0,0), 5)\n```",
            f"import rhinoscriptsyntax as rs\nrs.Add{shape.capitalize()}((0,0,0), 5)" if shape == "sphere" else f"import rhinoscriptsyntax as rs\nrs.AddSphere((0,0,0), 5)",
            "easy", "rhinoscriptsyntax", ["fix", "import", shape]))

    # Error handling patterns
    error_handling = [
        ("Add try/except to handle geometry creation failure",
         "import rhinoscriptsyntax as rs\ntry:\n    srf = rs.AddLoftSrf(curves)\n    if not srf:\n        print('Loft failed')\nexcept Exception as e:\n    print('Error:', str(e))",
         "medium", "rhinoscriptsyntax", ["fix", "error-handling"]),
        ("Add error handling to file read operation",
         "import rhino3dm\nimport os\npath = 'input.3dm'\nif os.path.exists(path):\n    model = rhino3dm.File3dm.Read(path)\n    if model:\n        print(f'Objects: {len(model.Objects)}')\n    else:\n        print('Failed to read file')\nelse:\n    print('File not found')",
         "medium", "rhino3dm", ["fix", "error-handling"]),
    ]
    for inst, code, diff, api, tags in error_handling:
        pairs.append(m(inst, code, diff, api, tags))

    return pairs
