import os
import shutil

def delete_folder_contents(folder_path):
    # Check if the folder exists
    if not os.path.exists(folder_path):
        print(f"The folder '{folder_path}' does not exist.")
        return

    # Get confirmation from the user
    dummy = input(f"Are you SURE you want to delete all contents in '{folder_path}'? This action cannot be undone. (yes/no): ")
    confirmation = input(f"That last prompt was a TRICK! It doesn't do anything. This one counts. Are you SUPER DUPER SURE you want to delete all contents in '{folder_path}'??? This action CANNOT be undone. (yes/no): ").strip().lower()

    if confirmation == 'yes':
        # Iterate over all items in the folder and delete them
        for item in os.listdir(folder_path):
            item_path = os.path.join(folder_path, item)
            try:
                if os.path.isfile(item_path) or os.path.islink(item_path):
                    os.unlink(item_path)  # Remove file or symlink
                elif os.path.isdir(item_path):
                    shutil.rmtree(item_path)  # Remove directory
                print(f"Deleted: {item_path}")
            except Exception as e:
                print(f"Failed to delete {item_path}: {e}")
        print(f"All contents of '{folder_path}' have been deleted. Don't say I didn't warn you!")
    else:
        print("Operation canceled. No changes were made. Phew!")

if __name__ == "__main__":
    folder_to_clear = "./output"
    delete_folder_contents(folder_to_clear)
