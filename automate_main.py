import subprocess
import csv
import os

# Path to the CSV file containing dataset names
datasets_csv = "datasets_csv.csv"

# Path to main.py (adjust if necessary)
main_script = "main.py"

# Ensure the CSV file exists
if not os.path.exists(datasets_csv):
    raise FileNotFoundError(f"Dataset CSV file '{datasets_csv}' not found.")

# Read dataset names from the CSV
with open(datasets_csv, "r") as file:
    datasets = [row[0] for row in csv.reader(file) if row]  # Skip empty rows

# Iterate over each dataset and invoke main.py
for dataset in datasets:
    print(f"Running {main_script} with dataset: {dataset}")
    result = subprocess.run(["python3", main_script, dataset, "--auto"])
    if result.returncode != 0:
        print(f"Error running {main_script} with dataset: {dataset}")
        break
    print(f"Completed {main_script} with dataset: {dataset}")