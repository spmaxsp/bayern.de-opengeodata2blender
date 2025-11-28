
from urllib.parse import urlparse
import geopandas as gpd
import fiona
from tqdm import tqdm
import mathutils


def gen_tree_download_list(raw_download_list):
    file_list = []

    for url in raw_download_list:
        filename = os.path.basename(urlparse(url).path)
        file_list.append({"name": filename, "url": url, "local": None})

    return file_list

def parse_metalink(metalink_path):
    """
    Parses a .metalink file and returns a list of dictionaries:
    [{"name": filename, "url": download_url, "local": None}, ...]
    Only takes the first URL for each file.
    """
    tree = ET.parse(metalink_path)
    root = tree.getroot()
    
    # Metalink namespace
    ns = {"ml": "urn:ietf:params:xml:ns:metalink"}

    file_list = []
    for file_elem in root.findall("ml:file", ns):
        filename = file_elem.get("name")
        url_elem = file_elem.find("ml:url", ns)
        if url_elem is not None and url_elem.text:
            file_list.append({"name": filename, "url": url_elem.text, "local": None})

    return file_list


def create_cube(x, y, z, height, ratio, name, collection_name):
    if collection_name in bpy.data.collections:
        collection = bpy.data.collections[collection_name]
    else:
        collection = bpy.data.collections.new(collection_name)
        bpy.context.scene.collection.children.link(collection)

    bpy.ops.object.select_all(action='DESELECT')
    bpy.ops.mesh.primitive_cube_add(location=(x, y, z + height/2))
    cube = bpy.context.active_object
    cube.name = "MyCube"
    cube.scale = ((height*ratio)/2, (height*ratio)/2, height/2)

    for coll in cube.users_collection:
        coll.objects.unlink(cube)
    collection.objects.link(cube)

def create_cube_fast(x, y, z, height, ratio, name, collection):
    # Create mesh and object directly (avoids bpy.ops)
    mesh = bpy.data.meshes.new(name + "_mesh")
    cube = bpy.data.objects.new(name, mesh)

    # Link to collection
    collection.objects.link(cube)

    # Define geometry (8 vertices of a cube)
    hw = (height * ratio) / 2
    hh = height / 2
    verts = [
        (-hw, -hw, -hh),
        ( hw, -hw, -hh),
        ( hw,  hw, -hh),
        (-hw,  hw, -hh),
        (-hw, -hw,  hh),
        ( hw, -hw,  hh),
        ( hw,  hw,  hh),
        (-hw,  hw,  hh),
    ]
    faces = [
        (0, 1, 2, 3),
        (4, 5, 6, 7),
        (0, 1, 5, 4),
        (2, 3, 7, 6),
        (1, 2, 6, 5),
        (3, 0, 4, 7)
    ]

    # Create mesh geometry
    mesh.from_pydata(verts, [], faces)
    mesh.update()

    # Set cube location
    cube.location = mathutils.Vector((x, y, z + hh))

    return cube


def import_trees(files, min_x, min_y, max_x, max_y, origin_utm32_x, origin_utm32_y, collection_name="Trees"):
    if collection_name in bpy.data.collections:
        collection = bpy.data.collections[collection_name]
    else:
        collection = bpy.data.collections.new(collection_name)
        bpy.context.scene.collection.children.link(collection)

    if not files:
        print("No GPKG files given. Nothing to import.\n")
        return

    for file_info in files:
        print(f"Importing GPKG: {file_info['name']}")

        # List all layers
        layers = fiona.listlayers(file_info['local'])
        print("Layers found in GeoPackage:", layers)

        # Iterate over all layers
        for layer in layers:
            print(f"\nProcessing layer: {layer}")
            gdf = gpd.read_file(file_info['local'], layer=layer, bbox=(min_x, min_y, max_x, max_y))
            total_trees = len(gdf)
            print(f"Total number of trees in this layer: {total_trees}")

            # Create trees object
            mesh = bpy.data.meshes.new(f"trees_{layer}" + "_mesh")
            cube = bpy.data.objects.new(f"trees_{layer}", mesh)
            collection.objects.link(cube)

            faces = []
            verts = []
            i = 0
            ratio = 0.6  # width-to-height ratio of the tree cubes

            for idx, row in tqdm(gdf.iterrows()):
                geom = row.geometry
                if geom.geom_type != "MultiPoint":
                    continue

                height = row.baumhoehe
                z = row.dgmhoehe

                for point in geom.geoms:
                    x, y = point.x, point.y

                    x -= origin_utm32_x
                    y -= origin_utm32_y

                    # Add geometry (8 vertices of a cube)
                    hw = (height * ratio) / 2
                    hh = height / 2
                    z = z + hh  # center the cube vertically
                    i = len(verts)
                    verts.append((x-hw, y-hw, z-hh) )
                    verts.append(( x+hw, y-hw, z-hh))
                    verts.append(( x+hw, y+hw, z-hh))
                    verts.append(( x-hw, y+hw, z-hh))
                    verts.append(( x-hw, y-hw, z+hh))
                    verts.append(( x+hw, y-hw, z+hh))
                    verts.append(( x+hw, y+hw, z+hh))
                    verts.append(( x-hw, y+hw, z+hh))

                    faces.append((i+0, i+1, i+2, i+3))
                    faces.append((i+4, i+5, i+6, i+7))
                    faces.append((i+0, i+1, i+5, i+4))
                    faces.append((i+2, i+3, i+7, i+6))
                    faces.append((i+1, i+2, i+6, i+5))
                    faces.append((i+3, i+0, i+4, i+7))

            # Create mesh geometry
            mesh.from_pydata(verts, [], faces)
            mesh.update()

                    #create_cube_fast(x-origin_utm32_x, y-origin_utm32_y, z, height, 0.6, f"tree_{layer}_{idx + 1}", collection)
                    #print(f"Tree {idx + 1}: Location=({x:.2f}, {y:.2f}, {z:.2f}), Height={height}m")