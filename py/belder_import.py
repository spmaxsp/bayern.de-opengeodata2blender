

import bpy

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
