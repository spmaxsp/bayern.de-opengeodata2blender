

import bpy
from tqdm import tqdm

def setup_blender_gis(srid, lat, lon, crs_x, crs_y):

    print("Setting CRS")
    bpy.context.scene["SRID"] = srid
    bpy.context.scene["crs x"] = crs_x
    bpy.context.scene["crs y"] = crs_y
    bpy.context.scene["latitude"] = lat
    bpy.context.scene["longitude"] = lon
    
    return True


def setup_city_json(crs_x, crs_y):
    world = bpy.context.scene.world
    if world is None:
        print("No world is assigned to the current scene.\n")
        return False

    bpy.context.scene.world["Axis_Origin_X_translation"] = -1 * crs_x
    bpy.context.scene.world["Axis_Origin_Y_translation"] = -1 * crs_y
    bpy.context.scene.world["Axis_Origin_Z_translation"] = 0
    bpy.context.scene.world["transform.X_translate"] = crs_x
    bpy.context.scene.world["transform.Y_translate"] = crs_y
    bpy.context.scene.world["transform.Z_translate"] = 0
    bpy.context.scene.world["transform.X_scale"] = 0.001
    bpy.context.scene.world["transform.Y_scale"] = 0.001
    bpy.context.scene.world["transform.Z_scale"] = 0.001
    bpy.context.scene.world["transformed"] = True
    return True


def batch_import_geotiff(files, collection_name="DEMs"):
    if not files:
        print("No GeoTIFF files given. Nothing to import.\n")
        return

    # Ensure the target collection exists
    if collection_name not in bpy.data.collections:
        dem_collection = bpy.data.collections.new(collection_name)
        bpy.context.scene.collection.children.link(dem_collection)
    else:
        dem_collection = bpy.data.collections[collection_name]

    for file_info in files:
        print(f"Importing GeoTIFF: {file_info['name']}")
        try:
            # Record objects in scene before import
            objs_before = set(bpy.context.scene.objects)

            bpy.ops.importgis.georaster(
                filepath=file_info['local'],
                importMode='DEM_RAW',
                fillNodata=True
            )

            # Record objects in scene after import
            objs_after = set(bpy.context.scene.objects)

            # Determine which objects were just added
            new_objs = objs_after - objs_before

            # Move new objects to DEM collection
            for obj in new_objs:
                # Unlink from current collections (optional)
                for coll in obj.users_collection:
                    coll.objects.unlink(obj)
                # Link to DEM collection
                dem_collection.objects.link(obj)

            print(f"  -> Successfully imported {len(new_objs)} object(s) into '{collection_name}'.\n")

        except Exception as e:
            print(f"  -> Failed to import: {file_info['local']}")
            print(f"     Error: {e}\n")
        
    
def batch_import_cityjson(files):

    if not files:
        print("No CityJson files given. Nothing to import.\n")
        return

    for file_info in files:
        print(f"Importing CityJson: {file_info['name']}")
        try:
            bpy.ops.cityjson.import_file(
                filepath=file_info['local'],
                clean_scene=False,
                reuse_materials=True,
                material_type='SURFACES'
            )
            print("  -> Successfully imported.\n")
        except Exception as e:
            print(f"  -> Failed to import: {file_info['local']}")
            print(f"     Error: {e}\n")

        clean_empty_objects()


def batch_import_ascii_grid(files, offset_x=0.0, offset_y=0.0, collection_name="DEMs"):

    if not files:
        print("No ASCII Grid files given. Nothing to import.\n")
        return

    print("Loading Points from ASCII Grid files...")
    pts = []
    for file_info in tqdm(files):
        with open(file_info['local'], "r") as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) == 3:
                    x, y, z = map(float, parts)
                    pts.append((x - offset_x, y - offset_y, z))


    pts.sort(key=lambda p: (p[1], p[0]))

    print("Total points loaded:", len(pts))
    print("Detecting grid spacing...")
    dx = None
    first_y = pts[0][1]

    for p in tqdm(pts[1:]):
        if abs(p[1] - first_y) < 1e-6:
            dx = abs(p[0] - pts[0][0])
            if dx > 1e-6:
                break

    dy = None
    for p in tqdm(pts):
        if abs(p[1] - first_y) > 1e-6:
            dy = abs(p[1] - first_y)
            break

    print("Detected dx =", dx, " dy =", dy)

    print("Computing grid indices...")
    min_x = min(p[0] for p in pts)
    min_y = min(p[1] for p in pts)

    grid = {}
    max_row = 0
    max_col = 0

    for (x, y, z) in tqdm(pts):
        col = round((x - min_x) / dx)
        row = round((y - min_y) / dy)

        grid[(row, col)] = z

        if row > max_row: max_row = row
        if col > max_col: max_col = col

    # Step 4: Build vertex list in (row-major order)
    verts = []
    index_map = {}   # (row,col) → vertex index

    for r in tqdm(range(max_row + 1)):
        for c in range(max_col + 1):
            if (r, c) in grid:
                z = grid[(r, c)]
                x = min_x + c * dx
                y = min_y + r * dy
                index_map[(r, c)] = len(verts)
                verts.append((x, y, z))
            else:
                index_map[(r, c)] = None  # missing

    # Step 5: Build faces
    faces = []

    for r in tqdm(range(max_row)):
        for c in range(max_col):

            v1 = index_map[(r, c)]
            v2 = index_map[(r, c+1)]
            v3 = index_map[(r+1, c+1)]
            v4 = index_map[(r+1, c)]

            # skip holes
            if None in (v1, v2, v3, v4):
                continue

            faces.append((v1, v2, v3, v4))

    print("Creating Blender mesh...")
    mesh = bpy.data.meshes.new("FastGridMesh")
    mesh.from_pydata(verts, [], faces)
    mesh.update()

    obj = bpy.data.objects.new("FastGridMesh", mesh)
    bpy.context.collection.objects.link(obj)

    #Move object to origin
    obj.location = (0.0, 0.0, 0.0)

    # Move to target collection
    if collection_name not in bpy.data.collections:
        dem_collection = bpy.data.collections.new(collection_name)
        bpy.context.scene.collection.children.link(dem_collection)
    else:
        dem_collection = bpy.data.collections[collection_name]
    dem_collection.objects.link(obj)