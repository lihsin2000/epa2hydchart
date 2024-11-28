import os

def delete_files(base_directory, extensions):
    """
    Deletes files with specified extensions in the given directory and its subdirectories.

    Args:
        base_directory (str): Path to the base directory.
        extensions (list): List of file extensions to delete (e.g., ['.dxf', '.svg']).
    """
    deleted_files = 0

    # Walk through the directory
    for root, dirs, files in os.walk(base_directory):
        for file in files:
            if any(file.lower().endswith(ext) for ext in extensions):
                file_path = os.path.join(root, file)
                try:
                    os.remove(file_path)
                    print(f"Deleted: {file_path}")
                    deleted_files += 1
                except Exception as e:
                    print(f"Failed to delete {file_path}: {e}")

    print(f"Total deleted files: {deleted_files}")

# Example usage
base_directory = "example/"  # Replace with your directory
extensions = ['.dxf', '.svg', 'png']               # File extensions to delete

delete_files(base_directory, extensions)
