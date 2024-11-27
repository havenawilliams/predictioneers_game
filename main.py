# Import necessary libraries
import os
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import argparse
import pygambit

# Import the simulation function
from game_simulation import run_game_simulation  # Assuming the function is in `game_simulation.py`

# Import functions
from pg_player_class import *
from generate_new_sheet import generate_sheet
from supporting_functions import *

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
args = parser.parse_args()

# Data entry functions
if not args.auto:
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

# Build the CSV file path
csv_file_path = os.path.join("data", csv_file)
if not os.path.exists(csv_file_path):
    raise FileNotFoundError(f"The file '{csv_file_path}' does not exist.")

# Load players from the specified CSV file
players = import_players_from_csv(csv_file_path)

# Load the game structure (adjust path to game structure as necessary)
g = pygambit.Game.read_game("game_alpha_0.0_game_1.gbt")

if args.jitter:
    print("jitter")

# If --jitter is not provided, perform post-simulation steps
if not args.jitter:
    #Run the game simulation
    simulation_results = run_game_simulation(players, g, Model, args)
    #Extract results
    final_status_quo = simulation_results["final_status_quo"]
    utility_recorder = simulation_results["utility_recorder"]
    position_recorder = simulation_results["position_recorder"]
    rounds_completed = simulation_results["rounds_completed"]

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

    # Create subfolder based on input CSV name and timestamp
    current_date = datetime.now().strftime('%Y-%m-%d-%H-%M')
    csv_base_name = os.path.splitext(os.path.basename(csv_file))[0]
    subfolder_name = f"{current_date}_{csv_base_name}"
    subfolder_path = os.path.join(output_dir, subfolder_name)
    os.makedirs(subfolder_path, exist_ok=True)

    # Save updated DataFrame to the subfolder
    output_csv_name = f"{csv_base_name}_positions.csv"
    output_csv_path = os.path.join(subfolder_path, output_csv_name)
    df_output.to_csv(output_csv_path, index=False)

    # Plot positions over rounds
    df_plot = pd.DataFrame(position_recorder).T
    plt.figure(figsize=(10, 6))
    for actor in df_plot.columns:
        plt.plot(df_plot.index, df_plot[actor], marker='o', label=actor)
        plt.annotate(actor, (df_plot.index[-1], df_plot[actor].iloc[-1]),
                     textcoords="offset points", xytext=(5, 0),
                     ha='left', rotation=45, fontsize=7)

    # Add title, labels, and legend
    plt.title('Change in Position per Actor Over Rounds', fontsize=14)
    plt.xlabel('Rounds', fontsize=12)
    plt.ylabel('Position', fontsize=12)
    plt.legend(fontsize=10)

    # Save the plot
    plot_file_name = f"{csv_base_name}_positions_plot.png"
    plot_file_path = os.path.join(subfolder_path, plot_file_name)
    plt.savefig(plot_file_path, bbox_inches='tight')
    plt.close()

    # Belief Matrix
    belief_matrix = pd.DataFrame(index=[player.name for player in players], columns=[player.name for player in players])

    # Populate belief matrix
    for player_a in players:
        for player_b in players:
            if player_a.name == player_b.name:
                belief_matrix.at[player_a.name, player_b.name] = 1.0
            else:
                belief_matrix.at[player_a.name, player_b.name] = player_a.beliefs.get(player_b.name, 0.0)

    # Save belief matrix
    beliefs_csv_name = f"{csv_base_name}_beliefs_matrix.csv"
    beliefs_csv_path = os.path.join(subfolder_path, beliefs_csv_name)
    belief_matrix.to_csv(beliefs_csv_path)

    # Notify user of saved results
    print(f"Results saved to '{subfolder_path}':")
    print(f"  - Positions data: {output_csv_name}")
    print(f"  - Plot: {plot_file_name}")
    print(f"  - Beliefs matrix: {beliefs_csv_name}")
