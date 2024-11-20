import os
import csv
from datetime import datetime

# Ensure directories exist
data_folder = "data"
output_folder = "output"

if not os.path.exists(data_folder):
    raise FileNotFoundError(f"The folder '{data_folder}' does not exist.")

if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# Path to input file
input_file = os.path.join(data_folder, "data.csv")

if not os.path.exists(input_file):
    raise FileNotFoundError(f"The file '{input_file}' does not exist in the '{data_folder}' folder.")

# Read data and calculate the sum
total_sum = 0
try:
    with open(input_file, 'r') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            total_sum += sum(map(int, row))  # Convert each value in the row to an integer and sum it
except ValueError:
    raise ValueError("The file contains non-integer values or is improperly formatted.")

# Generate the output filename
current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
output_file = os.path.join(output_folder, f"{current_time}_data_output.csv")

# Write the result to the output CSV
with open(output_file, 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["Sum"])
    writer.writerow([total_sum])

print(f"Output saved to: {output_file}")
