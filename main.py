# Import necessary libraries
import os
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import argparse
import pygambit
import numpy as np  # Added for jittering
import copy

# Import the simulation function
from game_simulation import run_game_simulation  # Assuming the function is in `game_simulation.py`

# Import functions
from pg_player_class import *
from generate_new_sheet import generate_sheet
from supporting_functions import list_recent_csv_files, get_actual_outcome_from_index, save_calibration_data

# Set version number for the script
version_number = 0.1

# Set up argparse
parser = argparse.ArgumentParser(description="Run the Predictioneers Game simulation.")
parser.add_argument(
    "csv_file",
    nargs="?",  # Makes this argument optional
    default=None,
    help="The name of the dataset (CSV file) to use."
)
parser.add_argument(
    "--auto",
    action="store_true",
    help="Run the script in automated mode (no prompts)."
)
parser.add_argument(
    "--jitter",
    action="store_true",
    help="Skip saving calibration data and subsequent steps."
)
parser.add_argument(
    "--cutoff",
    action = "store_true",
    help = "Turns off "
)
args = parser.parse_args()

# Data entry functions
if not args.auto and not args.jitter:
    print("Welcome to my recreation of Bruce Bueno de Mesquita's Predictioneer's Game!\nIf you don't know what that means, read the readme!")

# Get the CSV file
if args.csv_file:
    csv_file = args.csv_file
else:
    while True:
        user_input = input("Enter the name of the dataset (CSV file) to use, type 'recent' to list recent files, or type 'create sheet' to generate a new blank sheet: ").strip()
        if user_input.lower() == "recent":
            recent_csvs = list_recent_csv_files("data")
            if recent_csvs:
                print("Most recently modified CSV files:")
                for idx, file_name in enumerate(recent_csvs, start=1):
                    print(f"{idx}. {file_name}")
            else:
                print("No CSV files found in the 'data' directory.")
        elif user_input.lower() == "create sheet":
            generate_sheet()
            exit()
        else:
            csv_file = user_input
            break

# Ensure csv_base_name is defined
csv_base_name = os.path.splitext(os.path.basename(csv_file))[0]

# Build the CSV file path
csv_file_path = os.path.join("data", csv_file)
if not os.path.exists(csv_file_path):
    raise FileNotFoundError(f"The file '{csv_file_path}' does not exist.")

# Load players from the specified CSV file
initial_players = import_players_from_csv(csv_file_path)

# Load the game structure (adjust path to game structure as necessary)
#g = pygambit.Game.read_game("game_alpha_0.0_game_1.gbt")

if args.jitter:
    # Jittered simulation block
    print("Jittering activated. Expect fewer prompts than normal.")
    num_iterations = int(input("How many iterations would you like to run? "))
    status_quo_recorder_all_runs = []

    for i in range(num_iterations):
        # Add jitter to player salience
        players = copy.deepcopy(initial_players)
        Model.update_status_quo(players)
        g = pygambit.Game.read_game("game_full.gbt")
        for player in players:
            player.salience += np.random.normal(0, 0.02)  # Small noise with mean 0 and std 0.01
            player.salience = np.clip(player.salience, 0, 1)

        # Run the simulation with jittered values
        if args.cutoff:
            simulation_results = run_game_simulation(players, g, Model, args, cutoff = True)
        else:
            simulation_results = run_game_simulation(players, g, Model, args, cutoff = False)

        # Extract and store the Model.status_quo for this run
        status_quo_recorder_all_runs.append(simulation_results["status_quo_recorder"])

    # Prepare data for plotting status quo over rounds across iterations
    status_quo_df = pd.DataFrame(status_quo_recorder_all_runs).T
    status_quo_df.columns = [f"Run {i+1}" for i in range(num_iterations)]

    # Plot status quo over rounds
    plt.figure(figsize=(10, 6))
    for col in status_quo_df.columns:
        plt.plot(status_quo_df.index, status_quo_df[col], marker='o', label=col)
    
    # Add title, labels, and legend
    plt.title('Change in Model.status_quo Over Rounds (Jittered)', fontsize=14)
    plt.xlabel('Rounds', fontsize=12)
    plt.ylabel('Model.status_quo Position', fontsize=12)
    plt.legend(fontsize=10)

    # Save the plot
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    current_date = datetime.now().strftime('%Y-%m-%d-%H-%M')
    subfolder_name = f"{current_date}_{csv_base_name}"
    subfolder_path = os.path.join(output_dir, subfolder_name)
    os.makedirs(subfolder_path, exist_ok=True)

    plot_file_name = f"{csv_base_name}_status_quo_jitter_plot.png"
    plot_file_path = os.path.join(subfolder_path, plot_file_name)
    plt.savefig(plot_file_path, bbox_inches='tight')
    plt.close()

    # Notify user of saved results
    print(f"Jittered simulation results saved to '{subfolder_path}':")
    print(f"  - Status quo plot: {plot_file_name}")

