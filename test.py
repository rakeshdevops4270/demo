import os
import subprocess
from pathlib import Path

def find_tool(search_app):
    """Find if a tool exists in system paths."""
    result = shutil.which(search_app)
    if result:
        print(f"{search_app} found at: {result}")
        return result
    print(f"{search_app} not found.")
    return None

def find_env_file(extract_path):
    """Find and process MSIX files, then check for .env files."""
    msix_bundle_path = None
    msix_bundle_name = None

    # Search for MSIX bundle files
    for root, _, files in os.walk(extract_path):
        for file in files:
            if file.endswith(".msixbundle") and ("x64" in file or "ARM64" in file):
                msix_bundle_path = root
                msix_bundle_name = file
                break
        if msix_bundle_path:
            break

    if not msix_bundle_path:
        print("No MSIX bundle found.")
        return

    msix_bundle_file = os.path.join(msix_bundle_path, msix_bundle_name)
    msix_bundle_new_directory = os.path.join(msix_bundle_path, msix_bundle_name.replace(".msixbundle", ""))

    os.makedirs(msix_bundle_new_directory, exist_ok=True)

    # Extract using 7-Zip
    zip_command = ["7z", "x", msix_bundle_file, f"-o{msix_bundle_new_directory}", "-aoa"]
    subprocess.run(zip_command, check=True)

    # Check for .env files
    env_files = list(Path(msix_bundle_new_directory).rglob("*.env"))

    if env_files:
        for file in env_files:
            print(f"ERROR: .env file found at {file}")
        exit(1)
    else:
        print(f"No .env file found in the directory: {msix_bundle_new_directory}")

if __name__ == "__main__":
    extract_path = "/path/to/extract"  # Update this path as per your Linux setup
    zip_app = find_tool("7z")
    find_env_file(extract_path)
