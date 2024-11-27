import subprocess
import csv
import os

# Path to the CSV file containing dataset names
datasets_csv = "datasets_csv.csv"

# Path to main.py (adjust if necessary)
main_script = "main.py"

# Function to display an explanation
def display_explanation():
    print("This script will automatically run the main script (main.py) for each dataset listed in the 'datasets_csv.csv' file.")
    print("Each dataset will be processed, and outputs will be generated and saved.")
    print("NOTE: This process could take some time, depending on the number of datasets and their size.")
    print("Data analysis results are grouped by version name in 'main.py'.")
    print("If you want to organize the outputs under a specific version name, please manually change the version number near the top of 'main.py' and then run this script again.")
    print()

# Ensure the CSV file exists
if not os.path.exists(datasets_csv):
    raise FileNotFoundError(f"Dataset CSV file '{datasets_csv}' not found.")

# Display the explanation
display_explanation()

# Ask for user confirmation to proceed
user_response = input("Are you sure you want to proceed? (yes/no): ").strip().lower()
if user_response != "yes":
    print("Operation canceled by user.")
    exit()

# Read dataset names from the CSV
with open(datasets_csv, "r") as file:
    datasets = [row[0] for row in csv.reader(file) if row]  # Skip empty rows

# Run main.py for each dataset
print("\nStarting the execution of main.py for each dataset...")
success_count = 0
failure_count = 0

for dataset in datasets:
    print(f"Running {main_script} with dataset: {dataset}")
    result = subprocess.run(["python3", main_script, dataset, "--auto"])
    if result.returncode != 0:
        print(f"Error running {main_script} with dataset: {dataset}")
        failure_count += 1
    else:
        print(f"Completed {main_script} with dataset: {dataset}")
        success_count += 1

# Provide a summary of the execution
print("\nExecution Summary:")
print(f"Total datasets processed: {len(datasets)}")
print(f"Successfully processed: {success_count}")
print(f"Failed to process: {failure_count}. You either have a misspelled dataset or your dataset is missing.")
print("\nOutputs have been generated for each dataset.")
print("For further analysis of the results, please use the 'diagnostics.py' script.")
