"""Template-based expansion to generate additional pairs across all categories.
Targets ~1700+ additional pairs via systematic variation."""

import math
import itertools

def m(instruction, code, category, difficulty, api, tags):
    return {"instruction": instruction, "code": code, "source": "synthetic",
            "category": category, "difficulty": difficulty, "api": api, "tags": tags}

RS = "import rhinoscriptsyntax as rs"
RSM = "import rhinoscriptsyntax as rs\nimport math"
RC = "import Rhino.Geometry as rg\nimport scriptcontext as sc"
RCM = "import Rhino.Geometry as rg\nimport scriptcontext as sc\nimport math"
REDRAW = "sc.doc.Views.Redraw()"
R3 = "import rhino3dm"

def generate():
    pairs = []

    # ═══════════════════════════════════════════════════════════
    # A) GEOMETRY CREATION — systematic coverage (~300)
    # ═══════════════════════════════════════════════════════════

    # Points at various coordinates
    point_coords = [(0,0,0),(1,2,3),(10,0,0),(0,10,0),(0,0,10),(-5,5,0),(100,200,300),(0.5,0.5,0.5)]
    for x,y,z in point_coords:
        pairs.append(m(f"Add a point at ({x},{y},{z})",
            f"{RS}\nrs.AddPoint({x},{y},{z})", "how_do_i_questions", "easy", "rhinoscriptsyntax", ["point"]))
        pairs.append(m(f"Create a Point3d at ({x},{y},{z}) using RhinoCommon",
            f"{RC}\npt = rg.Point3d({x},{y},{z})\nsc.doc.Objects.AddPoint(pt)\n{REDRAW}",
            "how_do_i_questions", "easy", "RhinoCommon", ["point"]))

    # Lines between coordinate pairs
    line_pairs = [((0,0,0),(10,0,0)),((0,0,0),(0,10,0)),((0,0,0),(0,0,10)),
                  ((5,5,0),(15,10,0)),((0,0,0),(10,10,10)),((-5,0,0),(5,0,0))]
    for (x1,y1,z1),(x2,y2,z2) in line_pairs:
        pairs.append(m(f"Draw a line from ({x1},{y1},{z1}) to ({x2},{y2},{z2})",
            f"{RS}\nrs.AddLine(({x1},{y1},{z1}),({x2},{y2},{z2}))",
            "how_do_i_questions", "easy", "rhinoscriptsyntax", ["line"]))

    # Circles at various centers/radii
    for cx,cy,cz in [(0,0,0),(5,5,0),(10,0,0),(0,0,5)]:
        for r in [1,3,5,10,20]:
            pairs.append(m(f"Create a circle at ({cx},{cy},{cz}) with radius {r}",
                f"{RS}\nrs.AddCircle(({cx},{cy},{cz}), {r})",
                "how_do_i_questions", "easy", "rhinoscriptsyntax", ["circle"]))

    # Spheres
    for r in [1,3,5,8,10,15]:
        for cx,cy,cz in [(0,0,0),(10,0,0),(0,0,5)]:
            pairs.append(m(f"Create a sphere at ({cx},{cy},{cz}) with radius {r}",
                f"{RS}\nrs.AddSphere(({cx},{cy},{cz}), {r})",
                "how_do_i_questions", "easy", "rhinoscriptsyntax", ["sphere"]))

    # Cylinders
    for r in [1,3,5]:
        for h in [5,10,20]:
            pairs.append(m(f"Create a cylinder with radius {r} and height {h}",
                f"{RS}\nrs.AddCylinder((0,0,0), {h}, {r})",
                "how_do_i_questions", "easy", "rhinoscriptsyntax", ["cylinder"]))

    # Cones
    for r in [3,5,8]:
        for h in [5,10,15]:
            pairs.append(m(f"Create a cone with base radius {r} and height {h}",
                f"{RS}\nrs.AddCone((0,0,0), {h}, {r})",
                "how_do_i_questions", "easy", "rhinoscriptsyntax", ["cone"]))

    # Arcs
    arcs = [((0,0,0),(10,0,0),(5,5,0)),((0,0,0),(10,10,0),(5,5,5)),((0,0,0),(20,0,0),(10,10,0))]
    for p1,p2,p3 in arcs:
        pairs.append(m(f"Create a 3-point arc through {p1}, {p3}, {p2}",
            f"{RS}\nrs.AddArc3Pt({p1},{p2},{p3})",
            "how_do_i_questions", "easy", "rhinoscriptsyntax", ["arc"]))

    # Polylines (various shapes)
    polylines = [
        ("triangle", [(0,0,0),(10,0,0),(5,8,0),(0,0,0)]),
        ("pentagon", [(5,0,0),(1.5,4.8,0),(-4,2.9,0),(-4,-2.9,0),(1.5,-4.8,0),(5,0,0)]),
        ("L-shape", [(0,0,0),(10,0,0),(10,5,0),(5,5,0),(5,10,0),(0,10,0),(0,0,0)]),
        ("T-shape", [(0,0,0),(10,0,0),(10,3,0),(7,3,0),(7,10,0),(3,10,0),(3,3,0),(0,3,0),(0,0,0)]),
        ("zigzag", [(0,0,0),(3,5,0),(6,0,0),(9,5,0),(12,0,0),(15,5,0)]),
    ]
    for name, pts in polylines:
        pts_str = str(pts)
        pairs.append(m(f"Draw a {name} polyline",
            f"{RS}\nrs.AddPolyline({pts_str})",
            "how_do_i_questions", "easy", "rhinoscriptsyntax", ["polyline", name]))

    # Interpolated curves
    for n_pts in [5,8,12,20]:
        pairs.append(m(f"Create a smooth interpolated curve through {n_pts} random points",
            f"{RSM}\nimport random\nrandom.seed(42)\npts = [(random.uniform(0,20), random.uniform(0,20), 0) for _ in range({n_pts})]\nrs.AddInterpCurve(pts)",
            "how_do_i_questions", "medium", "rhinoscriptsyntax", ["curve", "interpolated"]))

    # NURBS curves at various degrees
    for deg in [2,3,4,5]:
        n = deg + 3
        pairs.append(m(f"Create a degree-{deg} NURBS curve with {n} control points",
            f"{RS}\nimport random\nrandom.seed(42)\npts = [(i*3, random.uniform(-5,5), 0) for i in range({n})]\nrs.AddCurve(pts, {deg})",
            "how_do_i_questions", "medium", "rhinoscriptsyntax", ["nurbs", "curve"]))

    # ═══════════════════════════════════════════════════════════
    # B) TRANSFORM VARIATIONS (~200)
    # ═══════════════════════════════════════════════════════════
    shapes = [
        ("sphere", "obj = rs.AddSphere((0,0,0), 5)"),
        ("box", "obj = rs.AddBox([(0,0,0),(10,0,0),(10,10,0),(0,10,0),(0,0,10),(10,0,10),(10,10,10),(0,10,10)])"),
        ("cylinder", "obj = rs.AddCylinder((0,0,0), 10, 3)"),
        ("cone", "obj = rs.AddCone((0,0,0), 8, 4)"),
        ("circle", "obj = rs.AddCircle((0,0,0), 5)"),
    ]
    # Move by various vectors
    vectors = [(10,0,0),(0,10,0),(0,0,10),(5,5,5),(-10,0,0),(0,0,-5)]
    for s_name, s_code in shapes:
        for vx,vy,vz in vectors:
            pairs.append(m(f"Move a {s_name} by vector ({vx},{vy},{vz})",
                f"{RS}\n{s_code}\nrs.MoveObject(obj, ({vx},{vy},{vz}))",
                "multi_step_workflows", "easy", "rhinoscriptsyntax", ["move", s_name]))

    # Rotate by various angles
    for s_name, s_code in shapes:
        for angle in [15,30,45,60,90,120,180]:
            pairs.append(m(f"Rotate a {s_name} by {angle} degrees around the Z axis",
                f"{RS}\n{s_code}\nrs.RotateObject(obj, (0,0,0), {angle})",
                "multi_step_workflows", "easy", "rhinoscriptsyntax", ["rotate", s_name]))

    # Scale by various factors
    for s_name, s_code in shapes:
        for factor in [0.5, 2, 3, 0.25]:
            pairs.append(m(f"Scale a {s_name} by factor {factor} from origin",
                f"{RS}\n{s_code}\nrs.ScaleObject(obj, (0,0,0), ({factor},{factor},{factor}))",
                "multi_step_workflows", "easy", "rhinoscriptsyntax", ["scale", s_name]))

    # Copy + move
    for s_name, s_code in shapes[:3]:
        for n in [3,5,8]:
            for sp in [5,10]:
                pairs.append(m(f"Create {n} copies of a {s_name} spaced {sp} units along X",
                    f"{RS}\n{s_code}\nfor i in range(1, {n}):\n    rs.CopyObject(obj, (i*{sp}, 0, 0))",
                    "multi_step_workflows", "easy", "rhinoscriptsyntax", ["copy", "array", s_name]))

    # ═══════════════════════════════════════════════════════════
    # C) ADDITIONAL HOW-DO-I QUESTIONS (~200)
    # ═══════════════════════════════════════════════════════════

    # Geometry creation questions with RhinoCommon
    rc_creation = [
        ("create a line in RhinoCommon", f"line = rg.Line(rg.Point3d(0,0,0), rg.Point3d(10,0,0))\nsc.doc.Objects.AddLine(line)\n{REDRAW}"),
        ("create a circle in RhinoCommon", f"circle = rg.Circle(rg.Plane.WorldXY, 5.0)\nsc.doc.Objects.AddCircle(circle)\n{REDRAW}"),
        ("create a sphere in RhinoCommon", f"sphere = rg.Sphere(rg.Point3d.Origin, 5.0)\nbrep = sphere.ToBrep()\nsc.doc.Objects.AddBrep(brep)\n{REDRAW}"),
        ("create a box in RhinoCommon", f"box = rg.Box(rg.Plane.WorldXY, rg.Interval(0,10), rg.Interval(0,10), rg.Interval(0,10))\nsc.doc.Objects.AddBrep(box.ToBrep())\n{REDRAW}"),
        ("create a plane in RhinoCommon", "plane = rg.Plane(rg.Point3d(0,0,0), rg.Vector3d(0,0,1))\nprint('Plane created:', plane.Origin)"),
        ("create a polyline in RhinoCommon", f"pts = [rg.Point3d(i, 0, 0) for i in range(5)]\npline = rg.Polyline(pts)\nsc.doc.Objects.AddPolyline(pline)\n{REDRAW}"),
        ("create an arc in RhinoCommon", f"arc = rg.Arc(rg.Point3d(0,0,0), rg.Point3d(5,5,0), rg.Point3d(10,0,0))\nsc.doc.Objects.AddArc(arc)\n{REDRAW}"),
        ("create a cylinder in RhinoCommon", f"circle = rg.Circle(rg.Plane.WorldXY, 3.0)\ncyl = rg.Cylinder(circle, 10.0)\nbrep = cyl.ToBrep(True, True)\nsc.doc.Objects.AddBrep(brep)\n{REDRAW}"),
        ("add a text dot in RhinoCommon", f"dot = rg.TextDot('Label', rg.Point3d(0,0,0))\nsc.doc.Objects.AddTextDot(dot)\n{REDRAW}"),
    ]
    phrasings = ["How do I {}", "What's the way to {}", "How can I {} in Python?", "I need to {}"]
    for desc, body in rc_creation:
        for phr in phrasings:
            pairs.append(m(phr.format(desc), f"{RC}\n{body}",
                "how_do_i_questions", "easy", "RhinoCommon", ["create"]))

    # Surface creation questions
    surface_creations = [
        ("create a surface from four points", "rs.AddSrfPt([(0,0,0),(10,0,0),(10,10,3),(0,10,3)])"),
        ("extrude a circle into a cylinder surface", "circle = rs.AddCircle((0,0,0), 5)\npath = rs.AddLine((0,0,0),(0,0,10))\nrs.ExtrudeCurve(circle, path)"),
        ("create a surface of revolution", "profile = rs.AddLine((5,0,0),(5,0,10))\nrs.AddRevSrf(profile, ((0,0,0),(0,0,1)), 360)"),
        ("create a planar surface from a closed curve", "pts = [(0,0,0),(10,0,0),(10,10,0),(0,10,0),(0,0,0)]\ncrv = rs.AddPolyline(pts)\nrs.AddPlanarSrf([crv])"),
        ("create a lofted surface", "c1 = rs.AddCircle((0,0,0), 5)\nc2 = rs.AddCircle((0,0,10), 3)\nrs.AddLoftSrf([c1, c2])"),
        ("create a swept surface", "rail = rs.AddLine((0,0,0),(0,0,20))\nprofile = rs.AddCircle((0,0,0), 2)\nrs.AddSweep1(rail, [profile])"),
        ("create a pipe surface", "rail = rs.AddLine((0,0,0),(20,0,0))\nrs.AddPipe(rail, 0, 1.5)"),
        ("create an edge surface from four curves",
         "c1 = rs.AddLine((0,0,0),(10,0,0))\nc2 = rs.AddLine((10,0,0),(10,10,5))\nc3 = rs.AddLine((10,10,5),(0,10,5))\nc4 = rs.AddLine((0,10,5),(0,0,0))\nrs.AddEdgeSrf([c1,c2,c3,c4])"),
    ]
    for desc, body in surface_creations:
        for phr in phrasings[:3]:
            pairs.append(m(phr.format(desc), f"{RS}\n{body}",
                "how_do_i_questions", "medium", "rhinoscriptsyntax", ["surface", "create"]))

    # ═══════════════════════════════════════════════════════════
    # D) ADDITIONAL GRASSHOPPER PYTHON (~150)
    # ═══════════════════════════════════════════════════════════

    # Create geometry at each point in list
    gh_geo_at_points = [
        ("sphere", "rg.Sphere(pt, radius)"),
        ("circle", "rg.Circle(rg.Plane(pt, rg.Vector3d.ZAxis), radius).ToNurbsCurve()"),
        ("line upward", "rg.Line(pt, rg.Point3d(pt.X, pt.Y, pt.Z + height))"),
        ("cube", "rg.Box(rg.Plane(pt, rg.Vector3d.ZAxis), rg.Interval(-s/2,s/2), rg.Interval(-s/2,s/2), rg.Interval(0,s))"),
    ]
    for geo_name, geo_expr in gh_geo_at_points:
        pairs.append(m(
            f"GhPython: create a {geo_name} at each input point",
            f"import Rhino.Geometry as rg\nresult = []\nfor pt in pts:\n    result.append({geo_expr})\na = result",
            "grasshopper_python", "easy", "grasshopper", ["geometry", geo_name]))

    # Curve operations in GhPython
    gh_curve_ops = [
        ("get the length of a curve", "a = crv.GetLength()"),
        ("get the midpoint of a curve", "t = crv.Domain.Mid\na = crv.PointAt(t)"),
        ("get the tangent at curve midpoint", "t = crv.Domain.Mid\na = crv.TangentAt(t)"),
        ("check if a curve is closed", "a = crv.IsClosed"),
        ("divide a curve by count", "params = crv.DivideByCount(count, True)\na = [crv.PointAt(t) for t in params]"),
        ("get start and end points of a curve", "a = crv.PointAtStart\nb = crv.PointAtEnd"),
        ("reverse a curve", "crv.Reverse()\na = crv"),
        ("find closest point on curve to a point", "success, t = crv.ClosestPoint(pt)\na = crv.PointAt(t) if success else pt"),
        ("get the domain of a curve", "a = crv.Domain.T0\nb = crv.Domain.T1"),
        ("evaluate curve at parameter", "a = crv.PointAt(t)"),
        ("get curve degree", "a = crv.Degree"),
        ("get curve control points", "a = [crv.Points[i].Location for i in range(crv.Points.Count)]"),
        ("offset a curve in GhPython", "a = crv.Offset(rg.Plane.WorldXY, distance, 0.01, rg.CurveOffsetCornerStyle.Sharp)"),
        ("join multiple curves", "a = rg.Curve.JoinCurves(curves)"),
        ("find intersection between two curves", "events = rg.Intersect.Intersection.CurveCurve(crv_a, crv_b, 0.001, 0.001)\na = [e.PointA for e in events]"),
    ]
    for desc, body in gh_curve_ops:
        pairs.append(m(f"GhPython component to {desc}",
            f"import Rhino.Geometry as rg\n{body}",
            "grasshopper_python", "easy", "grasshopper", ["curve"]))

    # Surface operations in GhPython
    gh_srf_ops = [
        ("evaluate surface at UV", "a = srf.PointAt(u, v)"),
        ("get surface normal at UV", "a = srf.NormalAt(u, v)"),
        ("get surface frame at UV", "success, frame = srf.FrameAt(u, v)\na = frame if success else rg.Plane.WorldXY"),
        ("extract isocurve from surface", "a = srf.IsoCurve(direction, parameter)"),
        ("get surface domain", "a = srf.Domain(0)\nb = srf.Domain(1)"),
        ("create a grid of points on a surface", "result = []\nu_dom = srf.Domain(0)\nv_dom = srf.Domain(1)\nfor i in range(u_count):\n    for j in range(v_count):\n        u = u_dom.T0 + (u_dom.T1-u_dom.T0) * i / max(u_count-1,1)\n        v = v_dom.T0 + (v_dom.T1-v_dom.T0) * j / max(v_count-1,1)\n        result.append(srf.PointAt(u, v))\na = result"),
        ("get closest point on surface", "success, u, v = srf.ClosestPoint(pt)\na = srf.PointAt(u, v) if success else pt"),
    ]
    for desc, body in gh_srf_ops:
        pairs.append(m(f"GhPython: {desc}",
            f"import Rhino.Geometry as rg\n{body}",
            "grasshopper_python", "medium", "grasshopper", ["surface"]))

    # Vector math in GhPython
    gh_vector_ops = [
        ("add two vectors", "a = rg.Vector3d(v1.X+v2.X, v1.Y+v2.Y, v1.Z+v2.Z)"),
        ("scale a vector", "v = rg.Vector3d(vec)\nv *= factor\na = v"),
        ("get vector length", "a = vec.Length"),
        ("unitize a vector", "v = rg.Vector3d(vec)\nv.Unitize()\na = v"),
        ("cross product of two vectors", "a = rg.Vector3d.CrossProduct(v1, v2)"),
        ("dot product of two vectors", "a = v1 * v2"),
        ("angle between two vectors", "import math\na = math.degrees(rg.Vector3d.VectorAngle(v1, v2))"),
        ("rotate vector around Z axis", "import math\nangle = math.radians(degrees)\nc, s = math.cos(angle), math.sin(angle)\na = rg.Vector3d(vec.X*c-vec.Y*s, vec.X*s+vec.Y*c, vec.Z)"),
    ]
    for desc, body in gh_vector_ops:
        pairs.append(m(f"GhPython: {desc}",
            f"import Rhino.Geometry as rg\n{body}",
            "grasshopper_python", "easy", "grasshopper", ["vector", "math"]))

    # List processing in GhPython
    gh_list_ops = [
        ("filter points above a Z threshold", "a = [pt for pt in pts if pt.Z > threshold]"),
        ("sort points by X coordinate", "a = sorted(pts, key=lambda p: p.X)"),
        ("get every nth item from a list", "a = items[::n]"),
        ("shift a list by n positions", "a = items[n:] + items[:n]"),
        ("zip two lists of points into lines", "a = [rg.Line(a_pt, b_pt) for a_pt, b_pt in zip(pts_a, pts_b)]"),
        ("flatten a nested list", "a = [item for sublist in nested for item in sublist]"),
        ("get unique items preserving order", "seen = set()\na = []\nfor item in items:\n    if item not in seen:\n        seen.add(item)\n        a.append(item)"),
        ("reverse a list", "a = list(reversed(items))"),
        ("create pairs from consecutive items", "a = [(items[i], items[i+1]) for i in range(len(items)-1)]"),
        ("batch items into groups of n", "a = [items[i:i+n] for i in range(0, len(items), n)]"),
        ("find the minimum and maximum values", "a = min(values)\nb = max(values)"),
        ("running average of a list", "result = []\nfor i in range(len(values)):\n    window = values[max(0,i-n+1):i+1]\n    result.append(sum(window)/len(window))\na = result"),
    ]
    for desc, body in gh_list_ops:
        pairs.append(m(f"GhPython: {desc}",
            f"import Rhino.Geometry as rg\n{body}",
            "grasshopper_python", "easy", "grasshopper", ["list", "data"]))

    # More DataTree patterns
    gh_tree_extra = [
        ("Count items in each branch",
         "import Grasshopper as gh\nresult = []\nfor i in range(tree.BranchCount):\n    result.append(len(tree.Branch(i)))\na = result"),
        ("Get the first item from each branch",
         "import Grasshopper as gh\nimport Rhino.Geometry as rg\nresult = []\nfor i in range(tree.BranchCount):\n    branch = tree.Branch(i)\n    if len(branch) > 0:\n        result.append(branch[0])\na = result"),
        ("Get the last item from each branch",
         "import Grasshopper as gh\nimport Rhino.Geometry as rg\nresult = []\nfor i in range(tree.BranchCount):\n    branch = tree.Branch(i)\n    if len(branch) > 0:\n        result.append(branch[len(branch)-1])\na = result"),
        ("Weave two lists alternately into one",
         "import Rhino.Geometry as rg\nresult = []\nfor a_item, b_item in zip(list_a, list_b):\n    result.append(a_item)\n    result.append(b_item)\na = result"),
        ("Dispatch items into two lists by boolean pattern",
         "import Rhino.Geometry as rg\ntrue_list = []\nfalse_list = []\nfor item, flag in zip(items, pattern):\n    if flag:\n        true_list.append(item)\n    else:\n        false_list.append(item)\na = true_list\nb = false_list"),
    ]
    for desc, body in gh_tree_extra:
        pairs.append(m(f"GhPython: {desc}", body,
            "grasshopper_python", "medium", "grasshopper", ["datatree"]))

    # ═══════════════════════════════════════════════════════════
    # E) ADDITIONAL rhino3dm PAIRS (~150)
    # ═══════════════════════════════════════════════════════════

    # Create various geometry + save
    r3dm_geo = [
        ("10 circles with radii 1 to 10",
         f"for r in range(1, 11):\n    circle = rhino3dm.Circle(float(r))\n    model.Objects.AddCircle(circle)"),
        ("a spiral of points",
         f"import math\nfor i in range(100):\n    t = i * 0.2\n    model.Objects.AddPoint(rhino3dm.Point3d(5*math.cos(t), 5*math.sin(t), t*0.5))"),
        ("a grid of points on a plane",
         f"for i in range(10):\n    for j in range(10):\n        model.Objects.AddPoint(rhino3dm.Point3d(i*2, j*2, 0))"),
        ("random lines",
         f"import random\nrandom.seed(42)\nfor _ in range(20):\n    p1 = rhino3dm.Point3d(random.uniform(-10,10), random.uniform(-10,10), 0)\n    p2 = rhino3dm.Point3d(random.uniform(-10,10), random.uniform(-10,10), 0)\n    model.Objects.AddLine(p1, p2)"),
        ("a star polyline",
         f"import math\npts = rhino3dm.Point3dList(0)\nfor i in range(10):\n    angle = math.radians(i * 36)\n    r = 10 if i % 2 == 0 else 4\n    pts.Add(r*math.cos(angle), r*math.sin(angle), 0)\npts.Add(pts[0].X, pts[0].Y, pts[0].Z)"),
        ("concentric spheres",
         f"for r in [2, 4, 6, 8, 10]:\n    sphere = rhino3dm.Sphere(rhino3dm.Point3d(0,0,0), float(r))\n    model.Objects.AddSphere(sphere)"),
    ]
    for desc, add_code in r3dm_geo:
        pairs.append(m(f"Create a 3dm file with {desc}",
            f"{R3}\nmodel = rhino3dm.File3dm()\n{add_code}\nmodel.Write('output.3dm', 7)",
            "rhino3dm_standalone", "medium", "rhino3dm", ["create"]))

    # Read + query patterns
    r3dm_queries = [
        ("count all objects", "print(f'Total objects: {len(model.Objects)}')"),
        ("list layer names", "for i in range(len(model.Layers)):\n    print(model.Layers[i].Name)"),
        ("find all curves", "curves = [obj for obj in model.Objects if 'Curve' in type(obj.Geometry).__name__]\nprint(f'Curves: {len(curves)}')"),
        ("find all meshes", "meshes = [obj for obj in model.Objects if isinstance(obj.Geometry, rhino3dm.Mesh)]\nprint(f'Meshes: {len(meshes)}')"),
        ("print object names", "for obj in model.Objects:\n    if obj.Attributes.Name:\n        print(obj.Attributes.Name)"),
        ("get all point coordinates", "for obj in model.Objects:\n    geo = obj.Geometry\n    if isinstance(geo, rhino3dm.Point):\n        loc = geo.Location\n        print(f'{loc.X}, {loc.Y}, {loc.Z}')"),
    ]
    for desc, body in r3dm_queries:
        pairs.append(m(f"Read a 3dm file and {desc}",
            f"{R3}\nmodel = rhino3dm.File3dm.Read('input.3dm')\n{body}",
            "rhino3dm_standalone", "easy", "rhino3dm", ["read", "query"]))

    # File operations
    r3dm_file_ops = [
        ("copy all objects from one file to another",
         f"model_src = rhino3dm.File3dm.Read('source.3dm')\nmodel_dst = rhino3dm.File3dm()\nfor obj in model_src.Objects:\n    model_dst.Objects.Add(obj.Geometry)\nmodel_dst.Write('destination.3dm', 7)"),
        ("add a layer and put geometry on it",
         f"model = rhino3dm.File3dm()\nlayer = rhino3dm.Layer()\nlayer.Name = 'MyLayer'\nlayer.Color = (255, 0, 0, 255)\nidx = model.Layers.Add(layer)\nattr = rhino3dm.ObjectAttributes()\nattr.LayerIndex = idx\nmodel.Objects.AddPoint(rhino3dm.Point3d(0,0,0), attr)\nmodel.Write('layered.3dm', 7)"),
        ("create a file with named objects",
         f"model = rhino3dm.File3dm()\nfor i in range(5):\n    attr = rhino3dm.ObjectAttributes()\n    attr.Name = f'Point_{{i}}'\n    model.Objects.AddPoint(rhino3dm.Point3d(i, 0, 0), attr)\nmodel.Write('named.3dm', 7)"),
        ("filter objects by layer when reading",
         f"model = rhino3dm.File3dm.Read('input.3dm')\ntarget_layer = 0\nfor obj in model.Objects:\n    if obj.Attributes.LayerIndex == target_layer:\n        print(f'Object on target layer: {{type(obj.Geometry).__name__}}')"),
    ]
    for desc, body in r3dm_file_ops:
        pairs.append(m(desc.capitalize(),
            f"{R3}\n{body}",
            "rhino3dm_standalone", "medium", "rhino3dm", ["file"]))

    # Mesh creation variations
    for n in [5, 10, 20, 30]:
        pairs.append(m(f"Create a {n}x{n} mesh grid and save as 3dm",
            f"{R3}\nmodel = rhino3dm.File3dm()\nmesh = rhino3dm.Mesh()\nfor i in range({n}+1):\n    for j in range({n}+1):\n        mesh.Vertices.Add(j, i, 0)\nfor i in range({n}):\n    for j in range({n}):\n        a = i*({n}+1)+j\n        mesh.Faces.AddFace(a, a+1, a+{n}+2, a+{n}+1)\nmodel.Objects.AddMesh(mesh)\nmodel.Write('mesh_grid.3dm', 7)",
            "rhino3dm_standalone", "medium", "rhino3dm", ["mesh", "grid"]))

    # ═══════════════════════════════════════════════════════════
    # F) ADDITIONAL CODE FIXING (~150)
    # ═══════════════════════════════════════════════════════════

    # More argument errors across API methods
    more_arg_fixes = [
        ("rs.OffsetCurve(crv, 2)", "rs.OffsetCurve(crv, (0,0,0), 2)", "needs direction point"),
        ("rs.FilletCurves(c1, c2)", "rs.FilletCurves(c1, c2, 1.0)", "needs radius"),
        ("rs.ExtrudeCurve(crv, 10)", "path = rs.AddLine((0,0,0),(0,0,10))\nrs.ExtrudeCurve(crv, path)", "needs path curve not distance"),
        ("rs.AddLayer('Test', 'red')", "rs.AddLayer('Test', (255,0,0))", "color needs tuple"),
        ("rs.ObjectColor(obj, 'blue')", "rs.ObjectColor(obj, (0,0,255))", "color needs RGB tuple"),
        ("rs.AddText('Hello', 0, 0, 0)", "rs.AddText('Hello', (0,0,0))", "point needs tuple"),
        ("rs.AddTextDot('Label', 0, 0, 0)", "rs.AddTextDot('Label', (0,0,0))", "point needs tuple"),
        ("rs.Distance((0,0,0), 10)", "rs.Distance((0,0,0), (10,0,0))", "needs two points"),
        ("rs.MirrorObject(obj, (0,0,0))", "rs.MirrorObject(obj, (0,0,0), (0,1,0))", "mirror needs two points"),
        ("rs.ArrayLinear(obj, 5, 10)", "rs.CopyObject(obj, (10,0,0))", "ArrayLinear wrong args"),
    ]
    for buggy, fixed, desc in more_arg_fixes:
        pairs.append(m(
            f"Fix: {desc}:\n```python\nimport rhinoscriptsyntax as rs\n{buggy}\n```",
            f"import rhinoscriptsyntax as rs\n{fixed}",
            "code_fixing", "easy", "rhinoscriptsyntax", ["fix", "arguments"]))

    # More missing null checks with different patterns
    more_null_checks = [
        ("srf = rs.GetObject('Select')\nedges = rs.DuplicateEdgeCurves(srf)\nfor e in edges:\n    print(rs.CurveLength(e))",
         "srf = rs.GetObject('Select surface', 8)\nif srf:\n    edges = rs.DuplicateEdgeCurves(srf)\n    if edges:\n        for e in edges:\n            print(rs.CurveLength(e))"),
        ("objs = rs.AllObjects()\nfor obj in objs:\n    rs.ObjectColor(obj, (255,0,0))",
         "objs = rs.AllObjects()\nif objs:\n    for obj in objs:\n        rs.ObjectColor(obj, (255,0,0))"),
        ("crv = rs.GetObject('Select')\npts = rs.DivideCurve(crv, 10)\nfor pt in pts:\n    rs.AddPoint(pt)",
         "crv = rs.GetObject('Select curve', 4)\nif crv:\n    pts = rs.DivideCurve(crv, 10)\n    if pts:\n        for pt in pts:\n            rs.AddPoint(pt)"),
        ("a = rs.GetObject('First')\nb = rs.GetObject('Second')\nresult = rs.BooleanDifference(a, b)",
         "a = rs.GetObject('First', 16)\nb = rs.GetObject('Second', 16)\nif a and b:\n    result = rs.BooleanDifference(a, b, True)\n    if not result:\n        print('Boolean failed')"),
        ("crv = rs.GetObject('Select')\nmid = rs.CurveMidPoint(crv)\nrs.AddPoint(mid)",
         "crv = rs.GetObject('Select curve', 4)\nif crv:\n    mid = rs.CurveMidPoint(crv)\n    if mid:\n        rs.AddPoint(mid)"),
    ]
    for buggy, fixed in more_null_checks:
        pairs.append(m(
            f"Add proper null checking to this code:\n```python\nimport rhinoscriptsyntax as rs\n{buggy}\n```",
            f"import rhinoscriptsyntax as rs\n{fixed}",
            "code_fixing", "easy", "rhinoscriptsyntax", ["fix", "null-check"]))

    # More wrong method names
    more_method_fixes = [
        ("rs.PointCoordinates(pt)", "rs.PointCoordinates(pt)", "already correct but common confusion"),
        ("rs.CurveArea(crv)", "rs.CurveAreaCentroid(crv)", "CurveArea -> CurveAreaCentroid"),
        ("rs.SplitCurve(crv, pt)", "t = rs.CurveClosestPoint(crv, pt)\nrs.SplitCurve(crv, t)", "SplitCurve needs parameter not point"),
        ("rs.UnrollSurface(srf)", "rs.UnrollSrf(srf, False)", "wrong method name and missing arg"),
        ("rs.CapHoles(srf)", "rs.CapPlanarHoles(srf)", "CapHoles -> CapPlanarHoles"),
        ("rs.FlipSurface(srf)", "rs.FlipSurface(srf)", "method exists, common confusion with FlipNormals"),
        ("rs.IsPointOnCurve(pt, crv)", "rs.IsPointOnCurve(crv, pt)", "arguments reversed"),
        ("rs.CurveDivide(crv, 10)", "rs.DivideCurve(crv, 10)", "CurveDivide -> DivideCurve"),
        ("rs.SurfacePrincipalCurvatures(srf, 0.5, 0.5)", "rs.SurfaceCurvature(srf, (0.5, 0.5))", "wrong method and arg format"),
        ("rs.GetObjectType(obj)", "rs.ObjectType(obj)", "GetObjectType -> ObjectType"),
    ]
    for buggy, fixed, desc in more_method_fixes:
        pairs.append(m(
            f"Fix the method name ({desc}):\n```python\nimport rhinoscriptsyntax as rs\n{buggy}\n```",
            f"import rhinoscriptsyntax as rs\n{fixed}",
            "code_fixing", "easy", "rhinoscriptsyntax", ["fix", "method-name"]))

    # RhinoCommon type fixes
    rc_type_fixes = [
        ("rg.Point3d(0, 0)", "rg.Point3d(0, 0, 0)", "Point3d needs 3 args"),
        ("rg.Vector3d(1)", "rg.Vector3d(1, 0, 0)", "Vector3d needs 3 args"),
        ("rg.Plane(0, 0, 0)", "rg.Plane(rg.Point3d(0,0,0), rg.Vector3d(0,0,1))", "Plane needs Point3d and Vector3d"),
        ("rg.Line(0, 0, 0, 10, 0, 0)", "rg.Line(rg.Point3d(0,0,0), rg.Point3d(10,0,0))", "Line needs two Point3d"),
        ("rg.Circle(5)", "rg.Circle(rg.Plane.WorldXY, 5)", "Circle needs Plane and radius"),
        ("rg.Sphere(5)", "rg.Sphere(rg.Point3d.Origin, 5)", "Sphere needs center and radius"),
        ("rg.Arc(0, 0, 0, 5, 90)", "rg.Arc(rg.Circle(rg.Plane.WorldXY, 5), math.radians(90))", "Arc needs proper args"),
        ("rg.Box(10, 10, 10)", "rg.Box(rg.Plane.WorldXY, rg.Interval(0,10), rg.Interval(0,10), rg.Interval(0,10))", "Box needs Plane and Intervals"),
    ]
    for buggy, fixed, desc in rc_type_fixes:
        imp = "import Rhino.Geometry as rg\nimport scriptcontext as sc"
        if "math" in fixed:
            imp += "\nimport math"
        pairs.append(m(
            f"Fix type error ({desc}):\n```python\n{RC}\n{buggy}\n```",
            f"{imp}\n{fixed}",
            "code_fixing", "medium", "RhinoCommon", ["fix", "type-error"]))

    # ═══════════════════════════════════════════════════════════
    # G) ADDITIONAL DESIGN WORKFLOWS (~150)
    # ═══════════════════════════════════════════════════════════

    # More arraying with different shapes
    array_shapes = [("sphere", "rs.AddSphere((0,0,0), 1)"),
                    ("cube", "rs.AddBox([(0,0,0),(2,0,0),(2,2,0),(0,2,0),(0,0,2),(2,0,2),(2,2,2),(0,2,2)])"),
                    ("cylinder", "rs.AddCylinder((0,0,0), 3, 0.5)"),
                    ("cone", "rs.AddCone((0,0,0), 2, 1)")]
    for s_name, s_code in array_shapes:
        for count in [4, 6, 8, 10, 16]:
            pairs.append(m(
                f"Create a polar array of {count} {s_name}s at radius 10",
                f"{RSM}\n{s_code}\nrs.MoveObject(obj, (10,0,0))\nfor i in range(1, {count}):\n    copy = rs.CopyObject(obj)\n    rs.RotateObject(copy, (0,0,0), i*360.0/{count})",
                "design_workflows", "medium", "rhinoscriptsyntax", ["array", "polar", s_name]))

    # More sweep variations
    for prof_r in [0.5, 1.0, 2.0, 3.0]:
        pairs.append(m(
            f"Create a pipe with radius {prof_r} along a selected curve",
            f"{RS}\ncrv = rs.GetObject('Select curve', 4)\nif crv:\n    rs.AddPipe(crv, 0, {prof_r})",
            "design_workflows", "easy", "rhinoscriptsyntax", ["pipe", "sweep"]))

    # More loft variations
    for n in [3, 4, 5, 7, 10]:
        for shape in ["circles", "ellipses"]:
            if shape == "circles":
                crv_code = f"rs.AddCircle((0,0,i*3), 5 - i*0.2)"
            else:
                crv_code = f"rs.AddEllipse(rs.MovePlane(rs.WorldXYPlane(),(0,0,i*3)), 5-i*0.2, 3-i*0.1)"
            pairs.append(m(
                f"Loft {n} {shape} at different heights to create a tapered form",
                f"{RS}\ncurves = []\nfor i in range({n}):\n    crv = {crv_code}\n    curves.append(crv)\nrs.AddLoftSrf(curves)",
                "design_workflows", "medium", "rhinoscriptsyntax", ["loft", shape]))

    # Boolean with arrays
    for nx, ny in [(3,3),(4,4),(5,5),(3,5)]:
        for hole_r in [0.5, 1.0]:
            pairs.append(m(
                f"Create a {nx}x{ny} grid of cylindrical holes (r={hole_r}) in a plate",
                f"{RS}\nplate = rs.AddBox([(0,0,0),({nx*3+2},0,0),({nx*3+2},{ny*3+2},0),(0,{ny*3+2},0),(0,0,1),({nx*3+2},0,1),({nx*3+2},{ny*3+2},1),(0,{ny*3+2},1)])\nfor i in range({nx}):\n    for j in range({ny}):\n        cx = 2 + i*3\n        cy = 2 + j*3\n        hole = rs.AddCylinder((cx,cy,-0.5), 2, {hole_r})\n        result = rs.BooleanDifference(plate, hole, True)\n        if result:\n            plate = result[0]",
                "design_workflows", "hard", "rhinoscriptsyntax", ["boolean", "holes", "grid"]))

    # More offset operations
    for dist in [0.5, 1, 2, 3, 5]:
        pairs.append(m(
            f"Create a wall by offsetting a curve by {dist} and extruding",
            f"{RS}\ncrv = rs.GetObject('Select closed curve', 4)\nif crv:\n    inner = rs.OffsetCurve(crv, (0,0,0), {dist})\n    if inner:\n        path = rs.AddLine((0,0,0),(0,0,3))\n        outer_wall = rs.ExtrudeCurve(crv, path)\n        inner_wall = rs.ExtrudeCurve(inner[0], path)\n        rs.DeleteObject(path)",
            "design_workflows", "hard", "rhinoscriptsyntax", ["offset", "wall", "extrude"]))

    return pairs
