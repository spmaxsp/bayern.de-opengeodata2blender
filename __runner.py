import subprocess, sys
import bpy
subprocess.check_call([sys.executable, "-m", "pip", "install", "pyproj"])
subprocess.check_call([sys.executable, "-m", "pip", "install", "tqdm"])
subprocess.check_call([sys.executable, "-m", "pip", "install", "geopandas"])
subprocess.check_call([sys.executable, "-m", "pip", "install", "fiona"])

print("Enabling Blender GIS Add-ons")
for name in ["BlenderGIS-master", "Up3date-main"]:
    if (bpy.ops.preferences.addon_enable(module=name) == {'FINISHED'}):
        print(f"{name} enabled successfully.")
    else:
        print(f"Could not enable {name} \n Please ensure {name} is installed correctly.")
        raise ValueError

print("--------------------------------------------------")

_scripts_folder = "py"
_scripts = (
    "belder_import.py",
    "blender_helper.py",
    "cityjson.py",
    "global_helpers.py",
    "opengeodata.py",
    "fix_grid_mesh.py",
    "trees.py",
    "main.py"
)


PROJECT_NAME = "MyProject"

LATITUDE_FROM = 49.96908484
LONGITUDE_FROM = 9.1313874
LATITUDE_TO = 49.98641652
LONGITUDE_TO = 9.16554802

LATITUDE_SCENE_ORIGIN = 49.9718674767623
LONGITUDE_SCENE_ORIGIN = 9.161292440683683

IMPORT_TERRAIN = False
IMPORT_BUILDINGS = False
IMPORT_TREES = True

REPLACE_EXISTING_FILES = False
CLEAN_BLENDER = True


DOWNLOAD_LINKS = {
    "dgm1": "https://geoservices.bayern.de/services/poly2metalink/metalink/dgm1",
    "lod2": "https://geoservices.bayern.de/services/poly2metalink/metalink/lod2"
}
DOWNLOAD_LINK_TREES = ["https://geodaten.bayern.de/odd/m/8/baeume3d/data/123007_baeume.gpkg"] 
EWKT_STR = f"SRID=4326;POLYGON(({LONGITUDE_FROM} {LATITUDE_FROM},{LONGITUDE_FROM} {LATITUDE_TO},{LONGITUDE_TO} {LATITUDE_TO},{LONGITUDE_TO} {LATITUDE_FROM},{LONGITUDE_FROM} {LATITUDE_FROM}))"
TMP_PATH = "C:\\Users\\USER\\Documents\\opengeodata2blender\\temp\\"
JAVA_PATH = "C:\\Users\\USER\\Documents\\opengeodata2blender\\toolchain\\jdk-25.0.1\\"
CITYGMLTOOLS_PATH = "C:\\Users\\USER\\Documents\\opengeodata2blender\\toolchain\\citygml-tools-2.4.0\\citygml-tools.bat"  # Path to CityGMLTools jar file, if needed for further processing



####################################################################################################
# Based on 'bpy.types.WindowManager.popup_menu' in Blender 2.83.0 Python API documentation.    
# Search: popup_menu

def error_message_draw(self, context):
    self.layout.label(text=g_error_message)

def error_message(message):
    global g_error_message
    g_error_message = message
    bpy.context.window_manager.popup_menu(error_message_draw, title="Error", icon='ERROR')


####################################################################################################

import os

_dir = os.path.join(os.path.dirname(bpy.data.filepath), _scripts_folder)

for filename in _scripts:
    _script_filepath = os.path.join(_dir, filename)

    # Check if the script file exists, and if it's not checked then you will never know if the script file
    # is not found when this text editor is hidden during first start of blender because you won't see
    # an error message.
    if not os.path.exists(_script_filepath):
        error_message(f'The file "{filename}" is not found, if the project is zipped, then extract it.')
    else:
        exec(open(_script_filepath).read())