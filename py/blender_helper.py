

import bpy


def clean_scene():
    # Select everything
    bpy.ops.object.select_all(action='SELECT')
    # Delete all selected objects
    bpy.ops.object.delete(use_global=False)
    
    # Remove all collections except the main one
    for collection in bpy.data.collections:
        bpy.data.collections.remove(collection)
    
    # Remove all meshes, materials, etc. to really clean it up
    for datablock in (
        bpy.data.meshes,
        bpy.data.materials,
        bpy.data.images,
        bpy.data.textures,
        bpy.data.curves,
        bpy.data.cameras,
        bpy.data.lights,
    ):
        for block in datablock:
            datablock.remove(block)
    


def clean_empty_objects():
    print ("Cleaning up EMPTY-type objects...")
    # Deselect all objects
    bpy.ops.object.select_all(action='DESELECT')
    
    # Iterate through all objects in the scene
    for obj in bpy.data.objects:
        # Check if the object is an empty
        if obj.type == 'EMPTY':
            obj.select_set(True)

    # Delete selected empties
    bpy.ops.object.delete()


def assign_material_to_collection(collection_name, material_name, color=(1, 1, 1, 1), clean_unused=True):
    """
    Create (or get) a material and assign it to all mesh objects in a collection.
    Optionally remove all unused materials afterwards.

    Args:
        collection_name (str): Name of the target collection.
        material_name (str): Name of the material to create/use.
        color (tuple): RGBA color for the material (default white).
        clean_unused (bool): Whether to remove unused materials after assignment.
    """

    # --- Get or create collection ---
    collection = bpy.data.collections.get(collection_name)
    if not collection:
        print(f"Collection '{collection_name}' not found. Aborting material assignment.")
        return

    # --- Create or get material ---
    if material_name in bpy.data.materials:
        mat = bpy.data.materials[material_name]
    else:
        mat = bpy.data.materials.new(name=material_name)
        mat.use_nodes = False
        mat.diffuse_color = color

    # --- Assign material to all mesh objects in the collection ---
    print(f"Assigning material '{material_name}' to all mesh objects in collection '{collection_name}'...")
    for obj in collection.objects:
        if obj.type == 'MESH':
            mesh = obj.data
            mesh.materials.clear()
            mesh.materials.append(mat)


    # --- Clean up unused materials ---
    if clean_unused:
        print("Cleaning up unused materials...")
        removed = 0
        for m in list(bpy.data.materials):
            # Remove only materials that have no users and are not fake users
            if m.users == 0 and not m.use_fake_user:
                bpy.data.materials.remove(m)
                removed += 1

def delete_all_objects_outside_range(min_x, max_x, min_y, max_y):
    """
    Deletes all objects in the scene that are outside the specified X/Y range.

    Args:
        min_x (float): Minimum X coordinate.
        max_x (float): Maximum X coordinate.
        min_y (float): Minimum Y coordinate.
        max_y (float): Maximum Y coordinate.
    """
    
    # Expand the range slightly to avoid edge cases
    min_x -= 10
    min_y -= 10
    max_x += 10
    max_y += 10

    print(f"Delete objects completely outside range:")
    print(f"   X: {min_x} to {max_x}, Y: {min_y} to {max_y}")

    # Deselect everything first
    bpy.ops.object.select_all(action='DESELECT')

    # Function to check if an object's bounding box is outside the given range
    def is_outside_xy_bounds(obj, min_x, max_x, min_y, max_y):
        # Compute the world-space coordinates of the bounding box corners
        world_coords = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
        xs = [v.x for v in world_coords]
        ys = [v.y for v in world_coords]
        
        # If the entire object is outside the bounds, return True
        if max(xs) < min_x or min(xs) > max_x or max(ys) < min_y or min(ys) > max_y:
            return True
        return False

    # Loop through all objects in the scene
    for obj in bpy.data.objects:
        # You can limit this to meshes if you want:
        if obj.type != 'MESH':
            continue

        if is_outside_xy_bounds(obj, min_x, max_x, min_y, max_y):
            obj.select_set(True)

    # Delete all selected objects
    bpy.ops.object.delete()

    
