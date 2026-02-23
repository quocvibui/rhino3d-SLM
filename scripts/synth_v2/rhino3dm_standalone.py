"""rhino3dm standalone script pairs (~400+)."""

def m(instruction, code, difficulty, tags):
    return {"instruction": instruction, "code": code, "source": "synthetic",
            "category": "rhino3dm_standalone", "difficulty": difficulty, "api": "rhino3dm", "tags": tags}

def generate():
    pairs = []
    R3 = "import rhino3dm"

    # ── 1) Create new file + add single geometry ──
    single_geo = [
        ("point at origin", "model.Objects.AddPoint(rhino3dm.Point3d(0, 0, 0))", ["point"]),
        ("point at (5,10,3)", "model.Objects.AddPoint(rhino3dm.Point3d(5, 10, 3))", ["point"]),
        ("line from origin to (10,0,0)", "line = rhino3dm.Line(rhino3dm.Point3d(0,0,0), rhino3dm.Point3d(10,0,0))\nmodel.Objects.AddLine(line.From, line.To)", ["line"]),
        ("circle with radius 5", "circle = rhino3dm.Circle(5.0)\nmodel.Objects.AddCircle(circle)", ["circle"]),
        ("sphere with radius 3", "sphere = rhino3dm.Sphere(rhino3dm.Point3d(0,0,0), 3.0)\nmodel.Objects.AddSphere(sphere)", ["sphere"]),
    ]
    for desc, add_code, tags in single_geo:
        pairs.append(m(
            f"Create a 3dm file with a {desc} and save it",
            f"{R3}\nmodel = rhino3dm.File3dm()\n{add_code}\nmodel.Write('output.3dm', 7)",
            "easy", ["create", "save"] + tags))

    # Vary file names and coordinates
    coords = [(1,2,3), (0,0,10), (-5,5,0), (100,0,0)]
    for x, y, z in coords:
        pairs.append(m(
            f"Create a 3dm file with a point at ({x},{y},{z})",
            f"{R3}\nmodel = rhino3dm.File3dm()\nmodel.Objects.AddPoint(rhino3dm.Point3d({x},{y},{z}))\nmodel.Write('point_output.3dm', 7)",
            "easy", ["point", "create"]))

    # ── 2) Multiple geometry in one file ──
    multi_geo = [
        ("Create a 3dm file with 10 points along the X axis",
         f"{R3}\nmodel = rhino3dm.File3dm()\nfor i in range(10):\n    model.Objects.AddPoint(rhino3dm.Point3d(i, 0, 0))\nmodel.Write('points.3dm', 7)",
         "easy", ["points", "loop"]),
        ("Create a 3dm file with a grid of 25 points",
         f"{R3}\nmodel = rhino3dm.File3dm()\nfor i in range(5):\n    for j in range(5):\n        model.Objects.AddPoint(rhino3dm.Point3d(i*2, j*2, 0))\nmodel.Write('grid.3dm', 7)",
         "easy", ["grid", "points"]),
        ("Create a 3dm file with 5 concentric circles",
         f"{R3}\nmodel = rhino3dm.File3dm()\nfor r in range(1, 6):\n    circle = rhino3dm.Circle(float(r))\n    model.Objects.AddCircle(circle)\nmodel.Write('circles.3dm', 7)",
         "easy", ["circles", "concentric"]),
        ("Create a 3dm file with a star pattern of lines",
         f"{R3}\nimport math\nmodel = rhino3dm.File3dm()\ncenter = rhino3dm.Point3d(0,0,0)\nfor i in range(12):\n    angle = math.radians(i * 30)\n    end = rhino3dm.Point3d(10*math.cos(angle), 10*math.sin(angle), 0)\n    model.Objects.AddLine(center, end)\nmodel.Write('star.3dm', 7)",
         "medium", ["star", "lines"]),
        ("Create a 3dm file with multiple spheres at random positions",
         f"{R3}\nimport random\nrandom.seed(42)\nmodel = rhino3dm.File3dm()\nfor i in range(20):\n    center = rhino3dm.Point3d(random.uniform(-10,10), random.uniform(-10,10), random.uniform(-10,10))\n    sphere = rhino3dm.Sphere(center, random.uniform(0.5, 2.0))\n    model.Objects.AddSphere(sphere)\nmodel.Write('spheres.3dm', 7)",
         "medium", ["spheres", "random"]),
        ("Create a 3dm file with a polyline",
         f"{R3}\nmodel = rhino3dm.File3dm()\npts = [rhino3dm.Point3d(i, i*0.5, 0) for i in range(10)]\npline = rhino3dm.Polyline(0)\nfor pt in pts:\n    pline.Add(pt.X, pt.Y, pt.Z)\nmodel.Objects.AddPolyline(pline)\nmodel.Write('polyline.3dm', 7)",
         "medium", ["polyline"]),
    ]
    for inst, code, diff, tags in multi_geo:
        pairs.append(m(inst, code, diff, tags))

    # ── 3) Layer management ──
    layer_ops = [
        ("Create a 3dm file with three named layers",
         f"{R3}\nmodel = rhino3dm.File3dm()\nfor name in ['Layer1', 'Layer2', 'Layer3']:\n    layer = rhino3dm.Layer()\n    layer.Name = name\n    model.Layers.Add(layer)\nmodel.Write('layers.3dm', 7)",
         "easy", ["layers", "create"]),
        ("Create layers with different colors",
         f"{R3}\nmodel = rhino3dm.File3dm()\ncolors = [('Red', (255,0,0,255)), ('Green', (0,255,0,255)), ('Blue', (0,0,255,255))]\nfor name, color in colors:\n    layer = rhino3dm.Layer()\n    layer.Name = name\n    layer.Color = color\n    model.Layers.Add(layer)\nmodel.Write('colored_layers.3dm', 7)",
         "easy", ["layers", "color"]),
        ("Add geometry to a specific layer",
         f"{R3}\nmodel = rhino3dm.File3dm()\nlayer = rhino3dm.Layer()\nlayer.Name = 'Points'\nidx = model.Layers.Add(layer)\nattr = rhino3dm.ObjectAttributes()\nattr.LayerIndex = idx\nfor i in range(5):\n    model.Objects.AddPoint(rhino3dm.Point3d(i,0,0), attr)\nmodel.Write('layered.3dm', 7)",
         "medium", ["layers", "assign"]),
        ("Create a layer hierarchy (parent-child)",
         f"{R3}\nmodel = rhino3dm.File3dm()\nparent = rhino3dm.Layer()\nparent.Name = 'Building'\nparent_idx = model.Layers.Add(parent)\nchild = rhino3dm.Layer()\nchild.Name = 'Walls'\nchild.ParentLayerId = model.Layers[parent_idx].Id\nmodel.Layers.Add(child)\nmodel.Write('hierarchy.3dm', 7)",
         "medium", ["layers", "hierarchy"]),
        ("List all layers in a 3dm file",
         f"{R3}\nmodel = rhino3dm.File3dm.Read('input.3dm')\nfor i in range(len(model.Layers)):\n    layer = model.Layers[i]\n    print(f'Layer {{i}}: {{layer.Name}} (color: {{layer.Color}})')",
         "easy", ["layers", "list"]),
    ]
    for inst, code, diff, tags in layer_ops:
        pairs.append(m(inst, code, diff, tags))

    # ── 4) Read and iterate files ──
    read_ops = [
        ("Read a 3dm file and list all object types",
         f"{R3}\nmodel = rhino3dm.File3dm.Read('input.3dm')\nfor obj in model.Objects:\n    geo = obj.Geometry\n    print(f'Type: {{type(geo).__name__}}')",
         "easy", ["read", "iterate"]),
        ("Read a 3dm file and count objects by type",
         f"{R3}\nfrom collections import Counter\nmodel = rhino3dm.File3dm.Read('input.3dm')\ncounts = Counter()\nfor obj in model.Objects:\n    counts[type(obj.Geometry).__name__] += 1\nfor t, c in counts.items():\n    print(f'{{t}}: {{c}}')",
         "easy", ["read", "count"]),
        ("Read a 3dm file and print bounding box of each object",
         f"{R3}\nmodel = rhino3dm.File3dm.Read('input.3dm')\nfor obj in model.Objects:\n    geo = obj.Geometry\n    bb = geo.GetBoundingBox()\n    print(f'Min: {{bb.Min}}, Max: {{bb.Max}}')",
         "medium", ["read", "boundingbox"]),
        ("Read a 3dm file and extract all point coordinates",
         f"{R3}\nmodel = rhino3dm.File3dm.Read('input.3dm')\npoints = []\nfor obj in model.Objects:\n    geo = obj.Geometry\n    if isinstance(geo, rhino3dm.Point):\n        loc = geo.Location\n        points.append((loc.X, loc.Y, loc.Z))\nprint(f'Found {{len(points)}} points')\nfor pt in points:\n    print(pt)",
         "medium", ["read", "points", "extract"]),
        ("Read a 3dm file and report layer assignments",
         f"{R3}\nmodel = rhino3dm.File3dm.Read('input.3dm')\nfor obj in model.Objects:\n    attrs = obj.Attributes\n    layer_idx = attrs.LayerIndex\n    layer_name = model.Layers[layer_idx].Name\n    print(f'Object on layer: {{layer_name}}')",
         "medium", ["read", "layers"]),
        ("Read a 3dm file and get object names",
         f"{R3}\nmodel = rhino3dm.File3dm.Read('input.3dm')\nfor obj in model.Objects:\n    name = obj.Attributes.Name\n    if name:\n        print(f'Named object: {{name}}')",
         "easy", ["read", "names"]),
    ]
    for inst, code, diff, tags in read_ops:
        pairs.append(m(inst, code, diff, tags))

    # ── 5) NURBS curve creation ──
    nurbs_curves = [
        ("Create a degree-3 NURBS curve and save to 3dm",
         f"{R3}\nmodel = rhino3dm.File3dm()\npts = [rhino3dm.Point3d(i*2, i*0.5, 0) for i in range(6)]\ncrv = rhino3dm.NurbsCurve.Create(False, 3, pts)\nmodel.Objects.AddCurve(crv)\nmodel.Write('curve.3dm', 7)",
         "medium", ["nurbs", "curve"]),
        ("Create a closed NURBS curve (loop)",
         f"{R3}\nimport math\nmodel = rhino3dm.File3dm()\npts = []\nfor i in range(8):\n    angle = math.radians(i * 45)\n    pts.append(rhino3dm.Point3d(5*math.cos(angle), 5*math.sin(angle), 0))\ncrv = rhino3dm.NurbsCurve.Create(True, 3, pts)\nmodel.Objects.AddCurve(crv)\nmodel.Write('closed_curve.3dm', 7)",
         "medium", ["nurbs", "curve", "closed"]),
        ("Create multiple NURBS curves at different heights",
         f"{R3}\nmodel = rhino3dm.File3dm()\nfor z in range(5):\n    pts = [rhino3dm.Point3d(i, 0, z*3) for i in range(6)]\n    crv = rhino3dm.NurbsCurve.Create(False, 3, pts)\n    model.Objects.AddCurve(crv)\nmodel.Write('curves.3dm', 7)",
         "medium", ["nurbs", "curves", "multiple"]),
        ("Create a helix curve using NURBS control points",
         f"{R3}\nimport math\nmodel = rhino3dm.File3dm()\npts = []\nfor i in range(50):\n    t = i * 0.2\n    pts.append(rhino3dm.Point3d(5*math.cos(t), 5*math.sin(t), t*0.5))\ncrv = rhino3dm.NurbsCurve.Create(False, 3, pts)\nmodel.Objects.AddCurve(crv)\nmodel.Write('helix.3dm', 7)",
         "medium", ["helix", "curve"]),
        ("Create a sine wave curve",
         f"{R3}\nimport math\nmodel = rhino3dm.File3dm()\npts = [rhino3dm.Point3d(i*0.2, math.sin(i*0.2)*3, 0) for i in range(60)]\ncrv = rhino3dm.NurbsCurve.Create(False, 3, pts)\nmodel.Objects.AddCurve(crv)\nmodel.Write('sine.3dm', 7)",
         "medium", ["sine", "curve"]),
    ]
    for inst, code, diff, tags in nurbs_curves:
        pairs.append(m(inst, code, diff, tags))

    # ── 6) Mesh creation from scratch ──
    mesh_ops = [
        ("Create a triangle mesh and save to 3dm",
         f"{R3}\nmodel = rhino3dm.File3dm()\nmesh = rhino3dm.Mesh()\nmesh.Vertices.Add(0, 0, 0)\nmesh.Vertices.Add(10, 0, 0)\nmesh.Vertices.Add(5, 10, 0)\nmesh.Faces.AddFace(0, 1, 2)\nmodel.Objects.AddMesh(mesh)\nmodel.Write('triangle.3dm', 7)",
         "easy", ["mesh", "triangle"]),
        ("Create a quad mesh plane",
         f"{R3}\nmodel = rhino3dm.File3dm()\nmesh = rhino3dm.Mesh()\nrows, cols = 10, 10\nfor i in range(rows+1):\n    for j in range(cols+1):\n        mesh.Vertices.Add(j, i, 0)\nfor i in range(rows):\n    for j in range(cols):\n        a = i*(cols+1)+j\n        mesh.Faces.AddFace(a, a+1, a+cols+2, a+cols+1)\nmodel.Objects.AddMesh(mesh)\nmodel.Write('quad_plane.3dm', 7)",
         "medium", ["mesh", "grid", "quad"]),
        ("Create a mesh box (cube)",
         f"{R3}\nmodel = rhino3dm.File3dm()\nmesh = rhino3dm.Mesh()\nverts = [(0,0,0),(1,0,0),(1,1,0),(0,1,0),(0,0,1),(1,0,1),(1,1,1),(0,1,1)]\nfor v in verts:\n    mesh.Vertices.Add(v[0]*10, v[1]*10, v[2]*10)\nfaces = [(0,1,2,3),(4,7,6,5),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)]\nfor f in faces:\n    mesh.Faces.AddFace(f[0],f[1],f[2],f[3])\nmodel.Objects.AddMesh(mesh)\nmodel.Write('box_mesh.3dm', 7)",
         "medium", ["mesh", "box"]),
        ("Create a mesh with vertex colors",
         f"{R3}\nmodel = rhino3dm.File3dm()\nmesh = rhino3dm.Mesh()\nmesh.Vertices.Add(0, 0, 0)\nmesh.Vertices.Add(10, 0, 0)\nmesh.Vertices.Add(5, 10, 0)\nmesh.Faces.AddFace(0, 1, 2)\nmesh.VertexColors.Add(255, 0, 0)\nmesh.VertexColors.Add(0, 255, 0)\nmesh.VertexColors.Add(0, 0, 255)\nmodel.Objects.AddMesh(mesh)\nmodel.Write('colored_mesh.3dm', 7)",
         "medium", ["mesh", "colors"]),
        ("Create a mesh heightmap from a nested list of heights",
         f"{R3}\nmodel = rhino3dm.File3dm()\nmesh = rhino3dm.Mesh()\nimport math\nsize = 20\nfor i in range(size):\n    for j in range(size):\n        z = 3 * math.sin(i*0.5) * math.cos(j*0.5)\n        mesh.Vertices.Add(j, i, z)\nfor i in range(size-1):\n    for j in range(size-1):\n        a = i*size+j\n        mesh.Faces.AddFace(a, a+1, a+size+1, a+size)\nmodel.Objects.AddMesh(mesh)\nmodel.Write('heightmap.3dm', 7)",
         "hard", ["mesh", "heightmap"]),
        ("Create a mesh sphere approximation",
         f"{R3}\nimport math\nmodel = rhino3dm.File3dm()\nmesh = rhino3dm.Mesh()\nstacks, slices = 16, 24\nradius = 5.0\nfor i in range(stacks+1):\n    phi = math.pi * i / stacks\n    for j in range(slices):\n        theta = 2 * math.pi * j / slices\n        x = radius * math.sin(phi) * math.cos(theta)\n        y = radius * math.sin(phi) * math.sin(theta)\n        z = radius * math.cos(phi)\n        mesh.Vertices.Add(x, y, z)\nfor i in range(stacks):\n    for j in range(slices):\n        a = i*slices + j\n        b = i*slices + (j+1)%slices\n        c = (i+1)*slices + (j+1)%slices\n        d = (i+1)*slices + j\n        mesh.Faces.AddFace(a, b, c, d)\nmodel.Objects.AddMesh(mesh)\nmodel.Write('sphere_mesh.3dm', 7)",
         "hard", ["mesh", "sphere"]),
    ]
    for inst, code, diff, tags in mesh_ops:
        pairs.append(m(inst, code, diff, tags))

    # ── 7) Batch processing ──
    batch_ops = [
        ("Read a 3dm file and write a summary JSON",
         f"{R3}\nimport json\nmodel = rhino3dm.File3dm.Read('input.3dm')\nsummary = {{\n    'object_count': len(model.Objects),\n    'layer_count': len(model.Layers),\n    'layers': [model.Layers[i].Name for i in range(len(model.Layers))],\n}}\nwith open('summary.json', 'w') as f:\n    json.dump(summary, f, indent=2)\nprint('Summary written')",
         "medium", ["batch", "json", "summary"]),
        ("Process multiple 3dm files and extract point counts",
         f"{R3}\nimport os\nresults = {{}}\nfor fname in os.listdir('models/'):\n    if fname.endswith('.3dm'):\n        model = rhino3dm.File3dm.Read(os.path.join('models/', fname))\n        count = len(model.Objects)\n        results[fname] = count\n        print(f'{{fname}}: {{count}} objects')",
         "medium", ["batch", "multiple"]),
        ("Merge two 3dm files into one",
         f"{R3}\nmodel_a = rhino3dm.File3dm.Read('file_a.3dm')\nmodel_b = rhino3dm.File3dm.Read('file_b.3dm')\nmerged = rhino3dm.File3dm()\nfor obj in model_a.Objects:\n    geo = obj.Geometry\n    merged.Objects.Add(geo)\nfor obj in model_b.Objects:\n    geo = obj.Geometry\n    merged.Objects.Add(geo)\nmerged.Write('merged.3dm', 7)\nprint('Merged into merged.3dm')",
         "hard", ["batch", "merge"]),
        ("Read a 3dm and export all point coordinates to CSV",
         f"{R3}\nimport csv\nmodel = rhino3dm.File3dm.Read('input.3dm')\nwith open('points.csv', 'w', newline='') as f:\n    writer = csv.writer(f)\n    writer.writerow(['X', 'Y', 'Z'])\n    for obj in model.Objects:\n        geo = obj.Geometry\n        if isinstance(geo, rhino3dm.Point):\n            loc = geo.Location\n            writer.writerow([loc.X, loc.Y, loc.Z])\nprint('Exported to points.csv')",
         "medium", ["export", "csv"]),
        ("Create 3dm geometry from CSV coordinate data",
         f"{R3}\nimport csv\nmodel = rhino3dm.File3dm()\nwith open('data.csv', 'r') as f:\n    reader = csv.DictReader(f)\n    for row in reader:\n        x = float(row['X'])\n        y = float(row['Y'])\n        z = float(row['Z'])\n        model.Objects.AddPoint(rhino3dm.Point3d(x, y, z))\nmodel.Write('from_csv.3dm', 7)\nprint('Created from CSV')",
         "medium", ["import", "csv"]),
        ("Create geometry from JSON data",
         f"{R3}\nimport json\nmodel = rhino3dm.File3dm()\nwith open('geometry.json', 'r') as f:\n    data = json.load(f)\nfor item in data['points']:\n    model.Objects.AddPoint(rhino3dm.Point3d(item['x'], item['y'], item['z']))\nfor item in data.get('lines', []):\n    p1 = rhino3dm.Point3d(item['start']['x'], item['start']['y'], item['start']['z'])\n    p2 = rhino3dm.Point3d(item['end']['x'], item['end']['y'], item['end']['z'])\n    model.Objects.AddLine(p1, p2)\nmodel.Write('from_json.3dm', 7)",
         "hard", ["import", "json"]),
    ]
    for inst, code, diff, tags in batch_ops:
        pairs.append(m(inst, code, diff, tags))

    # ── 8) Geometry analysis ──
    analysis_ops = [
        ("Get the bounding box of all objects in a 3dm file",
         f"{R3}\nmodel = rhino3dm.File3dm.Read('input.3dm')\nbbox = rhino3dm.BoundingBox(rhino3dm.Point3d(1e10,1e10,1e10), rhino3dm.Point3d(-1e10,-1e10,-1e10))\nfor obj in model.Objects:\n    bb = obj.Geometry.GetBoundingBox()\n    if bb.IsValid:\n        bbox = rhino3dm.BoundingBox(\n            rhino3dm.Point3d(min(bbox.Min.X, bb.Min.X), min(bbox.Min.Y, bb.Min.Y), min(bbox.Min.Z, bb.Min.Z)),\n            rhino3dm.Point3d(max(bbox.Max.X, bb.Max.X), max(bbox.Max.Y, bb.Max.Y), max(bbox.Max.Z, bb.Max.Z))\n        )\nprint(f'Overall BBox: {{bbox.Min}} to {{bbox.Max}}')",
         "medium", ["boundingbox", "analysis"]),
        ("Check if a 3dm file contains any mesh objects",
         f"{R3}\nmodel = rhino3dm.File3dm.Read('input.3dm')\nhas_mesh = any(isinstance(obj.Geometry, rhino3dm.Mesh) for obj in model.Objects)\nprint(f'Contains meshes: {{has_mesh}}')",
         "easy", ["check", "mesh"]),
        ("Count vertices and faces in all meshes in a 3dm file",
         f"{R3}\nmodel = rhino3dm.File3dm.Read('input.3dm')\ntotal_verts = 0\ntotal_faces = 0\nfor obj in model.Objects:\n    geo = obj.Geometry\n    if isinstance(geo, rhino3dm.Mesh):\n        total_verts += len(geo.Vertices)\n        total_faces += len(geo.Faces)\nprint(f'Total vertices: {{total_verts}}, faces: {{total_faces}}')",
         "medium", ["mesh", "count", "analysis"]),
    ]
    for inst, code, diff, tags in analysis_ops:
        pairs.append(m(inst, code, diff, tags))

    # ── 9) Object attributes ──
    attr_ops = [
        ("Set object name when adding geometry",
         f"{R3}\nmodel = rhino3dm.File3dm()\nattr = rhino3dm.ObjectAttributes()\nattr.Name = 'MySphere'\nsphere = rhino3dm.Sphere(rhino3dm.Point3d(0,0,0), 5)\nmodel.Objects.AddSphere(sphere, attr)\nmodel.Write('named.3dm', 7)",
         "easy", ["attributes", "name"]),
        ("Set object color when adding geometry",
         f"{R3}\nmodel = rhino3dm.File3dm()\nattr = rhino3dm.ObjectAttributes()\nattr.ObjectColor = (255, 0, 0, 255)\nattr.ColorSource = rhino3dm.ObjectColorSource.ColorFromObject\nmodel.Objects.AddPoint(rhino3dm.Point3d(0,0,0), attr)\nmodel.Write('colored.3dm', 7)",
         "medium", ["attributes", "color"]),
    ]
    for inst, code, diff, tags in attr_ops:
        pairs.append(m(inst, code, diff, tags))

    # ── 10) Template expansion: varied file ops ──
    operations = ["read", "create", "modify", "analyze"]
    geo_types = ["point", "curve", "mesh", "sphere", "line"]
    file_actions = [
        ("Create a 3dm with {n} {geo}s in a line along X",
         f"{R3}\nmodel = rhino3dm.File3dm()\nfor i in range({{n}}):\n    model.Objects.AddPoint(rhino3dm.Point3d(i*2, 0, 0))\nmodel.Write('line_points.3dm', 7)"),
        ("Create a 3dm with {n} {geo}s in a circle",
         f"{R3}\nimport math\nmodel = rhino3dm.File3dm()\nfor i in range({{n}}):\n    angle = 2*math.pi*i/{{n}}\n    model.Objects.AddPoint(rhino3dm.Point3d(10*math.cos(angle), 10*math.sin(angle), 0))\nmodel.Write('circle_points.3dm', 7)"),
    ]
    for n in [5, 10, 20, 50]:
        for tmpl_inst, tmpl_code in file_actions:
            pairs.append(m(
                tmpl_inst.format(n=n, geo="point"),
                tmpl_code.format(n=n),
                "easy", ["template", "points"]))

    # ── 11) NurbsSurface creation ──
    surface_ops = [
        ("Create a NURBS surface from a grid of control points",
         f"{R3}\nmodel = rhino3dm.File3dm()\ndeg = 3\ncount_u, count_v = 6, 6\nsrf = rhino3dm.NurbsSurface.Create(3, False, deg+1, deg+1, count_u, count_v)\nfor i in range(count_u):\n    for j in range(count_v):\n        srf.Points.SetPoint(i, j, rhino3dm.Point3d(i*2, j*2, 0))\nmodel.Objects.AddSurface(srf)\nmodel.Write('surface.3dm', 7)",
         "hard", ["surface", "nurbs"]),
        ("Create a wavy NURBS surface",
         f"{R3}\nimport math\nmodel = rhino3dm.File3dm()\ndeg = 3\ncount_u, count_v = 10, 10\nsrf = rhino3dm.NurbsSurface.Create(3, False, deg+1, deg+1, count_u, count_v)\nfor i in range(count_u):\n    for j in range(count_v):\n        z = 2 * math.sin(i*0.5) * math.cos(j*0.5)\n        srf.Points.SetPoint(i, j, rhino3dm.Point3d(i*2, j*2, z))\nmodel.Objects.AddSurface(srf)\nmodel.Write('wavy_surface.3dm', 7)",
         "hard", ["surface", "wavy"]),
    ]
    for inst, code, diff, tags in surface_ops:
        pairs.append(m(inst, code, diff, tags))

    # ── 12) Practical standalone tasks ──
    practical = [
        ("Check if rhino3dm is installed and print version",
         f"{R3}\nprint(f'rhino3dm version: {{rhino3dm.__version__}}')",
         "easy", ["version", "check"]),
        ("Create an empty 3dm file",
         f"{R3}\nmodel = rhino3dm.File3dm()\nmodel.Write('empty.3dm', 7)\nprint('Empty file created')",
         "easy", ["empty", "file"]),
        ("Read a 3dm file and print its settings",
         f"{R3}\nmodel = rhino3dm.File3dm.Read('input.3dm')\nsettings = model.Settings\nprint(f'Model URL: {{settings.ModelUrl}}')",
         "easy", ["settings", "read"]),
        ("Duplicate all objects in a 3dm file with an offset",
         f"{R3}\nmodel = rhino3dm.File3dm.Read('input.3dm')\nnew_model = rhino3dm.File3dm()\nfor obj in model.Objects:\n    geo = obj.Geometry\n    new_model.Objects.Add(geo)\nnew_model.Write('duplicated.3dm', 7)",
         "medium", ["duplicate", "copy"]),
        ("Create a 3dm file with user-defined metadata in notes",
         f"{R3}\nmodel = rhino3dm.File3dm()\nmodel.Settings.ModelUrl = 'project_v1'\nmodel.Objects.AddPoint(rhino3dm.Point3d(0,0,0))\nmodel.Write('with_notes.3dm', 7)\nprint('File with metadata created')",
         "easy", ["metadata"]),
    ]
    for inst, code, diff, tags in practical:
        pairs.append(m(inst, code, diff, tags))

    return pairs
