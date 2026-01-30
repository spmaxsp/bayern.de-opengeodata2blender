

from datetime import datetime
import requests
import xml.etree.ElementTree as ET
from tqdm import tqdm


def download_metalink(url, optionstring, base_dir, datatype, projectname):
    """
    Downloads a metalink file via POST request and saves it to base_dir.
    The filename is generated using projectname, date, and datatype.
    """
    # Generate filename
    today = datetime.now().strftime("%Y%m%d")
    filename = f"{projectname}_{today}_{datatype}.metalink"
    filepath = os.path.join(base_dir, filename)

    # # Skip download if file already exists
    # if os.path.exists(filepath):
    #     print(f"Metalink already exists: {filename}")
    #     return filepath

    # Send POST request
    response = requests.post(url, data=optionstring)
    if response.status_code == 200:
        with open(filepath, "wb") as f:
            f.write(response.content)
        print(f"Metalink downloaded: {filename}")
        return filepath
    else:
        raise Exception(f"Failed to download metalink. Status code: {response.status_code}")
    

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


def download_meta_files(files_list, target_dir):
    """
    Downloads files given a list of dictionaries [{"name": filename, "url": download_url}].
    Respects REPLACE_EXISTING_FILES flag.
    Shows a progress bar for each file.
    """
    for file_info in files_list:
        filename = file_info["name"]
        url = file_info["url"]
        file_path = os.path.join(target_dir, filename)

        if os.path.exists(file_path) and not REPLACE_EXISTING_FILES:
            print(f"Skipping existing file: {filename}")
            file_info["local"] = file_path
            continue

        print(f"Downloading: {filename} from {url}")
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            total_size = int(response.headers.get('content-length', 0))
            chunk_size = 8192

            with open(file_path, "wb") as f, tqdm(
                total=total_size, unit='B', unit_scale=True, desc=filename, ncols=80
            ) as pbar:
                for chunk in response.iter_content(chunk_size=chunk_size):
                    if chunk:
                        f.write(chunk)
                        pbar.update(len(chunk))

            print(f"Downloaded: {filename}\n")
            file_info["local"] = file_path
        else:
            print(f"Failed to download {filename}, status code: {response.status_code}")

    return files_list

