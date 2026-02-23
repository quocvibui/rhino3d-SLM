"""Grasshopper Python (GhPython) component pairs (~400+)."""

def m(instruction, code, difficulty, tags):
    return {"instruction": instruction, "code": code, "source": "synthetic",
            "category": "grasshopper_python", "difficulty": difficulty, "api": "grasshopper", "tags": tags}

def generate():
    pairs = []

    # ── 1) Basic geometry creation in GhPython ──
    basic_geo = [
        ("Write a GhPython component that creates a point from x, y, z inputs",
         "import Rhino.Geometry as rg\na = rg.Point3d(x, y, z)", "easy", ["point"]),
        ("GhPython component to create a line between two input points",
         "import Rhino.Geometry as rg\na = rg.Line(pt1, pt2)", "easy", ["line"]),
        ("Create a circle from a center point and radius in GhPython",
         "import Rhino.Geometry as rg\nplane = rg.Plane(center, rg.Vector3d.ZAxis)\na = rg.Circle(plane, radius).ToNurbsCurve()", "easy", ["circle"]),
        ("GhPython: create a sphere from center and radius",
         "import Rhino.Geometry as rg\na = rg.Sphere(center, radius)", "easy", ["sphere"]),
        ("Create a polyline from a list of points in GhPython",
         "import Rhino.Geometry as rg\npline = rg.Polyline(pts)\na = pline.ToNurbsCurve()", "easy", ["polyline"]),
        ("GhPython: create a vector between two points",
         "import Rhino.Geometry as rg\na = rg.Vector3d(pt2 - pt1)", "easy", ["vector"]),
        ("Create a plane from origin, X, and Y vectors",
         "import Rhino.Geometry as rg\na = rg.Plane(origin, x_vec, y_vec)", "easy", ["plane"]),
        ("GhPython: create an arc through three points",
         "import Rhino.Geometry as rg\narc = rg.Arc(pt1, pt2, pt3)\na = arc.ToNurbsCurve()", "easy", ["arc"]),
        ("Create a rectangle in GhPython from width and height",
         "import Rhino.Geometry as rg\nplane = rg.Plane.WorldXY\ninterval_x = rg.Interval(0, width)\ninterval_y = rg.Interval(0, height)\na = rg.Rectangle3d(plane, interval_x, interval_y).ToNurbsCurve()", "easy", ["rectangle"]),
        ("GhPython: create a cylinder from base plane, radius, and height",
         "import Rhino.Geometry as rg\ncircle = rg.Circle(base_plane, radius)\ncyl = rg.Cylinder(circle, height)\na = cyl.ToBrep(True, True)", "medium", ["cylinder"]),
        ("Create a cone in GhPython",
         "import Rhino.Geometry as rg\nplane = rg.Plane(base_pt, rg.Vector3d.ZAxis)\na = rg.Cone(plane, height, radius)", "medium", ["cone"]),
        ("GhPython: create an interpolated curve from points",
         "import Rhino.Geometry as rg\na = rg.Curve.CreateInterpolatedCurve(pts, 3)", "easy", ["curve", "interpolated"]),
        ("Create a NURBS curve from control points in GhPython",
         "import Rhino.Geometry as rg\na = rg.NurbsCurve.Create(False, 3, pts)", "medium", ["nurbs", "curve"]),
        ("GhPython: create a surface from four corner points",
         "import Rhino.Geometry as rg\na = rg.NurbsSurface.CreateFromCorners(pt1, pt2, pt3, pt4)", "medium", ["surface", "corners"]),
        ("Create an ellipse in GhPython",
         "import Rhino.Geometry as rg\nplane = rg.Plane(center, rg.Vector3d.ZAxis)\nellipse = rg.Ellipse(plane, radius_x, radius_y)\na = ellipse.ToNurbsCurve()", "easy", ["ellipse"]),
    ]
    for inst, code, diff, tags in basic_geo:
        pairs.append(m(inst, code, diff, ["geometry"] + tags))

    # ── 2) DataTree input/output patterns ──
    tree_patterns = [
        ("Output a DataTree of points organized by rows",
         "import Grasshopper as gh\nimport Rhino.Geometry as rg\ntree = gh.DataTree[object]()\nfor i in range(rows):\n    path = gh.Kernel.Data.GH_Path(i)\n    for j in range(cols):\n        tree.Add(rg.Point3d(j * spacing, i * spacing, 0), path)\na = tree",
         "medium", ["datatree", "grid"]),
        ("Read branches from an input DataTree and process each",
         "import Grasshopper as gh\nimport Rhino.Geometry as rg\nresults = gh.DataTree[object]()\nfor i in range(tree.BranchCount):\n    branch = tree.Branch(i)\n    path = tree.Path(i)\n    moved = []\n    for pt in branch:\n        moved.append(rg.Point3d(pt.X + i, pt.Y, pt.Z))\n    results.AddRange(moved, path)\na = results",
         "hard", ["datatree", "branches"]),
        ("Flatten a DataTree to a single list",
         "import Grasshopper as gh\nimport Rhino.Geometry as rg\nflat = []\nfor i in range(tree.BranchCount):\n    for item in tree.Branch(i):\n        flat.append(item)\na = flat",
         "easy", ["datatree", "flatten"]),
        ("Graft a list into a DataTree with one item per branch",
         "import Grasshopper as gh\nimport Rhino.Geometry as rg\ntree_out = gh.DataTree[object]()\nfor i, item in enumerate(items):\n    path = gh.Kernel.Data.GH_Path(i)\n    tree_out.Add(item, path)\na = tree_out",
         "medium", ["datatree", "graft"]),
        ("Create a DataTree where each branch holds a pair of points",
         "import Grasshopper as gh\nimport Rhino.Geometry as rg\ntree = gh.DataTree[object]()\nfor i in range(count):\n    path = gh.Kernel.Data.GH_Path(i)\n    tree.Add(rg.Point3d(i, 0, 0), path)\n    tree.Add(rg.Point3d(i, 1, 0), path)\na = tree",
         "medium", ["datatree", "pairs"]),
        ("Partition a flat list into a DataTree with n items per branch",
         "import Grasshopper as gh\nn = partition_size\ntree = gh.DataTree[object]()\nfor i in range(0, len(items), n):\n    path = gh.Kernel.Data.GH_Path(i // n)\n    for item in items[i:i+n]:\n        tree.Add(item, path)\na = tree",
         "medium", ["datatree", "partition"]),
        ("Merge two DataTrees into one",
         "import Grasshopper as gh\nmerged = gh.DataTree[object]()\nfor i in range(tree_a.BranchCount):\n    merged.AddRange(list(tree_a.Branch(i)), tree_a.Path(i))\nfor i in range(tree_b.BranchCount):\n    merged.AddRange(list(tree_b.Branch(i)), tree_b.Path(i))\na = merged",
         "medium", ["datatree", "merge"]),
        ("Reverse each branch of a DataTree",
         "import Grasshopper as gh\nresult = gh.DataTree[object]()\nfor i in range(tree.BranchCount):\n    branch = list(tree.Branch(i))\n    branch.reverse()\n    result.AddRange(branch, tree.Path(i))\na = result",
         "easy", ["datatree", "reverse"]),
        ("Get the path indices from a DataTree",
         "import Grasshopper as gh\npaths = []\nfor i in range(tree.BranchCount):\n    p = tree.Path(i)\n    paths.append(str(p))\na = paths",
         "easy", ["datatree", "paths"]),
        ("Create a 2-level nested DataTree (matrix structure)",
         "import Grasshopper as gh\nimport Rhino.Geometry as rg\ntree = gh.DataTree[object]()\nfor i in range(rows):\n    for j in range(cols):\n        path = gh.Kernel.Data.GH_Path(i, j)\n        tree.Add(rg.Point3d(j, i, 0), path)\na = tree",
         "hard", ["datatree", "nested"]),
    ]
    for inst, code, diff, tags in tree_patterns:
        pairs.append(m(inst, code, diff, tags))

    # ── 3) ghpythonlib.components wrappers ──
    ghcomp_patterns = [
        ("Use ghpythonlib to move geometry by a vector",
         "import ghpythonlib.components as ghcomp\nimport Rhino.Geometry as rg\nvec = rg.Vector3d(dx, dy, dz)\na = ghcomp.Move(geometry, vec).geometry", "easy", ["move"]),
        ("Use ghpythonlib to rotate geometry around Z axis",
         "import ghpythonlib.components as ghcomp\nimport Rhino.Geometry as rg\nimport math\na = ghcomp.Rotate(geometry, math.radians(angle), rg.Plane.WorldXY).geometry", "easy", ["rotate"]),
        ("Boolean difference using ghpythonlib",
         "import ghpythonlib.components as ghcomp\na = ghcomp.SolidDifference(brep_a, brep_b)", "medium", ["boolean", "difference"]),
        ("Boolean union using ghpythonlib",
         "import ghpythonlib.components as ghcomp\na = ghcomp.SolidUnion(breps)", "medium", ["boolean", "union"]),
        ("Loft curves using ghpythonlib",
         "import ghpythonlib.components as ghcomp\na = ghcomp.Loft(curves, None, False)", "medium", ["loft"]),
        ("Offset a curve using ghpythonlib",
         "import ghpythonlib.components as ghcomp\nimport Rhino.Geometry as rg\na = ghcomp.OffsetCurve(curve, distance, rg.Plane.WorldXY, 1)", "easy", ["offset"]),
        ("Explode a polysurface using ghpythonlib",
         "import ghpythonlib.components as ghcomp\nresult = ghcomp.BrepComponents(brep)\na = result.faces", "easy", ["explode"]),
        ("Project a point onto a surface using ghpythonlib",
         "import ghpythonlib.components as ghcomp\nimport Rhino.Geometry as rg\na = ghcomp.ProjectPoint(point, rg.Vector3d(0,0,-1), surface)", "medium", ["project"]),
        ("Divide a curve by count using ghpythonlib",
         "import ghpythonlib.components as ghcomp\nresult = ghcomp.DivideCurve(curve, count, False)\na = result.points", "easy", ["divide"]),
        ("Create a pipe along a curve using ghpythonlib",
         "import ghpythonlib.components as ghcomp\na = ghcomp.Pipe(curve, radius, 1)", "easy", ["pipe"]),
        ("Scale geometry from a center point using ghpythonlib",
         "import ghpythonlib.components as ghcomp\nimport Rhino.Geometry as rg\na = ghcomp.Scale(geometry, rg.Plane(center, rg.Vector3d.ZAxis), factor).geometry", "easy", ["scale"]),
        ("Mirror geometry across a plane using ghpythonlib",
         "import ghpythonlib.components as ghcomp\nimport Rhino.Geometry as rg\na = ghcomp.Mirror(geometry, rg.Plane.WorldYZ).geometry", "easy", ["mirror"]),
        ("Extrude a curve along a vector using ghpythonlib",
         "import ghpythonlib.components as ghcomp\nimport Rhino.Geometry as rg\nvec = rg.Vector3d(0, 0, height)\na = ghcomp.Extrude(curve, vec)", "easy", ["extrude"]),
        ("Cap planar holes in a brep using ghpythonlib",
         "import ghpythonlib.components as ghcomp\na = ghcomp.CapHoles(brep)", "easy", ["cap"]),
        ("Get the area of a surface using ghpythonlib",
         "import ghpythonlib.components as ghcomp\nresult = ghcomp.Area(geometry)\na = result.area", "easy", ["area"]),
        ("Evaluate a surface at UV coordinates using ghpythonlib",
         "import ghpythonlib.components as ghcomp\nimport Rhino.Geometry as rg\nresult = ghcomp.EvaluateSurface(surface, rg.Point2d(u, v))\na = result.point", "medium", ["evaluate", "surface"]),
        ("Mesh a brep using ghpythonlib",
         "import ghpythonlib.components as ghcomp\na = ghcomp.MeshBrep(brep)", "easy", ["mesh"]),
        ("Contour a brep using ghpythonlib",
         "import ghpythonlib.components as ghcomp\nimport Rhino.Geometry as rg\na = ghcomp.Contour(brep, rg.Point3d(0,0,0), rg.Point3d(0,0,1), spacing)", "medium", ["contour"]),
    ]
    for inst, code, diff, tags in ghcomp_patterns:
        pairs.append(m(inst, code, diff, ["ghpythonlib"] + tags))

    # ── 4) Attractor-based patterns ──
    attractor_variations = [
        ("radius", "r = max(min_r, max_r - d * falloff)", "circles of varying radius"),
        ("height", "h = max(0.1, max_h * (1.0 / (1.0 + d * falloff)))", "boxes of varying height"),
        ("scale", "s = max(0.1, 1.0 - d * falloff / max_d)", "scaled copies"),
        ("spacing", "sp = min_sp + d * 0.1", "points with varying spacing"),
    ]
    for attr_type, calc, desc in attractor_variations:
        for shape in ["circle", "box", "sphere"]:
            if shape == "circle":
                geo_code = "circle = rg.Circle(rg.Plane(pt, rg.Vector3d.ZAxis), r)\n    result.append(circle.ToNurbsCurve())"
                var_name = "r"
            elif shape == "box":
                geo_code = "box = rg.Box(rg.Plane(pt, rg.Vector3d.ZAxis), rg.Interval(-0.5,0.5), rg.Interval(-0.5,0.5), rg.Interval(0,h))\n    result.append(box)"
                var_name = "h"
            else:
                geo_code = "result.append(rg.Sphere(pt, r))"
                var_name = "r"

            pairs.append(m(
                f"GhPython: create {desc} based on distance to attractor point",
                f"import Rhino.Geometry as rg\nimport math\nresult = []\nfor pt in pts:\n    d = pt.DistanceTo(attractor)\n    {var_name} = max(0.1, max_val - d * 0.2)\n    {geo_code}\na = result",
                "hard", ["attractor", shape, attr_type]))

    # ── 5) Point/curve manipulation ──
    manipulation = [
        ("Sort points by distance from a reference point",
         "import Rhino.Geometry as rg\nsorted_pts = sorted(pts, key=lambda p: p.DistanceTo(ref_pt))\na = sorted_pts",
         "easy", ["sort", "distance"]),
        ("Remove duplicate points within a tolerance",
         "import Rhino.Geometry as rg\nunique = []\ntol = 0.01\nfor pt in pts:\n    is_dup = False\n    for u in unique:\n        if pt.DistanceTo(u) < tol:\n            is_dup = True\n            break\n    if not is_dup:\n        unique.append(pt)\na = unique",
         "medium", ["deduplicate", "points"]),
        ("Find the centroid of a list of points",
         "import Rhino.Geometry as rg\nsum_x = sum(pt.X for pt in pts)\nsum_y = sum(pt.Y for pt in pts)\nsum_z = sum(pt.Z for pt in pts)\nn = len(pts)\na = rg.Point3d(sum_x/n, sum_y/n, sum_z/n)",
         "easy", ["centroid"]),
        ("Create a convex hull outline from 2D points",
         "import Rhino.Geometry as rg\nimport math\ndef cross(o, a, b):\n    return (a.X-o.X)*(b.Y-o.Y) - (a.Y-o.Y)*(b.X-o.X)\nsorted_pts = sorted(pts, key=lambda p: (p.X, p.Y))\nlower = []\nfor p in sorted_pts:\n    while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 0:\n        lower.pop()\n    lower.append(p)\nupper = []\nfor p in reversed(sorted_pts):\n    while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 0:\n        upper.pop()\n    upper.append(p)\nhull = lower[:-1] + upper[:-1]\nhull.append(hull[0])\na = rg.Polyline(hull).ToNurbsCurve()",
         "hard", ["convexhull"]),
        ("Connect nearest points with lines",
         "import Rhino.Geometry as rg\nlines = []\nfor i, pt in enumerate(pts):\n    min_d = float('inf')\n    nearest = None\n    for j, other in enumerate(pts):\n        if i != j:\n            d = pt.DistanceTo(other)\n            if d < min_d:\n                min_d = d\n                nearest = other\n    if nearest:\n        lines.append(rg.Line(pt, nearest))\na = lines",
         "medium", ["nearest", "lines"]),
        ("Offset each point along its associated curve normal",
         "import Rhino.Geometry as rg\nresult = []\nfor i, pt in enumerate(pts):\n    t = crv.ClosestPoint(pt)[1]\n    frame = None\n    success, frame = crv.PerpendicularFrameAt(t)\n    if success:\n        normal = frame.YAxis\n        result.append(pt + normal * offset_dist)\na = result",
         "hard", ["offset", "normal"]),
        ("Interpolate between two lists of points (blend)",
         "import Rhino.Geometry as rg\nresult = []\nfor a_pt, b_pt in zip(pts_a, pts_b):\n    x = a_pt.X * (1-t) + b_pt.X * t\n    y = a_pt.Y * (1-t) + b_pt.Y * t\n    z = a_pt.Z * (1-t) + b_pt.Z * t\n    result.append(rg.Point3d(x, y, z))\na = result",
         "medium", ["interpolate", "blend"]),
        ("Create circles at curve division points",
         "import Rhino.Geometry as rg\nparams = crv.DivideByCount(count, True)\nresult = []\nfor t in params:\n    pt = crv.PointAt(t)\n    frame = None\n    success, frame = crv.PerpendicularFrameAt(t)\n    if success:\n        circle = rg.Circle(frame, radius)\n        result.append(circle.ToNurbsCurve())\na = result",
         "hard", ["circles", "divide"]),
        ("Create a curve through the centroids of each tree branch",
         "import Rhino.Geometry as rg\nimport Grasshopper as gh\ncentroids = []\nfor i in range(tree.BranchCount):\n    branch = tree.Branch(i)\n    cx = sum(p.X for p in branch) / len(branch)\n    cy = sum(p.Y for p in branch) / len(branch)\n    cz = sum(p.Z for p in branch) / len(branch)\n    centroids.append(rg.Point3d(cx, cy, cz))\na = rg.Curve.CreateInterpolatedCurve(centroids, 3)",
         "hard", ["centroid", "datatree", "curve"]),
    ]
    for inst, code, diff, tags in manipulation:
        pairs.append(m(inst, code, diff, tags))

    # ── 6) Mesh generation patterns ──
    mesh_patterns = [
        ("Create a mesh grid in GhPython",
         "import Rhino.Geometry as rg\nmesh = rg.Mesh()\nfor i in range(rows+1):\n    for j in range(cols+1):\n        mesh.Vertices.Add(j*size, i*size, 0)\nfor i in range(rows):\n    for j in range(cols):\n        a = i*(cols+1)+j\n        mesh.Faces.AddFace(a, a+1, a+cols+2, a+cols+1)\nmesh.Normals.ComputeNormals()\na = mesh",
         "medium", ["mesh", "grid"]),
        ("Deform a mesh grid with a sine wave",
         "import Rhino.Geometry as rg\nimport math\nmesh = rg.Mesh()\nfor i in range(n+1):\n    for j in range(n+1):\n        z = amp * math.sin(i*freq) * math.cos(j*freq)\n        mesh.Vertices.Add(j, i, z)\nfor i in range(n):\n    for j in range(n):\n        a = i*(n+1)+j\n        mesh.Faces.AddFace(a, a+1, a+n+2, a+n+1)\nmesh.Normals.ComputeNormals()\na = mesh",
         "hard", ["mesh", "sine", "deform"]),
        ("Color mesh vertices by height (Z value)",
         "import Rhino.Geometry as rg\nimport System.Drawing as sd\nfor i in range(mesh.Vertices.Count):\n    z = mesh.Vertices[i].Z\n    t = max(0, min(1, (z - z_min) / (z_max - z_min)))\n    r = int(255 * t)\n    b = int(255 * (1-t))\n    mesh.VertexColors.Add(sd.Color.FromArgb(r, 0, b))\na = mesh",
         "hard", ["mesh", "color", "height"]),
        ("Create a mesh from a closed polyline (triangulated fan)",
         "import Rhino.Geometry as rg\nmesh = rg.Mesh()\ncenter = rg.Point3d(0,0,0)\nfor pt in pts:\n    center += rg.Point3d(pt.X/len(pts), pt.Y/len(pts), pt.Z/len(pts))\nmesh.Vertices.Add(center)\nfor pt in pts:\n    mesh.Vertices.Add(pt)\nfor i in range(len(pts)):\n    mesh.Faces.AddFace(0, i+1, (i+1)%len(pts)+1)\nmesh.Normals.ComputeNormals()\na = mesh",
         "medium", ["mesh", "fan"]),
        ("Weld mesh vertices within a tolerance",
         "import Rhino.Geometry as rg\nmesh.Weld(tolerance)\nmesh.Normals.ComputeNormals()\na = mesh",
         "easy", ["mesh", "weld"]),
        ("Smooth mesh vertices by averaging neighbors",
         "import Rhino.Geometry as rg\nfor iteration in range(steps):\n    new_verts = []\n    for i in range(mesh.Vertices.Count):\n        neighbors = mesh.Vertices.GetConnectedVertices(i)\n        if neighbors:\n            avg = rg.Point3d(0,0,0)\n            for n in neighbors:\n                avg += rg.Point3d(mesh.Vertices[n].X/len(neighbors), mesh.Vertices[n].Y/len(neighbors), mesh.Vertices[n].Z/len(neighbors))\n            new_verts.append(avg)\n        else:\n            new_verts.append(rg.Point3d(mesh.Vertices[i]))\n    for i, v in enumerate(new_verts):\n        mesh.Vertices.SetVertex(i, v)\nmesh.Normals.ComputeNormals()\na = mesh",
         "hard", ["mesh", "smooth"]),
    ]
    for inst, code, diff, tags in mesh_patterns:
        pairs.append(m(inst, code, diff, tags))

    # ── 7) Multi-output components ──
    multi_output = [
        ("Return both area and centroid from a curve",
         "import Rhino.Geometry as rg\namp = rg.AreaMassProperties.Compute(crv)\nif amp:\n    a = amp.Area\n    b = amp.Centroid\nelse:\n    a = 0\n    b = rg.Point3d.Origin",
         "medium", ["area", "centroid", "multi-output"]),
        ("Return length and midpoint of a curve",
         "import Rhino.Geometry as rg\na = crv.GetLength()\nt = crv.Domain.Mid\nb = crv.PointAt(t)",
         "easy", ["length", "midpoint", "multi-output"]),
        ("Split a list of numbers into positive and negative",
         "import Rhino.Geometry as rg\nfrom scriptcontext import sticky\npos = [x for x in values if x >= 0]\nneg = [x for x in values if x < 0]\na = pos\nb = neg",
         "easy", ["filter", "multi-output"]),
        ("Deconstruct a plane into origin, X, Y, Z axes",
         "import Rhino.Geometry as rg\na = plane.Origin\nb = plane.XAxis\nc = plane.YAxis\nd = plane.Normal",
         "easy", ["plane", "deconstruct", "multi-output"]),
        ("Return both the closest point and distance to a curve",
         "import Rhino.Geometry as rg\nsuccess, t = crv.ClosestPoint(pt)\nif success:\n    a = crv.PointAt(t)\n    b = pt.DistanceTo(a)\nelse:\n    a = pt\n    b = 0",
         "medium", ["closestpoint", "distance", "multi-output"]),
    ]
    for inst, code, diff, tags in multi_output:
        pairs.append(m(inst, code, diff, tags))

    # ── 8) treehelpers patterns ──
    th_patterns = [
        ("Convert a nested Python list to a DataTree using treehelpers",
         "import ghpythonlib.treehelpers as th\nimport Rhino.Geometry as rg\nnested = [[rg.Point3d(j, i, 0) for j in range(cols)] for i in range(rows)]\na = th.list_to_tree(nested)",
         "easy", ["treehelpers", "list_to_tree"]),
        ("Convert a DataTree to a nested Python list",
         "import ghpythonlib.treehelpers as th\nimport Rhino.Geometry as rg\nnested = th.tree_to_list(tree)\na = nested",
         "easy", ["treehelpers", "tree_to_list"]),
        ("Create a tree of circles from a nested list of radii",
         "import ghpythonlib.treehelpers as th\nimport Rhino.Geometry as rg\ncircles = []\nfor row in radii_nested:\n    row_circles = []\n    for r in row:\n        c = rg.Circle(rg.Plane.WorldXY, r).ToNurbsCurve()\n        row_circles.append(c)\n    circles.append(row_circles)\na = th.list_to_tree(circles)",
         "medium", ["treehelpers", "circles"]),
    ]
    for inst, code, diff, tags in th_patterns:
        pairs.append(m(inst, code, diff, tags))

    # ── 9) Pattern generation ──
    patterns = [
        ("Generate a hexagonal grid of points",
         "import Rhino.Geometry as rg\nimport math\nresult = []\nfor i in range(rows):\n    for j in range(cols):\n        x = j * spacing + (i % 2) * spacing * 0.5\n        y = i * spacing * math.sqrt(3) / 2\n        result.append(rg.Point3d(x, y, 0))\na = result",
         "medium", ["hexagonal", "grid"]),
        ("Generate a Fibonacci spiral of points",
         "import Rhino.Geometry as rg\nimport math\nresult = []\nfor i in range(count):\n    theta = i * math.radians(137.508)\n    r = math.sqrt(i) * scale\n    result.append(rg.Point3d(r*math.cos(theta), r*math.sin(theta), 0))\na = result",
         "hard", ["fibonacci", "spiral"]),
        ("Generate a random point cloud within a bounding box",
         "import Rhino.Geometry as rg\nimport random\nrandom.seed(seed)\nresult = []\nfor i in range(count):\n    x = random.uniform(0, width)\n    y = random.uniform(0, depth)\n    z = random.uniform(0, height)\n    result.append(rg.Point3d(x, y, z))\na = result",
         "easy", ["random", "pointcloud"]),
        ("Generate a grid of points with noise displacement",
         "import Rhino.Geometry as rg\nimport random\nimport math\nrandom.seed(seed)\nresult = []\nfor i in range(rows):\n    for j in range(cols):\n        x = j * spacing + random.uniform(-noise, noise)\n        y = i * spacing + random.uniform(-noise, noise)\n        z = random.uniform(-noise, noise)\n        result.append(rg.Point3d(x, y, z))\na = result",
         "medium", ["grid", "noise"]),
        ("Create concentric circles with varying radii",
         "import Rhino.Geometry as rg\nresult = []\nfor i in range(count):\n    r = (i + 1) * spacing\n    circle = rg.Circle(rg.Plane(center, rg.Vector3d.ZAxis), r)\n    result.append(circle.ToNurbsCurve())\na = result",
         "easy", ["concentric", "circles"]),
        ("Create a Voronoi-like nearest neighbor connectivity",
         "import Rhino.Geometry as rg\nlines = []\nfor i, p1 in enumerate(pts):\n    dists = []\n    for j, p2 in enumerate(pts):\n        if i != j:\n            dists.append((p1.DistanceTo(p2), j))\n    dists.sort()\n    for d, j in dists[:neighbors]:\n        lines.append(rg.Line(p1, pts[j]))\na = lines",
         "hard", ["voronoi", "connectivity"]),
        ("Create a diamond grid pattern of lines",
         "import Rhino.Geometry as rg\nlines = []\nfor i in range(rows):\n    for j in range(cols):\n        cx = j * spacing + (i % 2) * spacing * 0.5\n        cy = i * spacing * 0.5\n        top = rg.Point3d(cx, cy + spacing*0.5, 0)\n        right = rg.Point3d(cx + spacing*0.5, cy, 0)\n        bottom = rg.Point3d(cx, cy - spacing*0.5, 0)\n        left = rg.Point3d(cx - spacing*0.5, cy, 0)\n        lines.extend([rg.Line(top,right), rg.Line(right,bottom), rg.Line(bottom,left), rg.Line(left,top)])\na = lines",
         "hard", ["diamond", "grid"]),
    ]
    for inst, code, diff, tags in patterns:
        pairs.append(m(inst, code, diff, ["pattern"] + tags))

    # ── 10) Surface analysis ──
    srf_analysis = [
        ("Evaluate surface at UV and get normal",
         "import Rhino.Geometry as rg\npt = srf.PointAt(u, v)\nnml = srf.NormalAt(u, v)\na = pt\nb = nml",
         "easy", ["surface", "normal", "evaluate"]),
        ("Get surface curvature at a UV parameter",
         "import Rhino.Geometry as rg\ncurvature = srf.CurvatureAt(u, v)\nif curvature:\n    a = curvature.Kappa(0)\n    b = curvature.Kappa(1)\nelse:\n    a = 0\n    b = 0",
         "hard", ["surface", "curvature"]),
        ("Map a flat grid of points onto a surface using UV coordinates",
         "import Rhino.Geometry as rg\nresult = []\nu_dom = srf.Domain(0)\nv_dom = srf.Domain(1)\nfor i in range(u_count):\n    for j in range(v_count):\n        u = u_dom.T0 + (u_dom.T1-u_dom.T0) * i / (u_count-1)\n        v = v_dom.T0 + (v_dom.T1-v_dom.T0) * j / (v_count-1)\n        result.append(srf.PointAt(u, v))\na = result",
         "medium", ["surface", "map", "uv"]),
        ("Extract iso-curves from a surface at regular intervals",
         "import Rhino.Geometry as rg\ncurves = []\nu_dom = srf.Domain(0)\nfor i in range(count):\n    u = u_dom.T0 + (u_dom.T1-u_dom.T0) * i / (count-1)\n    iso = srf.IsoCurve(1, u)\n    if iso:\n        curves.append(iso)\na = curves",
         "medium", ["surface", "isocurve"]),
    ]
    for inst, code, diff, tags in srf_analysis:
        pairs.append(m(inst, code, diff, tags))

    # ── 11) Utility patterns ──
    utilities = [
        ("Remap a value from one domain to another",
         "import Rhino.Geometry as rg\ndef remap(val, src_min, src_max, dst_min, dst_max):\n    t = (val - src_min) / (src_max - src_min)\n    return dst_min + t * (dst_max - dst_min)\na = remap(value, in_min, in_max, out_min, out_max)",
         "easy", ["remap", "utility"]),
        ("Clamp a list of values between min and max",
         "import Rhino.Geometry as rg\na = [max(lo, min(hi, v)) for v in values]",
         "easy", ["clamp", "utility"]),
        ("Generate a color gradient between two colors based on parameter",
         "import Rhino.Geometry as rg\nimport System.Drawing as sd\ndef lerp_color(c1, c2, t):\n    r = int(c1.R + (c2.R - c1.R) * t)\n    g = int(c1.G + (c2.G - c1.G) * t)\n    b = int(c1.B + (c2.B - c1.B) * t)\n    return sd.Color.FromArgb(r, g, b)\na = [lerp_color(color_a, color_b, i/(count-1)) for i in range(count)]",
         "medium", ["color", "gradient"]),
        ("Store and retrieve data using sticky dictionary",
         "import scriptcontext as sc\nif 'my_data' not in sc.sticky:\n    sc.sticky['my_data'] = []\nsc.sticky['my_data'].append(new_value)\na = sc.sticky['my_data']",
         "medium", ["sticky", "persistent"]),
        ("Timer-based animation: increment counter each solve",
         "import scriptcontext as sc\nimport Rhino.Geometry as rg\nif 'counter' not in sc.sticky:\n    sc.sticky['counter'] = 0\nsc.sticky['counter'] += 1\nt = sc.sticky['counter'] * 0.1\na = rg.Point3d(10 * __import__('math').cos(t), 10 * __import__('math').sin(t), 0)",
         "hard", ["animation", "sticky"]),
    ]
    for inst, code, diff, tags in utilities:
        pairs.append(m(inst, code, diff, tags))

    # ── 12) Template expansion: geometry on surface points ──
    geo_types = [
        ("circle", "rg.Circle(rg.Plane(pt, nml), radius).ToNurbsCurve()"),
        ("sphere", "rg.Sphere(pt, radius)"),
        ("line along normal", "rg.Line(pt, pt + nml * length)"),
        ("box", "rg.Box(rg.Plane(pt, nml), rg.Interval(-s/2,s/2), rg.Interval(-s/2,s/2), rg.Interval(0,s))"),
    ]
    for geo_name, geo_expr in geo_types:
        pairs.append(m(
            f"Place a {geo_name} at each point on a surface grid, oriented to the surface normal",
            f"import Rhino.Geometry as rg\nresult = []\nu_dom = srf.Domain(0)\nv_dom = srf.Domain(1)\nfor i in range(u_count):\n    for j in range(v_count):\n        u = u_dom.T0 + (u_dom.T1-u_dom.T0) * i / max(u_count-1,1)\n        v = v_dom.T0 + (v_dom.T1-v_dom.T0) * j / max(v_count-1,1)\n        pt = srf.PointAt(u, v)\n        nml = srf.NormalAt(u, v)\n        result.append({geo_expr})\na = result",
            "hard", ["surface", "populate", geo_name]))

    return pairs
