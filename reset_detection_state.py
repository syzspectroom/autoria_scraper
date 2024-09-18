import os
import shutil
from tqdm import tqdm
import re

def get_original_path(file_path, root_dir='data/pictures'):
    """
    Reconstruct the original path based on the file name.
    Assumes the file name is an 8-digit ID that corresponds to its original subdirectory structure.
    """
    file_name = os.path.basename(file_path)
    # Extract the 8-digit ID from the filename
    match = re.match(r'(\d{8})', file_name)
    if match:
        id_part = match.group(1)
        # Create the subfolder structure: first 2 digits / next 2 digits / next 2 digits
        subfolder_path = os.path.join(id_part[:2], id_part[2:4], id_part[4:6])
        return os.path.join(root_dir, subfolder_path, file_name)
    else:
        raise ValueError(f"Unable to extract 8-digit ID from filename: {file_name}")

def move_file_back(file_path, root_dir='data/pictures'):
    """
    Move a file back to its original location in the root_dir.
    """
    original_path = get_original_path(file_path, root_dir)
    os.makedirs(os.path.dirname(original_path), exist_ok=True)
    shutil.move(file_path, original_path)
    return original_path

def clean_empty_dirs(directory):
    """
    Remove empty subdirectories in the given directory.
    """
    for root, dirs, files in os.walk(directory, topdown=False):
        for dir_name in dirs:
            dir_path = os.path.join(root, dir_name)
            if not os.listdir(dir_path):  # Check if the directory is empty
                os.rmdir(dir_path)
                print(f"Removed empty directory: {dir_path}")

def reset_detection_state(valid_dir='data/valid_pictures', invalid_dir='data/invalid_pictures', root_dir='data/pictures'):
    """
    Move images from valid_dir and invalid_dir back to their original locations in root_dir.
    """
    moved_files = 0
    errors = 0

    for source_dir in [valid_dir, invalid_dir]:
        if not os.path.exists(source_dir):
            print(f"Directory does not exist: {source_dir}")
            continue

        for root, _, files in os.walk(source_dir):
            for file in tqdm(files, desc=f"Moving files from {source_dir}", unit="file"):
                file_path = os.path.join(root, file)
                try:
                    new_path = move_file_back(file_path, root_dir)
                    print(f"Moved {file_path} to {new_path}")
                    moved_files += 1
                except Exception as e:
                    print(f"Error moving {file_path}: {str(e)}")
                    errors += 1

    # Clean up empty directories
    for dir_to_clean in [valid_dir, invalid_dir, root_dir]:
        clean_empty_dirs(dir_to_clean)

    print(f"\nReset complete. Moved {moved_files} files. Encountered {errors} errors.")

if __name__ == "__main__":
    reset_detection_state()
