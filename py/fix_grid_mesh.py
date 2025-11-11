
import bpy
import bmesh
from mathutils import Vector
from tqdm import tqdm


def fix_terrain_mesh(collection_name="DEMs"):
    """Fixes a terrain mesh made from tiled DEMs by remeshing it into a continuous surface.
    
    Assumes all terrain tiles are in a collection named 'DEMs'.
    Merges all meshes, removes duplicate vertices, and fills gaps between tiles.
    """

    print (f"Fixing terrain mesh in collection '{collection_name}'...")

    if collection_name not in bpy.data.collections:
        raise ValueError(f"Collection '{collection_name}' not found!")

    dem_collection = bpy.data.collections[collection_name]

    # Join all meshes in the DEM collection
    print ("Joining terrain meshes...")
    terrain_objects = [obj for obj in dem_collection.objects if obj.type == 'MESH']
    if not terrain_objects:
        raise ValueError(f"No mesh objects found in collection '{collection_name}'.")

    bpy.ops.object.select_all(action='DESELECT')

    for o in terrain_objects:
        o.select_set(True)

    bpy.context.view_layer.objects.active = terrain_objects[0]
    bpy.ops.object.join()

    obj = bpy.context.active_object
    mesh = obj.data

    # Build a BMesh from the object
    print ("Building BMesh...")
    bm = bmesh.new()
    bm.from_mesh(mesh)

    # Merge duplicate vertices first (seams often overlap)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.001)

    # Sort vertices into a 2D grid by X/Y
    verts = list(bm.verts)
    verts.sort(key=lambda v: (round(v.co.y, 3), round(v.co.x, 3)))  # row-major

    # Compute grid size
    xs = sorted(set(round(v.co.x, 3) for v in verts))
    ys = sorted(set(round(v.co.y, 3) for v in verts))
    nx, ny = len(xs), len(ys)

    print(f"Grid detected: {nx} x {ny} vertices")

    # Map coordinates to vertices
    coord_map = {(round(v.co.x, 3), round(v.co.y, 3)): v for v in verts}

    face_exists = bm.faces.get  # local reference for speed

    # Create faces for missing quads
    print ("Creating faces for missing quads...")
    for j in tqdm(range(ny - 1)):
        for i in range(nx - 1):
            v1 = coord_map[(xs[i], ys[j])]
            v2 = coord_map[(xs[i+1], ys[j])]
            v3 = coord_map[(xs[i+1], ys[j+1])]
            v4 = coord_map[(xs[i], ys[j+1])]
            
            # Only create if face doesn't exist
            if not face_exists((v1, v2, v3, v4)):
                bm.faces.new((v1, v2, v3, v4))

    # Write back to mesh
    print ("Writing back to mesh...")
    bm.to_mesh(mesh)
    bm.free()

    # Recalculate normals and update viewport
    print ("Recalculating normals...")
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.normals_make_consistent(inside=False)
    bpy.ops.object.mode_set(mode='OBJECT')

    print(f"Terrain from collection '{collection_name}' successfully remeshed as continuous surface!")
