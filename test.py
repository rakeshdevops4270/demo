import os
import sys
import zipfile
import argparse
from pathlib import Path

def extract_zip_file(zip_path, output_dir):
    """Extract a ZIP-format file (.msix/.msixbundle) to the specified directory."""
    print(f"📦 Extracting {zip_path} to {output_dir}")
    os.makedirs(output_dir, exist_ok=True)
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(output_dir)

def copy_file(src_path, dest_path):
    """Manually copy a file without using shutil."""
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    with open(src_path, 'rb') as src_file, open(dest_path, 'wb') as dest_file:
        dest_file.write(src_file.read())

def find_env_file(extract_path):
    """Find and process MSIX bundle files, and scan for .env files."""
    msix_bundle_path = None
    msix_bundle_name = None

    # Search for .msixbundle files
    for root, _, files in os.walk(extract_path):
        for file in files:
            if file.endswith(".msixbundle") and ("x64" in file or "ARM64" in file):
                msix_bundle_path = root
                msix_bundle_name = file
                break
        if msix_bundle_path:
            break

    if not msix_bundle_path or not msix_bundle_name:
        print("No matching .msixbundle file found.")
        return

    msix_bundle_file = os.path.join(msix_bundle_path, msix_bundle_name)
    msix_bundle_extract_dir = os.path.join(msix_bundle_path, msix_bundle_name.replace(".msixbundle", ""))
    extract_zip_file(msix_bundle_file, msix_bundle_extract_dir)

    # Look for .msix file inside the extracted .msixbundle
    msix_file_path = None
    for root, _, files in os.walk(msix_bundle_extract_dir):
        for file in files:
            if file.endswith(".msix") and ("x64" in file or "ARM64" in file):
                msix_file_path = os.path.join(root, file)
                break
        if msix_file_path:
            break

    if not msix_file_path:
        print("No matching .msix file found inside the bundle.")
        return

    msix_extract_dir = os.path.join(msix_bundle_extract_dir, Path(msix_file_path).stem)
    extract_zip_file(msix_file_path, msix_extract_dir)

    # Define temporary directory
    temp_dir = os.path.join(extract_path, "msix_temp")
    os.makedirs(temp_dir, exist_ok=True)

    # Manually copy files to temp_dir for path simplification
    for item in Path(msix_extract_dir).rglob("*"):
        if item.is_file():
            relative_path = item.relative_to(msix_extract_dir)
            target_path = Path(temp_dir) / relative_path
            copy_file(str(item), str(target_path))

    print(f"📁 Copied contents of {msix_extract_dir} to {temp_dir}")

    # Look for .env files
    env_files = list(Path(temp_dir).rglob("*.env"))

    if env_files:
        for file in env_files:
            print(f" .env file found at: {file}")
        sys.exit(1)
    else:
        print(f"✅ No .env file found in the directory: {temp_dir}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Search for .env files in an MSIX bundle.")
    parser.add_argument("extract_path", type=str, help="The path where the MSIX bundle is located.")
    args = parser.parse_args()

    find_env_file(args.extract_path)
