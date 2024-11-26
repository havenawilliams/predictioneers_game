import os
import pandas as pd

def update_pg_datasets_index(data_folder):
    """
    Updates or creates the 'pg_datasets_index.csv' file in the specified data folder.
    Prompts the user for input to populate the 'actual_result' column for new datasets.
    
    Args:
        data_folder (str): Path to the folder containing datasets.
    """
    index_file_path = os.path.join(data_folder, "pg_datasets_index.csv")
    datasets_in_folder = [f for f in os.listdir(data_folder) 
                          if f.endswith('.csv') and not f.startswith("fake_") and f != "pg_datasets_index.csv"]

    # Load or create the index file
    if os.path.exists(index_file_path):
        # Load existing index file
        pg_index = pd.read_csv(index_file_path)
    else:
        # Create an empty index file with the required columns
        pg_index = pd.DataFrame(columns=["dataset_name", "source", "actual_result"])
        print(f"Created new index file: {index_file_path}")

    # Get existing dataset names in the index
    existing_datasets = set(pg_index["dataset_name"]) if not pg_index.empty else set()

    # Add new datasets to the index
    new_datasets = [dataset for dataset in datasets_in_folder if dataset not in existing_datasets]

    if not new_datasets:
        print("No new datasets found. Index is up to date.")
        return

    for dataset_name in new_datasets:
        print(f"Processing new dataset: {dataset_name}")

        # Prompt for actual_result
        while True:
            user_input = input(f"Enter 'actual_result' (0-1) for {dataset_name} or 'skip' to leave it blank: ").strip()
            if user_input.lower() == "skip":
                actual_result = None
                break
            try:
                actual_result = float(user_input)
                if 0 <= actual_result <= 1:
                    break
                else:
                    print("Please enter a number between 0 and 1.")
            except ValueError:
                print("Invalid input. Please enter a number between 0 and 1, or 'skip'.")

        # Append the new dataset to the index
        pg_index = pd.concat([
            pg_index,
            pd.DataFrame({
                "dataset_name": [dataset_name],
                "source": ["source"],  # Placeholder for the 'source' column
                "actual_result": [actual_result]
            })
        ], ignore_index=True)

    # Save the updated index back to the file
    pg_index.to_csv(index_file_path, index=False)
    print(f"Updated index file saved to: {index_file_path}")

if __name__ == "__main__":
    # Define the path to the 'data' folder
    data_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

    # Ensure the folder exists
    if not os.path.exists(data_folder):
        print(f"Error: Data folder does not exist at path: {data_folder}")
    else:
        update_pg_datasets_index(data_folder)
