

from pyproj import Transformer
import os


def print_header(title: str):
    """Print a clean header section in the Blender console."""
    line = "=" * 80
    print("\n" + line)
    print(f"{title.upper():^80}")
    print(line + "\n")
    
    
    
def wgs84_to_utm32(lat, lon):
    """
    Convert WGS84 coordinates (latitude, longitude)
    to UTM zone 32N (EPSG:25832).
    Returns (x, y) in meters.
    """
    transformer = Transformer.from_crs("EPSG:4326", "EPSG:25832", always_xy=True)
    x, y = transformer.transform(lon, lat)
    return x, y


def setup_structure(base_dir):
    """
    Creates a folder structure:
    temp/
        LoD2/
            gml/
            json/
        DGM1/
        tree/
        DGM5/
    """
    # Define folder paths
    lod2_dir = os.path.join(base_dir, "LoD2")
    lod2_gml_dir = os.path.join(lod2_dir, "gml")
    lod2_json_dir = os.path.join(lod2_dir, "json")
    dgm1_dir = os.path.join(base_dir, "DGM1")
    tree_dir = os.path.join(base_dir, "tree")
    dgm5_dir = os.path.join(base_dir, "DGM5")

    # Create all directories if they don't exist
    for folder in [lod2_dir, lod2_gml_dir, lod2_json_dir, dgm1_dir, tree_dir, dgm5_dir]:
        os.makedirs(folder, exist_ok=True)

    return {
        "base": base_dir,
        "lod2_gml": lod2_gml_dir,
        "lod2_json": lod2_json_dir,
        "dgm1": dgm1_dir,
        "tree": tree_dir,
        "dgm5": dgm5_dir
    }

def extract_ascii_grids(dgm5_files, output_dir):
    """
    Extract ASCII grid files from downloaded DGM5 ZIP files.
    """
    import zipfile

    for file_info in dgm5_files:
        local_path = file_info.get("local")
        if local_path and local_path.endswith(".zip"):
            with zipfile.ZipFile(local_path, 'r') as zip_ref:
                zip_ref.extractall(output_dir)
                print(f"Extracted {local_path} to {output_dir}")
                dgm_ascii_path = os.path.join(output_dir, file_info["name"].replace(".zip", ".txt"))
                file_info["local"] = dgm_ascii_path  # Update path to point to extracted ASCII grid

    return dgm5_files