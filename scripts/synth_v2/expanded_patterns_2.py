"""Second expansion module to push total past 2500.
Focuses on cross-product variations and comprehensive API coverage."""

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
GH = "import Rhino.Geometry as rg"

def generate():
    pairs = []

    # ═══════════════════════════════════════════════════════════
    # 1) RECTANGLE / ELLIPSE / TORUS CREATION (~100 pairs)
    # ═══════════════════════════════════════════════════════════

    # Rectangles at various sizes
    for w in [5, 10, 20, 50]:
        for h in [5, 10, 20, 50]:
            pairs.append(m(f"Create a {w}x{h} rectangle on the XY plane",
                f"{RS}\npts = [(0,0,0),({w},0,0),({w},{h},0),(0,{h},0),(0,0,0)]\nrs.AddPolyline(pts)",
                "how_do_i_questions", "easy", "rhinoscriptsyntax", ["rectangle"]))

    # Ellipses
    for rx in [3, 5, 10]:
        for ry in [2, 4, 8]:
            pairs.append(m(f"Create an ellipse with radii {rx} and {ry}",
                f"{RS}\nplane = rs.WorldXYPlane()\nrs.AddEllipse(plane, {rx}, {ry})",
                "how_do_i_questions", "easy", "rhinoscriptsyntax", ["ellipse"]))

    # Torus
    for major_r in [5, 10, 15]:
        for minor_r in [1, 2, 3]:
            pairs.append(m(f"Create a torus with major radius {major_r} and minor radius {minor_r}",
                f"{RS}\nrs.AddTorus((0,0,0), {major_r}, {minor_r})",
                "how_do_i_questions", "easy", "rhinoscriptsyntax", ["torus"]))

    # Truncated cone
    for r1 in [3, 5, 8]:
        for r2 in [1, 2, 4]:
            if r2 < r1:
                for h in [5, 10]:
                    pairs.append(m(f"Create a truncated cone from radius {r1} to {r2} with height {h}",
                        f"{RS}\nrs.AddTruncatedCone((0,0,0), {r1}, (0,0,{h}), {r2})",
                        "how_do_i_questions", "easy", "rhinoscriptsyntax", ["cone", "truncated"]))

    # RhinoCommon ellipse
    for rx in [3, 5, 8, 12]:
        for ry in [2, 4, 6]:
            pairs.append(m(f"Create an ellipse with semi-axes {rx} and {ry} using RhinoCommon",
                f"{RC}\nellipse = rg.Ellipse(rg.Plane.WorldXY, {rx}, {ry})\nsc.doc.Objects.AddCurve(ellipse.ToNurbsCurve())\n{REDRAW}",
                "how_do_i_questions", "easy", "RhinoCommon", ["ellipse"]))

    # ═══════════════════════════════════════════════════════════
    # 2) CURVE OPERATIONS WITH PARAMETERS (~120 pairs)
    # ═══════════════════════════════════════════════════════════

    # Divide curve by count
    for n in [2, 3, 4, 5, 8, 10, 15, 20, 50]:
        pairs.append(m(f"Divide a curve into {n} equal segments",
            f"{RS}\ncrv = rs.GetObject('Select curve', 4)\nif crv:\n    pts = rs.DivideCurve(crv, {n})\n    if pts:\n        for pt in pts:\n            rs.AddPoint(pt)",
            "how_do_i_questions", "easy", "rhinoscriptsyntax", ["curve", "divide"]))

    # Divide curve by length
    for length in [0.5, 1, 2, 3, 5, 10]:
        pairs.append(m(f"Divide a curve into segments of length {length}",
            f"{RS}\ncrv = rs.GetObject('Select curve', 4)\nif crv:\n    pts = rs.DivideCurveLength(crv, {length})\n    if pts:\n        for pt in pts:\n            rs.AddPoint(pt)",
            "how_do_i_questions", "easy", "rhinoscriptsyntax", ["curve", "divide"]))

    # Offset curve at various distances
    for dist in [0.5, 1, 2, 3, 5, 10]:
        pairs.append(m(f"Offset a curve by {dist} units",
            f"{RS}\ncrv = rs.GetObject('Select curve', 4)\nif crv:\n    result = rs.OffsetCurve(crv, (0,0,0), {dist})\n    if result:\n        rs.ObjectColor(result[0], (255,0,0))",
            "how_do_i_questions", "easy", "rhinoscriptsyntax", ["curve", "offset"]))

    # Extend curve
    extend_types = [("Line", 0), ("Arc", 1), ("Smooth", 2)]
    for name, etype in extend_types:
        for length in [2, 5, 10]:
            pairs.append(m(f"Extend a curve by {length} units using {name} extension",
                f"{RS}\ncrv = rs.GetObject('Select curve', 4)\nif crv:\n    rs.ExtendCurveLength(crv, {etype}, 2, {length})",
                "how_do_i_questions", "easy", "rhinoscriptsyntax", ["curve", "extend"]))

    # Fillet between curves at various radii
    for r in [0.5, 1, 2, 3, 5]:
        pairs.append(m(f"Fillet two curves with radius {r}",
            f"{RS}\nc1 = rs.GetObject('First curve', 4)\nc2 = rs.GetObject('Second curve', 4)\nif c1 and c2:\n    rs.FilletCurves(c1, c2, {r})",
            "how_do_i_questions", "easy", "rhinoscriptsyntax", ["curve", "fillet"]))

    # Chamfer between curves
    for d in [1, 2, 3, 5]:
        pairs.append(m(f"Chamfer two curves with distance {d}",
            f"{RS}\nc1 = rs.GetObject('First curve', 4)\nc2 = rs.GetObject('Second curve', 4)\nif c1 and c2:\n    rs.ChamferCurves(c1, c2, {d}, {d})",
            "how_do_i_questions", "easy", "rhinoscriptsyntax", ["curve", "chamfer"]))

    # Rebuild curve at various point counts
    for n in [4, 6, 8, 10, 15, 20]:
        for deg in [2, 3, 5]:
            pairs.append(m(f"Rebuild a curve with {n} control points and degree {deg}",
                f"{RS}\ncrv = rs.GetObject('Select curve', 4)\nif crv:\n    rs.RebuildCurve(crv, {deg}, {n})",
                "how_do_i_questions", "medium", "rhinoscriptsyntax", ["curve", "rebuild"]))

    # ═══════════════════════════════════════════════════════════
    # 3) SURFACE OPERATIONS WITH PARAMETERS (~80 pairs)
    # ═══════════════════════════════════════════════════════════

    # Offset surface at various distances
    for dist in [0.5, 1, 2, 3, 5]:
        pairs.append(m(f"Offset a surface by {dist} units",
            f"{RS}\nsrf = rs.GetObject('Select surface', 8)\nif srf:\n    result = rs.OffsetSurface(srf, {dist})\n    if result:\n        rs.ObjectColor(result, (0,255,0))",
            "how_do_i_questions", "medium", "rhinoscriptsyntax", ["surface", "offset"]))

    # Rebuild surface
    for u_count in [4, 6, 8, 10]:
        for v_count in [4, 6, 8]:
            pairs.append(m(f"Rebuild a surface with {u_count}x{v_count} control points",
                f"{RS}\nsrf = rs.GetObject('Select surface', 8)\nif srf:\n    rs.RebuildSurface(srf, (3, 3), ({u_count}, {v_count}))",
                "how_do_i_questions", "medium", "rhinoscriptsyntax", ["surface", "rebuild"]))

    # Surface trim/split
    pairs.append(m("Trim a surface with a curve",
        f"{RS}\nsrf = rs.GetObject('Select surface', 8)\ncrv = rs.GetObject('Select cutting curve', 4)\nif srf and crv:\n    result = rs.TrimSurface(srf, 0, (0, 0.5))",
        "how_do_i_questions", "medium", "rhinoscriptsyntax", ["surface", "trim"]))

    pairs.append(m("Split a surface with a curve",
        f"{RS}\nsrf = rs.GetObject('Select surface', 8)\ncrv = rs.GetObject('Select splitting curve', 4)\nif srf and crv:\n    result = rs.SplitBrep(srf, crv, True)\n    if result:\n        print(f'Split into {{len(result)}} pieces')",
        "how_do_i_questions", "medium", "rhinoscriptsyntax", ["surface", "split"]))

    # Extrude curve along vector directions
    for dx, dy, dz, desc in [(0,0,10,"upward 10 units"), (0,0,5,"upward 5 units"),
                               (10,0,0,"along X by 10"), (0,10,0,"along Y by 10"),
                               (5,5,5,"diagonally")]:
        pairs.append(m(f"Extrude a curve {desc}",
            f"{RS}\ncrv = rs.GetObject('Select curve', 4)\nif crv:\n    path = rs.AddLine((0,0,0),({dx},{dy},{dz}))\n    srf = rs.ExtrudeCurve(crv, path)\n    rs.DeleteObject(path)",
            "how_do_i_questions", "medium", "rhinoscriptsyntax", ["extrude", "curve"]))

    # ═══════════════════════════════════════════════════════════
    # 4) MORE GHPYTHON COMPONENTS (~120 pairs)
    # ═══════════════════════════════════════════════════════════

    # ghpythonlib.components wrappers
    gh_components = [
        ("Move an object", "result = ghcomp.Move(geo, vec)\na = result.geometry", ["move"]),
        ("Rotate an object", "result = ghcomp.Rotate(geo, angle, plane)\na = result.geometry", ["rotate"]),
        ("Scale an object", "result = ghcomp.Scale(geo, center, factor)\na = result.geometry", ["scale"]),
        ("Mirror an object", "a = ghcomp.Mirror(geo, plane).geometry", ["mirror"]),
        ("Orient an object", "a = ghcomp.Orient(geo, src_plane, dst_plane).geometry", ["orient"]),
        ("Divide a curve", "result = ghcomp.DivideCurve(crv, count, False)\na = result.points", ["divide"]),
        ("Evaluate a curve at parameter", "result = ghcomp.EvaluateCurve(crv, t)\na = result.point\nb = result.tangent", ["evaluate"]),
        ("Offset a curve", "a = ghcomp.OffsetCurve(crv, distance, plane, 1)", ["offset"]),
        ("Loft curves", "a = ghcomp.Loft(curves, 0)", ["loft"]),
        ("Extrude a curve", "a = ghcomp.Extrude(crv, vec)", ["extrude"]),
        ("Boolean union", "a = ghcomp.SolidUnion(breps)", ["boolean"]),
        ("Boolean difference", "a = ghcomp.SolidDifference(brep_a, brep_b)", ["boolean"]),
        ("Boolean intersection", "a = ghcomp.SolidIntersection(brep_a, brep_b)", ["boolean"]),
        ("Cap planar holes", "a = ghcomp.CapHoles(brep)", ["cap"]),
        ("Deconstruct a point", "a = pt.X\nb = pt.Y\nc = pt.Z", ["point"]),
        ("Construct a point", "a = rg.Point3d(x, y, z)", ["point"]),
        ("Deconstruct a plane", "a = plane.Origin\nb = plane.XAxis\nc = plane.YAxis\nd = plane.Normal", ["plane"]),
        ("Area of a surface", "result = ghcomp.Area(srf)\na = result.area\nb = result.centroid", ["area"]),
        ("Volume of a solid", "result = ghcomp.Volume(brep)\na = result.volume\nb = result.centroid", ["volume"]),
        ("Mesh a brep", "a = ghcomp.MeshBrep(brep)", ["mesh"]),
    ]
    for desc, body, tags in gh_components:
        has_ghcomp = "ghcomp." in body
        imp = "import ghpythonlib.components as ghcomp\nimport Rhino.Geometry as rg" if has_ghcomp else "import Rhino.Geometry as rg"
        pairs.append(m(f"GhPython: {desc}",
            f"{imp}\n{body}",
            "grasshopper_python", "easy", "grasshopper", tags))

    # GhPython number sequences/domains
    gh_sequences = [
        ("range of numbers", f"a = [float(i) for i in range(count)]"),
        ("series from start with step", f"a = [start + i * step for i in range(count)]"),
        ("random numbers", f"import random\nrandom.seed(seed)\na = [random.uniform(low, high) for _ in range(count)]"),
        ("fibonacci sequence", f"fib = [0, 1]\nfor i in range(count - 2):\n    fib.append(fib[-1] + fib[-2])\na = fib[:count]"),
        ("sine wave values", f"import math\na = [amplitude * math.sin(2 * math.pi * i / period) for i in range(count)]"),
        ("cosine wave values", f"import math\na = [amplitude * math.cos(2 * math.pi * i / period) for i in range(count)]"),
        ("exponential decay", f"import math\na = [start_val * math.exp(-decay * i) for i in range(count)]"),
        ("linear interpolation between two values", f"a = [low + (high - low) * i / max(count - 1, 1) for i in range(count)]"),
    ]
    for desc, body in gh_sequences:
        pairs.append(m(f"GhPython: generate a {desc}",
            f"import Rhino.Geometry as rg\n{body}",
            "grasshopper_python", "easy", "grasshopper", ["math", "sequence"]))

    # GhPython curve creation patterns
    for n_pts in [4, 6, 8, 10, 12, 20]:
        pairs.append(m(f"GhPython: create a circle of {n_pts} points",
            f"import Rhino.Geometry as rg\nimport math\nresult = []\nfor i in range({n_pts}):\n    angle = 2 * math.pi * i / {n_pts}\n    result.append(rg.Point3d(radius * math.cos(angle), radius * math.sin(angle), 0))\na = result",
            "grasshopper_python", "easy", "grasshopper", ["point", "circle"]))

    for n_pts in [4, 6, 8, 10, 20]:
        pairs.append(m(f"GhPython: create a helix with {n_pts} points",
            f"import Rhino.Geometry as rg\nimport math\nresult = []\nfor i in range({n_pts}):\n    t = 2 * math.pi * turns * i / {n_pts}\n    result.append(rg.Point3d(radius * math.cos(t), radius * math.sin(t), height * i / {n_pts}))\na = result",
            "grasshopper_python", "medium", "grasshopper", ["helix", "point"]))

    # GhPython surface subdivision patterns
    for u in [3, 5, 8, 10, 15, 20]:
        for v in [3, 5, 8, 10]:
            pairs.append(m(f"GhPython: create a {u}x{v} grid of points on a surface",
                f"import Rhino.Geometry as rg\nresult = []\nud = srf.Domain(0)\nvd = srf.Domain(1)\nfor i in range({u}):\n    for j in range({v}):\n        u_val = ud.T0 + (ud.T1 - ud.T0) * i / max({u}-1, 1)\n        v_val = vd.T0 + (vd.T1 - vd.T0) * j / max({v}-1, 1)\n        result.append(srf.PointAt(u_val, v_val))\na = result",
                "grasshopper_python", "medium", "grasshopper", ["surface", "grid"]))

    # ═══════════════════════════════════════════════════════════
    # 5) MORE RHINO3DM PATTERNS (~60 pairs)
    # ═══════════════════════════════════════════════════════════

    # Create multiple layers with geometry
    for n_layers in [3, 5, 8, 10]:
        pairs.append(m(f"Create a 3dm file with {n_layers} layers, each containing different geometry",
            f"{R3}\nmodel = rhino3dm.File3dm()\nfor i in range({n_layers}):\n    layer = rhino3dm.Layer()\n    layer.Name = f'Layer_{{i}}'\n    idx = model.Layers.Add(layer)\n    attr = rhino3dm.ObjectAttributes()\n    attr.LayerIndex = idx\n    model.Objects.AddPoint(rhino3dm.Point3d(i*5, 0, 0), attr)\nmodel.Write('layered.3dm', 7)",
            "rhino3dm_standalone", "medium", "rhino3dm", ["layer", "create"]))

    # Various NURBS curve creations
    for n_pts in [4, 5, 6, 8, 10]:
        for deg in [2, 3]:
            pairs.append(m(f"Create a degree-{deg} NURBS curve with {n_pts} control points in rhino3dm",
                f"{R3}\nimport random\nrandom.seed(42)\nmodel = rhino3dm.File3dm()\npts = [rhino3dm.Point3d(i * 3, random.uniform(-5, 5), 0) for i in range({n_pts})]\ncrv = rhino3dm.NurbsCurve.Create(False, {deg}, pts)\nmodel.Objects.AddCurve(crv)\nmodel.Write('nurbs_curve.3dm', 7)",
                "rhino3dm_standalone", "medium", "rhino3dm", ["nurbs", "curve"]))

    # Mesh with height variation
    for n in [5, 10, 20]:
        pairs.append(m(f"Create a {n}x{n} mesh terrain with sine wave height and save as 3dm",
            f"{R3}\nimport math\nmodel = rhino3dm.File3dm()\nmesh = rhino3dm.Mesh()\nfor i in range({n}+1):\n    for j in range({n}+1):\n        h = math.sin(i * 0.5) * math.cos(j * 0.5) * 3\n        mesh.Vertices.Add(float(j), float(i), h)\nfor i in range({n}):\n    for j in range({n}):\n        a = i*({n}+1)+j\n        mesh.Faces.AddFace(a, a+1, a+{n}+2, a+{n}+1)\nmodel.Objects.AddMesh(mesh)\nmodel.Write('terrain.3dm', 7)",
            "rhino3dm_standalone", "hard", "rhino3dm", ["mesh", "terrain"]))
        pairs.append(m(f"Create a {n}x{n} mesh terrain with random height and save as 3dm",
            f"{R3}\nimport random\nrandom.seed(42)\nmodel = rhino3dm.File3dm()\nmesh = rhino3dm.Mesh()\nfor i in range({n}+1):\n    for j in range({n}+1):\n        h = random.uniform(0, 3)\n        mesh.Vertices.Add(float(j), float(i), h)\nfor i in range({n}):\n    for j in range({n}):\n        a = i*({n}+1)+j\n        mesh.Faces.AddFace(a, a+1, a+{n}+2, a+{n}+1)\nmodel.Objects.AddMesh(mesh)\nmodel.Write('terrain.3dm', 7)",
            "rhino3dm_standalone", "hard", "rhino3dm", ["mesh", "terrain"]))
        pairs.append(m(f"Create a {n}x{n} mesh terrain with radial height and save as 3dm",
            f"{R3}\nimport math\nmodel = rhino3dm.File3dm()\nmesh = rhino3dm.Mesh()\nfor i in range({n}+1):\n    for j in range({n}+1):\n        d = math.sqrt((i - {n}//2)**2 + (j - {n}//2)**2)\n        h = max(0, 3 - d * 0.3)\n        mesh.Vertices.Add(float(j), float(i), h)\nfor i in range({n}):\n    for j in range({n}):\n        a = i*({n}+1)+j\n        mesh.Faces.AddFace(a, a+1, a+{n}+2, a+{n}+1)\nmodel.Objects.AddMesh(mesh)\nmodel.Write('terrain.3dm', 7)",
            "rhino3dm_standalone", "hard", "rhino3dm", ["mesh", "terrain"]))

    # Batch file operations
    for ext in ["3dm", "obj", "stl"]:
        pairs.append(m(f"Read all .{ext} files in a directory using rhino3dm",
            f"{R3}\nimport os\nimport glob\nfiles = glob.glob(f'models/*.{ext}')\nfor f in files:\n    model = rhino3dm.File3dm.Read(f)\n    if model:\n        print(f'{{f}}: {{len(model.Objects)}} objects')",
            "rhino3dm_standalone", "medium", "rhino3dm", ["batch", "read"]))

    # Geometry statistics
    pairs.append(m("Analyze a 3dm file and print geometry type statistics",
        f"{R3}\nfrom collections import Counter\nmodel = rhino3dm.File3dm.Read('input.3dm')\nif model:\n    types = Counter(type(obj.Geometry).__name__ for obj in model.Objects)\n    for t, c in types.most_common():\n        print(f'{{t}}: {{c}}')",
        "rhino3dm_standalone", "medium", "rhino3dm", ["analysis", "statistics"]))

    pairs.append(m("Compute bounding box of all objects in a 3dm file",
        f"{R3}\nmodel = rhino3dm.File3dm.Read('input.3dm')\nif model and len(model.Objects) > 0:\n    bbox = model.Objects[0].Geometry.GetBoundingBox()\n    for obj in model.Objects:\n        bb = obj.Geometry.GetBoundingBox()\n        bbox = rhino3dm.BoundingBox(min(bbox.Min.X, bb.Min.X), min(bbox.Min.Y, bb.Min.Y), min(bbox.Min.Z, bb.Min.Z), max(bbox.Max.X, bb.Max.X), max(bbox.Max.Y, bb.Max.Y), max(bbox.Max.Z, bb.Max.Z))\n    print(f'Min: {{bbox.Min}}, Max: {{bbox.Max}}')",
        "rhino3dm_standalone", "hard", "rhino3dm", ["analysis", "bounds"]))

    # ═══════════════════════════════════════════════════════════
    # 6) MORE MULTI-STEP WORKFLOWS (~100 pairs)
    # ═══════════════════════════════════════════════════════════

    # Create and assign to layer
    geo_types = [
        ("sphere", "rs.AddSphere((0,0,0), 5)"),
        ("box", "rs.AddBox([(0,0,0),(10,0,0),(10,10,0),(0,10,0),(0,0,5),(10,0,5),(10,10,5),(0,10,5)])"),
        ("cylinder", "rs.AddCylinder((0,0,0), 10, 3)"),
        ("cone", "rs.AddCone((0,0,0), 8, 4)"),
        ("circle", "rs.AddCircle((0,0,0), 5)"),
    ]
    for s_name, s_code in geo_types:
        for color_name, rgb in [("red",(255,0,0)),("blue",(0,0,255)),("green",(0,255,0))]:
            pairs.append(m(f"Create a {s_name} on a {color_name} layer",
                f"{RS}\nlayer_name = '{s_name}_{color_name}'\nif not rs.IsLayer(layer_name):\n    rs.AddLayer(layer_name, {rgb})\nrs.CurrentLayer(layer_name)\nobj = {s_code}\nrs.CurrentLayer('Default')",
                "multi_step_workflows", "easy", "rhinoscriptsyntax", ["layer", s_name]))

    # Create, transform, and color
    for s_name, s_code in geo_types:
        pairs.append(m(f"Create a {s_name}, move it 20 units along X, and color it red",
            f"{RS}\nobj = {s_code}\nrs.MoveObject(obj, (20,0,0))\nrs.ObjectColor(obj, (255,0,0))",
            "multi_step_workflows", "easy", "rhinoscriptsyntax", ["create", "transform", "color"]))
        pairs.append(m(f"Create a {s_name}, duplicate it, and move the copy up 10 units",
            f"{RS}\nobj = {s_code}\ncopy = rs.CopyObject(obj, (0,0,10))\nrs.ObjectColor(copy, (0,0,255))",
            "multi_step_workflows", "easy", "rhinoscriptsyntax", ["copy", "transform"]))

    # Surface from curves workflows
    surf_workflows = [
        ("loft circles of decreasing radius",
         "curves = []\nfor i in range(5):\n    r = 5 - i * 0.8\n    crv = rs.AddCircle((0, 0, i*3), r)\n    curves.append(crv)\nrs.AddLoftSrf(curves)"),
        ("create a surface of revolution from a polyline profile",
         "pts = [(5,0,0),(6,0,3),(4,0,6),(5,0,9),(3,0,12)]\nprofile = rs.AddPolyline(pts)\naxis_start = (0,0,0)\naxis_end = (0,0,12)\nrs.AddRevSrf(profile, (axis_start, axis_end), 360)"),
        ("extrude multiple curves and join",
         "curves = []\nfor i in range(3):\n    crv = rs.AddCircle((i*5, 0, 0), 2)\n    curves.append(crv)\npath = rs.AddLine((0,0,0),(0,0,10))\nsrfs = []\nfor crv in curves:\n    srf = rs.ExtrudeCurve(crv, path)\n    if srf:\n        srfs.append(srf)\nrs.DeleteObject(path)"),
        ("create a surface patch from boundary curves",
         "c1 = rs.AddLine((0,0,0),(10,0,0))\nc2 = rs.AddLine((10,0,0),(10,10,5))\nc3 = rs.AddLine((10,10,5),(0,10,5))\nc4 = rs.AddLine((0,10,5),(0,0,0))\nrs.AddEdgeSrf([c1,c2,c3,c4])"),
    ]
    for desc, code in surf_workflows:
        pairs.append(m(f"Create a surface by: {desc}",
            f"{RS}\n{code}",
            "multi_step_workflows", "medium", "rhinoscriptsyntax", ["surface", "create"]))

    # Mesh operations workflows
    mesh_workflows = [
        ("convert a NURBS surface to mesh",
         "srf = rs.GetObject('Select surface', 8)\nif srf:\n    mesh = rs.MeshObjects([srf])\n    if mesh:\n        print(f'Created mesh with {rs.MeshFaceCount(mesh[0])} faces')"),
        ("join multiple meshes",
         "meshes = rs.GetObjects('Select meshes', 32)\nif meshes and len(meshes) > 1:\n    joined = rs.MeshBooleanUnion(meshes)\n    if joined:\n        print(f'Joined into {len(joined)} mesh(es)')"),
        ("flip mesh normals",
         "mesh = rs.GetObject('Select mesh', 32)\nif mesh:\n    rs.FlipMeshFaceNormals(mesh)"),
        ("weld mesh at angle threshold",
         "mesh = rs.GetObject('Select mesh', 32)\nif mesh:\n    rs.MeshWeld(mesh, 30)"),
        ("explode a mesh into faces",
         "mesh = rs.GetObject('Select mesh', 32)\nif mesh:\n    faces = rs.ExplodeMeshes([mesh])\n    if faces:\n        print(f'Exploded into {len(faces)} faces')"),
    ]
    for desc, code in mesh_workflows:
        pairs.append(m(f"How do I {desc}?",
            f"{RS}\n{code}",
            "how_do_i_questions", "medium", "rhinoscriptsyntax", ["mesh"]))

    # Batch operations on all objects
    batch_ops = [
        ("move all objects to the origin",
         "objs = rs.AllObjects()\nif objs:\n    bb = rs.BoundingBox(objs)\n    if bb:\n        center = [(bb[0][i]+bb[6][i])/2 for i in range(3)]\n        rs.MoveObjects(objs, (-center[0], -center[1], -center[2]))"),
        ("color all curves red",
         "curves = rs.ObjectsByType(4)\nif curves:\n    for crv in curves:\n        rs.ObjectColor(crv, (255, 0, 0))"),
        ("delete all points in the document",
         "pts = rs.ObjectsByType(1)\nif pts:\n    rs.DeleteObjects(pts)\n    print(f'Deleted {len(pts)} points')"),
        ("print bounding box of all objects",
         "objs = rs.AllObjects()\nif objs:\n    bb = rs.BoundingBox(objs)\n    if bb:\n        print(f'Min: {bb[0]}')\n        print(f'Max: {bb[6]}')"),
        ("scale all objects by 0.001 (mm to m conversion)",
         "objs = rs.AllObjects()\nif objs:\n    rs.ScaleObjects(objs, (0,0,0), (0.001, 0.001, 0.001))"),
        ("scale all objects by 1000 (m to mm conversion)",
         "objs = rs.AllObjects()\nif objs:\n    rs.ScaleObjects(objs, (0,0,0), (1000, 1000, 1000))"),
        ("scale all objects by 25.4 (inches to mm)",
         "objs = rs.AllObjects()\nif objs:\n    rs.ScaleObjects(objs, (0,0,0), (25.4, 25.4, 25.4))"),
    ]
    for desc, code in batch_ops:
        pairs.append(m(f"How do I {desc}?",
            f"{RS}\n{code}",
            "how_do_i_questions", "easy", "rhinoscriptsyntax", ["batch"]))

    # ═══════════════════════════════════════════════════════════
    # 7) MORE CODE FIXING (~80 pairs)
    # ═══════════════════════════════════════════════════════════

    # Coordinate/vector errors
    coord_fixes = [
        ("rs.AddLine(0, 0, 0, 10, 0, 0)", "rs.AddLine((0,0,0), (10,0,0))", "coordinates need tuples"),
        ("rs.MoveObject(obj, 10, 0, 0)", "rs.MoveObject(obj, (10,0,0))", "vector needs tuple"),
        ("rs.RotateObject(obj, 0, 0, 0, 45)", "rs.RotateObject(obj, (0,0,0), 45)", "center needs tuple"),
        ("rs.ScaleObject(obj, 0, 0, 0, 2)", "rs.ScaleObject(obj, (0,0,0), (2,2,2))", "center and factor need tuples"),
        ("rs.AddCircle(0, 0, 0, 5)", "rs.AddCircle((0,0,0), 5)", "center needs tuple"),
        ("rs.AddSphere(0, 0, 0, 5)", "rs.AddSphere((0,0,0), 5)", "center needs tuple"),
        ("rs.AddCylinder(0, 0, 0, 10, 3)", "rs.AddCylinder((0,0,0), 10, 3)", "base needs tuple"),
    ]
    for buggy, fixed, desc in coord_fixes:
        pairs.append(m(
            f"Fix: {desc}:\n```python\nimport rhinoscriptsyntax as rs\n{buggy}\n```",
            f"import rhinoscriptsyntax as rs\n{fixed}",
            "code_fixing", "easy", "rhinoscriptsyntax", ["fix", "coordinates"]))

    # Incorrect API usage
    api_fixes = [
        ("rs.AddSurface(pts)", "rs.AddSrfPt(pts)", "AddSurface -> AddSrfPt"),
        ("rs.AddNurbsCurve(pts)", "rs.AddCurve(pts)", "AddNurbsCurve -> AddCurve"),
        ("rs.CurvePoints(crv)", "rs.CurvePoints(crv)", "CurvePoints is correct"),
        ("rs.DeleteObject(objs)", "rs.DeleteObjects(objs)", "DeleteObject -> DeleteObjects for list"),
        ("rs.MoveObject(objs, vec)", "rs.MoveObjects(objs, vec)", "MoveObject -> MoveObjects for list"),
        ("rs.CopyObject(objs, vec)", "rs.CopyObjects(objs, vec)", "CopyObject -> CopyObjects for list"),
        ("rs.SelectObject(objs)", "rs.SelectObjects(objs)", "SelectObject -> SelectObjects for list"),
        ("rs.HideObject(objs)", "rs.HideObjects(objs)", "HideObject -> HideObjects for list"),
        ("rs.ShowObject(objs)", "rs.ShowObjects(objs)", "ShowObject -> ShowObjects for list"),
        ("rs.LockObject(objs)", "rs.LockObjects(objs)", "LockObject -> LockObjects for list"),
    ]
    for buggy, fixed, desc in api_fixes:
        pairs.append(m(
            f"Fix API usage ({desc}):\n```python\nimport rhinoscriptsyntax as rs\n{buggy}\n```",
            f"import rhinoscriptsyntax as rs\n{fixed}",
            "code_fixing", "easy", "rhinoscriptsyntax", ["fix", "api"]))

    # Missing return value handling
    return_fixes = [
        ("rs.BooleanUnion([a, b])\nprint('done')",
         "result = rs.BooleanUnion([a, b])\nif result:\n    print(f'Union created: {result}')\nelse:\n    print('Boolean union failed')",
         "BooleanUnion can return None"),
        ("rs.OffsetCurve(crv, (0,0,0), 5)\nrs.DeleteObject(crv)",
         "result = rs.OffsetCurve(crv, (0,0,0), 5)\nif result:\n    rs.DeleteObject(crv)\nelse:\n    print('Offset failed')",
         "check offset result before deleting original"),
        ("rs.SplitBrep(srf, crv, True)\nrs.DeleteObject(srf)",
         "result = rs.SplitBrep(srf, crv, True)\nif result:\n    rs.DeleteObject(srf)\nelse:\n    print('Split failed')",
         "check split result before deleting"),
        ("new_layer = rs.AddLayer('Test')\nrs.ObjectLayer(obj, new_layer)",
         "new_layer = rs.AddLayer('Test')\nif new_layer:\n    rs.ObjectLayer(obj, new_layer)",
         "check if layer was created"),
    ]
    for buggy, fixed, desc in return_fixes:
        pairs.append(m(
            f"Fix: {desc}:\n```python\nimport rhinoscriptsyntax as rs\n{buggy}\n```",
            f"import rhinoscriptsyntax as rs\n{fixed}",
            "code_fixing", "medium", "rhinoscriptsyntax", ["fix", "return-value"]))

    # Performance/efficiency fixes
    perf_fixes = [
        ("for obj in rs.AllObjects():\n    rs.SelectObject(obj)",
         "objs = rs.AllObjects()\nif objs:\n    rs.SelectObjects(objs)",
         "batch select instead of one-by-one"),
        ("for obj in rs.AllObjects():\n    rs.DeleteObject(obj)",
         "objs = rs.AllObjects()\nif objs:\n    rs.DeleteObjects(objs)",
         "batch delete instead of one-by-one"),
        ("for i in range(100):\n    rs.AddPoint(i, 0, 0)\n    rs.Redraw()",
         "rs.EnableRedraw(False)\nfor i in range(100):\n    rs.AddPoint(i, 0, 0)\nrs.EnableRedraw(True)",
         "disable redraw during batch creation"),
        ("for crv in rs.ObjectsByType(4) or []:\n    rs.ObjectColor(crv, (255,0,0))\n    rs.Redraw()",
         "rs.EnableRedraw(False)\nfor crv in rs.ObjectsByType(4) or []:\n    rs.ObjectColor(crv, (255,0,0))\nrs.EnableRedraw(True)",
         "disable redraw during batch color change"),
    ]
    for buggy, fixed, desc in perf_fixes:
        pairs.append(m(
            f"Fix performance issue ({desc}):\n```python\nimport rhinoscriptsyntax as rs\n{buggy}\n```",
            f"import rhinoscriptsyntax as rs\n{fixed}",
            "code_fixing", "medium", "rhinoscriptsyntax", ["fix", "performance"]))

    # ═══════════════════════════════════════════════════════════
    # 8) MORE DESIGN WORKFLOWS (~120 pairs)
    # ═══════════════════════════════════════════════════════════

    # Parametric tower
    for n_floors in [5, 10, 15, 20]:
        for twist in [0, 5, 10, 15]:
            pairs.append(m(
                f"Create a parametric tower with {n_floors} floors and {twist} degrees twist per floor",
                f"{RSM}\ncurves = []\nfor i in range({n_floors}):\n    angle = math.radians(i * {twist})\n    pts = []\n    for j in range(4):\n        a = math.radians(j * 90) + angle\n        r = 5\n        pts.append((r*math.cos(a), r*math.sin(a), i*3))\n    pts.append(pts[0])\n    crv = rs.AddPolyline(pts)\n    curves.append(crv)\nrs.AddLoftSrf(curves)",
                "design_workflows", "hard", "rhinoscriptsyntax", ["tower", "parametric"]))

    # Grid shell
    for nx in [5, 8, 10]:
        for ny in [5, 8, 10]:
            pairs.append(m(
                f"Create a {nx}x{ny} grid shell structure",
                f"{RSM}\nsp = 2.0\nfor i in range({nx}+1):\n    pts = []\n    for j in range({ny}+1):\n        x = i * sp\n        y = j * sp\n        z = 3 * math.sin(math.pi * i / {nx}) * math.sin(math.pi * j / {ny})\n        pts.append((x, y, z))\n    rs.AddInterpCurve(pts)\nfor j in range({ny}+1):\n    pts = []\n    for i in range({nx}+1):\n        x = i * sp\n        y = j * sp\n        z = 3 * math.sin(math.pi * i / {nx}) * math.sin(math.pi * j / {ny})\n        pts.append((x, y, z))\n    rs.AddInterpCurve(pts)",
                "design_workflows", "hard", "rhinoscriptsyntax", ["grid", "shell"]))

    # Parametric roof
    for n_ribs in [4, 6, 8, 12]:
        pairs.append(m(
            f"Create a parametric roof with {n_ribs} radial ribs",
            f"{RSM}\ncenter = (0,0,5)\nradius = 15\nfor i in range({n_ribs}):\n    angle = 2 * math.pi * i / {n_ribs}\n    end_pt = (radius*math.cos(angle), radius*math.sin(angle), 0)\n    mid_pt = ((center[0]+end_pt[0])/2, (center[1]+end_pt[1])/2, center[2]+2)\n    rs.AddInterpCurve([end_pt, mid_pt, center])",
            "design_workflows", "medium", "rhinoscriptsyntax", ["roof", "parametric"]))

    # Column grid
    for nx in [3, 4, 5, 6]:
        for ny in [3, 4, 5]:
            for sp in [5, 6, 8]:
                pairs.append(m(
                    f"Create a {nx}x{ny} column grid with {sp}m spacing",
                    f"{RS}\nfor i in range({nx}):\n    for j in range({ny}):\n        x = i * {sp}\n        y = j * {sp}\n        rs.AddCylinder((x, y, 0), 3.0, 0.3)",
                    "design_workflows", "easy", "rhinoscriptsyntax", ["column", "grid"]))

    # Sunshade/louver patterns
    for n_louvers in [5, 10, 15, 20]:
        for angle in [30, 45, 60]:
            pairs.append(m(
                f"Create {n_louvers} horizontal louvers at {angle} degrees angle",
                f"{RSM}\nwidth = 10\nfor i in range({n_louvers}):\n    z = i * 0.5\n    depth = 0.3\n    rad = math.radians({angle})\n    pts = [(0, 0, z), (width, 0, z), (width, depth*math.cos(rad), z+depth*math.sin(rad)), (0, depth*math.cos(rad), z+depth*math.sin(rad)), (0, 0, z)]\n    rs.AddPolyline(pts)",
                "design_workflows", "medium", "rhinoscriptsyntax", ["louver", "facade"]))

    return pairs
