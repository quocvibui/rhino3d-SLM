"""Multi-step geometry workflow pairs (~450+)."""

def m(instruction, code, difficulty, api, tags):
    return {"instruction": instruction, "code": code, "source": "synthetic",
            "category": "multi_step_workflows", "difficulty": difficulty, "api": api, "tags": tags}

def generate():
    pairs = []

    # ── Helper: rhinoscriptsyntax prefix ──
    RS = "import rhinoscriptsyntax as rs"
    RSM = "import rhinoscriptsyntax as rs\nimport math"
    RC = "import Rhino.Geometry as rg\nimport scriptcontext as sc"
    RCM = "import Rhino.Geometry as rg\nimport scriptcontext as sc\nimport math"
    REDRAW = "sc.doc.Views.Redraw()"

    # ═══════════════════════════════════════════════════════════
    # 1) EXTRUDE + CAP workflows  (rs)
    # ═══════════════════════════════════════════════════════════
    shapes_2d = [
        ("circle", "crv = rs.AddCircle((0,0,0), {r})", [5,8,12]),
        ("rectangle", "crv = rs.AddRectangle(rs.WorldXYPlane(), {w}, {h})", [(10,5),(20,10),(8,8)]),
        ("ellipse", "crv = rs.AddEllipse(rs.WorldXYPlane(), {a}, {b})", [(10,5),(6,3),(15,8)]),
    ]
    for shape, tmpl, params in shapes_2d:
        for p in params:
            if isinstance(p, tuple):
                code_line = tmpl.format(w=p[0], h=p[1]) if "w" in tmpl else tmpl.format(a=p[0], b=p[1])
                dim = f"{p[0]}x{p[1]}"
            else:
                code_line = tmpl.format(r=p)
                dim = str(p)
            for ht in [10, 20]:
                pairs.append(m(
                    f"Create a {shape} ({dim}), extrude it {ht} units along Z, and cap the openings",
                    f"{RS}\n{code_line}\npath = rs.AddLine((0,0,0),(0,0,{ht}))\nsrf = rs.ExtrudeCurve(crv, path)\nrs.CapPlanarHoles(srf)\nrs.DeleteObjects([crv, path])",
                    "medium", "rhinoscriptsyntax", ["extrude", "cap", shape]))

    # ═══════════════════════════════════════════════════════════
    # 2) REVOLVE workflows  (rs)
    # ═══════════════════════════════════════════════════════════
    profiles = [
        ("vase profile", "pts = [(2,0,0),(3,0,2),(4,0,5),(3.5,0,8),(2.5,0,10),(3,0,12)]\nprofile = rs.AddInterpCurve(pts)"),
        ("wine glass profile", "pts = [(4,0,0),(4,0,0.5),(0.5,0,1),(0.5,0,6),(2,0,7),(3,0,7.5)]\nprofile = rs.AddInterpCurve(pts)"),
        ("bowl profile", "pts = [(5,0,0),(5,0,1),(4,0,3),(2,0,4),(0,0,4)]\nprofile = rs.AddInterpCurve(pts)"),
        ("bottle profile", "pts = [(3,0,0),(3,0,5),(2,0,8),(1.5,0,10),(1.5,0,12),(1,0,13)]\nprofile = rs.AddInterpCurve(pts)"),
        ("lampshade profile", "pts = [(2,0,0),(3,0,2),(5,0,5),(6,0,8)]\nprofile = rs.AddInterpCurve(pts)"),
    ]
    for name, prof_code in profiles:
        for angle in [360, 270, 180]:
            ang_desc = "" if angle == 360 else f" ({angle} degrees)"
            pairs.append(m(
                f"Create a {name} by revolving a profile curve around the Z axis{ang_desc}",
                f"{RS}\n{prof_code}\naxis_start = (0,0,0)\naxis_end = (0,0,1)\nrs.AddRevSrf(profile, (axis_start, axis_end), {angle})\nrs.DeleteObject(profile)",
                "medium", "rhinoscriptsyntax", ["revolve", name.split()[0]]))

    # ═══════════════════════════════════════════════════════════
    # 3) LOFT workflows  (rs)
    # ═══════════════════════════════════════════════════════════
    for n_sections in [3, 5, 8]:
        for shape_type in ["circles", "rectangles", "mixed"]:
            if shape_type == "circles":
                loop = f"curves = []\nfor i in range({n_sections}):\n    r = 5 + i * 0.5\n    c = rs.AddCircle((0,0,i*3), r)\n    curves.append(c)"
            elif shape_type == "rectangles":
                loop = f"curves = []\nfor i in range({n_sections}):\n    s = 5 + i\n    plane = rs.MovePlane(rs.WorldXYPlane(), (0,0,i*3))\n    c = rs.AddRectangle(plane, s, s)\n    curves.append(c)"
            else:
                loop = f"curves = []\nfor i in range({n_sections}):\n    if i % 2 == 0:\n        c = rs.AddCircle((0,0,i*3), 5)\n    else:\n        plane = rs.MovePlane(rs.WorldXYPlane(), (0,0,i*3))\n        c = rs.AddRectangle(plane, 8, 8)\n    curves.append(c)"
            pairs.append(m(
                f"Loft {n_sections} {shape_type} sections at increasing heights to form a tower shape",
                f"{RS}\n{loop}\nrs.AddLoftSrf(curves)",
                "medium", "rhinoscriptsyntax", ["loft", "sections", shape_type]))

    # ═══════════════════════════════════════════════════════════
    # 4) BOOLEAN workflows  (rs)
    # ═══════════════════════════════════════════════════════════
    bool_ops = [
        ("BooleanUnion", "union", "combine"),
        ("BooleanDifference", "difference", "subtract"),
        ("BooleanIntersection", "intersection", "intersect"),
    ]
    shape_pairs = [
        ("box and sphere", "a = rs.AddBox([(0,0,0),(10,0,0),(10,10,0),(0,10,0),(0,0,10),(10,0,10),(10,10,10),(0,10,10)])\nb = rs.AddSphere((5,5,5), 7)"),
        ("two overlapping boxes", "a = rs.AddBox([(0,0,0),(10,0,0),(10,10,0),(0,10,0),(0,0,10),(10,0,10),(10,10,10),(0,10,10)])\nb = rs.AddBox([(5,5,0),(15,5,0),(15,15,0),(5,15,0),(5,5,10),(15,5,10),(15,15,10),(5,15,10)])"),
        ("cylinder and box", "cyl = rs.AddCylinder((5,5,0), 12, 4)\na = cyl\nb = rs.AddBox([(0,0,0),(10,0,0),(10,10,0),(0,10,0),(0,0,8),(10,0,8),(10,10,8),(0,10,8)])"),
        ("two spheres", "a = rs.AddSphere((0,0,0), 6)\nb = rs.AddSphere((4,0,0), 6)"),
    ]
    for op_func, op_name, op_verb in bool_ops:
        for desc, setup in shape_pairs:
            pairs.append(m(
                f"Boolean {op_name} of {desc}",
                f"{RS}\n{setup}\nresult = rs.{op_func}(a, b, True)\nif not result:\n    print('Boolean {op_name} failed')",
                "medium", "rhinoscriptsyntax", ["boolean", op_name]))

    # ═══════════════════════════════════════════════════════════
    # 5) PIPE + ARRAY workflows  (rs)
    # ═══════════════════════════════════════════════════════════
    curves_for_pipe = [
        ("straight line", "rail = rs.AddLine((0,0,0),(20,0,0))"),
        ("arc", "rail = rs.AddArc3Pt((0,0,0),(20,0,0),(10,5,0))"),
        ("helix path", f"pts = []\nfor i in range(100):\n    t = i * 0.1\n    pts.append((5*math.cos(t), 5*math.sin(t), t))\nrail = rs.AddInterpCurve(pts)"),
        ("sine wave", f"pts = []\nfor i in range(60):\n    x = i * 0.5\n    pts.append((x, 3*math.sin(x*0.5), 0))\nrail = rs.AddInterpCurve(pts)"),
    ]
    for desc, rail_code in curves_for_pipe:
        for radius in [0.5, 1.0, 2.0]:
            imp = RSM if "math" in rail_code else RS
            pairs.append(m(
                f"Create a pipe with radius {radius} along a {desc}",
                f"{imp}\n{rail_code}\nrs.AddPipe(rail, 0, {radius})",
                "medium", "rhinoscriptsyntax", ["pipe", "sweep"]))

    # ═══════════════════════════════════════════════════════════
    # 6) CREATE + ARRAY workflows  (rs)
    # ═══════════════════════════════════════════════════════════
    array_items = [
        ("column", "obj = rs.AddCylinder((0,0,0), 10, 1)"),
        ("box", "obj = rs.AddBox([(0,0,0),(2,0,0),(2,2,0),(0,2,0),(0,0,3),(2,0,3),(2,2,3),(0,2,3)])"),
        ("sphere", "obj = rs.AddSphere((0,0,0), 1.5)"),
    ]
    for desc, create_code in array_items:
        for nx, ny, spacing in [(5,5,4), (3,8,5), (10,10,3)]:
            pairs.append(m(
                f"Create a {nx}x{ny} grid array of {desc}s with {spacing}-unit spacing",
                f"{RS}\n{create_code}\nfor i in range({nx}):\n    for j in range({ny}):\n        if i == 0 and j == 0:\n            continue\n        rs.CopyObject(obj, (i*{spacing}, j*{spacing}, 0))",
                "medium", "rhinoscriptsyntax", ["array", "grid", desc]))

    # Polar array
    for desc, create_code in array_items:
        for count in [6, 8, 12]:
            pairs.append(m(
                f"Create a polar array of {count} {desc}s around the Z axis at radius 10",
                f"{RSM}\n{create_code}\nrs.MoveObject(obj, (10,0,0))\nfor i in range(1, {count}):\n    angle = i * 360.0 / {count}\n    copy = rs.CopyObject(obj)\n    rs.RotateObject(copy, (0,0,0), angle)",
                "medium", "rhinoscriptsyntax", ["array", "polar", desc]))

    # ═══════════════════════════════════════════════════════════
    # 7) SWEEP workflows  (rs)
    # ═══════════════════════════════════════════════════════════
    sweep_profiles = [
        ("circular", "profile = rs.AddCircle(rs.MovePlane(rs.WorldXYPlane(),(0,0,0)), 1)"),
        ("rectangular", "profile = rs.AddRectangle(rs.WorldXYPlane(), 2, 1)"),
        ("triangular", "profile = rs.AddPolyline([(0,0,0),(1,0,0),(0.5,1,0),(0,0,0)])"),
    ]
    sweep_rails = [
        ("straight rail", "rail = rs.AddLine((0,0,0),(0,0,20))"),
        ("curved rail", "rail = rs.AddInterpCurve([(0,0,0),(5,0,5),(0,0,10),(-5,0,15),(0,0,20)])"),
        ("spiral rail", f"pts = []\nfor i in range(80):\n    t = i * 0.1\n    pts.append((3*math.cos(t), 3*math.sin(t), t))\nrail = rs.AddInterpCurve(pts)"),
    ]
    for prof_desc, prof_code in sweep_profiles:
        for rail_desc, rail_code in sweep_rails:
            imp = RSM if "math" in rail_code else RS
            pairs.append(m(
                f"Sweep a {prof_desc} profile along a {rail_desc}",
                f"{imp}\n{prof_code}\n{rail_code}\nrs.AddSweep1(rail, [profile])",
                "medium", "rhinoscriptsyntax", ["sweep", prof_desc]))

    # ═══════════════════════════════════════════════════════════
    # 8) CREATE + TRANSFORM + LAYER workflows  (rs)
    # ═══════════════════════════════════════════════════════════
    objects = [
        ("sphere", "obj = rs.AddSphere((0,0,0), 5)"),
        ("box", "obj = rs.AddBox([(0,0,0),(10,0,0),(10,10,0),(0,10,0),(0,0,10),(10,0,10),(10,10,10),(0,10,10)])"),
        ("cylinder", "obj = rs.AddCylinder((0,0,0), 10, 3)"),
        ("cone", "obj = rs.AddCone((0,0,0), 8, 4)"),
    ]
    transforms = [
        ("move it to (20,0,0)", "rs.MoveObject(obj, (20,0,0))"),
        ("rotate it 45 degrees around Z", "rs.RotateObject(obj, (0,0,0), 45)"),
        ("scale it by 2x from origin", "rs.ScaleObject(obj, (0,0,0), (2,2,2))"),
        ("mirror it across the YZ plane", "rs.MirrorObject(obj, (0,0,0), (0,1,0))"),
    ]
    layers = ["Geometry", "Walls", "Structure", "Furniture"]
    for obj_desc, obj_code in objects:
        for tr_desc, tr_code in transforms:
            for layer in layers[:1]:  # just one layer per combo to control count
                pairs.append(m(
                    f"Create a {obj_desc}, {tr_desc}, and assign it to layer '{layer}'",
                    f"{RS}\nif not rs.IsLayer('{layer}'):\n    rs.AddLayer('{layer}')\n{obj_code}\n{tr_code}\nrs.ObjectLayer(obj, '{layer}')",
                    "easy", "rhinoscriptsyntax", ["transform", "layer", obj_desc]))

    # ═══════════════════════════════════════════════════════════
    # 9) MULTI-SHAPE ASSEMBLY workflows  (rs)
    # ═══════════════════════════════════════════════════════════
    assemblies = [
        ("table", "top = rs.AddBox([(0,0,9),(20,0,9),(20,12,9),(0,12,9),(0,0,10),(20,0,10),(20,12,10),(0,12,10)])\nlegs = []\nfor x,y in [(1,1),(18,1),(1,10),(18,10)]:\n    leg = rs.AddCylinder((x,y,0), 9, 0.8)\n    legs.append(leg)"),
        ("chair", "seat = rs.AddBox([(0,0,4),(5,0,4),(5,5,4),(0,5,4),(0,0,5),(5,0,5),(5,5,5),(0,5,5)])\nback = rs.AddBox([(0,4.5,5),(5,4.5,5),(5,5,5),(0,5,5),(0,4.5,10),(5,4.5,10),(5,5,10),(0,5,10)])\nfor x,y in [(0.5,0.5),(4,0.5),(0.5,4),(4,4)]:\n    rs.AddCylinder((x,y,0), 4, 0.4)"),
        ("bookshelf", "for i in range(5):\n    shelf = rs.AddBox([(0,0,i*3),(10,0,i*3),(10,2,i*3),(0,2,i*3),(0,0,i*3+0.3),(10,0,i*3+0.3),(10,2,i*3+0.3),(0,2,i*3+0.3)])\nside_l = rs.AddBox([(0,0,0),(0.3,0,0),(0.3,2,0),(0,2,0),(0,0,12),(0.3,0,12),(0.3,2,12),(0,2,12)])\nside_r = rs.AddBox([(9.7,0,0),(10,0,0),(10,2,0),(9.7,2,0),(9.7,0,12),(10,0,12),(10,2,12),(9.7,2,12)])"),
        ("window frame", "outer = rs.AddRectangle(rs.WorldXYPlane(), 10, 15)\ninner = rs.AddRectangle(rs.MovePlane(rs.WorldXYPlane(),(1,1,0)), 8, 13)\nmid_h = rs.AddLine((1,7.5,0),(9,7.5,0))\nmid_v = rs.AddLine((5,1,0),(5,14,0))"),
        ("staircase", "for i in range(10):\n    step = rs.AddBox([(0,i*3,i*2),(10,i*3,i*2),(10,i*3+3,i*2),(0,i*3+3,i*2),(0,i*3,i*2+2),(10,i*3,i*2+2),(10,i*3+3,i*2+2),(0,i*3+3,i*2+2)])"),
    ]
    for name, code in assemblies:
        pairs.append(m(
            f"Build a simple {name} from basic geometry primitives",
            f"{RS}\n{code}",
            "hard", "rhinoscriptsyntax", ["assembly", name]))

    # ═══════════════════════════════════════════════════════════
    # 10) RhinoCommon multi-step workflows
    # ═══════════════════════════════════════════════════════════
    rc_workflows = [
        ("Create a sphere, apply a scaling transform, and add to document",
         f"{RC}\nsphere = rg.Sphere(rg.Point3d(0,0,0), 5)\nbrep = sphere.ToBrep()\nxform = rg.Transform.Scale(rg.Point3d.Origin, 2.0)\nbrep.Transform(xform)\nsc.doc.Objects.AddBrep(brep)\n{REDRAW}",
         "medium", ["sphere", "transform", "scale"]),
        ("Create a box, translate it, then rotate around Z axis",
         f"{RCM}\nbox = rg.Box(rg.Plane.WorldXY, rg.Interval(0,10), rg.Interval(0,10), rg.Interval(0,10))\nbrep = box.ToBrep()\nmove = rg.Transform.Translation(rg.Vector3d(5,0,0))\nrot = rg.Transform.Rotation(math.radians(45), rg.Vector3d.ZAxis, rg.Point3d.Origin)\nbrep.Transform(move)\nbrep.Transform(rot)\nsc.doc.Objects.AddBrep(brep)\n{REDRAW}",
         "medium", ["box", "translate", "rotate"]),
        ("Create a circle, extrude it into a cylinder brep",
         f"{RC}\nplane = rg.Plane.WorldXY\ncircle = rg.Circle(plane, 5.0)\ncurve = circle.ToNurbsCurve()\npath = rg.Line(rg.Point3d(0,0,0), rg.Point3d(0,0,10))\nsrf = rg.SumSurface.Create(curve, path.ToNurbsCurve())\nsc.doc.Objects.AddSurface(srf)\n{REDRAW}",
         "medium", ["circle", "extrude", "cylinder"]),
        ("Create a mesh plane, deform its vertices with a sine wave, and add it",
         f"{RCM}\nmesh = rg.Mesh()\nfor i in range(20):\n    for j in range(20):\n        z = 2 * math.sin(i * 0.5) * math.cos(j * 0.5)\n        mesh.Vertices.Add(i, j, z)\nfor i in range(19):\n    for j in range(19):\n        a = i * 20 + j\n        mesh.Faces.AddFace(a, a+1, a+21, a+20)\nmesh.Normals.ComputeNormals()\nsc.doc.Objects.AddMesh(mesh)\n{REDRAW}",
         "hard", ["mesh", "sine", "deform"]),
        ("Create multiple lines radiating from origin and add them as a group",
         f"{RCM}\nimport Rhino\nids = []\nfor i in range(12):\n    angle = math.radians(i * 30)\n    end = rg.Point3d(10*math.cos(angle), 10*math.sin(angle), 0)\n    line = rg.Line(rg.Point3d.Origin, end)\n    oid = sc.doc.Objects.AddLine(line)\n    ids.append(oid)\nidx = sc.doc.Groups.Add()\nfor oid in ids:\n    sc.doc.Groups.AddToGroup(idx, oid)\n{REDRAW}",
         "medium", ["lines", "group", "radial"]),
        ("Create a torus mesh from scratch using parametric equations",
         f"{RCM}\nmesh = rg.Mesh()\nR, r = 10, 3\nn, m2 = 40, 20\nfor i in range(n):\n    u = 2 * math.pi * i / n\n    for j in range(m2):\n        v = 2 * math.pi * j / m2\n        x = (R + r*math.cos(v)) * math.cos(u)\n        y = (R + r*math.cos(v)) * math.sin(u)\n        z = r * math.sin(v)\n        mesh.Vertices.Add(x, y, z)\nfor i in range(n):\n    for j in range(m2):\n        a = i*m2 + j\n        b = i*m2 + (j+1)%m2\n        c = ((i+1)%n)*m2 + (j+1)%m2\n        d = ((i+1)%n)*m2 + j\n        mesh.Faces.AddFace(a, b, c, d)\nmesh.Normals.ComputeNormals()\nsc.doc.Objects.AddMesh(mesh)\n{REDRAW}",
         "hard", ["torus", "mesh", "parametric"]),
        ("Create two curves and loft between them using RhinoCommon",
         f"{RC}\npts1 = [rg.Point3d(i, 0, 0) for i in range(11)]\npts2 = [rg.Point3d(i, 0, 10) for i in range(11)]\nc1 = rg.NurbsCurve.Create(False, 3, pts1)\nc2 = rg.NurbsCurve.Create(False, 3, pts2)\nlofts = rg.Brep.CreateFromLoft([c1, c2], rg.Point3d.Unset, rg.Point3d.Unset, rg.LoftType.Normal, False)\nfor loft in lofts:\n    sc.doc.Objects.AddBrep(loft)\n{REDRAW}",
         "hard", ["loft", "curves", "brep"]),
        ("Create a NURBS surface from a grid of control points",
         f"{RC}\ndeg_u, deg_v = 3, 3\ncount_u, count_v = 6, 6\nsrf = rg.NurbsSurface.Create(3, False, deg_u+1, deg_v+1, count_u, count_v)\nfor i in range(count_u):\n    for j in range(count_v):\n        srf.Points.SetPoint(i, j, rg.Point3d(i*2, j*2, 0))\nsc.doc.Objects.AddSurface(srf)\n{REDRAW}",
         "hard", ["nurbs", "surface", "controlpoints"]),
    ]
    for inst, code, diff, tags in rc_workflows:
        pairs.append(m(inst, code, diff, "RhinoCommon", tags))

    # ═══════════════════════════════════════════════════════════
    # 11) FILLET + CHAMFER workflows  (rs)
    # ═══════════════════════════════════════════════════════════
    for radius in [0.5, 1.0, 2.0]:
        pairs.append(m(
            f"Create two intersecting lines and fillet them with radius {radius}",
            f"{RS}\nl1 = rs.AddLine((0,0,0),(10,0,0))\nl2 = rs.AddLine((5,-5,0),(5,5,0))\nrs.FilletCurves(l1, l2, {radius})",
            "easy", "rhinoscriptsyntax", ["fillet", "curves"]))

    # ═══════════════════════════════════════════════════════════
    # 12) OFFSET + EXTRUDE (wall from outline)
    # ═══════════════════════════════════════════════════════════
    outlines = [
        ("rectangular outline", "crv = rs.AddRectangle(rs.WorldXYPlane(), 20, 15)"),
        ("L-shaped outline", "pts = [(0,0,0),(20,0,0),(20,10,0),(10,10,0),(10,15,0),(0,15,0),(0,0,0)]\ncrv = rs.AddPolyline(pts)"),
        ("circular outline", "crv = rs.AddCircle((0,0,0), 10)"),
    ]
    for desc, outline_code in outlines:
        for thickness in [0.3, 0.5]:
            for height in [3, 5]:
                pairs.append(m(
                    f"Create a wall from a {desc}: offset inward by {thickness}, extrude to height {height}",
                    f"{RS}\n{outline_code}\ninner = rs.OffsetCurve(crv, (0,0,0), {thickness})\nif inner:\n    path = rs.AddLine((0,0,0),(0,0,{height}))\n    wall_outer = rs.ExtrudeCurve(crv, path)\n    wall_inner = rs.ExtrudeCurve(inner[0], path)\n    rs.DeleteObject(path)",
                    "hard", "rhinoscriptsyntax", ["offset", "extrude", "wall"]))

    # ═══════════════════════════════════════════════════════════
    # 13) SURFACE SUBDIVISION workflows
    # ═══════════════════════════════════════════════════════════
    for u_div, v_div in [(5,5),(8,8),(10,10),(4,8)]:
        pairs.append(m(
            f"Subdivide a selected surface into a {u_div}x{v_div} grid of points",
            f"{RS}\nsrf = rs.GetObject('Select surface', 8)\nif srf:\n    u_dom = rs.SurfaceDomain(srf, 0)\n    v_dom = rs.SurfaceDomain(srf, 1)\n    for i in range({u_div}+1):\n        for j in range({v_div}+1):\n            u = u_dom[0] + (u_dom[1]-u_dom[0]) * i / {u_div}\n            v = v_dom[0] + (v_dom[1]-v_dom[0]) * j / {v_div}\n            pt = rs.EvaluateSurface(srf, u, v)\n            rs.AddPoint(pt)",
            "medium", "rhinoscriptsyntax", ["surface", "subdivide", "grid"]))

    # ═══════════════════════════════════════════════════════════
    # 14) CURVE OPERATIONS  (join, offset, rebuild)
    # ═══════════════════════════════════════════════════════════
    pairs.extend([
        m("Join multiple curves into one and rebuild with fewer control points",
          f"{RS}\ncrvs = rs.GetObjects('Select curves', 4)\nif crvs:\n    joined = rs.JoinCurves(crvs, True)\n    if joined:\n        for c in joined:\n            rs.RebuildCurve(c, 3, 10)",
          "medium", "rhinoscriptsyntax", ["join", "rebuild", "curve"]),
        m("Create a curve, offset it both sides, and loft between them",
          f"{RS}\npts = [(0,0,0),(5,3,0),(10,0,0),(15,4,0),(20,0,0)]\ncrv = rs.AddInterpCurve(pts)\noff1 = rs.OffsetCurve(crv, (0,1,0), 2)\noff2 = rs.OffsetCurve(crv, (0,-1,0), 2)\nif off1 and off2:\n    rs.AddLoftSrf([off1[0], crv, off2[0]])",
          "hard", "rhinoscriptsyntax", ["offset", "loft", "curve"]),
        m("Split a curve at its midpoint and color each half differently",
          f"{RS}\ncrv = rs.GetObject('Select curve', 4)\nif crv:\n    dom = rs.CurveDomain(crv)\n    mid = (dom[0] + dom[1]) / 2.0\n    parts = rs.SplitCurve(crv, mid)\n    if parts:\n        rs.ObjectColor(parts[0], (255,0,0))\n        if len(parts) > 1:\n            rs.ObjectColor(parts[1], (0,0,255))",
          "medium", "rhinoscriptsyntax", ["split", "color", "curve"]),
        m("Divide a curve into equal segments and place spheres at each point",
          f"{RS}\ncrv = rs.GetObject('Select curve', 4)\nif crv:\n    pts = rs.DivideCurve(crv, 20)\n    for pt in pts:\n        rs.AddSphere(pt, 0.5)",
          "medium", "rhinoscriptsyntax", ["divide", "sphere", "curve"]),
        m("Extend a curve by 5 units on both ends",
          f"{RS}\ncrv = rs.GetObject('Select curve', 4)\nif crv:\n    rs.ExtendCurveLength(crv, 0, 2, 5)",
          "easy", "rhinoscriptsyntax", ["extend", "curve"]),
    ])

    # ═══════════════════════════════════════════════════════════
    # 15) SURFACE from CURVES workflows
    # ═══════════════════════════════════════════════════════════
    srf_from_curve = [
        ("planar surface from a closed curve",
         f"{RS}\npts = [(0,0,0),(10,0,0),(10,10,0),(5,12,0),(0,10,0),(0,0,0)]\ncrv = rs.AddPolyline(pts)\nrs.AddPlanarSrf([crv])",
         "easy", ["planar", "surface"]),
        ("surface from four edge curves",
         f"{RS}\nc1 = rs.AddLine((0,0,0),(10,0,0))\nc2 = rs.AddLine((10,0,0),(10,10,5))\nc3 = rs.AddLine((10,10,5),(0,10,5))\nc4 = rs.AddLine((0,10,5),(0,0,0))\nrs.AddEdgeSrf([c1,c2,c3,c4])",
         "medium", ["edge", "surface"]),
        ("surface from a network of curves",
         f"{RS}\nh1 = rs.AddLine((0,0,0),(10,0,0))\nh2 = rs.AddLine((0,10,0),(10,10,3))\nv1 = rs.AddLine((0,0,0),(0,10,0))\nv2 = rs.AddLine((10,0,0),(10,10,3))\nrs.AddNetworkSrf([h1,h2,v1,v2])",
         "hard", ["network", "surface"]),
    ]
    for desc, code, diff, tags in srf_from_curve:
        pairs.append(m(f"Create a {desc}", code, diff, "rhinoscriptsyntax", tags))

    # ═══════════════════════════════════════════════════════════
    # 16) EXPORT / IMPORT workflows
    # ═══════════════════════════════════════════════════════════
    pairs.extend([
        m("Select objects and export them to a new 3dm file",
          f"{RS}\nobjs = rs.GetObjects('Select objects to export')\nif objs:\n    rs.SelectObjects(objs)\n    rs.Command('-Export \"C:/temp/export.3dm\" Enter')",
          "easy", "rhinoscriptsyntax", ["export", "file"]),
        m("Create geometry and set its name and layer before saving",
          f"{RS}\nif not rs.IsLayer('Export'):\n    rs.AddLayer('Export', (0,255,0))\nsphere = rs.AddSphere((0,0,0), 5)\nrs.ObjectName(sphere, 'MainSphere')\nrs.ObjectLayer(sphere, 'Export')",
          "easy", "rhinoscriptsyntax", ["name", "layer", "organize"]),
    ])

    # ═══════════════════════════════════════════════════════════
    # 17) PARAMETRIC PATTERNS  (tower twist, facade, spiral stair)
    # ═══════════════════════════════════════════════════════════
    parametric = [
        ("Create a twisted tower with floors that rotate 3 degrees per level",
         f"{RSM}\nfor i in range(30):\n    angle = math.radians(i * 3)\n    pts = []\n    for j in range(4):\n        a = angle + math.radians(j * 90)\n        pts.append((8*math.cos(a), 8*math.sin(a), i*3))\n    pts.append(pts[0])\n    rs.AddPolyline(pts)\n    if i > 0:\n        prev_angle = math.radians((i-1)*3)\n        for j in range(4):\n            a1 = prev_angle + math.radians(j*90)\n            a2 = angle + math.radians(j*90)\n            rs.AddLine((8*math.cos(a1),8*math.sin(a1),(i-1)*3),(8*math.cos(a2),8*math.sin(a2),i*3))",
         "hard", ["tower", "twist", "parametric"]),
        ("Generate a spiral staircase with 20 steps",
         f"{RSM}\nfor i in range(20):\n    angle = math.radians(i * 18)\n    x1 = 2 * math.cos(angle)\n    y1 = 2 * math.sin(angle)\n    x2 = 6 * math.cos(angle)\n    y2 = 6 * math.sin(angle)\n    z = i * 0.3\n    angle2 = math.radians((i+1) * 18)\n    x3 = 6 * math.cos(angle2)\n    y3 = 6 * math.sin(angle2)\n    pts = [(x1,y1,z),(x2,y2,z),(x3,y3,z+0.3),(2*math.cos(angle2),2*math.sin(angle2),z+0.3),(x1,y1,z)]\n    rs.AddPolyline(pts)",
         "hard", ["spiral", "staircase", "parametric"]),
        ("Create a parametric facade with windows that vary in size based on height",
         f"{RSM}\nwall = rs.AddSrfPt([(0,0,0),(30,0,0),(30,0,20),(0,0,20)])\nfor i in range(6):\n    for j in range(4):\n        cx = 2.5 + i * 5\n        cz = 2.5 + j * 5\n        size = 1.5 + j * 0.3\n        pts = [(cx-size,0,cz-size),(cx+size,0,cz-size),(cx+size,0,cz+size),(cx-size,0,cz+size),(cx-size,0,cz-size)]\n        rs.AddPolyline(pts)",
         "hard", ["facade", "windows", "parametric"]),
        ("Create a wavy roof surface from sine-deformed curves",
         f"{RSM}\ncurves = []\nfor i in range(5):\n    pts = []\n    for j in range(20):\n        x = j * 1.0\n        y = i * 5.0\n        z = 8 + 2 * math.sin(j * 0.5 + i * 0.3)\n        pts.append((x, y, z))\n    curves.append(rs.AddInterpCurve(pts))\nrs.AddLoftSrf(curves)",
         "hard", ["roof", "wave", "loft"]),
        ("Create a tensile structure by deforming a mesh with attractors",
         f"{RCM}\nmesh = rg.Mesh()\nfor i in range(30):\n    for j in range(30):\n        mesh.Vertices.Add(i, j, 0)\nfor i in range(29):\n    for j in range(29):\n        a = i*30+j\n        mesh.Faces.AddFace(a, a+1, a+31, a+30)\nattractors = [rg.Point3d(10,10,0), rg.Point3d(20,20,0)]\nfor i in range(mesh.Vertices.Count):\n    pt = mesh.Vertices[i]\n    z = 0\n    for att in attractors:\n        d = pt.DistanceTo(att)\n        z += 5.0 / (1 + d * 0.3)\n    mesh.Vertices.SetVertex(i, pt.X, pt.Y, z)\nmesh.Normals.ComputeNormals()\nsc.doc.Objects.AddMesh(mesh)\n{REDRAW}",
         "hard", ["tensile", "mesh", "attractor"]),
    ]
    for inst, code, diff, tags in parametric:
        pairs.append(m(inst, code, diff,
                       "RhinoCommon" if "rg." in code else "rhinoscriptsyntax", tags))

    # ═══════════════════════════════════════════════════════════
    # 18) MIRROR + JOIN workflows
    # ═══════════════════════════════════════════════════════════
    for desc, obj_code in objects:
        pairs.append(m(
            f"Create a {desc}, mirror it across the X axis, and join the two halves",
            f"{RS}\n{obj_code}\nmirror = rs.MirrorObject(obj, (0,0,0), (1,0,0), True)\nrs.BooleanUnion([obj, mirror])",
            "medium", "rhinoscriptsyntax", ["mirror", "join", "boolean"]))

    # ═══════════════════════════════════════════════════════════
    # 19) ANALYZE + MODIFY workflows
    # ═══════════════════════════════════════════════════════════
    pairs.extend([
        m("Select a closed curve, measure its area, and print it",
          f"{RS}\ncrv = rs.GetObject('Select closed curve', 4)\nif crv and rs.IsCurveClosed(crv):\n    area = rs.CurveAreaCentroid(crv)\n    if area:\n        print('Area:', area[0])",
          "easy", "rhinoscriptsyntax", ["area", "curve", "measure"]),
        m("Select two objects and print the minimum distance between them",
          f"{RS}\na = rs.GetObject('Select first object')\nb = rs.GetObject('Select second object')\nif a and b:\n    pts = rs.CurveClosestObject(a, b) if rs.IsCurve(a) else None\n    if pts:\n        print('Distance:', rs.Distance(pts[1], pts[2]))",
          "medium", "rhinoscriptsyntax", ["distance", "measure"]),
        m("Get bounding box of selected objects and draw it as wireframe",
          f"{RS}\nobjs = rs.GetObjects('Select objects')\nif objs:\n    bb = rs.BoundingBox(objs)\n    if bb:\n        rs.AddBox(bb)",
          "easy", "rhinoscriptsyntax", ["boundingbox", "wireframe"]),
        m("Evaluate surface at center and draw normal vector there",
          f"{RS}\nsrf = rs.GetObject('Select surface', 8)\nif srf:\n    u_dom = rs.SurfaceDomain(srf, 0)\n    v_dom = rs.SurfaceDomain(srf, 1)\n    u_mid = (u_dom[0] + u_dom[1]) / 2\n    v_mid = (v_dom[0] + v_dom[1]) / 2\n    pt = rs.EvaluateSurface(srf, u_mid, v_mid)\n    normal = rs.SurfaceNormal(srf, (u_mid, v_mid))\n    if pt and normal:\n        rs.AddLine(pt, [pt[0]+normal[0]*3, pt[1]+normal[1]*3, pt[2]+normal[2]*3])",
          "medium", "rhinoscriptsyntax", ["normal", "surface", "evaluate"]),
    ])

    # ═══════════════════════════════════════════════════════════
    # 20) CONVERT MESH ↔ NURBS
    # ═══════════════════════════════════════════════════════════
    pairs.extend([
        m("Convert a selected mesh to a NURBS polysurface",
          f"{RS}\nmesh = rs.GetObject('Select mesh', 32)\nif mesh:\n    brep = rs.MeshToNurb(mesh)\n    if brep:\n        rs.DeleteObject(mesh)",
          "easy", "rhinoscriptsyntax", ["mesh", "nurbs", "convert"]),
        m("Convert a selected surface to a mesh with custom density",
          f"{RS}\nsrf = rs.GetObject('Select surface', 8)\nif srf:\n    mesh = rs.MeshSurface(srf)\n    if mesh:\n        print('Created mesh from surface')",
          "easy", "rhinoscriptsyntax", ["surface", "mesh", "convert"]),
    ])

    return pairs
