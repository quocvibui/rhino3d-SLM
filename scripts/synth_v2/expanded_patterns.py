"""Expanded template patterns to push total pair count past 2500.
Covers: object queries, layer management, transforms, analysis,
GhPython, design workflows, code fixing, selection/filtering."""

import math

def m(instruction, code, category, difficulty, api, tags):
    return {"instruction": instruction, "code": code, "source": "synthetic",
            "category": category, "difficulty": difficulty, "api": api, "tags": tags}

RS = "import rhinoscriptsyntax as rs"
RSM = "import rhinoscriptsyntax as rs\nimport math"
RC = "import Rhino.Geometry as rg\nimport scriptcontext as sc"
RCM = "import Rhino.Geometry as rg\nimport scriptcontext as sc\nimport math"
REDRAW = "sc.doc.Views.Redraw()"
R3 = "import rhino3dm"
GH = "import Rhino.Geometry as rg\nimport Grasshopper as gh\nfrom Grasshopper.Kernel.Data import GH_Path\nfrom Grasshopper import DataTree"

def generate():
    pairs = []

    # ═══════════════════════════════════════════════════════════
    # 1) OBJECT PROPERTY QUERIES (~200 pairs)
    # ═══════════════════════════════════════════════════════════

    # ObjectType checks for different geometry types
    obj_types = [
        ("point", 1), ("curve", 4), ("surface", 8), ("polysurface", 16),
        ("mesh", 32), ("light", 256), ("annotation", 512), ("block", 4096),
    ]
    for name, filt in obj_types:
        pairs.append(m(f"Select all {name}s in the document",
            f"{RS}\nobjs = rs.ObjectsByType({filt})\nif objs:\n    print(f'Found {{len(objs)}} {name}(s)')\n    rs.SelectObjects(objs)",
            "how_do_i_questions", "easy", "rhinoscriptsyntax", ["selection", name]))
        pairs.append(m(f"How do I get all {name} objects?",
            f"{RS}\nobjs = rs.ObjectsByType({filt})\nif objs:\n    for obj in objs:\n        print(rs.ObjectName(obj) or obj)",
            "how_do_i_questions", "easy", "rhinoscriptsyntax", ["query", name]))
        pairs.append(m(f"Count {name}s in the document",
            f"{RS}\nobjs = rs.ObjectsByType({filt})\ncount = len(objs) if objs else 0\nprint(f'{name}s: {{count}}')",
            "how_do_i_questions", "easy", "rhinoscriptsyntax", ["count", name]))

    # Curve property queries
    curve_props = [
        ("length", "rs.CurveLength(crv)"),
        ("start point", "rs.CurveStartPoint(crv)"),
        ("end point", "rs.CurveEndPoint(crv)"),
        ("midpoint", "rs.CurveMidPoint(crv)"),
        ("degree", "rs.CurveDegree(crv)"),
        ("domain", "rs.CurveDomain(crv)"),
        ("point count", "rs.CurvePointCount(crv)"),
        ("is closed", "rs.IsCurveClosed(crv)"),
        ("is planar", "rs.IsCurvePlanar(crv)"),
        ("is linear", "rs.IsCurveLinear(crv)"),
        ("bounding box", "rs.BoundingBox(crv)"),
        ("area centroid", "rs.CurveAreaCentroid(crv)"),
    ]
    for prop_name, prop_code in curve_props:
        pairs.append(m(f"Get the {prop_name} of a selected curve",
            f"{RS}\ncrv = rs.GetObject('Select curve', 4)\nif crv:\n    result = {prop_code}\n    print(f'{prop_name}: {{result}}')",
            "how_do_i_questions", "easy", "rhinoscriptsyntax", ["curve", "property"]))
        pairs.append(m(f"Print the {prop_name} of every curve in the document",
            f"{RS}\ncurves = rs.ObjectsByType(4)\nif curves:\n    for crv in curves:\n        result = {prop_code}\n        print(f'{{rs.ObjectName(crv) or crv}}: {{result}}')",
            "how_do_i_questions", "medium", "rhinoscriptsyntax", ["curve", "batch"]))

    # Surface property queries
    srf_props = [
        ("area", "rs.SurfaceArea(srf)"),
        ("is planar", "rs.IsSurfacePlanar(srf)"),
        ("is closed", "rs.IsSurfaceClosed(srf, 0)"),
        ("domain in U", "rs.SurfaceDomain(srf, 0)"),
        ("domain in V", "rs.SurfaceDomain(srf, 1)"),
        ("degree in U", "rs.SurfaceDegree(srf, 0)"),
        ("degree in V", "rs.SurfaceDegree(srf, 1)"),
        ("point count in U", "rs.SurfacePointCount(srf)[0]"),
        ("normal at center", "du = rs.SurfaceDomain(srf, 0)\n    dv = rs.SurfaceDomain(srf, 1)\n    result = rs.SurfaceNormal(srf, ((du[0]+du[1])/2, (dv[0]+dv[1])/2))"),
    ]
    for prop_name, prop_code in srf_props:
        pairs.append(m(f"Get the {prop_name} of a surface",
            f"{RS}\nsrf = rs.GetObject('Select surface', 8)\nif srf:\n    result = {prop_code}\n    print(f'{prop_name}: {{result}}')",
            "how_do_i_questions", "easy", "rhinoscriptsyntax", ["surface", "property"]))

    # Object name/color/material operations
    obj_ops = [
        ("rename an object", "rs.ObjectName(obj, 'NewName')"),
        ("get the name of an object", "name = rs.ObjectName(obj)\nprint(f'Name: {name}')"),
        ("change object color to red", "rs.ObjectColor(obj, (255, 0, 0))"),
        ("change object color to blue", "rs.ObjectColor(obj, (0, 0, 255))"),
        ("change object color to green", "rs.ObjectColor(obj, (0, 255, 0))"),
        ("get the color of an object", "color = rs.ObjectColor(obj)\nprint(f'Color: {color}')"),
        ("change an object to wireframe display", "rs.ObjectDisplayMode(obj, 0)"),
        ("change an object to shaded display", "rs.ObjectDisplayMode(obj, 2)"),
        ("lock an object", "rs.LockObject(obj)"),
        ("unlock an object", "rs.UnlockObject(obj)"),
        ("hide an object", "rs.HideObject(obj)"),
        ("show a hidden object", "rs.ShowObject(obj)"),
        ("check if object is valid", "valid = rs.IsObjectValid(obj)\nprint(f'Valid: {valid}')"),
        ("get object type", "otype = rs.ObjectType(obj)\nprint(f'Type: {otype}')"),
        ("duplicate an object", "copy = rs.CopyObject(obj, (0, 0, 0))"),
    ]
    for desc, code in obj_ops:
        pairs.append(m(f"How do I {desc}?",
            f"{RS}\nobj = rs.GetObject('Select object')\nif obj:\n    {code}",
            "how_do_i_questions", "easy", "rhinoscriptsyntax", ["object", "property"]))

    # ═══════════════════════════════════════════════════════════
    # 2) LAYER MANAGEMENT (~80 pairs)
    # ═══════════════════════════════════════════════════════════

    colors = [("Red", (255,0,0)), ("Blue", (0,0,255)), ("Green", (0,255,0)),
              ("Yellow", (255,255,0)), ("Cyan", (0,255,255)), ("Magenta", (255,0,255)),
              ("Orange", (255,165,0)), ("White", (255,255,255))]
    for name, rgb in colors:
        pairs.append(m(f"Create a layer named '{name}' with {name.lower()} color",
            f"{RS}\nrs.AddLayer('{name}', {rgb})",
            "how_do_i_questions", "easy", "rhinoscriptsyntax", ["layer", "create"]))

    # Layer operations
    layer_ops = [
        ("get all layer names", "layers = rs.LayerNames()\nif layers:\n    for l in layers:\n        print(l)"),
        ("turn off a layer", "rs.LayerVisible('LayerName', False)"),
        ("turn on a layer", "rs.LayerVisible('LayerName', True)"),
        ("lock a layer", "rs.LayerLocked('LayerName', True)"),
        ("unlock a layer", "rs.LayerLocked('LayerName', False)"),
        ("delete a layer", "rs.DeleteLayer('LayerName')"),
        ("rename a layer", "rs.RenameLayer('OldName', 'NewName')"),
        ("get current layer", "current = rs.CurrentLayer()\nprint(f'Current layer: {current}')"),
        ("set current layer", "rs.CurrentLayer('LayerName')"),
        ("get layer color", "color = rs.LayerColor('LayerName')\nprint(f'Color: {color}')"),
        ("set layer color", "rs.LayerColor('LayerName', (255, 0, 0))"),
        ("get objects on a layer", "objs = rs.ObjectsByLayer('LayerName')\nif objs:\n    print(f'Objects: {len(objs)}')"),
        ("move object to a layer", "rs.ObjectLayer(obj, 'TargetLayer')"),
        ("create sublayer", "rs.AddLayer('Parent::Child')"),
        ("get layer of an object", "layer = rs.ObjectLayer(obj)\nprint(f'Layer: {layer}')"),
        ("check if layer exists", "exists = rs.IsLayer('LayerName')\nprint(f'Exists: {exists}')"),
    ]
    for desc, code in layer_ops:
        pairs.append(m(f"How do I {desc}?",
            f"{RS}\n{code}",
            "how_do_i_questions", "easy", "rhinoscriptsyntax", ["layer"]))
    for desc, code in layer_ops:
        pairs.append(m(f"What is the command to {desc} in Python?",
            f"{RS}\n{code}",
            "how_do_i_questions", "easy", "rhinoscriptsyntax", ["layer"]))

    # Multi-layer operations
    for n in [5, 10, 15, 20]:
        pairs.append(m(f"Create {n} layers named Layer_01 through Layer_{n:02d}",
            f"{RS}\nfor i in range(1, {n+1}):\n    rs.AddLayer(f'Layer_{{i:02d}}')",
            "how_do_i_questions", "easy", "rhinoscriptsyntax", ["layer", "batch"]))
    for n in [5, 10, 15, 20]:
        pairs.append(m(f"Create {n} layers with rainbow colors",
            f"{RSM}\nfor i in range({n}):\n    hue = i * 360.0 / {n}\n    r = int(128 + 127 * math.cos(math.radians(hue)))\n    g = int(128 + 127 * math.cos(math.radians(hue - 120)))\n    b = int(128 + 127 * math.cos(math.radians(hue - 240)))\n    rs.AddLayer(f'Color_{{i:02d}}', (r, g, b))",
            "how_do_i_questions", "medium", "rhinoscriptsyntax", ["layer", "color"]))

    # ═══════════════════════════════════════════════════════════
    # 3) ADDITIONAL TRANSFORMS & COMBOS (~150 pairs)
    # ═══════════════════════════════════════════════════════════

    # Mirror operations
    shapes_basic = [("sphere", "rs.AddSphere((0,0,0), 5)"),
                    ("box", "rs.AddBox([(0,0,0),(10,0,0),(10,10,0),(0,10,0),(0,0,5),(10,0,5),(10,10,5),(0,10,5)])"),
                    ("circle", "rs.AddCircle((5,5,0), 3)")]
    mirror_planes = [("YZ plane", "(0,0,0)", "(0,1,0)"),
                     ("XZ plane", "(0,0,0)", "(1,0,0)"),
                     ("XY plane", "(0,0,0)", "(0,0,1)")]
    for s_name, s_code in shapes_basic:
        for mp_name, mp1, mp2 in mirror_planes:
            pairs.append(m(f"Mirror a {s_name} across the {mp_name}",
                f"{RS}\nobj = {s_code}\nrs.MirrorObject(obj, {mp1}, {mp2}, True)",
                "multi_step_workflows", "easy", "rhinoscriptsyntax", ["mirror", s_name]))

    # Orient operations (copy from plane to plane)
    for s_name, s_code in shapes_basic:
        pairs.append(m(f"Orient a {s_name} from XY to XZ plane",
            f"{RS}\nobj = {s_code}\nrs.OrientObject(obj, [(0,0,0),(1,0,0),(0,1,0)], [(0,0,0),(1,0,0),(0,0,1)])",
            "multi_step_workflows", "medium", "rhinoscriptsyntax", ["orient", s_name]))
        pairs.append(m(f"Orient a {s_name} from XY to YZ plane",
            f"{RS}\nobj = {s_code}\nrs.OrientObject(obj, [(0,0,0),(1,0,0),(0,1,0)], [(0,0,0),(0,1,0),(0,0,1)])",
            "multi_step_workflows", "medium", "rhinoscriptsyntax", ["orient", s_name]))

    # Multi-transform: create + move + rotate + scale
    for s_name, s_code in shapes_basic:
        pairs.append(m(f"Create a {s_name}, move it, rotate it 45 degrees, and scale it by 2x",
            f"{RS}\nobj = {s_code}\nrs.MoveObject(obj, (10, 0, 0))\nrs.RotateObject(obj, (10,0,0), 45)\nrs.ScaleObject(obj, (10,0,0), (2,2,2))",
            "multi_step_workflows", "medium", "rhinoscriptsyntax", ["transform", "combo", s_name]))

    # RhinoCommon transforms
    rc_transforms = [
        ("translate", "rg.Transform.Translation(rg.Vector3d(10, 0, 0))"),
        ("rotate 45 degrees around Z", "rg.Transform.Rotation(math.radians(45), rg.Vector3d.ZAxis, rg.Point3d.Origin)"),
        ("scale by 2", "rg.Transform.Scale(rg.Point3d.Origin, 2.0)"),
        ("mirror across YZ", "rg.Transform.Mirror(rg.Plane.WorldYZ)"),
        ("shear", "rg.Transform.Shear(rg.Plane.WorldXY, rg.Vector3d(0.3, 0, 0), rg.Vector3d(0, 0.3, 0), rg.Vector3d(0, 0, 1))"),
    ]
    for desc, xform_code in rc_transforms:
        pairs.append(m(f"Apply a RhinoCommon {desc} transform to selected objects",
            f"{RCM}\nobjs = [o.Id for o in sc.doc.Objects]\nxform = {xform_code}\nfor obj_id in objs:\n    sc.doc.Objects.Transform(obj_id, xform, True)\n{REDRAW}",
            "multi_step_workflows", "medium", "RhinoCommon", ["transform", "rhinocommon"]))

    # Linear arrays with different spacings and directions
    for axis, vec in [("X", "(sp,0,0)"), ("Y", "(0,sp,0)"), ("Z", "(0,0,sp)")]:
        for n in [3, 5, 8, 10, 20]:
            for sp in [2, 5, 10]:
                pairs.append(m(
                    f"Create a linear array of {n} objects along {axis} with spacing {sp}",
                    f"{RS}\nobj = rs.GetObject('Select object')\nif obj:\n    sp = {sp}\n    for i in range(1, {n}):\n        rs.CopyObject(obj, {vec})",
                    "multi_step_workflows", "easy", "rhinoscriptsyntax", ["array", "linear"]))

    # ═══════════════════════════════════════════════════════════
    # 4) GEOMETRY ANALYSIS (~100 pairs)
    # ═══════════════════════════════════════════════════════════

    # Bounding box operations
    bb_ops = [
        ("get bounding box dimensions",
         "bb = rs.BoundingBox(obj)\nif bb:\n    dx = rs.Distance(bb[0], bb[1])\n    dy = rs.Distance(bb[0], bb[3])\n    dz = rs.Distance(bb[0], bb[4])\n    print(f'Width: {dx}, Depth: {dy}, Height: {dz}')"),
        ("get bounding box center",
         "bb = rs.BoundingBox(obj)\nif bb:\n    cx = (bb[0][0] + bb[6][0]) / 2\n    cy = (bb[0][1] + bb[6][1]) / 2\n    cz = (bb[0][2] + bb[6][2]) / 2\n    rs.AddPoint(cx, cy, cz)"),
        ("get bounding box volume",
         "bb = rs.BoundingBox(obj)\nif bb:\n    dx = rs.Distance(bb[0], bb[1])\n    dy = rs.Distance(bb[0], bb[3])\n    dz = rs.Distance(bb[0], bb[4])\n    print(f'Volume: {dx * dy * dz}')"),
        ("draw bounding box edges",
         "bb = rs.BoundingBox(obj)\nif bb:\n    edges = [(0,1),(1,2),(2,3),(3,0),(4,5),(5,6),(6,7),(7,4),(0,4),(1,5),(2,6),(3,7)]\n    for a, b in edges:\n        rs.AddLine(bb[a], bb[b])"),
    ]
    for desc, code in bb_ops:
        pairs.append(m(f"How do I {desc}?",
            f"{RS}\nobj = rs.GetObject('Select object')\nif obj:\n    {code}",
            "how_do_i_questions", "medium", "rhinoscriptsyntax", ["analysis", "bounding-box"]))

    # Distance and measurement
    measure_ops = [
        ("measure distance between two points",
         "p1 = rs.GetPoint('First point')\np2 = rs.GetPoint('Second point')\nif p1 and p2:\n    d = rs.Distance(p1, p2)\n    print(f'Distance: {d}')"),
        ("find closest point on a curve to a point",
         "crv = rs.GetObject('Select curve', 4)\npt = rs.GetPoint('Select point')\nif crv and pt:\n    t = rs.CurveClosestPoint(crv, pt)\n    cp = rs.EvaluateCurve(crv, t)\n    print(f'Closest point: {cp}')"),
        ("find closest point on a surface to a point",
         "srf = rs.GetObject('Select surface', 8)\npt = rs.GetPoint('Select point')\nif srf and pt:\n    uv = rs.SurfaceClosestPoint(srf, pt)\n    cp = rs.EvaluateSurface(srf, uv[0], uv[1])\n    print(f'Closest point: {cp}')"),
        ("calculate curve curvature at midpoint",
         "crv = rs.GetObject('Select curve', 4)\nif crv:\n    t = rs.CurveDomain(crv)\n    mid_t = (t[0] + t[1]) / 2\n    curv = rs.CurveCurvature(crv, mid_t)\n    if curv:\n        print(f'Curvature: {curv[3]}')"),
        ("measure angle between two lines",
         "l1 = rs.GetObject('First line', 4)\nl2 = rs.GetObject('Second line', 4)\nif l1 and l2:\n    v1 = rs.VectorCreate(rs.CurveEndPoint(l1), rs.CurveStartPoint(l1))\n    v2 = rs.VectorCreate(rs.CurveEndPoint(l2), rs.CurveStartPoint(l2))\n    angle = rs.VectorAngle(v1, v2)\n    print(f'Angle: {angle} degrees')"),
    ]
    for desc, code in measure_ops:
        pairs.append(m(f"How do I {desc}?",
            f"{RS}\n{code}",
            "how_do_i_questions", "medium", "rhinoscriptsyntax", ["analysis", "measure"]))

    # Surface analysis
    srf_analysis = [
        ("evaluate surface at a UV parameter",
         "srf = rs.GetObject('Select surface', 8)\nif srf:\n    dom_u = rs.SurfaceDomain(srf, 0)\n    dom_v = rs.SurfaceDomain(srf, 1)\n    u = (dom_u[0] + dom_u[1]) / 2\n    v = (dom_v[0] + dom_v[1]) / 2\n    pt = rs.EvaluateSurface(srf, u, v)\n    print(f'Point at center: {pt}')"),
        ("create a grid of points on a surface",
         "srf = rs.GetObject('Select surface', 8)\nif srf:\n    du = rs.SurfaceDomain(srf, 0)\n    dv = rs.SurfaceDomain(srf, 1)\n    for i in range(11):\n        for j in range(11):\n            u = du[0] + (du[1] - du[0]) * i / 10\n            v = dv[0] + (dv[1] - dv[0]) * j / 10\n            pt = rs.EvaluateSurface(srf, u, v)\n            rs.AddPoint(pt)"),
        ("get surface normals at grid points",
         "srf = rs.GetObject('Select surface', 8)\nif srf:\n    du = rs.SurfaceDomain(srf, 0)\n    dv = rs.SurfaceDomain(srf, 1)\n    for i in range(5):\n        for j in range(5):\n            u = du[0] + (du[1] - du[0]) * i / 4\n            v = dv[0] + (dv[1] - dv[0]) * j / 4\n            pt = rs.EvaluateSurface(srf, u, v)\n            n = rs.SurfaceNormal(srf, (u, v))\n            rs.AddLine(pt, rs.PointAdd(pt, rs.VectorScale(n, 2)))"),
        ("extract isocurves from a surface",
         "srf = rs.GetObject('Select surface', 8)\nif srf:\n    du = rs.SurfaceDomain(srf, 0)\n    for i in range(11):\n        u = du[0] + (du[1] - du[0]) * i / 10\n        crv = rs.ExtractIsoCurve(srf, (u, 0), 1)\n        if crv:\n            rs.ObjectColor(crv[0], (255, 0, 0))"),
        ("get Gaussian curvature at surface center",
         "srf = rs.GetObject('Select surface', 8)\nif srf:\n    du = rs.SurfaceDomain(srf, 0)\n    dv = rs.SurfaceDomain(srf, 1)\n    u = (du[0] + du[1]) / 2\n    v = (dv[0] + dv[1]) / 2\n    data = rs.SurfaceCurvature(srf, (u, v))\n    if data:\n        print(f'Gaussian curvature: {data[7]}')"),
    ]
    for desc, code in srf_analysis:
        pairs.append(m(f"How do I {desc}?",
            f"{RS}\n{code}",
            "how_do_i_questions", "medium", "rhinoscriptsyntax", ["surface", "analysis"]))

    # Volume/area calculations
    vol_area = [
        ("calculate volume of a closed polysurface",
         "obj = rs.GetObject('Select closed polysurface', 16)\nif obj:\n    if rs.IsPolysurfaceClosed(obj):\n        vol = rs.SurfaceVolume(obj)\n        if vol:\n            print(f'Volume: {vol[0]}')\n    else:\n        print('Object is not closed')"),
        ("calculate surface area",
         "obj = rs.GetObject('Select surface or polysurface', 8+16)\nif obj:\n    area = rs.SurfaceArea(obj)\n    if area:\n        print(f'Area: {area[0]}')"),
        ("calculate centroid of a closed solid",
         "obj = rs.GetObject('Select closed solid', 16)\nif obj:\n    centroid = rs.SurfaceVolumeCentroid(obj)\n    if centroid:\n        print(f'Centroid: {centroid[0]}')\n        rs.AddPoint(centroid[0])"),
    ]
    for desc, code in vol_area:
        pairs.append(m(f"How do I {desc}?",
            f"{RS}\n{code}",
            "how_do_i_questions", "medium", "rhinoscriptsyntax", ["analysis", "volume"]))

    # ═══════════════════════════════════════════════════════════
    # 5) GRASSHOPPER PYTHON EXPANDED (~200 pairs)
    # ═══════════════════════════════════════════════════════════

    # DataTree construction patterns
    for n_branches in [3, 5, 8, 10]:
        for items_per in [4, 6, 10]:
            pairs.append(m(
                f"GhPython: create a DataTree with {n_branches} branches of {items_per} numbers each",
                f"{GH}\ntree = DataTree[float]()\nfor i in range({n_branches}):\n    path = GH_Path(i)\n    for j in range({items_per}):\n        tree.Add(float(i * {items_per} + j), path)\na = tree",
                "grasshopper_python", "medium", "grasshopper", ["datatree", "create"]))

    # DataTree from point grid
    for nx in [3, 5, 8, 10]:
        for ny in [3, 5, 8]:
            pairs.append(m(
                f"GhPython: create a {nx}x{ny} point grid as DataTree (one branch per row)",
                f"{GH}\ntree = DataTree[rg.Point3d]()\nfor i in range({nx}):\n    path = GH_Path(i)\n    for j in range({ny}):\n        tree.Add(rg.Point3d(i, j, 0), path)\na = tree",
                "grasshopper_python", "medium", "grasshopper", ["datatree", "grid"]))

    # GhPython mesh operations
    gh_mesh_ops = [
        ("get mesh face count", "a = mesh.Faces.Count"),
        ("get mesh vertex count", "a = mesh.Vertices.Count"),
        ("get mesh face centers", "centers = []\nfor i in range(mesh.Faces.Count):\n    f = mesh.Faces[i]\n    if f.IsQuad:\n        c = rg.Point3d((mesh.Vertices[f.A].X+mesh.Vertices[f.B].X+mesh.Vertices[f.C].X+mesh.Vertices[f.D].X)/4,\n                       (mesh.Vertices[f.A].Y+mesh.Vertices[f.B].Y+mesh.Vertices[f.C].Y+mesh.Vertices[f.D].Y)/4,\n                       (mesh.Vertices[f.A].Z+mesh.Vertices[f.B].Z+mesh.Vertices[f.C].Z+mesh.Vertices[f.D].Z)/4)\n    else:\n        c = rg.Point3d((mesh.Vertices[f.A].X+mesh.Vertices[f.B].X+mesh.Vertices[f.C].X)/3,\n                       (mesh.Vertices[f.A].Y+mesh.Vertices[f.B].Y+mesh.Vertices[f.C].Y)/3,\n                       (mesh.Vertices[f.A].Z+mesh.Vertices[f.B].Z+mesh.Vertices[f.C].Z)/3)\n    centers.append(c)\na = centers"),
        ("get mesh face normals", "a = [rg.Vector3d(mesh.FaceNormals[i]) for i in range(mesh.FaceNormals.Count)]"),
        ("check if mesh is closed", "a = mesh.IsClosed"),
        ("get mesh edges as lines", "edges = mesh.TopologyEdges\na = [edges.EdgeLine(i) for i in range(edges.Count)]"),
        ("get mesh volume", "vol = rg.VolumeMassProperties.Compute(mesh)\na = vol.Volume if vol else 0"),
        ("color mesh vertices by height", "import System.Drawing as sd\nmesh.VertexColors.CreateMonotoneMesh(sd.Color.White)\nfor i in range(mesh.Vertices.Count):\n    z = mesh.Vertices[i].Z\n    t = max(0, min(1, z / max_z)) if max_z > 0 else 0\n    mesh.VertexColors[i] = sd.Color.FromArgb(int(t*255), 0, int((1-t)*255))\na = mesh"),
    ]
    for desc, body in gh_mesh_ops:
        pairs.append(m(f"GhPython: {desc}",
            f"import Rhino.Geometry as rg\n{body}",
            "grasshopper_python", "medium", "grasshopper", ["mesh"]))

    # GhPython transformation patterns
    gh_xforms = [
        ("move points by a vector",
         "a = [rg.Point3d(pt.X + vec.X, pt.Y + vec.Y, pt.Z + vec.Z) for pt in pts]"),
        ("rotate points around origin",
         "import math\nangle = math.radians(degrees)\nresult = []\nfor pt in pts:\n    x = pt.X * math.cos(angle) - pt.Y * math.sin(angle)\n    y = pt.X * math.sin(angle) + pt.Y * math.cos(angle)\n    result.append(rg.Point3d(x, y, pt.Z))\na = result"),
        ("scale points from a center",
         "result = []\nfor pt in pts:\n    dx = pt.X - center.X\n    dy = pt.Y - center.Y\n    dz = pt.Z - center.Z\n    result.append(rg.Point3d(center.X + dx*factor, center.Y + dy*factor, center.Z + dz*factor))\na = result"),
        ("project points to XY plane",
         "a = [rg.Point3d(pt.X, pt.Y, 0) for pt in pts]"),
        ("project points to a surface",
         "result = []\nfor pt in pts:\n    success, u, v = srf.ClosestPoint(pt)\n    if success:\n        result.append(srf.PointAt(u, v))\na = result"),
        ("offset points along normals",
         "result = []\nfor pt, normal in zip(pts, normals):\n    n = rg.Vector3d(normal)\n    n.Unitize()\n    n *= distance\n    result.append(rg.Point3d(pt.X + n.X, pt.Y + n.Y, pt.Z + n.Z))\na = result"),
    ]
    for desc, body in gh_xforms:
        pairs.append(m(f"GhPython: {desc}",
            f"import Rhino.Geometry as rg\n{body}",
            "grasshopper_python", "medium", "grasshopper", ["transform"]))

    # GhPython math/remapping
    gh_math = [
        ("remap a value from one range to another",
         "def remap(val, src_lo, src_hi, dst_lo, dst_hi):\n    t = (val - src_lo) / (src_hi - src_lo)\n    return dst_lo + t * (dst_hi - dst_lo)\na = remap(x, src_min, src_max, dst_min, dst_max)"),
        ("linear interpolation between two points",
         "a = rg.Point3d(pt_a.X + t*(pt_b.X-pt_a.X), pt_a.Y + t*(pt_b.Y-pt_a.Y), pt_a.Z + t*(pt_b.Z-pt_a.Z))"),
        ("create a sine wave of points",
         "import math\nresult = []\nfor i in range(count):\n    x = i * spacing\n    y = amplitude * math.sin(2 * math.pi * frequency * x / (count * spacing))\n    result.append(rg.Point3d(x, y, 0))\na = result"),
        ("create a spiral of points",
         "import math\nresult = []\nfor i in range(count):\n    t = i * 2 * math.pi * turns / count\n    r = start_radius + (end_radius - start_radius) * i / count\n    result.append(rg.Point3d(r * math.cos(t), r * math.sin(t), i * height / count))\na = result"),
        ("smooth a list of numbers (moving average)",
         "result = []\nfor i in range(len(values)):\n    start = max(0, i - window // 2)\n    end = min(len(values), i + window // 2 + 1)\n    result.append(sum(values[start:end]) / (end - start))\na = result"),
        ("normalize values to 0-1 range",
         "lo = min(values)\nhi = max(values)\nrng = hi - lo if hi != lo else 1\na = [(v - lo) / rng for v in values]"),
    ]
    for desc, body in gh_math:
        pairs.append(m(f"GhPython: {desc}",
            f"import Rhino.Geometry as rg\n{body}",
            "grasshopper_python", "medium", "grasshopper", ["math"]))

    # GhPython pattern generation on surfaces
    for u_div in [5, 10, 15, 20]:
        for v_div in [5, 10, 15]:
            pairs.append(m(
                f"GhPython: panelize a surface with {u_div}x{v_div} divisions",
                f"import Rhino.Geometry as rg\npanels = []\nu_dom = srf.Domain(0)\nv_dom = srf.Domain(1)\nfor i in range({u_div}):\n    for j in range({v_div}):\n        u0 = u_dom.T0 + (u_dom.T1-u_dom.T0) * i / {u_div}\n        u1 = u_dom.T0 + (u_dom.T1-u_dom.T0) * (i+1) / {u_div}\n        v0 = v_dom.T0 + (v_dom.T1-v_dom.T0) * j / {v_div}\n        v1 = v_dom.T0 + (v_dom.T1-v_dom.T0) * (j+1) / {v_div}\n        pts = [srf.PointAt(u0,v0), srf.PointAt(u1,v0), srf.PointAt(u1,v1), srf.PointAt(u0,v1), srf.PointAt(u0,v0)]\n        panels.append(rg.Polyline(pts).ToNurbsCurve())\na = panels",
                "grasshopper_python", "hard", "grasshopper", ["panelize", "surface"]))

    # GhPython attractor patterns expanded
    for geo_type, geo_expr in [("circle", "rg.Circle(rg.Plane(pt, rg.Vector3d.ZAxis), r).ToNurbsCurve()"),
                                 ("sphere", "rg.Sphere(pt, r)")]:
        for grid_n in [5, 10, 15]:
            pairs.append(m(
                f"GhPython: create a {grid_n}x{grid_n} grid of {geo_type}s sized by distance to attractor",
                f"import Rhino.Geometry as rg\nimport math\nresult = []\nfor i in range({grid_n}):\n    for j in range({grid_n}):\n        pt = rg.Point3d(i * spacing, j * spacing, 0)\n        d = pt.DistanceTo(attractor)\n        r = min_r + (max_r - min_r) * (1 - d / max_dist) if d < max_dist else min_r\n        result.append({geo_expr})\na = result",
                "grasshopper_python", "hard", "grasshopper", ["attractor", geo_type]))

    # ═══════════════════════════════════════════════════════════
    # 6) MORE DESIGN WORKFLOWS (~120 pairs)
    # ═══════════════════════════════════════════════════════════

    # Facade panel types
    facade_types = [
        ("rectangular panels", "rs.AddSrfPt([p00, p10, p11, p01])"),
        ("triangulated panels", "rs.AddSrfPt([p00, p10, p11])\n        rs.AddSrfPt([p00, p11, p01])"),
        ("diamond panels", "mid_b = rs.PointDivide(rs.PointAdd(p00, p10), 2)\n        mid_t = rs.PointDivide(rs.PointAdd(p01, p11), 2)\n        mid_l = rs.PointDivide(rs.PointAdd(p00, p01), 2)\n        mid_r = rs.PointDivide(rs.PointAdd(p10, p11), 2)\n        rs.AddSrfPt([mid_b, mid_r, mid_t, mid_l])"),
    ]
    for n_u in [4, 6, 8, 10]:
        for n_v in [4, 6, 8]:
            for ptype, pcode in facade_types:
                pairs.append(m(
                    f"Create a {n_u}x{n_v} facade of {ptype} on a surface",
                    f"{RS}\nsrf = rs.GetObject('Select surface', 8)\nif srf:\n    du = rs.SurfaceDomain(srf, 0)\n    dv = rs.SurfaceDomain(srf, 1)\n    for i in range({n_u}):\n        for j in range({n_v}):\n            u0 = du[0] + (du[1]-du[0]) * i / {n_u}\n            u1 = du[0] + (du[1]-du[0]) * (i+1) / {n_u}\n            v0 = dv[0] + (dv[1]-dv[0]) * j / {n_v}\n            v1 = dv[0] + (dv[1]-dv[0]) * (j+1) / {n_v}\n            p00 = rs.EvaluateSurface(srf, u0, v0)\n            p10 = rs.EvaluateSurface(srf, u1, v0)\n            p11 = rs.EvaluateSurface(srf, u1, v1)\n            p01 = rs.EvaluateSurface(srf, u0, v1)\n            {pcode}",
                    "design_workflows", "hard", "rhinoscriptsyntax", ["facade", "paneling"]))

    # Waffle/section structure
    for n_x in [3, 5, 8]:
        for n_y in [3, 5, 8]:
            pairs.append(m(
                f"Create a waffle structure with {n_x} sections in X and {n_y} in Y through a surface",
                f"{RS}\nsrf = rs.GetObject('Select surface', 8)\nif srf:\n    bb = rs.BoundingBox(srf)\n    x0, y0, z0 = bb[0]\n    x1, y1, z1 = bb[6]\n    for i in range({n_x}):\n        x = x0 + (x1-x0) * (i+1) / ({n_x}+1)\n        plane = rs.PlaneFromPoints((x,y0,z0),(x,y1,z0),(x,y0,z1))\n        section = rs.AddSrfSectionCrvs(srf, plane)\n    for j in range({n_y}):\n        y = y0 + (y1-y0) * (j+1) / ({n_y}+1)\n        plane = rs.PlaneFromPoints((x0,y,z0),(x1,y,z0),(x0,y,z1))\n        section = rs.AddSrfSectionCrvs(srf, plane)",
                "design_workflows", "hard", "rhinoscriptsyntax", ["waffle", "section"]))

    # Space frame / truss
    for n in [3, 5, 8]:
        pairs.append(m(
            f"Create a {n}x{n} space frame with diagonal bracing",
            f"{RSM}\nsp = 3.0\nfor i in range({n}):\n    for j in range({n}):\n        x, y = i*sp, j*sp\n        rs.AddLine((x,y,0),(x+sp,y,0))\n        rs.AddLine((x,y,0),(x,y+sp,0))\n        rs.AddLine((x,y,sp),(x+sp,y,sp))\n        rs.AddLine((x,y,sp),(x,y+sp,sp))\n        rs.AddLine((x,y,0),(x,y,sp))\n        rs.AddLine((x,y,0),(x+sp,y+sp,sp))",
            "design_workflows", "hard", "rhinoscriptsyntax", ["truss", "frame"]))

    # Staircase variations
    for n_steps in [8, 12, 16, 20, 24]:
        for rise in [0.17, 0.18, 0.20]:
            tread = round(0.30 if rise <= 0.18 else 0.28, 2)
            pairs.append(m(
                f"Create a staircase with {n_steps} steps (rise={rise}m, tread={tread}m)",
                f"{RS}\nrise = {rise}\ntread = {tread}\nwidth = 1.2\nfor i in range({n_steps}):\n    x = i * tread\n    z = i * rise\n    pts = [(x,0,z),(x+tread,0,z),(x+tread,width,z),(x,width,z),(x,0,z+rise),(x+tread,0,z+rise),(x+tread,width,z+rise),(x,width,z+rise)]\n    rs.AddBox(pts)",
                "design_workflows", "medium", "rhinoscriptsyntax", ["staircase"]))

    # Window wall with different window counts
    for cols in [3, 4, 5, 6]:
        for rows in [2, 3, 4, 5]:
            pairs.append(m(
                f"Create a wall with a {cols}x{rows} grid of windows",
                f"{RS}\nwall_w = {cols * 2 + 1}\nwall_h = {rows * 1.5 + 0.5}\nwall = rs.AddBox([(0,0,0),(wall_w,0,0),(wall_w,0.3,0),(0,0.3,0),(0,0,wall_h),(wall_w,0,wall_h),(wall_w,0.3,wall_h),(0,0.3,wall_h)])\nfor c in range({cols}):\n    for r in range({rows}):\n        wx = 0.5 + c * 2\n        wz = 0.5 + r * 1.5\n        window = rs.AddBox([(wx,-0.1,wz),(wx+1,-0.1,wz),(wx+1,0.4,wz),(wx,0.4,wz),(wx,-0.1,wz+1),(wx+1,-0.1,wz+1),(wx+1,0.4,wz+1),(wx,0.4,wz+1)])\n        result = rs.BooleanDifference(wall, window, True)\n        if result:\n            wall = result[0]",
                "design_workflows", "hard", "rhinoscriptsyntax", ["wall", "window", "boolean"]))

    # ═══════════════════════════════════════════════════════════
    # 7) MORE CODE FIXING (~120 pairs)
    # ═══════════════════════════════════════════════════════════

    # Python 2 to 3 migration issues
    py2_fixes = [
        ("print 'hello'", "print('hello')", "print statement to function"),
        ("print obj, 'text'", "print(obj, 'text')", "print with comma to function"),
        ("x = raw_input('Enter:')", "x = input('Enter:')", "raw_input to input"),
        ("d.has_key('k')", "'k' in d", "has_key to in operator"),
        ("items = d.iteritems()", "items = d.items()", "iteritems to items"),
        ("keys = d.iterkeys()", "keys = d.keys()", "iterkeys to keys"),
        ("vals = d.itervalues()", "vals = d.values()", "itervalues to values"),
        ("r = range(10)\nprint r[5]", "r = list(range(10))\nprint(r[5])", "range indexing needs list()"),
        ("x = map(str, nums)", "x = list(map(str, nums))", "map needs list()"),
        ("x = filter(None, items)", "x = list(filter(None, items))", "filter needs list()"),
        ("try:\n    x = 1/0\nexcept Exception, e:\n    print(e)", "try:\n    x = 1/0\nexcept Exception as e:\n    print(e)", "except syntax"),
        ("raise ValueError, 'msg'", "raise ValueError('msg')", "raise syntax"),
    ]
    for buggy, fixed, desc in py2_fixes:
        pairs.append(m(
            f"Fix Python 2 to 3 issue ({desc}):\n```python\nimport rhinoscriptsyntax as rs\n{buggy}\n```",
            f"import rhinoscriptsyntax as rs\n{fixed}",
            "code_fixing", "easy", "rhinoscriptsyntax", ["fix", "python2to3"]))

    # Missing scriptcontext operations
    sc_fixes = [
        ("rg.Point3d(0,0,0)", f"pt = rg.Point3d(0,0,0)\nsc.doc.Objects.AddPoint(pt)\n{REDRAW}",
         "created geometry but didn't add to document"),
        ("line = rg.Line(rg.Point3d(0,0,0), rg.Point3d(10,0,0))", f"line = rg.Line(rg.Point3d(0,0,0), rg.Point3d(10,0,0))\nsc.doc.Objects.AddLine(line)\n{REDRAW}",
         "line not added to document"),
        ("circle = rg.Circle(rg.Plane.WorldXY, 5)\nsc.doc.Objects.AddCircle(circle)", f"circle = rg.Circle(rg.Plane.WorldXY, 5)\nsc.doc.Objects.AddCircle(circle)\n{REDRAW}",
         "missing Redraw"),
        ("brep = rg.Brep.CreateFromSphere(rg.Sphere(rg.Point3d.Origin, 5))", f"brep = rg.Brep.CreateFromSphere(rg.Sphere(rg.Point3d.Origin, 5))\nsc.doc.Objects.AddBrep(brep)\n{REDRAW}",
         "brep not added to document"),
    ]
    for buggy, fixed, desc in sc_fixes:
        pairs.append(m(
            f"Fix: {desc}:\n```python\n{RC}\n{buggy}\n```",
            f"{RC}\n{fixed}",
            "code_fixing", "easy", "RhinoCommon", ["fix", "scriptcontext"]))

    # Wrong loop patterns
    loop_fixes = [
        ("for i in len(objs):\n    print(objs[i])", "for i in range(len(objs)):\n    print(objs[i])", "missing range()"),
        ("for obj in rs.AllObjects:\n    print(obj)", "for obj in rs.AllObjects():\n    print(obj)", "missing parentheses on function call"),
        ("pts = rs.DivideCurve(crv, 10)\nfor i, pt in pts:\n    print(i, pt)", "pts = rs.DivideCurve(crv, 10)\nfor i, pt in enumerate(pts):\n    print(i, pt)", "missing enumerate"),
        ("for crv in rs.ObjectsByType(4):\n    l = rs.CurveLength(crv)\n    total += l", "total = 0\nfor crv in rs.ObjectsByType(4) or []:\n    l = rs.CurveLength(crv)\n    total += l", "uninitialized total and no null check"),
        ("while True:\n    pt = rs.GetPoint('Next')\n    pts.append(pt)", "pts = []\nwhile True:\n    pt = rs.GetPoint('Next')\n    if not pt:\n        break\n    pts.append(pt)", "infinite loop and uninitialized list"),
    ]
    for buggy, fixed, desc in loop_fixes:
        pairs.append(m(
            f"Fix loop error ({desc}):\n```python\nimport rhinoscriptsyntax as rs\n{buggy}\n```",
            f"import rhinoscriptsyntax as rs\n{fixed}",
            "code_fixing", "easy", "rhinoscriptsyntax", ["fix", "loop"]))

    # Collection / list errors
    list_fixes = [
        ("pts = rs.DivideCurve(crv, 10)\nprint(pts.Count)", "pts = rs.DivideCurve(crv, 10)\nif pts:\n    print(len(pts))", ".Count vs len()"),
        ("objs = rs.AllObjects()\nobjs.Add(new_obj)", "objs = list(rs.AllObjects() or [])\nobjs.append(new_obj)", ".Add vs .append"),
        ("colors = rs.ObjectColor(obj)\nprint(colors.R)", "color = rs.ObjectColor(obj)\nprint(color[0])", ".R vs tuple index"),
        ("pt = rs.GetPoint('Pick')\nx = pt.X", "pt = rs.GetPoint('Pick')\nif pt:\n    x = pt[0]", ".X vs tuple index"),
        ("for i in range(len(objs)):\n    del objs[i]", "for obj in list(objs or []):\n    rs.DeleteObject(obj)", "modifying list during iteration"),
    ]
    for buggy, fixed, desc in list_fixes:
        pairs.append(m(
            f"Fix collection error ({desc}):\n```python\nimport rhinoscriptsyntax as rs\n{buggy}\n```",
            f"import rhinoscriptsyntax as rs\n{fixed}",
            "code_fixing", "easy", "rhinoscriptsyntax", ["fix", "collection"]))

    # GhPython-specific fixes
    gh_fixes = [
        ("import ghpythonlib.components as ghcomp\nresult = ghcomp.Move(geo, vector)\na = result",
         "import ghpythonlib.components as ghcomp\nresult = ghcomp.Move(geo, vector)\na = result.geometry",
         "Move returns named tuple, need .geometry"),
        ("from Grasshopper.Kernel.Data import GH_Path\nfrom Grasshopper import DataTree\ntree = DataTree()\ntree.Add(x, GH_Path(0))",
         "from Grasshopper.Kernel.Data import GH_Path\nfrom Grasshopper import DataTree\ntree = DataTree[object]()\ntree.Add(x, GH_Path(0))",
         "DataTree needs type parameter"),
        ("a = [pt.X for pt in x]",
         "import Rhino.Geometry as rg\na = [pt.X for pt in x]",
         "missing Rhino.Geometry import"),
        ("import rhinoscriptsyntax as rs\na = rs.AddPoint(0,0,0)",
         "import Rhino.Geometry as rg\na = rg.Point3d(0, 0, 0)",
         "rhinoscriptsyntax not available in GhPython, use RhinoCommon"),
        ("tree = DataTree[float]()\nfor i in range(n):\n    for j in range(m):\n        tree.Add(vals[i][j], GH_Path(i, j))",
         "from Grasshopper.Kernel.Data import GH_Path\nfrom Grasshopper import DataTree\ntree = DataTree[float]()\nfor i in range(n):\n    for j in range(m):\n        tree.Add(vals[i][j], GH_Path(i, j))\na = tree",
         "missing imports and output assignment"),
        ("pts = list(x)\na = rg.NurbsCurve.Create(False, 3, pts)",
         "import Rhino.Geometry as rg\nfrom System.Collections.Generic import List\npt_list = List[rg.Point3d]()\nfor pt in x:\n    pt_list.Add(pt)\na = rg.NurbsCurve.Create(False, 3, pt_list)",
         "need .NET List for NurbsCurve.Create"),
    ]
    for buggy, fixed, desc in gh_fixes:
        pairs.append(m(
            f"Fix GhPython bug ({desc}):\n```python\n{buggy}\n```",
            fixed,
            "code_fixing", "medium", "grasshopper", ["fix", "ghpython"]))

    # rhino3dm-specific fixes
    r3_fixes = [
        ("model = rhino3dm.File3dm()\nmodel.Objects.AddPoint(0, 0, 0)",
         "import rhino3dm\nmodel = rhino3dm.File3dm()\nmodel.Objects.AddPoint(rhino3dm.Point3d(0, 0, 0))",
         "AddPoint needs Point3d, not raw coordinates"),
        ("model = rhino3dm.File3dm.Read('file.3dm')\nfor obj in model.Objects:\n    print(obj.Name)",
         "import rhino3dm\nmodel = rhino3dm.File3dm.Read('file.3dm')\nfor obj in model.Objects:\n    print(obj.Attributes.Name)",
         "name is on Attributes, not object"),
        ("model.Write('output.3dm')",
         "import rhino3dm\nmodel.Write('output.3dm', 7)",
         "Write needs version parameter"),
        ("circle = rhino3dm.Circle(5)\nmodel.Objects.Add(circle)",
         "import rhino3dm\ncircle = rhino3dm.Circle(5)\nmodel.Objects.AddCircle(circle)",
         "use AddCircle, not generic Add"),
        ("layer = rhino3dm.Layer()\nlayer.Name = 'Test'\nlayer.Color = 'red'\nmodel.Layers.Add(layer)",
         "import rhino3dm\nlayer = rhino3dm.Layer()\nlayer.Name = 'Test'\nlayer.Color = (255, 0, 0, 255)\nmodel.Layers.Add(layer)",
         "color needs RGBA tuple"),
    ]
    for buggy, fixed, desc in r3_fixes:
        pairs.append(m(
            f"Fix rhino3dm error ({desc}):\n```python\nimport rhino3dm\n{buggy}\n```",
            fixed,
            "code_fixing", "easy", "rhino3dm", ["fix", "rhino3dm"]))

    # ═══════════════════════════════════════════════════════════
    # 8) SELECTION & USER INPUT (~80 pairs)
    # ═══════════════════════════════════════════════════════════

    # GetObject with different filters
    get_obj_filters = [
        ("point", 1), ("curve", 4), ("surface", 8), ("polysurface", 16),
        ("mesh", 32), ("any object", 0),
    ]
    for name, filt in get_obj_filters:
        filt_str = f", {filt}" if filt else ""
        pairs.append(m(f"Prompt the user to select a {name}",
            f"{RS}\nobj = rs.GetObject('Select a {name}'{filt_str})\nif obj:\n    print(f'Selected: {{obj}}')",
            "how_do_i_questions", "easy", "rhinoscriptsyntax", ["selection", "input"]))
        pairs.append(m(f"Prompt the user to select multiple {name}s",
            f"{RS}\nobjs = rs.GetObjects('Select {name}s'{filt_str})\nif objs:\n    print(f'Selected {{len(objs)}} object(s)')",
            "how_do_i_questions", "easy", "rhinoscriptsyntax", ["selection", "input"]))

    # GetPoint variations
    pt_inputs = [
        ("pick a point", "pt = rs.GetPoint('Pick a point')"),
        ("pick two points for a line", "p1 = rs.GetPoint('Start point')\nif p1:\n    p2 = rs.GetPoint('End point')\n    if p2:\n        rs.AddLine(p1, p2)"),
        ("pick points until Enter", "pts = rs.GetPoints()\nif pts:\n    rs.AddPolyline(pts)"),
        ("pick a point on a surface", "srf = rs.GetObject('Select surface', 8)\nif srf:\n    pt = rs.GetPointOnSurface(srf, 'Pick point on surface')\n    if pt:\n        rs.AddPoint(pt)"),
        ("pick a point on a curve", "crv = rs.GetObject('Select curve', 4)\nif crv:\n    pt = rs.GetPointOnCurve(crv, 'Pick point on curve')\n    if pt:\n        rs.AddPoint(pt)"),
    ]
    for desc, code in pt_inputs:
        pairs.append(m(f"How do I {desc}?",
            f"{RS}\n{code}",
            "how_do_i_questions", "easy", "rhinoscriptsyntax", ["input", "point"]))

    # Numeric input
    num_inputs = [
        ("get a number from the user", "n = rs.GetReal('Enter a number')\nif n is not None:\n    print(f'You entered: {n}')"),
        ("get an integer from the user", "n = rs.GetInteger('Enter an integer')\nif n is not None:\n    print(f'You entered: {n}')"),
        ("get a string from the user", "s = rs.GetString('Enter text')\nif s:\n    print(f'You entered: {s}')"),
        ("show a message box", "rs.MessageBox('Operation complete!')"),
        ("get a boolean from the user", "result = rs.GetBoolean('Choose', ['Option', 'No', 'Yes'], [True])\nif result:\n    print(f'Choice: {result[0]}')"),
        ("create a list box selection", "items = ['Option A', 'Option B', 'Option C']\nresult = rs.ListBox(items, 'Choose an option')\nif result:\n    print(f'Selected: {result}')"),
    ]
    for desc, code in num_inputs:
        pairs.append(m(f"How do I {desc}?",
            f"{RS}\n{code}",
            "how_do_i_questions", "easy", "rhinoscriptsyntax", ["input", "dialog"]))

    # ═══════════════════════════════════════════════════════════
    # 9) MULTI-STEP RHINOCOMMON WORKFLOWS (~100 pairs)
    # ═══════════════════════════════════════════════════════════

    # Intersection operations
    intersection_ops = [
        ("intersect two curves",
         f"objs = sc.doc.Objects.GetObjectList(Rhino.DocObjects.ObjectType.Curve)\ncurves = [obj.CurveGeometry for obj in objs]\nif len(curves) >= 2:\n    events = rg.Intersect.Intersection.CurveCurve(curves[0], curves[1], 0.001, 0.001)\n    for e in events:\n        sc.doc.Objects.AddPoint(e.PointA)\n    {REDRAW}"),
        ("intersect a curve and a surface",
         f"events = rg.Intersect.Intersection.CurveSurface(crv, srf, 0.001, 0.001)\nif events:\n    for i in range(events.Count):\n        if events[i].IsPoint:\n            sc.doc.Objects.AddPoint(events[i].PointA)\n{REDRAW}"),
        ("intersect two surfaces",
         f"result, curves, pts = rg.Intersect.Intersection.SurfaceSurface(srf_a, srf_b, 0.001)\nif result:\n    for crv in curves:\n        sc.doc.Objects.AddCurve(crv)\n{REDRAW}"),
        ("project points onto a surface",
         f"result = rg.Intersect.Intersection.ProjectPointsToBreps([brep], pts, rg.Vector3d.ZAxis, 0.001)\nfor pt in result:\n    sc.doc.Objects.AddPoint(pt)\n{REDRAW}"),
    ]
    for desc, code in intersection_ops:
        pairs.append(m(f"How do I {desc} using RhinoCommon?",
            f"import Rhino\nimport Rhino.Geometry as rg\nimport scriptcontext as sc\n{code}",
            "multi_step_workflows", "hard", "RhinoCommon", ["intersection"]))

    # Brep operations with RhinoCommon
    brep_ops = [
        ("create a box and fillet its edges",
         f"box = rg.Box(rg.Plane.WorldXY, rg.Interval(0,10), rg.Interval(0,10), rg.Interval(0,5))\nbrep = box.ToBrep()\nedge_ids = [i for i in range(brep.Edges.Count)]\nresult = rg.Brep.CreateFilletEdges(brep, edge_ids, [0.5]*len(edge_ids), [0.5]*len(edge_ids), rg.BlendType.Fillet, rg.RailType.DistanceFromEdge, 0.001)\nif result:\n    for b in result:\n        sc.doc.Objects.AddBrep(b)\n{REDRAW}"),
        ("split a brep with a plane",
         f"brep = sc.doc.Objects.Find(obj_id).BrepGeometry\nplane = rg.Plane.WorldXY\nsplitter = rg.Brep.CreatePlanarBreps([rg.Circle(plane, 1000).ToNurbsCurve()], 0.001)\nif splitter:\n    result = brep.Split(splitter[0], 0.001)\n    for b in result:\n        sc.doc.Objects.AddBrep(b)\n    {REDRAW}"),
        ("boolean union two breps",
         f"box1 = rg.Box(rg.Plane.WorldXY, rg.Interval(0,10), rg.Interval(0,10), rg.Interval(0,5)).ToBrep()\nbox2 = rg.Box(rg.Plane(rg.Point3d(5,5,0), rg.Vector3d.ZAxis), rg.Interval(0,10), rg.Interval(0,10), rg.Interval(0,5)).ToBrep()\nresult = rg.Brep.CreateBooleanUnion([box1, box2], 0.001)\nif result:\n    for b in result:\n        sc.doc.Objects.AddBrep(b)\n{REDRAW}"),
        ("create a pipe from a curve",
         f"crv = rg.NurbsCurve.CreateFromLine(rg.Line(rg.Point3d(0,0,0), rg.Point3d(0,0,20)))\nbreps = rg.Brep.CreatePipe(crv, 2.0, False, rg.PipeCapMode.Flat, True, 0.001, 0.001)\nfor b in breps:\n    sc.doc.Objects.AddBrep(b)\n{REDRAW}"),
    ]
    for desc, code in brep_ops:
        pairs.append(m(f"{desc} using RhinoCommon",
            f"{RCM}\n{code}",
            "multi_step_workflows", "hard", "RhinoCommon", ["brep"]))

    # NURBS surface creation
    nurbs_srf_ops = [
        ("loft two curves",
         f"c1 = rg.Circle(rg.Plane.WorldXY, 5).ToNurbsCurve()\nc2 = rg.Circle(rg.Plane(rg.Point3d(0,0,10), rg.Vector3d.ZAxis), 3).ToNurbsCurve()\nloft = rg.Brep.CreateFromLoft([c1, c2], rg.Point3d.Unset, rg.Point3d.Unset, rg.LoftType.Normal, False)\nfor b in loft:\n    sc.doc.Objects.AddBrep(b)\n{REDRAW}"),
        ("revolve a profile curve",
         f"profile = rg.LineCurve(rg.Point3d(3,0,0), rg.Point3d(3,0,10))\naxis = rg.Line(rg.Point3d.Origin, rg.Point3d(0,0,1))\nbrep = rg.RevSurface.Create(profile, axis, 0, 2*math.pi)\nif brep:\n    sc.doc.Objects.AddSurface(brep)\n{REDRAW}"),
        ("sweep a profile along a rail",
         f"rail = rg.NurbsCurve.CreateFromLine(rg.Line(rg.Point3d(0,0,0), rg.Point3d(20,0,10)))\nprofile = rg.Circle(rg.Plane.WorldXY, 1.5).ToNurbsCurve()\nbreps = rg.Brep.CreateFromSweep(rail, profile, True, 0.001)\nfor b in breps:\n    sc.doc.Objects.AddBrep(b)\n{REDRAW}"),
    ]
    for desc, code in nurbs_srf_ops:
        pairs.append(m(f"How do I {desc} in RhinoCommon?",
            f"{RCM}\n{code}",
            "multi_step_workflows", "hard", "RhinoCommon", ["surface", "nurbs"]))

    # ═══════════════════════════════════════════════════════════
    # 10) IMPORT/EXPORT & FILE OPS (~50 pairs)
    # ═══════════════════════════════════════════════════════════

    formats = [
        ("STL", "stl"), ("OBJ", "obj"), ("STEP", "stp"), ("IGES", "igs"),
        ("DXF", "dxf"), ("3DS", "3ds"), ("AI", "ai"), ("SVG", "svg"),
    ]
    for fmt_name, ext in formats:
        pairs.append(m(f"Export selected objects to {fmt_name}",
            f"{RS}\nobjs = rs.GetObjects('Select objects to export')\nif objs:\n    rs.SelectObjects(objs)\n    rs.Command(f'-_Export \"C:/output.{ext}\" _Enter', False)",
            "how_do_i_questions", "easy", "rhinoscriptsyntax", ["export", ext]))
        pairs.append(m(f"Import a {fmt_name} file",
            f"{RS}\nrs.Command('-_Import \"C:/input.{ext}\" _Enter', False)",
            "how_do_i_questions", "easy", "rhinoscriptsyntax", ["import", ext]))
        pairs.append(m(f"How do I export to {fmt_name} format?",
            f"{RS}\nrs.Command('-_Export \"C:/model.{ext}\" _Enter', False)",
            "how_do_i_questions", "easy", "rhinoscriptsyntax", ["export", ext]))

    # Save/Open operations
    file_ops = [
        ("save the current file", "rs.Command('-_Save', False)"),
        ("save as a new file", "rs.Command('-_SaveAs \"C:/new_file.3dm\" _Enter', False)"),
        ("open a file", "rs.Command('-_Open \"C:/file.3dm\" _Enter', False)"),
        ("export selected as 3dm", "objs = rs.GetObjects('Select')\nif objs:\n    rs.SelectObjects(objs)\n    rs.Command('-_Export \"C:/selection.3dm\" _Enter', False)"),
    ]
    for desc, code in file_ops:
        pairs.append(m(f"How do I {desc}?",
            f"{RS}\n{code}",
            "how_do_i_questions", "easy", "rhinoscriptsyntax", ["file"]))

    # ═══════════════════════════════════════════════════════════
    # 11) GROUPS & BLOCKS (~40 pairs)
    # ═══════════════════════════════════════════════════════════

    group_ops = [
        ("group selected objects",
         "objs = rs.GetObjects('Select objects to group')\nif objs:\n    grp = rs.AddGroup()\n    rs.AddObjectsToGroup(objs, grp)\n    print(f'Grouped {len(objs)} objects')"),
        ("ungroup objects",
         "obj = rs.GetObject('Select grouped object')\nif obj:\n    groups = rs.ObjectGroups(obj)\n    if groups:\n        for g in groups:\n            rs.DeleteGroup(g)"),
        ("get all objects in a group",
         "groups = rs.GroupNames()\nif groups:\n    for g in groups:\n        objs = rs.ObjectsByGroup(g)\n        print(f'Group {g}: {len(objs) if objs else 0} objects')"),
        ("create named groups for each layer",
         "layers = rs.LayerNames()\nif layers:\n    for layer in layers:\n        objs = rs.ObjectsByLayer(layer)\n        if objs:\n            grp = rs.AddGroup(f'grp_{layer}')\n            rs.AddObjectsToGroup(objs, grp)"),
    ]
    for desc, code in group_ops:
        pairs.append(m(f"How do I {desc}?",
            f"{RS}\n{code}",
            "how_do_i_questions", "medium", "rhinoscriptsyntax", ["group"]))

    # Block operations
    block_ops = [
        ("create a block from selected objects",
         "objs = rs.GetObjects('Select objects for block')\nif objs:\n    base_pt = rs.GetPoint('Base point')\n    if base_pt:\n        rs.AddBlock(objs, base_pt, 'MyBlock', True)"),
        ("insert a block instance",
         "if rs.IsBlock('MyBlock'):\n    rs.InsertBlock('MyBlock', (0,0,0))"),
        ("list all block definitions",
         "blocks = rs.BlockNames()\nif blocks:\n    for b in blocks:\n        print(b)"),
        ("explode a block instance",
         "obj = rs.GetObject('Select block instance', 4096)\nif obj:\n    if rs.IsBlockInstance(obj):\n        pieces = rs.ExplodeBlockInstance(obj)\n        print(f'Exploded into {len(pieces)} objects')"),
        ("get block instance insertion point",
         "obj = rs.GetObject('Select block instance', 4096)\nif obj and rs.IsBlockInstance(obj):\n    pt = rs.BlockInstanceInsertPoint(obj)\n    print(f'Insert point: {pt}')"),
        ("array block instances along a line",
         "if rs.IsBlock('MyBlock'):\n    for i in range(10):\n        rs.InsertBlock('MyBlock', (i*5, 0, 0))"),
    ]
    for desc, code in block_ops:
        pairs.append(m(f"How do I {desc}?",
            f"{RS}\n{code}",
            "how_do_i_questions", "medium", "rhinoscriptsyntax", ["block"]))

    # ═══════════════════════════════════════════════════════════
    # 12) DISPLAY & VISUALIZATION (~40 pairs)
    # ═══════════════════════════════════════════════════════════

    # View operations
    view_ops = [
        ("set the view to top", "rs.ViewProjection('Top', 1)"),
        ("set the view to perspective", "rs.ViewProjection('Perspective', 2)"),
        ("zoom to fit all objects", "rs.ZoomExtents()"),
        ("zoom to selected objects", "rs.ZoomSelected()"),
        ("set named view", "rs.RestoreNamedView('Front')"),
        ("capture viewport to file", "rs.Command('-_ViewCaptureToFile \"C:/capture.png\" _Width=1920 _Height=1080 _Enter', False)"),
        ("set display mode to wireframe", "rs.ViewDisplayMode('Perspective', 'Wireframe')"),
        ("set display mode to shaded", "rs.ViewDisplayMode('Perspective', 'Shaded')"),
        ("set display mode to rendered", "rs.ViewDisplayMode('Perspective', 'Rendered')"),
        ("set display mode to ghosted", "rs.ViewDisplayMode('Perspective', 'Ghosted')"),
    ]
    for desc, code in view_ops:
        pairs.append(m(f"How do I {desc}?",
            f"{RS}\n{code}",
            "how_do_i_questions", "easy", "rhinoscriptsyntax", ["view", "display"]))

    # Text and annotation
    text_ops = [
        ("add a text dot at a point",
         "pt = rs.GetPoint('Pick location')\nif pt:\n    rs.AddTextDot('Label', pt)"),
        ("add text at a point",
         "pt = rs.GetPoint('Pick location')\nif pt:\n    rs.AddText('Hello World', pt, 2.0)"),
        ("label all objects with their type",
         "objs = rs.AllObjects()\nif objs:\n    for obj in objs:\n        otype = rs.ObjectType(obj)\n        pt = rs.BoundingBox(obj)\n        if pt:\n            center = [(pt[0][i]+pt[6][i])/2 for i in range(3)]\n            rs.AddTextDot(str(otype), center)"),
        ("add dimension between two points",
         "p1 = rs.GetPoint('First point')\nif p1:\n    p2 = rs.GetPoint('Second point')\n    if p2:\n        mid = ((p1[0]+p2[0])/2, (p1[1]+p2[1])/2+2, (p1[2]+p2[2])/2)\n        rs.AddLinearDimension(p1, p2, mid)"),
    ]
    for desc, code in text_ops:
        pairs.append(m(f"How do I {desc}?",
            f"{RS}\n{code}",
            "how_do_i_questions", "easy", "rhinoscriptsyntax", ["text", "annotation"]))

    return pairs
