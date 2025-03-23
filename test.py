import os
import subprocess
from pathlib import Path

def find_tool(source_directory, search_app):
    for root, dirs, files in os.walk(source_directory):
        if search_app in files:
            tool_path = os.path.join(root, search_app)
            print(f"{search_app} tool found here: {tool_path}")
            return tool_path
    print(f"{search_app} not found.")
    return None

def find_env_file(extract_path):
    msix_bundle_path = None
    msix_bundle_name = None
    for root, dirs, files in os.walk(extract_path):
        for file in files:
            if file.endswith(".msixbundle") and ("x64" in file or "ARM64" in file):
                msix_bundle_path = root
                msix_bundle_name = file
                break
        if msix_bundle_path:
            break

    if not msix_bundle_path or not msix_bundle_name:
        print("No MSIX bundle found.")
        return

    msix_bundle_file = os.path.join(msix_bundle_path, msix_bundle_name)
    msix_bundle_new_directory = os.path.join(msix_bundle_path, msix_bundle_name)
    os.makedirs(msix_bundle_new_directory, exist_ok=True)
    subprocess.run([zip_app, "x", msix_bundle_file, f"-o{msix_bundle_new_directory}", "-aoa"], check=True)

    msix_path = None
    msix_name = None
    for root, dirs, files in os.walk(msix_bundle_new_directory):
        for file in files:
            if file.endswith(".msix") and ("x64" in file or "ARM64" in file):
                msix_path = root
                msix_name = file
                break
        if msix_path:
            break

    if not msix_path or not msix_name:
        print("No MSIX file found.")
        return

    msix_file = os.path.join(msix_path, msix_name)
    msix_new_directory = os.path.join(msix_bundle_new_directory, msix_name.replace(".msix", ""))
    msix_new_directory = f"\\\\?\\{msix_new_directory}"
    subprocess.run([zip_app, "x", msix_file, f"-o{msix_new_directory}", "-aoa"], check=True)

    msix_temp_directory = os.path.join(os.environ.get("BUILD_SOURCESDIRECTORY", ""), "msix_temp")
    os.makedirs(msix_temp_directory, exist_ok=True)
    subprocess.run(["cp", "-r", f"{msix_new_directory}/*", msix_temp_directory], check=True)

    print(f"Copied contents of {msix_new_directory} to {msix_temp_directory}")

    env_files = list(Path(msix_temp_directory).rglob("*.env"))

    if env_files:
        for env_file in env_files:
            print(f".env file found at: {env_file}")
            exit(1)
    else:
        print(f"No .env file found in the directory: {msix_temp_directory}")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Search for .env files in an MSIX bundle.")
    parser.add_argument("extract_path", type=str, help="The path where the MSIX bundle is extracted.")
    args = parser.parse_args()

    zip_app = find_tool("/usr/bin", "7z")
    if not zip_app:
        exit(1)

    find_env_file(args.extract_path)
