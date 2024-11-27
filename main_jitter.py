import subprocess
import os
import random
import csv
import matplotlib.pyplot as plt
from datetime import datetime

# Path to the main.py script
main_script = "main.py"

# Function to add random jitter to salience values
def jitter_salience(players, jitter_range=0.1):
    """Apply random jitter to players' salience values."""
    for player in players:
        original_salience = float(player.get("salience", 0.5))  # Default to 0.5 if not specified
        player["salience"] = max(0, min(1, original_salience + random.uniform(-jitter_range, jitter_range)))

# Get the dataset from the user
dataset = input("Enter the name of the dataset (CSV file) to use: ").strip()
if not dataset:
    print("No dataset provided. Exiting.")
    exit()

dataset_path = os.path.join("data", dataset)
if not os.path.exists(dataset_path):
    print(f"Dataset '{dataset_path}' does not exist. Exiting.")
    exit()

# Load original player data from the dataset
players = []
with open(dataset_path, "r") as file:
    reader = csv.DictReader(file)
    players = [row for row in reader]

if not players:
    print(f"Failed to load player data from '{dataset_path}'. Ensure the file is not empty.")
    exit()

# Prepare directory for outputs
output_dir = "output"
os.makedirs(output_dir, exist_ok=True)

# Subfolder for this simulation
timestamp = datetime.now().strftime('%Y-%m-%d-%H-%M')
simulation_folder = os.path.join(output_dir, f"{timestamp}_{os.path.splitext(dataset)[0]}")
os.makedirs(simulation_folder, exist_ok=True)

# Run the simulation for multiple iterations
iterations = 10
status_quo_results = []

print("\nStarting simulation with jittered salience values...")

for iteration in range(1, iterations + 1):
    print(f"Running iteration {iteration}...")
    
    # Apply jitter to player salience
    jittered_players = players.copy()
    jitter_salience(jittered_players)
    
    # Save jittered players to a temporary CSV file
    temp_players_file = os.path.join(simulation_folder, f"players_iteration_{iteration}.csv")
    with open(temp_players_file, "w", newline="") as temp_file:
        writer = csv.DictWriter(temp_file, fieldnames=jittered_players[0].keys())
        writer.writeheader()
        writer.writerows(jittered_players)
    
    # Run the main script with the jittered players
    result = subprocess.run(
        ["python3", main_script, dataset, "--auto"],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        print(f"Error during iteration {iteration}: {result.stderr}")
        status_quo_results.append(None)
    else:
        try:
            # Parse the output to extract status quo (assuming it is outputted as text or JSON-like structure)
            output_lines = result.stdout.splitlines()
            for line in output_lines:
                if "status_quo" in line:
                    status_quo = float(line.split(":")[1].strip())
                    status_quo_results.append(status_quo)
                    break
        except Exception as e:
            print(f"Failed to parse output for iteration {iteration}: {e}")
            status_quo_results.append(None)

# Generate a plot of status quo across iterations
if status_quo_results:
    plt.figure(figsize=(10, 6))
    plt.plot(range(1, iterations + 1), status_quo_results, marker='o', linestyle='-', label="Status Quo")
    plt.xlabel("Iteration")
    plt.ylabel("Status Quo")
    plt.title("Status Quo Movement Across Iterations")
    plt.legend()
    plt.grid(True)
    
    # Save the plot
    plot_path = os.path.join(simulation_folder, "status_quo_iterations.png")
    plt.savefig(plot_path, bbox_inches='tight')
    plt.close()
    
    print(f"\nSimulation completed. Results saved in '{simulation_folder}':")
    print(f"  - Status quo plot: {plot_path}")
else:
    print("No valid status quo data was recorded. Check the main script's output.")
