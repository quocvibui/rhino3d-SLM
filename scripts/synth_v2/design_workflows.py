"""Common design workflow pairs (~400+): paneling, booleans, mesh, unrolling, lofting, sweeping."""

def m(instruction, code, difficulty, api, tags):
    return {"instruction": instruction, "code": code, "source": "synthetic",
            "category": "design_workflows", "difficulty": difficulty, "api": api, "tags": tags}

RS = "import rhinoscriptsyntax as rs"
RSM = "import rhinoscriptsyntax as rs\nimport math"
RC = "import Rhino.Geometry as rg\nimport scriptcontext as sc"
RCM = "import Rhino.Geometry as rg\nimport scriptcontext as sc\nimport math"
REDRAW = "sc.doc.Views.Redraw()"

def generate():
    pairs = []

    # ═══════════════════════════════════════════════════════════
    # 1) PANELING workflows
    # ═══════════════════════════════════════════════════════════
    panel_types = [
        ("rectangular", "corners = [\n                rs.EvaluateSurface(srf, u0, v0),\n                rs.EvaluateSurface(srf, u0+u_step, v0),\n                rs.EvaluateSurface(srf, u0+u_step, v0+v_step),\n                rs.EvaluateSurface(srf, u0, v0+v_step),\n                rs.EvaluateSurface(srf, u0, v0)\n            ]\n            rs.AddPolyline(corners)"),
        ("diamond", "mid_t = rs.EvaluateSurface(srf, u0+u_step/2, v0)\n            mid_r = rs.EvaluateSurface(srf, u0+u_step, v0+v_step/2)\n            mid_b = rs.EvaluateSurface(srf, u0+u_step/2, v0+v_step)\n            mid_l = rs.EvaluateSurface(srf, u0, v0+v_step/2)\n            rs.AddPolyline([mid_t, mid_r, mid_b, mid_l, mid_t])"),
        ("triangular", "p1 = rs.EvaluateSurface(srf, u0, v0)\n            p2 = rs.EvaluateSurface(srf, u0+u_step, v0)\n            p3 = rs.EvaluateSurface(srf, u0+u_step/2, v0+v_step)\n            rs.AddPolyline([p1, p2, p3, p1])"),
        ("X-pattern", "p1 = rs.EvaluateSurface(srf, u0, v0)\n            p2 = rs.EvaluateSurface(srf, u0+u_step, v0)\n            p3 = rs.EvaluateSurface(srf, u0+u_step, v0+v_step)\n            p4 = rs.EvaluateSurface(srf, u0, v0+v_step)\n            rs.AddLine(p1, p3)\n            rs.AddLine(p2, p4)"),
    ]
    for divs in [6, 8, 10, 12]:
        for panel_name, panel_code in panel_types:
            pairs.append(m(
                f"Panel a surface with {panel_name} tiles ({divs}x{divs} grid)",
                f"{RS}\nsrf = rs.GetObject('Select surface', 8)\nif srf:\n    u_dom = rs.SurfaceDomain(srf, 0)\n    v_dom = rs.SurfaceDomain(srf, 1)\n    u_step = (u_dom[1]-u_dom[0]) / {divs}\n    v_step = (v_dom[1]-v_dom[0]) / {divs}\n    for i in range({divs}):\n        for j in range({divs}):\n            u0 = u_dom[0] + i * u_step\n            v0 = v_dom[0] + j * v_step\n            {panel_code}",
                "hard", "rhinoscriptsyntax", ["paneling", panel_name]))

    # Paneling with offset
    for offset in [0.2, 0.5, 1.0]:
        pairs.append(m(
            f"Panel a surface with rectangular tiles offset inward by {offset}",
            f"{RS}\nsrf = rs.GetObject('Select surface', 8)\nif srf:\n    u_dom = rs.SurfaceDomain(srf, 0)\n    v_dom = rs.SurfaceDomain(srf, 1)\n    n = 8\n    u_step = (u_dom[1]-u_dom[0]) / n\n    v_step = (v_dom[1]-v_dom[0]) / n\n    margin = {offset} / max(u_step, v_step)\n    for i in range(n):\n        for j in range(n):\n            u0 = u_dom[0] + i*u_step + u_step*margin\n            v0 = v_dom[0] + j*v_step + v_step*margin\n            u1 = u_dom[0] + (i+1)*u_step - u_step*margin\n            v1 = v_dom[0] + (j+1)*v_step - v_step*margin\n            corners = [rs.EvaluateSurface(srf,u0,v0), rs.EvaluateSurface(srf,u1,v0),\n                       rs.EvaluateSurface(srf,u1,v1), rs.EvaluateSurface(srf,u0,v1),\n                       rs.EvaluateSurface(srf,u0,v0)]\n            rs.AddPolyline(corners)",
            "hard", "rhinoscriptsyntax", ["paneling", "offset"]))

    # Paneling with variable size
    pairs.append(m(
        "Panel a surface with rectangles that get smaller toward the top",
        f"{RSM}\nsrf = rs.GetObject('Select surface', 8)\nif srf:\n    u_dom = rs.SurfaceDomain(srf, 0)\n    v_dom = rs.SurfaceDomain(srf, 1)\n    n = 10\n    u_step = (u_dom[1]-u_dom[0]) / n\n    v_step = (v_dom[1]-v_dom[0]) / n\n    for i in range(n):\n        for j in range(n):\n            shrink = 1.0 - j * 0.05\n            u0 = u_dom[0] + i*u_step + u_step*(1-shrink)/2\n            v0 = v_dom[0] + j*v_step\n            u1 = u0 + u_step * shrink\n            v1 = v0 + v_step\n            corners = [rs.EvaluateSurface(srf,u0,v0), rs.EvaluateSurface(srf,u1,v0),\n                       rs.EvaluateSurface(srf,u1,v1), rs.EvaluateSurface(srf,u0,v1),\n                       rs.EvaluateSurface(srf,u0,v0)]\n            rs.AddPolyline(corners)",
        "hard", "rhinoscriptsyntax", ["paneling", "variable"]))

    # Hexagonal paneling
    pairs.append(m(
        "Create a hexagonal paneling pattern on a surface",
        f"{RSM}\nsrf = rs.GetObject('Select surface', 8)\nif srf:\n    u_dom = rs.SurfaceDomain(srf, 0)\n    v_dom = rs.SurfaceDomain(srf, 1)\n    n_u, n_v = 8, 8\n    u_step = (u_dom[1]-u_dom[0]) / n_u\n    v_step = (v_dom[1]-v_dom[0]) / n_v\n    for i in range(n_u):\n        for j in range(n_v):\n            u_c = u_dom[0] + (i + 0.5) * u_step\n            v_c = v_dom[0] + (j + 0.5 + (i % 2) * 0.5) * v_step\n            hex_pts = []\n            for k in range(7):\n                angle = math.radians(k * 60)\n                u = u_c + u_step * 0.4 * math.cos(angle)\n                v = v_c + v_step * 0.4 * math.sin(angle)\n                u = max(u_dom[0], min(u_dom[1], u))\n                v = max(v_dom[0], min(v_dom[1], v))\n                hex_pts.append(rs.EvaluateSurface(srf, u, v))\n            if len(hex_pts) >= 3:\n                rs.AddPolyline(hex_pts)",
        "hard", "rhinoscriptsyntax", ["paneling", "hexagonal"]))

    # ═══════════════════════════════════════════════════════════
    # 2) BOOLEAN workflows
    # ═══════════════════════════════════════════════════════════
    # Window openings
    for n_x, n_y in [(3,4), (5,3), (4,6)]:
        for win_w, win_h in [(1.5, 2.0), (2.0, 2.5)]:
            pairs.append(m(
                f"Create a wall with {n_x}x{n_y} window openings ({win_w}x{win_h} each)",
                f"{RS}\nwall = rs.AddBox([(0,0,0),(20,0,0),(20,0.3,0),(0,0.3,0),(0,0,15),(20,0,15),(20,0.3,15),(0,0.3,15)])\nfor i in range({n_x}):\n    for j in range({n_y}):\n        cx = 3 + i * 5\n        cz = 3 + j * 3.5\n        hole = rs.AddBox([(cx-{win_w/2},-0.5,cz-{win_h/2}),(cx+{win_w/2},-0.5,cz-{win_h/2}),(cx+{win_w/2},0.8,cz-{win_h/2}),(cx-{win_w/2},0.8,cz-{win_h/2}),(cx-{win_w/2},-0.5,cz+{win_h/2}),(cx+{win_w/2},-0.5,cz+{win_h/2}),(cx+{win_w/2},0.8,cz+{win_h/2}),(cx-{win_w/2},0.8,cz+{win_h/2})])\n        result = rs.BooleanDifference(wall, hole, True)\n        if result:\n            wall = result[0]",
                "hard", "rhinoscriptsyntax", ["boolean", "windows"]))

    # Hole patterns
    hole_patterns = [
        ("grid", "positions = [(i*sp, j*sp) for i in range(nx) for j in range(ny)]"),
        ("circular", f"positions = []\nfor k in range(n):\n    angle = math.radians(k * 360.0 / n)\n    positions.append((cx + r*math.cos(angle), cy + r*math.sin(angle)))"),
        ("random", "import random\nrandom.seed(42)\npositions = [(random.uniform(1,9), random.uniform(1,9)) for _ in range(n)]"),
    ]
    for pattern_name, pos_code in hole_patterns:
        pairs.append(m(
            f"Create a plate with {pattern_name} pattern of circular holes",
            f"{RSM}\nplate = rs.AddBox([(0,0,0),(10,0,0),(10,10,0),(0,10,0),(0,0,0.5),(10,0,0.5),(10,10,0.5),(0,10,0.5)])\nholes = []\nfor x, y in [(i,j) for i in range(2,9,2) for j in range(2,9,2)]:\n    cyl = rs.AddCylinder((x,y,-0.5), 1.5, 0.5)\n    result = rs.BooleanDifference(plate, cyl, True)\n    if result:\n        plate = result[0]",
            "hard", "rhinoscriptsyntax", ["boolean", "holes", pattern_name]))

    # ═══════════════════════════════════════════════════════════
    # 3) MESH CLEANUP workflows
    # ═══════════════════════════════════════════════════════════
    mesh_cleanup = [
        ("Weld mesh vertices and unify normals",
         f"{RS}\nmesh = rs.GetObject('Select mesh', 32)\nif mesh:\n    rs.MeshWeldVertices(mesh, 0.01)\n    rs.UnifyMeshNormals(mesh)\n    print('Mesh cleaned')",
         "easy", ["mesh", "weld", "normals"]),
        ("Check mesh for issues and repair",
         f"{RS}\nmesh = rs.GetObject('Select mesh', 32)\nif mesh:\n    if not rs.IsMeshClosed(mesh):\n        print('Mesh is not closed')\n    naked = rs.MeshNakedEdgePoints(mesh)\n    if naked:\n        print(f'Naked edges found: {{len(naked)}}')\n    rs.MeshWeldVertices(mesh, 0.01)",
         "medium", ["mesh", "repair", "check"]),
        ("Convert all surfaces to meshes with custom settings",
         f"{RS}\nsrfs = rs.ObjectsByType(8)\nif srfs:\n    for srf in srfs:\n        mesh = rs.MeshSurface(srf)\n        if mesh:\n            rs.ObjectLayer(mesh, rs.ObjectLayer(srf))\n    print(f'Converted {{len(srfs)}} surfaces')",
         "medium", ["mesh", "convert"]),
        ("Reduce mesh polygon count",
         f"{RC}\nimport Rhino\ngo = Rhino.Input.Custom.GetObject()\ngo.SetCommandPrompt('Select mesh')\ngo.GeometryFilter = Rhino.DocObjects.ObjectType.Mesh\ngo.Get()\nif go.CommandResult() == Rhino.Commands.Result.Success:\n    mesh = go.Object(0).Mesh()\n    params = rg.MeshReduceParameters()\n    params.DesiredPolygonCount = int(mesh.Faces.Count * 0.5)\n    reducer = rg.MeshReduce()\n    reduced = reducer.Reduce(mesh, params)\n    if reduced:\n        sc.doc.Objects.Replace(go.Object(0).ObjectId, reduced)\n        {REDRAW}",
         "hard", ["mesh", "reduce"]),
        ("Smooth a mesh by averaging vertex positions",
         f"{RC}\nimport Rhino\ngo = Rhino.Input.Custom.GetObject()\ngo.SetCommandPrompt('Select mesh')\ngo.GeometryFilter = Rhino.DocObjects.ObjectType.Mesh\ngo.Get()\nif go.CommandResult() == Rhino.Commands.Result.Success:\n    mesh = go.Object(0).Mesh()\n    rg.Mesh.Smooth(mesh, 0.5, True, True, True, True, rg.SmoothingCoordinateSystem.World, rg.Plane.WorldXY)\n    sc.doc.Objects.Replace(go.Object(0).ObjectId, mesh)\n    {REDRAW}",
         "hard", ["mesh", "smooth"]),
        ("Color mesh vertices by curvature",
         f"{RCM}\nimport System.Drawing as sd\nimport Rhino\ngo = Rhino.Input.Custom.GetObject()\ngo.SetCommandPrompt('Select mesh')\ngo.GeometryFilter = Rhino.DocObjects.ObjectType.Mesh\ngo.Get()\nif go.CommandResult() == Rhino.Commands.Result.Success:\n    mesh = go.Object(0).Mesh()\n    mesh.VertexColors.CreateMonotoneMesh(sd.Color.White)\n    for i in range(mesh.Vertices.Count):\n        nml = mesh.Normals[i]\n        angle = math.acos(max(-1, min(1, rg.Vector3f(0,0,1) * nml)))\n        t = angle / math.pi\n        r = int(255 * t)\n        b = int(255 * (1-t))\n        mesh.VertexColors[i] = sd.Color.FromArgb(r, 0, b)\n    sc.doc.Objects.Replace(go.Object(0).ObjectId, mesh)\n    {REDRAW}",
         "hard", ["mesh", "color", "curvature"]),
    ]
    for inst, code, diff, tags in mesh_cleanup:
        api = "RhinoCommon" if "rg." in code else "rhinoscriptsyntax"
        pairs.append(m(inst, code, diff, api, tags))

    # ═══════════════════════════════════════════════════════════
    # 4) UNROLLING workflows
    # ═══════════════════════════════════════════════════════════
    unroll_ops = [
        ("Unroll a selected surface for fabrication",
         f"{RS}\nsrf = rs.GetObject('Select surface', 8)\nif srf:\n    result = rs.UnrollSrf(srf, False)\n    if result:\n        print('Unrolled successfully')",
         "easy", ["unroll"]),
        ("Unroll a surface and add text labels at corners",
         f"{RS}\nsrf = rs.GetObject('Select surface', 8)\nif srf:\n    result = rs.UnrollSrf(srf, False)\n    if result:\n        for piece in result:\n            if rs.IsSurface(piece):\n                edges = rs.DuplicateEdgeCurves(piece)\n                for edge in edges:\n                    start = rs.CurveStartPoint(edge)\n                    rs.AddTextDot('*', start)",
         "medium", ["unroll", "labels"]),
        ("Unroll a polysurface into flat pieces",
         f"{RS}\nbrep = rs.GetObject('Select polysurface', 16)\nif brep:\n    exploded = rs.ExplodePolysurfaces(brep, False)\n    if exploded:\n        offset = 0\n        for piece in exploded:\n            flat = rs.UnrollSrf(piece, False)\n            if flat:\n                rs.MoveObjects(flat, (offset, -30, 0))\n                offset += 15",
         "hard", ["unroll", "polysurface"]),
        ("Unroll and add fold/tab lines for physical fabrication",
         f"{RS}\nsrf = rs.GetObject('Select surface', 8)\nif srf:\n    result = rs.UnrollSrf(srf, False)\n    if result:\n        for piece in result:\n            if rs.IsSurface(piece):\n                edges = rs.DuplicateEdgeCurves(piece)\n                for edge in edges:\n                    mid = rs.CurveMidPoint(edge)\n                    tan = rs.CurveTangent(edge, rs.CurveClosestPoint(edge, mid))\n                    if tan:\n                        perp = (-tan[1], tan[0], 0)\n                        rs.AddLine(mid, [mid[0]+perp[0]*2, mid[1]+perp[1]*2, mid[2]])",
         "hard", ["unroll", "fabrication", "tabs"]),
    ]
    for inst, code, diff, tags in unroll_ops:
        pairs.append(m(inst, code, diff, "rhinoscriptsyntax", tags))

    # ═══════════════════════════════════════════════════════════
    # 5) LOFTING workflows
    # ═══════════════════════════════════════════════════════════
    # Section-based lofting
    section_types = [
        ("circles", "rs.AddCircle((0,0,z), r)"),
        ("rectangles", "rs.AddRectangle(rs.MovePlane(rs.WorldXYPlane(),(0,0,z)), w, h)"),
        ("ellipses", "rs.AddEllipse(rs.MovePlane(rs.WorldXYPlane(),(0,0,z)), a, b)"),
    ]
    for shape_name, shape_code in section_types:
        for n_sections in [3, 5, 8]:
            pairs.append(m(
                f"Loft {n_sections} {shape_name} sections at increasing heights",
                f"{RS}\ncurves = []\nfor i in range({n_sections}):\n    z = i * 5\n    r = 5 + i * 0.5\n    w = r * 2\n    h = r * 1.5\n    a = r\n    b = r * 0.7\n    crv = {shape_code}\n    curves.append(crv)\nrs.AddLoftSrf(curves)",
                "medium", "rhinoscriptsyntax", ["loft", shape_name]))

    # Loft with twist
    pairs.append(m(
        "Create a twisted lofted surface from rotated rectangles",
        f"{RSM}\ncurves = []\nfor i in range(10):\n    z = i * 3\n    angle = math.radians(i * 15)\n    c = math.cos(angle)\n    s = math.sin(angle)\n    pts = []\n    for dx, dy in [(-3,-2),(3,-2),(3,2),(-3,2),(-3,-2)]:\n        rx = dx*c - dy*s\n        ry = dx*s + dy*c\n        pts.append((rx, ry, z))\n    curves.append(rs.AddPolyline(pts))\nrs.AddLoftSrf(curves)",
        "hard", "rhinoscriptsyntax", ["loft", "twist"]))

    # Loft and cap
    for cap in [True, False]:
        cap_desc = "and cap the ends" if cap else ""
        cap_code = "\nif srf:\n    rs.CapPlanarHoles(srf)" if cap else ""
        pairs.append(m(
            f"Loft between three circles at different heights {cap_desc}",
            f"{RS}\nc1 = rs.AddCircle((0,0,0), 8)\nc2 = rs.AddCircle((0,0,5), 6)\nc3 = rs.AddCircle((0,0,10), 4)\nsrf = rs.AddLoftSrf([c1, c2, c3]){cap_code}",
            "medium", "rhinoscriptsyntax", ["loft", "cap"] if cap else ["loft"]))

    # ═══════════════════════════════════════════════════════════
    # 6) SWEEPING workflows
    # ═══════════════════════════════════════════════════════════
    # 1-rail sweep
    profiles = [("circle", "rs.AddCircle(rs.MovePlane(rs.WorldXYPlane(),(0,0,0)), r)"),
                ("rectangle", "rs.AddRectangle(rs.WorldXYPlane(), w, h)"),
                ("triangle", "rs.AddPolyline([(0,0,0),(s,0,0),(s/2,s*0.866,0),(0,0,0)])")]
    rails = [("straight", "rs.AddLine((0,0,0),(0,0,20))"),
             ("arc", "rs.AddArc3Pt((0,0,0),(20,0,0),(10,5,0))"),
             ("curved", "rs.AddInterpCurve([(0,0,0),(5,0,5),(0,0,10),(-5,0,15),(0,0,20)])")]
    for prof_name, prof_code in profiles:
        for rail_name, rail_code in rails:
            pairs.append(m(
                f"Sweep a {prof_name} profile along a {rail_name} rail",
                f"{RS}\nr = 1\nw = 2\nh = 1\ns = 2\nprofile = {prof_code}\nrail = {rail_code}\nrs.AddSweep1(rail, [profile])",
                "medium", "rhinoscriptsyntax", ["sweep", prof_name, rail_name]))

    # 2-rail sweep
    pairs.extend([
        m("Sweep between two rails with a cross-section",
          f"{RS}\nrail1 = rs.AddLine((0,0,0),(20,0,0))\nrail2 = rs.AddLine((0,10,0),(20,10,5))\nprofile = rs.AddLine((0,0,0),(0,10,0))\nrs.AddSweep2([rail1, rail2], [profile])",
          "medium", "rhinoscriptsyntax", ["sweep2"]),
        m("Create a variable-width sweep between two curved rails",
          f"{RS}\nrail1 = rs.AddInterpCurve([(0,0,0),(10,0,3),(20,0,0)])\nrail2 = rs.AddInterpCurve([(0,5,0),(10,8,3),(20,5,0)])\nprofile = rs.AddLine((0,0,0),(0,5,0))\nrs.AddSweep2([rail1, rail2], [profile])",
          "hard", "rhinoscriptsyntax", ["sweep2", "variable"]),
    ])

    # Pipe variations
    for cap in [0, 1, 2]:
        cap_names = {0: "no caps", 1: "flat caps", 2: "round caps"}
        pairs.append(m(
            f"Create a pipe along a curve with {cap_names[cap]}",
            f"{RS}\ncrv = rs.GetObject('Select curve', 4)\nif crv:\n    rs.AddPipe(crv, 0, 2, cap={cap})",
            "easy", "rhinoscriptsyntax", ["pipe", "cap"]))

    # Variable radius pipe
    pairs.append(m(
        "Create a variable-radius pipe that tapers along the curve",
        f"{RS}\ncrv = rs.GetObject('Select curve', 4)\nif crv:\n    dom = rs.CurveDomain(crv)\n    params = [dom[0], (dom[0]+dom[1])/2, dom[1]]\n    radii = [3, 1.5, 0.5]\n    rs.AddPipe(crv, params, radii)",
        "hard", "rhinoscriptsyntax", ["pipe", "variable"]))

    # ═══════════════════════════════════════════════════════════
    # 7) ARRAYING workflows
    # ═══════════════════════════════════════════════════════════
    # Linear arrays
    for nx, ny, nz in [(5,1,1),(3,3,1),(2,2,3),(10,1,1),(1,5,1)]:
        for sp in [3, 5]:
            desc_parts = []
            if nx > 1: desc_parts.append(f"{nx} along X")
            if ny > 1: desc_parts.append(f"{ny} along Y")
            if nz > 1: desc_parts.append(f"{nz} along Z")
            desc = " and ".join(desc_parts)
            pairs.append(m(
                f"Array selected object {desc} with {sp}-unit spacing",
                f"{RS}\nobj = rs.GetObject('Select object')\nif obj:\n    for i in range({nx}):\n        for j in range({ny}):\n            for k in range({nz}):\n                if i == 0 and j == 0 and k == 0:\n                    continue\n                rs.CopyObject(obj, (i*{sp}, j*{sp}, k*{sp}))",
                "medium", "rhinoscriptsyntax", ["array", "linear"]))

    # Polar arrays
    for count in [4, 6, 8, 12, 24]:
        pairs.append(m(
            f"Create a polar array of {count} copies around the Z axis",
            f"{RS}\nobj = rs.GetObject('Select object')\nif obj:\n    for i in range(1, {count}):\n        copy = rs.CopyObject(obj)\n        rs.RotateObject(copy, (0,0,0), i * 360.0/{count})",
            "easy", "rhinoscriptsyntax", ["array", "polar"]))

    # Array along curve
    pairs.extend([
        m("Array an object along a curve at equal intervals",
          f"{RS}\nobj = rs.GetObject('Select object')\ncrv = rs.GetObject('Select curve', 4)\nif obj and crv:\n    pts = rs.DivideCurve(crv, 10)\n    origin = rs.BoundingBox(obj)\n    if origin and pts:\n        for pt in pts[1:]:\n            copy = rs.CopyObject(obj, [pt[i]-origin[0][i] for i in range(3)])",
          "hard", "rhinoscriptsyntax", ["array", "curve"]),
        m("Array objects along curve with orientation following tangent",
          f"{RSM}\nobj = rs.GetObject('Select object')\ncrv = rs.GetObject('Select curve', 4)\nif obj and crv:\n    params = rs.DivideCurve(crv, 15, False, True)\n    if params:\n        for t in params:\n            pt = rs.EvaluateCurve(crv, t)\n            tan = rs.CurveTangent(crv, t)\n            if pt and tan:\n                angle = math.degrees(math.atan2(tan[1], tan[0]))\n                copy = rs.CopyObject(obj, pt)\n                rs.RotateObject(copy, pt, angle)",
          "hard", "rhinoscriptsyntax", ["array", "curve", "orient"]),
    ])

    # ═══════════════════════════════════════════════════════════
    # 8) FILLET & CHAMFER workflows
    # ═══════════════════════════════════════════════════════════
    for radius in [0.5, 1.0, 2.0, 3.0]:
        pairs.append(m(
            f"Fillet two selected curves with radius {radius}",
            f"{RS}\nc1 = rs.GetObject('First curve', 4)\nc2 = rs.GetObject('Second curve', 4)\nif c1 and c2:\n    rs.FilletCurves(c1, c2, {radius})",
            "easy", "rhinoscriptsyntax", ["fillet", "curves"]))

    # Edge filleting
    pairs.extend([
        m("Fillet all edges of a selected brep",
          f"{RS}\nbrep = rs.GetObject('Select polysurface', 16)\nif brep:\n    edges = rs.GetEdgeCurves(brep)\n    if edges:\n        for edge in edges:\n            rs.FilletSrf(brep, edge[0], 0.5)",
          "hard", "rhinoscriptsyntax", ["fillet", "edges"]),
    ])

    # ═══════════════════════════════════════════════════════════
    # 9) OFFSET OPERATIONS
    # ═══════════════════════════════════════════════════════════
    for dist in [1, 2, 5]:
        pairs.append(m(
            f"Offset a selected curve by {dist} units",
            f"{RS}\ncrv = rs.GetObject('Select curve', 4)\nif crv:\n    direction = rs.GetPoint('Offset direction')\n    if direction:\n        result = rs.OffsetCurve(crv, direction, {dist})\n        if result:\n            print('Offset created')",
            "easy", "rhinoscriptsyntax", ["offset", "curve"]))

    for dist in [1, 2, 3]:
        pairs.append(m(
            f"Offset a surface by {dist} units in its normal direction",
            f"{RS}\nsrf = rs.GetObject('Select surface', 8)\nif srf:\n    result = rs.OffsetSurface(srf, {dist})\n    if result:\n        print('Surface offset created')",
            "easy", "rhinoscriptsyntax", ["offset", "surface"]))

    # ═══════════════════════════════════════════════════════════
    # 10) SECTION CUTTING
    # ═══════════════════════════════════════════════════════════
    pairs.extend([
        m("Cut sections through a brep at regular intervals along Z",
          f"{RS}\nbrep = rs.GetObject('Select solid', 16)\nif brep:\n    bb = rs.BoundingBox(brep)\n    if bb:\n        z_min = bb[0][2]\n        z_max = bb[4][2]\n        interval = (z_max - z_min) / 10\n        for i in range(11):\n            z = z_min + i * interval\n            plane = rs.WorldXYPlane()\n            plane = rs.MovePlane(plane, (0, 0, z))\n            sections = rs.AddPlaneSurface(plane, 100, 100)\n            if sections:\n                result = rs.IntersectBreps(brep, sections)\n                rs.DeleteObject(sections)",
          "hard", "rhinoscriptsyntax", ["section", "cutting"]),
        m("Generate contour lines on a surface at height intervals",
          f"{RS}\nsrf = rs.GetObject('Select surface', 8)\nif srf:\n    bb = rs.BoundingBox(srf)\n    if bb:\n        z_min = bb[0][2]\n        z_max = bb[4][2]\n        n = 10\n        for i in range(n + 1):\n            z = z_min + (z_max - z_min) * i / n\n            contours = rs.AddSrfContourCrvs(srf, (0,0,z), (0,0,z+0.01))\n            if contours:\n                for c in contours:\n                    rs.ObjectColor(c, (0, int(255*i/n), int(255*(1-i/n))))",
          "hard", "rhinoscriptsyntax", ["contour", "section"]),
    ])

    # ═══════════════════════════════════════════════════════════
    # 11) RhinoCommon design workflows
    # ═══════════════════════════════════════════════════════════
    rc_workflows = [
        ("Create a parametric wavy wall using RhinoCommon",
         f"{RCM}\npts1 = []\npts2 = []\nfor i in range(40):\n    x = i * 0.5\n    y = 3 * math.sin(x * 0.5)\n    pts1.append(rg.Point3d(x, y, 0))\n    pts2.append(rg.Point3d(x, y, 10))\nc1 = rg.Curve.CreateInterpolatedCurve(pts1, 3)\nc2 = rg.Curve.CreateInterpolatedCurve(pts2, 3)\nlofts = rg.Brep.CreateFromLoft([c1, c2], rg.Point3d.Unset, rg.Point3d.Unset, rg.LoftType.Normal, False)\nfor loft in lofts:\n    sc.doc.Objects.AddBrep(loft)\n{REDRAW}",
         "hard", "RhinoCommon", ["wall", "wavy", "loft"]),
        ("Create a mesh terrain from random height values",
         f"{RCM}\nimport random\nrandom.seed(42)\nn = 30\nmesh = rg.Mesh()\nfor i in range(n):\n    for j in range(n):\n        z = random.uniform(0, 5)\n        mesh.Vertices.Add(i, j, z)\nfor i in range(n-1):\n    for j in range(n-1):\n        a = i*n+j\n        mesh.Faces.AddFace(a, a+1, a+n+1, a+n)\nmesh.Normals.ComputeNormals()\nsc.doc.Objects.AddMesh(mesh)\n{REDRAW}",
         "hard", "RhinoCommon", ["mesh", "terrain"]),
        ("Create a tubular structure from a series of circles along a path",
         f"{RCM}\npath_pts = [rg.Point3d(0,0,0), rg.Point3d(5,0,3), rg.Point3d(10,0,0), rg.Point3d(15,0,4), rg.Point3d(20,0,0)]\npath = rg.Curve.CreateInterpolatedCurve(path_pts, 3)\nparams = path.DivideByCount(20, True)\ncircles = []\nfor t in params:\n    pt = path.PointAt(t)\n    success, frame = path.PerpendicularFrameAt(t)\n    if success:\n        circle = rg.Circle(frame, 1.5)\n        circles.append(circle.ToNurbsCurve())\nlofts = rg.Brep.CreateFromLoft(circles, rg.Point3d.Unset, rg.Point3d.Unset, rg.LoftType.Normal, False)\nfor loft in lofts:\n    sc.doc.Objects.AddBrep(loft)\n{REDRAW}",
         "hard", "RhinoCommon", ["tube", "loft", "path"]),
    ]
    for inst, code, diff, api, tags in rc_workflows:
        pairs.append(m(inst, code, diff, api, tags))

    return pairs
