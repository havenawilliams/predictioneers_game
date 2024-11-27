# Import necessary libraries
import os
import pygambit
import pandas as pd
from itertools import combinations
import matplotlib.pyplot as plt
from datetime import datetime
import argparse

# Import functions
from pg_player_class import Player, Model, import_players_from_csv
from play_game import get_solution, play_game, Bayesian_updating, update_position
from update_game import *
from check_utility import check_utility_decreasing
from generate_new_sheet import generate_sheet

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
args = parser.parse_args()

# Data entry functions
if not args.auto:
    print("Welcome to my recreation of Bruce Bueno de Mesquita's Predictioneer's Game!\nIf you don't know what that means, read the readme!")

def list_recent_csv_files(directory, count=3):
    """
    List the most recently modified CSV files in a directory.
    """
    all_files = [os.path.join(directory, f) for f in os.listdir(directory) if f.endswith(".csv")]
    recent_files = sorted(all_files, key=os.path.getmtime, reverse=True)[:count]
    return [os.path.basename(f) for f in recent_files]

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

# Check for actual_result
actual_result = get_actual_outcome_from_index(csv_file)

# Load a game structure
g = pygambit.Game.read_game("game_alpha_0.0_game_1.gbt")

# Load players from the specified CSV file
players = import_players_from_csv(csv_file_path)

# Create dictionary for games per player
games_for_combinations = {}
for combination in combinations(players, 2):
    key = tuple(player.name for player in combination)
    games_for_combinations[key] = g

# Initialize status quo
initial_status_quo = Model.status_quo

# Initialize round number
round_number = 0

# Initialize data structure to capture intra-round data
utility_recorder = {}
position_recorder = {}

# Main game loop
finished_updating_positions = args.auto  # Skip position updates if in auto mode

while round_number < 100:
    # Record initial round data
    utility_recorder[round_number] = {}
    position_recorder[round_number] = {}
    for player in players:
        utility_recorder[round_number][player.name] = player.utility(Model.status_quo)
        position_recorder[round_number][player.name] = player.position

    # Store previous round positions
    for player in players:
        player.previous_position = player.position

    # Model each player pair
    for player_pair in combinations(players, 2):
        Model.update_status_quo(players)

        # Update player probabilities of victory over another
        player_pair[0].conflict_probabilities(player_pair[1], players)
        player_pair[1].conflict_probabilities(player_pair[0], players)

        # Update the game
        players_for_round = tuple(player.name for player in player_pair)
        games_for_combinations[players_for_round].set_chance_probs(
            games_for_combinations[players_for_round].root.infoset,
            [player_pair[0].beliefs[player_pair[1].name], 1 - player_pair[0].beliefs[player_pair[1].name]]
        )
        update_game(player_pair[0], player_pair[1], games_for_combinations[players_for_round])

        # Compute the solution of the updated game
        solution = get_solution(g)

        # Get the credible outcomes
        credible_proposals = play_game(player_pair[0], player_pair[1], g, 1, solution)

        # Bayesian updating
        Bayesian_updating(g, credible_proposals, solution, player_pair[0], player_pair[1])

        # Update positions
        update_position(player_pair[0], player_pair[1], games_for_combinations[players_for_round], credible_proposals)

    # Check end game rule
    if check_utility_decreasing(round_number, utility_recorder):
        break

    round_number += 1

print(f"Game finished with status quo {Model.status_quo} after {round_number} rounds.")

# Save calibration data
def save_calibration_data(data_set_name, forecasted_result):
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

# Save calibration data at the end of the game
save_calibration_data(csv_file, Model.status_quo)

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
