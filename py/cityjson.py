

import os
import shlex


def convert_to_cityjson(files, output_dir, java_path=JAVA_PATH, citygmltools_path=CITYGMLTOOLS_PATH):
    """
    Converts a GML file to CityJSON using CityGMLTools.
    Requires JAVA_PATH and CITYGMLTOOLS_PATH to be set.
    """

    for file_info in files:
        gml_file = file_info["local"]
        if gml_file is None:
            print(f"Skipping conversion for {file_info['name']} as it was not downloaded.")
            continue

        abs_input_file = os.path.abspath(gml_file)
        abs_output_file = abs_input_file.replace(".gml", ".json")
        abs_output_file_move = os.path.join(os.path.abspath(output_dir), f"{os.path.splitext(file_info['name'])[0]}.json")

        # If output file exists and REPLACE_EXISTING_FILES is False, skip conversion
        if os.path.exists(abs_output_file_move) and not REPLACE_EXISTING_FILES:
            file_info["local"] = abs_output_file_move
            print(f"Skipping conversion for existing file: {abs_output_file_move}")
            continue

        # Set up environment for Java
        env = os.environ.copy()
        env["JAVA_HOME"] = java_path

        # Construct the command
        cmd = f'"{citygmltools_path}" to-cityjson "{abs_input_file}"'

        print(f"\nRunning CityGMLTools for {file_info['name']}...")

        try:
            result = subprocess.run(
                shlex.split(cmd),
                env=env,
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                print(f"Successfully converted {file_info['name']} to CityJSON")
            else:
                print(f"Conversion failed for {file_info['name']}")
                print(f"STDERR:\n{result.stderr.strip()}")
                print(f"STDOUT:\n{result.stdout.strip()}")
        except Exception as e:
            print(f"Failed to run citygml-tools: {e}")
        finally:
            print(f"Moving {abs_output_file} to {abs_output_file_move}...")
            # Determine if the output file was created
            if os.path.exists(abs_output_file):
                try:
                    os.replace(abs_output_file, abs_output_file_move)
                    file_info["local"] = abs_output_file_move
                except Exception as e:
                    print(f"Failed to move file: {e}")

    return files