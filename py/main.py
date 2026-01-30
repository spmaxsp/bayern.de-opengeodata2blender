
# from global_helpers import setup_structure, wgs84_to_utm32, print_header
# from opengeodata import download_metalink, parse_metalink, download_meta_files
# from cityjson import convert_to_cityjson

# from blender_helper import clean_scene
# from belder_import import setup_city_json, setup_blender_gis, batch_import_cityjson, batch_import_geotiff

# no imports needed because blender has already loaded all required files !!!!!!!!!!!!!!!

import json

if __name__ == "__main__":

    if USE_CONFIGURATION_FILE:
        print("Loading configuration from file...")
        with open(CONFIGURATION_FILEPATH, 'r') as config_file:
            config = json.load(config_file)

            PROJECT_NAME = config["meta"]["title"]
            LATITUDE_FROM = config["area"]["ne"]["lat"]
            LONGITUDE_FROM = config["area"]["ne"]["lng"]
            LATITUDE_TO = config["area"]["sw"]["lat"]
            LONGITUDE_TO = config["area"]["sw"]["lng"]
            LATITUDE_SCENE_ORIGIN = config["origin"]["lat"]
            LONGITUDE_SCENE_ORIGIN = config["origin"]["lng"]
            IMPORT_TERRAIN = config["import"]["terrain"]
            IMPORT_BUILDINGS = config["import"]["buildings"]
            IMPORT_TREES = config["import"]["trees"]
            TERRAIN_HIGH_RESOLUTION = False
            REPLACE_EXISTING_FILES = config["import"]["replaceExistingFiles"]
            CLEAN_BLENDER = config["import"]["cleanBlender"]

    print("Configuration:")
    print(f"  Project Name: {PROJECT_NAME}")
    print(f"  Area from ({LATITUDE_FROM}, {LONGITUDE_FROM}) to ({LATITUDE_TO}, {LONGITUDE_TO})")
    print(f"  Scene Origin: ({LATITUDE_SCENE_ORIGIN}, {LONGITUDE_SCENE_ORIGIN})")
    print(f"  Import Terrain: {IMPORT_TERRAIN}")
    print(f"  Import Buildings: {IMPORT_BUILDINGS}")
    print(f"  Import Trees: {IMPORT_TREES}")
    print(f"  Replace Existing Files: {REPLACE_EXISTING_FILES}")
    print(f"  Clean Blender: {CLEAN_BLENDER}")

    print_header("RUNNING IMPORTER (PHASE 0: SETUP)...")
    
    print("Initializing folder structure...")
    dirs = setup_structure(TMP_PATH)
    print(dirs)
    
    if CLEAN_BLENDER:
        print("Cleaning blender-scene...")
        clean_scene()
        
    
    print_header("RUNNING IMPORTER (PHASE I: DOWNLOAD FILES)...")

    print("Downloading metalink files...")
    EWKT_STR = f"SRID=4326;POLYGON(({LONGITUDE_FROM} {LATITUDE_FROM},{LONGITUDE_FROM} {LATITUDE_TO},{LONGITUDE_TO} {LATITUDE_TO},{LONGITUDE_TO} {LATITUDE_FROM},{LONGITUDE_FROM} {LATITUDE_FROM}))"
    if IMPORT_BUILDINGS:
        lod2_metalink_file = download_metalink(DOWNLOAD_LINKS["lod2"], EWKT_STR, dirs["base"], "lod2", PROJECT_NAME)
    if IMPORT_TERRAIN and TERRAIN_HIGH_RESOLUTION:
        dgm1_metalink_file = download_metalink(DOWNLOAD_LINKS["dgm1"], EWKT_STR, dirs["base"], "dgm1", PROJECT_NAME)
    if IMPORT_TERRAIN and not TERRAIN_HIGH_RESOLUTION:
        dgm5_metalink_file = download_metalink(DOWNLOAD_LINKS["dgm5"], EWKT_STR, dirs["base"], "dgm5", PROJECT_NAME)

    print("Parsing metalink files...")
    if IMPORT_BUILDINGS:
        lod2_files = parse_metalink(lod2_metalink_file)
        print("LoD2 Files:")
        for file_info in lod2_files:
            print(f"  {file_info['name']}: {file_info['url']}")
    if IMPORT_TERRAIN and TERRAIN_HIGH_RESOLUTION:
        dgm1_files = parse_metalink(dgm1_metalink_file)
        print("DGM1 Files:")
        for file_info in dgm1_files:
            print(f"  {file_info['name']}: {file_info['url']}")
    if IMPORT_TERRAIN and not TERRAIN_HIGH_RESOLUTION:
        dgm5_files = parse_metalink(dgm5_metalink_file)
        print("DGM5 Files:")
        for file_info in dgm5_files:
            print(f"  {file_info['name']}: {file_info['url']}")
    if IMPORT_TREES:
        tree_files = gen_tree_download_list(DOWNLOAD_LINK_TREES)
        print("GEOPACKAGE Files:")
        for file_info in tree_files:
            print(f"  {file_info['name']}: {file_info['url']}")

    print("Downloading files...")
    if IMPORT_BUILDINGS:
        lod2_files = download_meta_files(lod2_files, dirs["lod2_gml"])
    if IMPORT_TERRAIN and TERRAIN_HIGH_RESOLUTION:
        dgm1_files = download_meta_files(dgm1_files, dirs["dgm1"])
    if IMPORT_TERRAIN and not TERRAIN_HIGH_RESOLUTION:
        dgm5_files = download_meta_files(dgm5_files, dirs["dgm5"])
        dgm5_files = extract_ascii_grids(dgm5_files, dirs["dgm5"])
    if IMPORT_TREES:
        tree_files = download_meta_files(tree_files, dirs["tree"])

    print("\nSummary of downloaded files:")
    if IMPORT_BUILDINGS:
        print("LoD2 Files:")
        for file_info in lod2_files:
            if file_info["local"]:
                print(f"  {file_info['name']}: {file_info['local']}")
    if IMPORT_TERRAIN and TERRAIN_HIGH_RESOLUTION:
        print("DGM1 Files:")
        for file_info in dgm1_files:
            if file_info["local"]:
                print(f"  {file_info['name']}: {file_info['local']}")
    if IMPORT_TERRAIN and not TERRAIN_HIGH_RESOLUTION:
        print("DGM5 Files:")
        for file_info in dgm5_files:
            if file_info["local"]:
                print(f"  {file_info['name']}: {file_info['local']}")
    if IMPORT_TREES:
        print("GEOPACKAGE Files:")
        for file_info in tree_files:
            if file_info["local"]:
                print(f"  {file_info['name']}: {file_info['local']}")

    print("All downloads completed.")
    
    if IMPORT_BUILDINGS:
        print("Converting LoD2 GML files to CityJSON...")
        lod2_files = convert_to_cityjson(lod2_files, dirs["lod2_json"])
    
    
    print_header("RUNNING IMPORTER (PHASE II: SETUP SCENE)...")

    origin_utm32_x, origin_utm32_y = wgs84_to_utm32(LATITUDE_SCENE_ORIGIN, LONGITUDE_SCENE_ORIGIN)
    print(f"Origin in UTM32: X={origin_utm32_x:.2f}, Y={origin_utm32_y:.2f}")
    
    min_x, min_y = wgs84_to_utm32(LATITUDE_FROM, LONGITUDE_FROM)
    max_x, max_y = wgs84_to_utm32(LATITUDE_TO, LONGITUDE_TO)

    setup_blender_gis("EPSG:25832", LONGITUDE_SCENE_ORIGIN, LONGITUDE_SCENE_ORIGIN, origin_utm32_x, origin_utm32_y)
    setup_city_json(origin_utm32_x, origin_utm32_y)

    print_header("RUNNING IMPORTER (PHASE III: LOAD BUILDINGS)...")
    
    if IMPORT_BUILDINGS:
        batch_import_cityjson(lod2_files)
        min_x_fromorigin = min_x - origin_utm32_x
        min_y_fromorigin = min_y - origin_utm32_y
        max_x_fromorigin = max_x - origin_utm32_x
        max_y_fromorigin = max_y - origin_utm32_y
        delete_all_objects_outside_range(min_x_fromorigin, max_x_fromorigin, min_y_fromorigin, max_y_fromorigin)

    print_header("RUNNING IMPORTER (PHASE IV: LOAD GROUND)...")
    
    if IMPORT_TERRAIN:
        if TERRAIN_HIGH_RESOLUTION:
            batch_import_geotiff(dgm1_files)
            fix_terrain_mesh()
        else:
            batch_import_ascii_grid(dgm5_files, offset_x=origin_utm32_x, offset_y=origin_utm32_y)

    print_header("RUNNING IMPORTER (PHASE V: LOAD TREES)...")
    
    if IMPORT_TREES:
        import_trees(tree_files, min_x, min_y, max_x, max_y, origin_utm32_x, origin_utm32_y)

    print_header("RUNNING IMPORTER (PHASE VI: FINALIZE SCENE)...")

    
    
    assign_material_to_collection("DEMs", "itu_concrete", (0.6, 0.6, 0.6, 1))
    assign_material_to_collection("LoD2", "itu_brick", (0.7, 0.2, 0.2, 1))
    assign_material_to_collection("Trees", "itu_wood", (0.1, 0.7, 0.2, 1))

    print_header("IMPORTER FINISHED.")

    last_run_time = None
    blender_file_path = None
    mitsuba_export_path = None

    template_path = bpy.data.filepath
    template_dir = os.path.dirname(template_path)

    if SAVE_AS_COPY:
        print("Saving Blender file...")
        
        blender_file_path = os.path.join(template_dir, f"{PROJECT_NAME}.blend")
        print(f"  Output Path: {blender_file_path}")
        bpy.ops.wm.save_as_mainfile(
            filepath=blender_file_path,
            copy=True
        )
        last_run_time = datetime.now().isoformat()
        print("Blender file saved.")

    if AUTO_EXPORT_MITSUBA:
        print("Exporting scene to Mitsuba format...")


        # Create Mitsuba output directory
        mitsuba_dir = os.path.join(template_dir, f"mitsuba_{PROJECT_NAME}")
        os.makedirs(mitsuba_dir, exist_ok=True)

        # Output XML path
        mitsuba_export_path = os.path.join(mitsuba_dir, f"{PROJECT_NAME}.xml")
        bpy.ops.export_scene.mitsuba(
            filepath=mitsuba_export_path,
            export_ids=True,
            axis_forward='Y',
            axis_up='Z'
        )
        print("Mitsuba export written to:", mitsuba_export_path)


    if USE_CONFIGURATION_FILE:
        print("Writing back status to configuration file...")
        with open(CONFIGURATION_FILEPATH, 'r+') as config_file:
            config = json.load(config_file)
            config["status"]["lastBlenderRun"] = last_run_time
            config["status"]["blenderFile"] = blender_file_path
            config["status"]["mitsubaFile"] = os.path.relpath(mitsuba_export_path, template_dir) if mitsuba_export_path else None
            config_file.seek(0)
            json.dump(config, config_file, indent=4)
            config_file.truncate()