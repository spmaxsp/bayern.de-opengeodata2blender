
# from global_helpers import setup_structure, wgs84_to_utm32, print_header
# from opengeodata import download_metalink, parse_metalink, download_meta_files
# from cityjson import convert_to_cityjson

# from blender_helper import clean_scene
# from belder_import import setup_city_json, setup_blender_gis, batch_import_cityjson, batch_import_geotiff

# no imports needed because blender has already loaded all required files !!!!!!!!!!!!!!!

if __name__ == "__main__":
    
    print_header("RUNNING IMPORTER (PHASE 0: SETUP)...")
    
    print("Initializing folder structure...")
    dirs = setup_structure(TMP_PATH)
    print(dirs)
    
    if CLEAN_BLENDER:
        print("Cleaning blender-scene...")
        clean_scene()
        
    
    print_header("RUNNING IMPORTER (PHASE I: DOWNLOAD FILES)...")

    print("Downloading metalink files...")
    if IMPORT_BUILDINGS:
        lod2_metalink_file = download_metalink(DOWNLOAD_LINKS["lod2"], EWKT_STR, dirs["base"], "lod2", PROJECT_NAME)
    if IMPORT_TERRAIN:
        dgm1_metalink_file = download_metalink(DOWNLOAD_LINKS["dgm1"], EWKT_STR, dirs["base"], "dgm1", PROJECT_NAME)

    print("Parsing metalink files...")
    if IMPORT_BUILDINGS:
        lod2_files = parse_metalink(lod2_metalink_file)
        print("LoD2 Files:")
        for file_info in lod2_files:
            print(f"  {file_info['name']}: {file_info['url']}")
    if IMPORT_TERRAIN:
        dgm1_files = parse_metalink(dgm1_metalink_file)
        print("DGM1 Files:")
        for file_info in dgm1_files:
            print(f"  {file_info['name']}: {file_info['url']}")

    print("Downloading files...")
    if IMPORT_BUILDINGS:
        lod2_files = download_meta_files(lod2_files, dirs["lod2_gml"])
    if IMPORT_TERRAIN:
        dgm1_files = download_meta_files(dgm1_files, dirs["dgm1"])

    print("\nSummary of downloaded files:")
    if IMPORT_BUILDINGS:
        print("LoD2 Files:")
        for file_info in lod2_files:
            if file_info["local"]:
                print(f"  {file_info['name']}: {file_info['local']}")
    if IMPORT_TERRAIN:
        print("DGM1 Files:")
        for file_info in dgm1_files:
            if file_info["local"]:
                print(f"  {file_info['name']}: {file_info['local']}")

    print("All downloads completed.")
    
    if IMPORT_BUILDINGS:
        print("Converting LoD2 GML files to CityJSON...")
        lod2_files = convert_to_cityjson(lod2_files, dirs["lod2_json"])
    
    
    print_header("RUNNING IMPORTER (PHASE II: SETUP SCENE)...")

    origin_utm32_x, origin_utm32_y = wgs84_to_utm32(LATITUDE_SCENE_ORIGIN, LONGITUDE_SCENE_ORIGIN)
    print(f"Origin in UTM32: X={origin_utm32_x:.2f}, Y={origin_utm32_y:.2f}")
    setup_blender_gis("EPSG:25832", LONGITUDE_SCENE_ORIGIN, LONGITUDE_SCENE_ORIGIN, origin_utm32_x, origin_utm32_y)
    setup_city_json(origin_utm32_x, origin_utm32_y)

    print_header("RUNNING IMPORTER (PHASE III: LOAD GROUND)...")
    
    if IMPORT_TERRAIN:
        batch_import_geotiff(dgm1_files)
        fix_terrain_mesh()

    print_header("RUNNING IMPORTER (PHASE IV: LOAD BUILDINGS)...")
    
    if IMPORT_BUILDINGS:
        batch_import_cityjson(lod2_files)

    print_header("RUNNING IMPORTER (PHASE V: FINALIZE SCENE)...")

    clean_empty_objects()
    
    assign_material_to_collection("DEMs", "itu_concrete", (0.6, 0.6, 0.6, 1))
    assign_material_to_collection("LoD2", "itu_brick", (0.7, 0.2, 0.2, 1))

    min_x, min_y = wgs84_to_utm32(LATITUDE_FROM, LONGITUDE_FROM)
    max_x, max_y = wgs84_to_utm32(LATITUDE_TO, LONGITUDE_TO)
    min_x -= origin_utm32_x
    min_y -= origin_utm32_y
    max_x -= origin_utm32_x
    max_y -= origin_utm32_y

    delete_all_objects_outside_range(min_x, max_x, min_y, max_y)

    print_header("IMPORTER FINISHED.")