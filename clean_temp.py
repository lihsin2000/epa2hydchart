import os
import shutil
import globals


def delete_all_files(base_directory):
    """
    Deletes all files in the specified directory and its subdirectories.

    Args:
        base_directory (str): Path to the base directory.
    """
    deleted_files = 0

    # Walk through the directory
    for root, dirs, files in os.walk(base_directory):
        for file in files:
            file_path = os.path.join(root, file)
            try:
                os.remove(file_path)
                globals.logger.info(f"Deleted: {file_path}")
                deleted_files += 1
            except Exception as e:
                globals.logger.error(f"Failed to delete {file_path}: {e}")
                globals.logger.exception(e)

    globals.logger.info(f"Total deleted files: {deleted_files}")


def delete_empty_directories(base_directory):
    """Deletes all empty directories in the specified directory and its subdirectories."""
    for root, dirs, _ in os.walk(base_directory, topdown=False):
        for dir_name in dirs:
            dir_path = os.path.join(root, dir_name)
            try:
                if not os.listdir(dir_path):  # Check if the directory is empty
                    os.rmdir(dir_path)
                    globals.logger.info(f"Deleted empty directory: {dir_path}")
            except Exception as e:
                globals.logger.error(f"Failed to delete directory {dir_path}: {e}")
                globals.logger.exception(e)


# Example usage
base_directory = "temp/"  # Replace with your directory path

delete_all_files(base_directory)
delete_empty_directories(base_directory)