else:
    # Non-jittered simulation block
    players = copy.deepcopy(initial_players)
    Model.update_status_quo(players)
    g = pygambit.Game.read_game("game_full.gbt")

    #Save data------------------------------------------------------------------------------------------------------------
    if args.cutoff:
        simulation_results = run_game_simulation(players, g, Model, args, cutoff = True)
    else:
        simulation_results = run_game_simulation(players, g, Model, args, cutoff = False)
    final_status_quo = simulation_results["final_status_quo"]
    utility_recorder = simulation_results["utility_recorder"]
    position_recorder = simulation_results["position_recorder"]
    rounds_completed = simulation_results["rounds_completed"]
    status_quo_recorder = simulation_results["status_quo_recorder"]

    # Save calibration data
    save_calibration_data(csv_file, final_status_quo, args, version_number)

    # Prepare output data
    output_data = {
        "name": [player.name for player in players],
        "position": [player.position for player in players],
        "capabilities": [player.capabilities for player in players],
        "salience": [player.salience for player in players],
        "resolve": [player.resolve for player in players],
        "true_hawk_type": [player.true_hawk_type for player in players],
        "true_retaliatory_type": [player.true_retaliatory_type for player in players],
    }
    df_output = pd.DataFrame(output_data)

    # Create output directory
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    current_date = datetime.now().strftime('%Y-%m-%d-%H-%M')
    subfolder_name = f"{current_date}_{csv_base_name}"
    subfolder_path = os.path.join(output_dir, subfolder_name)
    os.makedirs(subfolder_path, exist_ok=True)

    # Combine position_recorder and status quo for plotting
    df_positions = pd.DataFrame(position_recorder).T
    df_status_quo = pd.DataFrame({"Status Quo": list(status_quo_recorder)})
    df_combined = pd.concat([df_positions, df_status_quo], axis=1)

    # Generate combined plot
    plt.figure(figsize=(10, 6))
    for actor in df_positions.columns:
        plt.plot(df_positions.index, df_positions[actor], marker='o', label=f"{actor} (Position)")

    plt.plot(df_status_quo.index, df_status_quo["Status Quo"], marker='x', color='black', label="Status Quo")

    # Add title, labels, and legend
    plt.title('Change in Positions and Status Quo Over Rounds', fontsize=14)
    plt.xlabel('Rounds', fontsize=12)
    plt.ylabel('Position / Status Quo', fontsize=12)
    plt.legend(fontsize=10)

    # Save the plot
    plot_file_name = f"{csv_base_name}_positions_and_status_quo_plot.png"
    plot_file_path = os.path.join(subfolder_path, plot_file_name)
    plt.savefig(plot_file_path, bbox_inches='tight')
    plt.close()

    # Save data structures
    # Belief Matrix
    belief_matrix = pd.DataFrame(index=[player.name for player in players], columns=[player.name for player in players])

    # Populate belief matrix
    for player_a in players:
        for player_b in players:
            if player_a.name == player_b.name:
                belief_matrix.at[player_a.name, player_b.name] = 1.0
            else:
                belief_matrix.at[player_a.name, player_b.name] = player_a.beliefs.get(player_b.name, 0.0)

    # Record belief matrix
    beliefs_csv_name = f"{csv_base_name}_beliefs_matrix.csv"
    beliefs_csv_path = os.path.join(subfolder_path, beliefs_csv_name)
    belief_matrix.to_csv(beliefs_csv_path)

    # Save updated DataFrame to the subfolder
    output_csv_name = f"{csv_base_name}_positions.csv"
    output_csv_path = os.path.join(subfolder_path, output_csv_name)
    df_output.to_csv(output_csv_path, index=False)

    # Record utility_recorder to CSV
    utility_df = pd.DataFrame(utility_recorder).T
    utility_csv_name = f"{csv_base_name}_utility_recorder.csv"
    utility_csv_path = os.path.join(subfolder_path, utility_csv_name)
    utility_df.to_csv(utility_csv_path, index_label="Round")
    
    # Record position_recorder to CSV
    position_df = pd.DataFrame(position_recorder).T
    position_csv_name = f"{csv_base_name}_position_recorder.csv"
    position_csv_path = os.path.join(subfolder_path, position_csv_name)
    position_df.to_csv(position_csv_path, index_label="Round")

    # Record status_quo_recorder to CSV
    status_quo_df = pd.DataFrame({"Status Quo": list(status_quo_recorder)})
    status_quo_csv_name = f"{csv_base_name}_status_quo_recorder.csv"
    status_quo_csv_path = os.path.join(subfolder_path, status_quo_csv_name)
    status_quo_df.to_csv(status_quo_csv_path, index_label="Round")

    # Notify user of saved results
    print(f"Results saved to '{subfolder_path}':")
    print(f"  - Positions data: {output_csv_name}")
    print(f"  - Plot: {plot_file_name}")
    print(f"  - Beliefs matrix: {beliefs_csv_name}")
    print(f"  - Utility recorder: {utility_csv_name}")
    print(f"  - Position recorder: {position_csv_name}")
    print(f"  - Status quo recorder: {status_quo_csv_name}")

