"""Realistic 'how do I...' user question pairs (~500+)."""

def m(instruction, code, difficulty, api, tags):
    return {"instruction": instruction, "code": code, "source": "synthetic",
            "category": "how_do_i_questions", "difficulty": difficulty, "api": api, "tags": tags}

RS = "import rhinoscriptsyntax as rs"
RC = "import Rhino.Geometry as rg\nimport scriptcontext as sc"
RCM = "import Rhino.Geometry as rg\nimport scriptcontext as sc\nimport math"
REDRAW = "sc.doc.Views.Redraw()"

def generate():
    pairs = []

    # ── 1) Curve queries (rs) ──
    curve_queries = [
        ("find the length of a curve", "print('Length:', rs.CurveLength(crv))", ["length"]),
        ("get the midpoint of a curve", "print('Midpoint:', rs.CurveMidPoint(crv))", ["midpoint"]),
        ("get the start point of a curve", "print('Start:', rs.CurveStartPoint(crv))", ["startpoint"]),
        ("get the end point of a curve", "print('End:', rs.CurveEndPoint(crv))", ["endpoint"]),
        ("check if a curve is closed", "print('Closed:', rs.IsCurveClosed(crv))", ["closed"]),
        ("check if a curve is planar", "print('Planar:', rs.IsCurvePlanar(crv))", ["planar"]),
        ("get the degree of a curve", "print('Degree:', rs.CurveDegree(crv))", ["degree"]),
        ("get the domain of a curve", "dom = rs.CurveDomain(crv)\nprint('Domain:', dom)", ["domain"]),
        ("find the tangent at a curve midpoint", "dom = rs.CurveDomain(crv)\nt = (dom[0]+dom[1])/2\nprint('Tangent:', rs.CurveTangent(crv, t))", ["tangent"]),
        ("evaluate a point at parameter 0.5 on a curve", "dom = rs.CurveDomain(crv)\nt = (dom[0]+dom[1])/2\nprint('Point:', rs.EvaluateCurve(crv, t))", ["evaluate"]),
        ("get the curvature at the midpoint of a curve", "dom = rs.CurveDomain(crv)\nt = (dom[0]+dom[1])/2\nprint('Curvature:', rs.CurveCurvature(crv, t))", ["curvature"]),
        ("count the control points of a curve", "pts = rs.CurvePoints(crv)\nprint('Control points:', len(pts))", ["controlpoints"]),
        ("get the edit points of a curve", "pts = rs.CurveEditPoints(crv)\nfor pt in pts:\n    rs.AddPoint(pt)", ["editpoints"]),
        ("find the closest point on a curve to (5,5,0)", "t = rs.CurveClosestPoint(crv, (5,5,0))\npt = rs.EvaluateCurve(crv, t)\nprint('Closest:', pt)", ["closestpoint"]),
        ("divide a curve into 10 equal parts", "pts = rs.DivideCurve(crv, 10)\nfor pt in pts:\n    rs.AddPoint(pt)", ["divide"]),
        ("divide a curve by length of 2.0", "pts = rs.DivideCurveLength(crv, 2.0)\nif pts:\n    for pt in pts:\n        rs.AddPoint(pt)", ["divide", "length"]),
        ("reverse the direction of a curve", "rs.ReverseCurve(crv)\nprint('Curve reversed')", ["reverse"]),
        ("rebuild a curve to degree 3 with 10 control points", "rs.RebuildCurve(crv, 3, 10)\nprint('Curve rebuilt')", ["rebuild"]),
        ("check the area enclosed by a closed curve", "area = rs.CurveAreaCentroid(crv)\nif area:\n    print('Area:', area[0])", ["area"]),
        ("get the weight of a NURBS curve control point", "w = rs.CurveWeights(crv)\nif w:\n    print('Weights:', w)", ["weights"]),
    ]
    # Generate with varied phrasing
    phrasings = [
        "How do I {desc}?",
        "What's the best way to {desc}?",
        "How can I {desc} in Rhino Python?",
        "I need to {desc}",
    ]
    for desc, body, tags in curve_queries:
        for i, phr in enumerate(phrasings):
            code = f"{RS}\ncrv = rs.GetObject('Select curve', 4)\nif crv:\n    {body}"
            pairs.append(m(phr.format(desc=desc), code, "easy", "rhinoscriptsyntax", ["curve"] + tags))

    # ── 2) Surface queries (rs) ──
    surface_queries = [
        ("get the area of a surface", "amp = rs.SurfaceArea(srf)\nif amp:\n    print('Area:', amp[0])", ["area"]),
        ("evaluate a point on a surface at UV (0.5, 0.5)", "u_dom = rs.SurfaceDomain(srf, 0)\nv_dom = rs.SurfaceDomain(srf, 1)\nu = (u_dom[0]+u_dom[1])/2\nv = (v_dom[0]+v_dom[1])/2\npt = rs.EvaluateSurface(srf, u, v)\nrs.AddPoint(pt)", ["evaluate", "uv"]),
        ("get the normal of a surface at its center", "u_dom = rs.SurfaceDomain(srf, 0)\nv_dom = rs.SurfaceDomain(srf, 1)\nu = (u_dom[0]+u_dom[1])/2\nv = (v_dom[0]+v_dom[1])/2\nnml = rs.SurfaceNormal(srf, (u,v))\nprint('Normal:', nml)", ["normal"]),
        ("get the domain of a surface in U and V", "u_dom = rs.SurfaceDomain(srf, 0)\nv_dom = rs.SurfaceDomain(srf, 1)\nprint('U:', u_dom, 'V:', v_dom)", ["domain"]),
        ("check if a surface is planar", "print('Planar:', rs.IsSurfacePlanar(srf))", ["planar"]),
        ("find the closest point on a surface to (5,5,5)", "param = rs.SurfaceClosestPoint(srf, (5,5,5))\npt = rs.EvaluateSurface(srf, param[0], param[1])\nprint('Closest:', pt)", ["closestpoint"]),
        ("extract the isocurves of a surface", "u_dom = rs.SurfaceDomain(srf, 0)\nfor i in range(5):\n    u = u_dom[0] + (u_dom[1]-u_dom[0]) * i / 4\n    crv = rs.ExtractIsoCurve(srf, (u, 0), 1)\n    if crv:\n        print('Extracted isocurve at u =', u)", ["isocurve"]),
        ("check the degree of a surface", "deg_u = rs.SurfaceDegree(srf, 0)\ndeg_v = rs.SurfaceDegree(srf, 1)\nprint('Degrees:', deg_u, deg_v)", ["degree"]),
        ("get the volume of a closed polysurface", "vol = rs.SurfaceVolume(srf)\nif vol:\n    print('Volume:', vol[0])", ["volume"]),
        ("convert a surface to a mesh", "mesh = rs.MeshSurface(srf)\nprint('Meshed:', mesh)", ["mesh", "convert"]),
        ("rebuild a surface with new point counts", "rs.RebuildSurface(srf, (3,3), (10,10))\nprint('Surface rebuilt')", ["rebuild"]),
        ("offset a surface by 2 units", "off = rs.OffsetSurface(srf, 2.0)\nprint('Offset:', off)", ["offset"]),
        ("trim a surface with a curve", "crv = rs.GetObject('Select trim curve', 4)\nif crv:\n    rs.TrimSurface(srf, 1)", ["trim"]),
        ("extract the edges of a surface", "edges = rs.DuplicateEdgeCurves(srf)\nprint('Edges:', len(edges))", ["edges"]),
        ("check if a surface is trimmed", "print('Trimmed:', rs.IsSurfaceTrimmed(srf))", ["trimmed"]),
    ]
    for desc, body, tags in surface_queries:
        for i, phr in enumerate(phrasings[:3]):
            code = f"{RS}\nsrf = rs.GetObject('Select surface', 8)\nif srf:\n    {body}"
            pairs.append(m(phr.format(desc=desc), code, "medium", "rhinoscriptsyntax", ["surface"] + tags))

    # ── 3) Mesh queries (rs) ──
    mesh_queries = [
        ("get the vertex count of a mesh", "verts = rs.MeshVertices(mesh)\nprint('Vertices:', len(verts))", ["vertices"]),
        ("get the face count of a mesh", "faces = rs.MeshFaces(mesh, False)\nprint('Faces:', len(faces)//4)", ["faces"]),
        ("get the face normals of a mesh", "normals = rs.MeshFaceNormals(mesh)\nprint('Normals:', len(normals))", ["normals"]),
        ("check if a mesh is closed", "print('Closed:', rs.IsMeshClosed(mesh))", ["closed"]),
        ("weld the vertices of a mesh", "rs.MeshWeldVertices(mesh, 0.01)\nprint('Mesh welded')", ["weld"]),
        ("unweld a mesh at angle threshold 20 degrees", "rs.UnweldMesh(mesh, 20)\nprint('Mesh unwelded')", ["unweld"]),
        ("get the bounding box of a mesh", "bb = rs.BoundingBox(mesh)\nif bb:\n    print('Min:', bb[0], 'Max:', bb[6])", ["boundingbox"]),
        ("flip all mesh normals", "rs.FlipMeshNormals(mesh)\nprint('Normals flipped')", ["flip", "normals"]),
        ("get the area of a mesh", "area = rs.MeshArea([mesh])\nif area:\n    print('Area:', area[1])", ["area"]),
        ("get the volume of a closed mesh", "vol = rs.MeshVolume([mesh])\nif vol:\n    print('Volume:', vol[1])", ["volume"]),
    ]
    for desc, body, tags in mesh_queries:
        for phr in phrasings[:3]:
            code = f"{RS}\nmesh = rs.GetObject('Select mesh', 32)\nif mesh:\n    {body}"
            pairs.append(m(phr.format(desc=desc), code, "easy", "rhinoscriptsyntax", ["mesh"] + tags))

    # ── 4) Object property questions (rs) ──
    prop_queries = [
        ("get the name of an object", "name = rs.ObjectName(obj)\nprint('Name:', name)", ["name"]),
        ("set the name of an object", "rs.ObjectName(obj, 'MyObject')\nprint('Name set')", ["name", "set"]),
        ("get the layer of an object", "layer = rs.ObjectLayer(obj)\nprint('Layer:', layer)", ["layer"]),
        ("move an object to a different layer", "rs.ObjectLayer(obj, 'NewLayer')", ["layer", "move"]),
        ("change the color of an object to red", "rs.ObjectColor(obj, (255, 0, 0))", ["color"]),
        ("get the color of an object", "color = rs.ObjectColor(obj)\nprint('Color:', color)", ["color", "get"]),
        ("lock an object so it can't be moved", "rs.LockObject(obj)\nprint('Object locked')", ["lock"]),
        ("unlock a locked object", "rs.UnlockObject(obj)\nprint('Object unlocked')", ["unlock"]),
        ("hide an object", "rs.HideObject(obj)\nprint('Object hidden')", ["hide"]),
        ("show a hidden object", "rs.ShowObject(obj)\nprint('Object shown')", ["show"]),
        ("check the type of an object", "otype = rs.ObjectType(obj)\nprint('Type:', otype)", ["type"]),
        ("copy an object to a new location", "copy = rs.CopyObject(obj, (10,0,0))\nprint('Copied:', copy)", ["copy"]),
        ("delete an object", "rs.DeleteObject(obj)\nprint('Deleted')", ["delete"]),
        ("get the material index of an object", "idx = rs.ObjectMaterialIndex(obj)\nprint('Material:', idx)", ["material"]),
        ("assign a material to an object", "idx = rs.AddMaterialToObject(obj)\nprint('Material assigned:', idx)", ["material", "assign"]),
    ]
    for desc, body, tags in prop_queries:
        for phr in phrasings[:2]:
            code = f"{RS}\nobj = rs.GetObject('Select object')\nif obj:\n    {body}"
            pairs.append(m(phr.format(desc=desc), code, "easy", "rhinoscriptsyntax", ["property"] + tags))

    # ── 5) Layer management (rs) ──
    layer_queries = [
        ("How do I create a new layer?", f"{RS}\nrs.AddLayer('NewLayer')", ["create"]),
        ("How do I create a layer with a specific color?", f"{RS}\nrs.AddLayer('RedLayer', (255,0,0))", ["create", "color"]),
        ("How do I delete a layer?", f"{RS}\nrs.DeleteLayer('OldLayer')", ["delete"]),
        ("How do I rename a layer?", f"{RS}\nrs.RenameLayer('OldName', 'NewName')", ["rename"]),
        ("How do I turn off a layer?", f"{RS}\nrs.LayerVisible('MyLayer', False)", ["visibility"]),
        ("How do I turn on a layer?", f"{RS}\nrs.LayerVisible('MyLayer', True)", ["visibility"]),
        ("How do I lock a layer?", f"{RS}\nrs.LayerLocked('MyLayer', True)", ["lock"]),
        ("How do I get all layer names?", f"{RS}\nlayers = rs.LayerNames()\nfor l in layers:\n    print(l)", ["list"]),
        ("How do I check if a layer exists?", f"{RS}\nprint(rs.IsLayer('MyLayer'))", ["exists"]),
        ("How do I set the current layer?", f"{RS}\nrs.CurrentLayer('MyLayer')", ["current"]),
        ("How do I get the color of a layer?", f"{RS}\ncolor = rs.LayerColor('MyLayer')\nprint('Color:', color)", ["color", "get"]),
        ("How do I change a layer's color?", f"{RS}\nrs.LayerColor('MyLayer', (0, 128, 255))", ["color", "set"]),
        ("How do I get all objects on a specific layer?", f"{RS}\nobjs = rs.ObjectsByLayer('MyLayer')\nprint('Objects:', len(objs) if objs else 0)", ["objects"]),
        ("How do I move all objects from one layer to another?", f"{RS}\nobjs = rs.ObjectsByLayer('OldLayer')\nif objs:\n    for obj in objs:\n        rs.ObjectLayer(obj, 'NewLayer')", ["move", "objects"]),
        ("How do I create nested sublayers?", f"{RS}\nrs.AddLayer('Parent')\nrs.AddLayer('Parent::Child')", ["sublayer", "nested"]),
        ("How do I purge empty layers?", f"{RS}\nfor layer in rs.LayerNames():\n    objs = rs.ObjectsByLayer(layer)\n    if not objs or len(objs) == 0:\n        if layer != rs.CurrentLayer():\n            rs.DeleteLayer(layer)", ["purge"]),
    ]
    for inst, code, tags in layer_queries:
        pairs.append(m(inst, code, "easy", "rhinoscriptsyntax", ["layer"] + tags))

    # ── 6) Selection & filtering (rs) ──
    selection_queries = [
        ("How do I select all curves in the document?", f"{RS}\ncurves = rs.ObjectsByType(4)\nif curves:\n    rs.SelectObjects(curves)\n    print('Selected', len(curves), 'curves')", ["select", "curves"]),
        ("How do I select all objects on a layer?", f"{RS}\nobjs = rs.ObjectsByLayer('MyLayer')\nif objs:\n    rs.SelectObjects(objs)", ["select", "layer"]),
        ("How do I select objects by name?", f"{RS}\nobjs = rs.ObjectsByName('Part*')\nif objs:\n    rs.SelectObjects(objs)", ["select", "name"]),
        ("How do I select all surfaces?", f"{RS}\nsurfaces = rs.ObjectsByType(8)\nif surfaces:\n    rs.SelectObjects(surfaces)\n    print('Selected', len(surfaces), 'surfaces')", ["select", "surfaces"]),
        ("How do I select all meshes?", f"{RS}\nmeshes = rs.ObjectsByType(32)\nif meshes:\n    rs.SelectObjects(meshes)\n    print('Selected', len(meshes), 'meshes')", ["select", "meshes"]),
        ("How do I filter selected objects by type?", f"{RS}\nobjs = rs.GetObjects('Select objects')\nif objs:\n    curves = [o for o in objs if rs.IsCurve(o)]\n    surfaces = [o for o in objs if rs.IsSurface(o)]\n    print('Curves:', len(curves), 'Surfaces:', len(surfaces))", ["filter", "type"]),
        ("How do I select all points?", f"{RS}\npoints = rs.ObjectsByType(1)\nif points:\n    rs.SelectObjects(points)", ["select", "points"]),
        ("How do I deselect all objects?", f"{RS}\nrs.UnselectAllObjects()", ["deselect"]),
        ("How do I get currently selected objects?", f"{RS}\nobjs = rs.SelectedObjects()\nprint('Selected:', len(objs) if objs else 0)", ["selected", "get"]),
        ("How do I select objects by color?", f"{RS}\nobjs = rs.AllObjects()\nif objs:\n    red = [o for o in objs if rs.ObjectColor(o) == (255,0,0,255)]\n    if red:\n        rs.SelectObjects(red)", ["select", "color"]),
    ]
    for inst, code, tags in selection_queries:
        pairs.append(m(inst, code, "easy", "rhinoscriptsyntax", tags))

    # ── 7) Transform questions (rs) ──
    transform_queries = [
        ("How do I move an object by a vector?", f"{RS}\nobj = rs.GetObject('Select object')\nif obj:\n    rs.MoveObject(obj, (10, 5, 0))", ["move"]),
        ("How do I rotate an object around a point?", f"{RS}\nobj = rs.GetObject('Select object')\nif obj:\n    rs.RotateObject(obj, (0,0,0), 45)", ["rotate"]),
        ("How do I scale an object uniformly?", f"{RS}\nobj = rs.GetObject('Select object')\nif obj:\n    rs.ScaleObject(obj, (0,0,0), (2,2,2))", ["scale"]),
        ("How do I scale an object non-uniformly?", f"{RS}\nobj = rs.GetObject('Select object')\nif obj:\n    rs.ScaleObject(obj, (0,0,0), (2,1,0.5))", ["scale", "nonuniform"]),
        ("How do I mirror an object across a plane?", f"{RS}\nobj = rs.GetObject('Select object')\nif obj:\n    rs.MirrorObject(obj, (0,0,0), (0,1,0), True)", ["mirror"]),
        ("How do I orient an object from one plane to another?", f"{RS}\nobj = rs.GetObject('Select object')\nif obj:\n    p1 = rs.GetPoint('From point')\n    p2 = rs.GetPoint('To point')\n    if p1 and p2:\n        rs.OrientObject(obj, [p1], [p2])", ["orient"]),
        ("How do I move objects to the origin?", f"{RS}\nobj = rs.GetObject('Select object')\nif obj:\n    bb = rs.BoundingBox(obj)\n    if bb:\n        center = [(bb[0][i]+bb[6][i])/2 for i in range(3)]\n        rs.MoveObject(obj, [-c for c in center])", ["move", "origin"]),
        ("How do I rotate an object around an arbitrary axis?", f"{RS}\nobj = rs.GetObject('Select object')\nif obj:\n    rs.RotateObject(obj, (0,0,0), 45, (0,0,1))", ["rotate", "axis"]),
        ("How do I project a curve onto a surface?", f"{RS}\ncrv = rs.GetObject('Select curve', 4)\nsrf = rs.GetObject('Select surface', 8)\nif crv and srf:\n    projected = rs.ProjectCurveToSurface(crv, srf, (0,0,-1))\n    if projected:\n        print('Projected', len(projected), 'curves')", ["project", "curve", "surface"]),
        ("How do I create a linear array of an object?", f"{RS}\nobj = rs.GetObject('Select object')\nif obj:\n    for i in range(1, 10):\n        rs.CopyObject(obj, (i*5, 0, 0))", ["array", "linear"]),
        ("How do I create a polar array?", f"{RS}\nimport math\nobj = rs.GetObject('Select object')\nif obj:\n    for i in range(1, 8):\n        copy = rs.CopyObject(obj)\n        rs.RotateObject(copy, (0,0,0), i*360.0/8)", ["array", "polar"]),
    ]
    for inst, code, tags in transform_queries:
        pairs.append(m(inst, code, "easy", "rhinoscriptsyntax", ["transform"] + tags))

    # ── 8) Creation questions with varied phrasing ──
    creation_questions = [
        ("create a sphere at a specific point", f"{RS}\npt = rs.GetPoint('Pick center')\nif pt:\n    radius = rs.GetReal('Enter radius', 5)\n    if radius:\n        rs.AddSphere(pt, radius)", "easy", ["sphere", "create"]),
        ("draw a line between two picked points", f"{RS}\np1 = rs.GetPoint('Start')\nif p1:\n    p2 = rs.GetPoint('End')\n    if p2:\n        rs.AddLine(p1, p2)", "easy", ["line", "create"]),
        ("create a box with specific dimensions", f"{RS}\nw = rs.GetReal('Width', 10)\nh = rs.GetReal('Height', 10)\nd = rs.GetReal('Depth', 10)\nif w and h and d:\n    corners = [(0,0,0),(w,0,0),(w,d,0),(0,d,0),(0,0,h),(w,0,h),(w,d,h),(0,d,h)]\n    rs.AddBox(corners)", "easy", ["box", "create"]),
        ("create a cylinder at a picked point", f"{RS}\npt = rs.GetPoint('Pick base center')\nif pt:\n    r = rs.GetReal('Radius', 3)\n    h = rs.GetReal('Height', 10)\n    if r and h:\n        rs.AddCylinder(pt, h, r)", "easy", ["cylinder", "create"]),
        ("create a cone", f"{RS}\nbase = rs.GetPoint('Base center')\nif base:\n    rs.AddCone(base, 10, 5)", "easy", ["cone", "create"]),
        ("create a torus", f"{RC}\ntorus = rg.Torus(rg.Plane.WorldXY, 10, 3)\nmesh = rg.Mesh.CreateFromSphere(rg.Sphere(rg.Point3d.Origin, 1), 10, 10)\nbrep = torus.ToRevSurface().ToBrep()\nsc.doc.Objects.AddBrep(brep)\n{REDRAW}", "medium", ["torus", "create"]),
        ("add text to the document", f"{RS}\npt = rs.GetPoint('Pick text location')\nif pt:\n    rs.AddText('Hello Rhino', pt, 2.0)", "easy", ["text", "create"]),
        ("create a text dot", f"{RS}\npt = rs.GetPoint('Pick location')\nif pt:\n    rs.AddTextDot('Label', pt)", "easy", ["textdot", "create"]),
        ("create a surface from 4 corner points", f"{RS}\nrs.AddSrfPt([(0,0,0),(10,0,0),(10,10,3),(0,10,3)])", "easy", ["surface", "create"]),
        ("create a planar surface from a boundary curve", f"{RS}\ncrv = rs.GetObject('Select closed planar curve', 4)\nif crv:\n    srf = rs.AddPlanarSrf([crv])\n    if srf:\n        print('Surface created')", "easy", ["surface", "planar", "create"]),
        ("create a pipe along a curve", f"{RS}\ncrv = rs.GetObject('Select rail curve', 4)\nif crv:\n    radius = rs.GetReal('Pipe radius', 1.0)\n    if radius:\n        rs.AddPipe(crv, 0, radius)", "easy", ["pipe", "create"]),
        ("create a lofted surface from multiple curves", f"{RS}\ncrvs = rs.GetObjects('Select section curves', 4)\nif crvs and len(crvs) >= 2:\n    rs.AddLoftSrf(crvs)", "medium", ["loft", "create"]),
    ]
    for desc, code, diff, tags in creation_questions:
        for phr in phrasings[:3]:
            pairs.append(m(phr.format(desc=desc), code, diff, "rhinoscriptsyntax" if "rs." in code else "RhinoCommon", tags))

    # ── 9) RhinoCommon-specific questions ──
    rc_questions = [
        ("How do I create a Point3d in RhinoCommon?", f"{RC}\npt = rg.Point3d(5.0, 10.0, 3.0)\nsc.doc.Objects.AddPoint(pt)\n{REDRAW}", "easy", ["point", "create"]),
        ("How do I compute the distance between two points in RhinoCommon?", f"{RC}\np1 = rg.Point3d(0,0,0)\np2 = rg.Point3d(3,4,0)\nprint('Distance:', p1.DistanceTo(p2))", "easy", ["distance", "point"]),
        ("How do I create a vector and unitize it?", f"{RC}\nvec = rg.Vector3d(3, 4, 0)\nvec.Unitize()\nprint('Unit vector:', vec)", "easy", ["vector", "unitize"]),
        ("How do I create a plane from origin and normal?", f"{RC}\nplane = rg.Plane(rg.Point3d(0,0,5), rg.Vector3d(0,0,1))\nprint('Plane origin:', plane.Origin)", "easy", ["plane"]),
        ("How do I create a bounding box around objects?", f"{RC}\nimport Rhino\ngo = Rhino.Input.Custom.GetObject()\ngo.SetCommandPrompt('Select objects')\ngo.GetMultiple(1, 0)\nif go.CommandResult() == Rhino.Commands.Result.Success:\n    bbox = rg.BoundingBox.Empty\n    for i in range(go.ObjectCount):\n        geo = go.Object(i).Geometry()\n        bbox.Union(geo.GetBoundingBox(True))\n    print('Min:', bbox.Min, 'Max:', bbox.Max)", "medium", ["boundingbox"]),
        ("How do I add a circle and get its GUID?", f"{RC}\ncircle = rg.Circle(rg.Plane.WorldXY, 5)\nguid = sc.doc.Objects.AddCircle(circle)\n{REDRAW}\nprint('GUID:', guid)", "easy", ["circle", "guid"]),
        ("How do I transform objects in RhinoCommon?", f"{RCM}\nimport Rhino\ngo = Rhino.Input.Custom.GetObject()\ngo.SetCommandPrompt('Select object')\ngo.Get()\nif go.CommandResult() == Rhino.Commands.Result.Success:\n    objref = go.Object(0)\n    xform = rg.Transform.Translation(rg.Vector3d(10,0,0))\n    sc.doc.Objects.Transform(objref, xform, True)\n    {REDRAW}", "medium", ["transform"]),
        ("How do I compute the intersection of two curves?", f"{RC}\nimport Rhino\ngo = Rhino.Input.Custom.GetObject()\ngo.SetCommandPrompt('Select two curves')\ngo.GeometryFilter = Rhino.DocObjects.ObjectType.Curve\ngo.GetMultiple(2, 2)\nif go.CommandResult() == Rhino.Commands.Result.Success:\n    c1 = go.Object(0).Curve()\n    c2 = go.Object(1).Curve()\n    events = rg.Intersect.Intersection.CurveCurve(c1, c2, 0.001, 0.001)\n    for e in events:\n        sc.doc.Objects.AddPoint(e.PointA)\n    {REDRAW}", "hard", ["intersection", "curves"]),
        ("How do I get the area of a Brep?", f"{RC}\nimport Rhino\ngo = Rhino.Input.Custom.GetObject()\ngo.SetCommandPrompt('Select surface')\ngo.GeometryFilter = Rhino.DocObjects.ObjectType.Brep\ngo.Get()\nif go.CommandResult() == Rhino.Commands.Result.Success:\n    brep = go.Object(0).Brep()\n    amp = rg.AreaMassProperties.Compute(brep)\n    if amp:\n        print('Area:', amp.Area)", "medium", ["area", "brep"]),
        ("How do I find the centroid of a closed curve?", f"{RC}\nimport Rhino\ngo = Rhino.Input.Custom.GetObject()\ngo.SetCommandPrompt('Select closed curve')\ngo.GeometryFilter = Rhino.DocObjects.ObjectType.Curve\ngo.Get()\nif go.CommandResult() == Rhino.Commands.Result.Success:\n    crv = go.Object(0).Curve()\n    amp = rg.AreaMassProperties.Compute(crv)\n    if amp:\n        sc.doc.Objects.AddPoint(amp.Centroid)\n        {REDRAW}", "medium", ["centroid", "curve"]),
        ("How do I access object attributes like name and layer?", f"{RC}\nimport Rhino\ngo = Rhino.Input.Custom.GetObject()\ngo.SetCommandPrompt('Select object')\ngo.Get()\nif go.CommandResult() == Rhino.Commands.Result.Success:\n    obj = go.Object(0).Object()\n    attrs = obj.Attributes\n    print('Name:', attrs.Name)\n    print('Layer:', sc.doc.Layers[attrs.LayerIndex].Name)", "medium", ["attributes", "name", "layer"]),
    ]
    for inst, code, diff, tags in rc_questions:
        pairs.append(m(inst, code, diff, "RhinoCommon", tags))

    # ── 10) Import/Export questions (rs) ──
    io_queries = [
        ("How do I export selected objects to a file?", f"{RS}\nobjs = rs.GetObjects('Select objects to export')\nif objs:\n    rs.SelectObjects(objs)\n    rs.Command('-Export \"output.3dm\" Enter')", ["export"]),
        ("How do I import a file into the current document?", f"{RS}\nrs.Command('-Import \"model.3dm\" Enter')", ["import"]),
        ("How do I save the current file?", f"{RS}\nrs.Command('-Save')", ["save"]),
        ("How do I export to STL format?", f"{RS}\nobjs = rs.GetObjects('Select meshes', 32)\nif objs:\n    rs.SelectObjects(objs)\n    rs.Command('-Export \"output.stl\" Enter')", ["export", "stl"]),
        ("How do I change the document units to millimeters?", f"{RS}\nrs.UnitSystem(2)", ["units"]),
        ("How do I get the current unit system?", f"{RS}\nunit = rs.UnitSystem()\nprint('Unit system:', unit)", ["units", "get"]),
        ("How do I export to DXF?", f"{RS}\nrs.Command('-Export \"output.dxf\" Enter')", ["export", "dxf"]),
    ]
    for inst, code, tags in io_queries:
        pairs.append(m(inst, code, "easy", "rhinoscriptsyntax", ["io"] + tags))

    # ── 11) Group operations ──
    group_queries = [
        ("How do I group objects together?", f"{RS}\nobjs = rs.GetObjects('Select objects to group')\nif objs:\n    grp = rs.AddGroup()\n    rs.AddObjectsToGroup(objs, grp)", ["group", "create"]),
        ("How do I ungroup objects?", f"{RS}\nobj = rs.GetObject('Select grouped object')\nif obj:\n    groups = rs.ObjectGroups(obj)\n    if groups:\n        rs.DeleteGroup(groups[0])", ["group", "delete"]),
        ("How do I get all groups in the document?", f"{RS}\ngroups = rs.GroupNames()\nif groups:\n    for g in groups:\n        print(g)", ["group", "list"]),
        ("How do I select all objects in a group?", f"{RS}\nobj = rs.GetObject('Select one object from group')\nif obj:\n    groups = rs.ObjectGroups(obj)\n    if groups:\n        members = rs.ObjectsByGroup(groups[0])\n        rs.SelectObjects(members)", ["group", "select"]),
    ]
    for inst, code, tags in group_queries:
        pairs.append(m(inst, code, "easy", "rhinoscriptsyntax", tags))

    # ── 12) User input questions ──
    input_queries = [
        ("How do I ask the user to pick a point?", f"{RS}\npt = rs.GetPoint('Click a point')\nif pt:\n    print('Point:', pt)", ["getpoint"]),
        ("How do I ask the user for a number?", f"{RS}\nval = rs.GetReal('Enter a value', 5.0)\nif val is not None:\n    print('Value:', val)", ["getreal"]),
        ("How do I ask the user for a string?", f"{RS}\ntxt = rs.GetString('Enter text')\nif txt:\n    print('Text:', txt)", ["getstring"]),
        ("How do I ask the user for an integer?", f"{RS}\nval = rs.GetInteger('Enter count', 10, 1, 100)\nif val is not None:\n    print('Count:', val)", ["getinteger"]),
        ("How do I let the user choose from a list?", f"{RS}\noptions = ['Option A', 'Option B', 'Option C']\nchoice = rs.ListBox(options, 'Pick one')\nif choice:\n    print('Chosen:', choice)", ["listbox"]),
        ("How do I show a message box?", f"{RS}\nrs.MessageBox('Operation complete!')", ["messagebox"]),
        ("How do I ask the user for two points?", f"{RS}\np1 = rs.GetPoint('First point')\nif p1:\n    p2 = rs.GetPoint('Second point')\n    if p2:\n        print('Distance:', rs.Distance(p1, p2))", ["getpoint", "two"]),
        ("How do I ask the user for a boolean yes/no?", f"{RS}\nresult = rs.GetBoolean('Settings', [('DoSomething', 'No', 'Yes')], [False])\nif result:\n    print('Choice:', result[0])", ["getboolean"]),
    ]
    for inst, code, tags in input_queries:
        pairs.append(m(inst, code, "easy", "rhinoscriptsyntax", ["input"] + tags))

    # ── 13) Analysis / measurement ──
    analysis_queries = [
        ("How do I measure the distance between two objects?", f"{RS}\na = rs.GetObject('First object')\nb = rs.GetObject('Second object')\nif a and b:\n    pt_a = rs.BoundingBox(a)\n    pt_b = rs.BoundingBox(b)\n    if pt_a and pt_b:\n        d = rs.Distance(pt_a[0], pt_b[0])\n        print('Approximate distance:', d)", "easy", ["distance"]),
        ("How do I find where two curves intersect?", f"{RS}\nc1 = rs.GetObject('First curve', 4)\nc2 = rs.GetObject('Second curve', 4)\nif c1 and c2:\n    pts = rs.CurveCurveIntersection(c1, c2)\n    if pts:\n        for p in pts:\n            rs.AddPoint(p[1])\n        print('Intersections:', len(pts))", "medium", ["intersection", "curves"]),
        ("How do I find where a curve intersects a surface?", f"{RS}\ncrv = rs.GetObject('Select curve', 4)\nsrf = rs.GetObject('Select surface', 8)\nif crv and srf:\n    pts = rs.CurveSurfaceIntersection(crv, srf)\n    if pts:\n        for p in pts:\n            rs.AddPoint(p[1])\n        print('Intersections:', len(pts))", "medium", ["intersection", "curve", "surface"]),
        ("How do I check if a point is inside a closed curve?", f"{RS}\ncrv = rs.GetObject('Select closed curve', 4)\nif crv:\n    pt = rs.GetPoint('Pick point')\n    if pt:\n        result = rs.PointInPlanarClosedCurve(pt, crv)\n        if result == 1:\n            print('Inside')\n        elif result == 2:\n            print('On boundary')\n        else:\n            print('Outside')", "medium", ["containment", "point"]),
        ("How do I get the angle between two vectors?", f"{RC}\nimport math\nv1 = rg.Vector3d(1, 0, 0)\nv2 = rg.Vector3d(0, 1, 0)\nangle = rg.Vector3d.VectorAngle(v1, v2)\nprint('Angle (degrees):', math.degrees(angle))", "easy", ["angle", "vector"]),
    ]
    for inst, code, diff, tags in analysis_queries:
        api = "RhinoCommon" if "rg." in code else "rhinoscriptsyntax"
        pairs.append(m(inst, code, diff, api, ["analysis"] + tags))

    return pairs
