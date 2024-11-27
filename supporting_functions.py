import os
import pandas as pd
from datetime import datetime

def list_recent_csv_files(directory, count=3):
    """
    List the most recently modified CSV files in a directory.
    """
    all_files = [os.path.join(directory, f) for f in os.listdir(directory) if f.endswith(".csv")]
    recent_files = sorted(all_files, key=os.path.getmtime, reverse=True)[:count]
    return [os.path.basename(f) for f in recent_files]

def get_actual_outcome_from_index(data_set_name):
    """
    Checks the 'pg_datasets_index.csv' file to see if there is an existing 
    actual_result for the given dataset. Returns the actual_result if found, 
    otherwise returns None.
    """
    index_file_path = os.path.join("data", "pg_datasets_index.csv")
    if not os.path.exists(index_file_path):
        return None  # No index file exists
    
    # Load the index file
    pg_index = pd.read_csv(index_file_path)
    
    # Check for the dataset name in the index
    dataset_row = pg_index[pg_index['dataset_name'] == data_set_name]
    if not dataset_row.empty and not pd.isna(dataset_row.iloc[0]['actual_result']):
        return dataset_row.iloc[0]['actual_result']  # Return the existing actual_result
    
    return None  # No actual_result found or it is empty

# Save calibration data
def save_calibration_data(data_set_name, forecasted_result, args, version_number):
    if not args.auto:
        save_to_calibration = input("Save forecast results? (yes/no): ").strip().lower()
    else:
        save_to_calibration = "yes"

    if save_to_calibration not in ["yes", "y"]:
        print("Results not saved.")
        return

    # Initialize actual_result
    actual_result = get_actual_outcome_from_index(data_set_name)  # Check if there's an existing value
    if actual_result is None:  # If not, prompt the user
        while True:
            try:
                actual_result = float(input("Enter the actual outcome (0-1): ").strip())
                if 0 <= actual_result <= 1:
                    break
                else:
                    print("Please enter a number between 0 and 1.")
            except ValueError:
                print("Invalid input. Please enter a valid float between 0 and 1.")

    # Save data
    folder = "calibration_data"
    os.makedirs(folder, exist_ok=True)
    file_path = os.path.join(folder, "calibration_data.csv")

    if not os.path.exists(file_path):
        pd.DataFrame(columns=["data_set_name", "forecasted_result", "actual_result", "date_of_forecast", "version_number"]).to_csv(file_path, index=False)

    date_of_forecast = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    calibration_data = pd.read_csv(file_path)

    # Create a DataFrame for the new row
    new_row = pd.DataFrame([{
        "data_set_name": data_set_name,
        "forecasted_result": forecasted_result,
        "actual_result": actual_result,
        "date_of_forecast": date_of_forecast,
        "version_number": version_number
    }])

    # Concatenate the new row with the existing data
    calibration_data = pd.concat([calibration_data, new_row], ignore_index=True)

    # Save the updated DataFrame
    calibration_data.to_csv(file_path, index=False)

    print(f"Forecast results saved to {file_path}.")