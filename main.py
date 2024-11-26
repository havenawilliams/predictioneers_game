# Import necessary libraries
import os
import pygambit
import pandas as pd
from itertools import combinations
import matplotlib.pyplot as plt
from datetime import datetime
import argparse
import os

# Set version number for the script
version_number= 0.1

# Import functions
from pg_player_class import Player, Model, import_players_from_csv
from play_game import get_solution, play_game, Bayesian_updating, update_position
from update_game import *
from check_utility import check_utility_decreasing
from generate_new_sheet import generate_sheet

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

#Data entry functions

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

# Load a game structure. Multiple copies will eventually be made.
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
        if not finished_updating_positions:
            while True:
                update_choice = input("Do you want to update any player's positions? \nThis step simulates a shock where a player suddenly changes their position. \n(yes/no/finished): ").strip().lower()
                if update_choice == "yes":
                    player_update = input("Enter player name and position in the format. eg United States = 0.5: ")
                    try:
                        player_name, position = map(str.strip, player_update.split('='))
                        position = float(position)
                        player = next((p for p in players if p.name == player_name), None)
                        if player:
                            player.position = position
                            print(f"Updated {player.name}'s position to {player.position}.")
                        else:
                            print(f"Player '{player_name}' not found.")
                    except ValueError:
                        print("Invalid input format. Please use 'Player Name = Position' (e.g., 'United States = 0.5').")
                elif update_choice == "no":
                    break
                elif update_choice == "finished":
                    finished_updating_positions = True
                    break
                else:
                    print("Invalid choice. Please enter 'yes', 'no', or 'finished'.")

            # Record updated positions after user input
            for player in players:
                position_recorder[round_number][player.name] = player.position

        break

    print(f"Game continues past round {round_number}. Status quo: {Model.status_quo}")

    # Update round number
    round_number += 1


# Game conclusion
print(f"Game is finished with status quo {Model.status_quo} after round {round_number}.")
#------------------------------------------------------------------------------------------
# Begin process to further export data

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

# Set up the output directory
output_dir = "output"
os.makedirs(output_dir, exist_ok=True)

# Generate a subfolder in the output directory based on the input CSV name and current date
current_date = datetime.now().strftime('%Y-%m-%d-%H-%M')
csv_base_name = os.path.splitext(os.path.basename(csv_file))[0]
subfolder_name = f"{current_date}_{csv_base_name}"
subfolder_path = os.path.join(output_dir, subfolder_name)
os.makedirs(subfolder_path, exist_ok=True)

#------------------------------------------------------------------------------------------

def save_calibration_data(data_set_name, forecasted_result):
    """
    Ask the user if they want to save the calibration data and, if so, save it.
    """
    # Ask the user if they want to save the forecast
    if not args.auto:
        save_to_calibration = input("Do you want to save the results of this forecast to your calibration data? (yes/no): ").strip().lower()
    else:
        save_to_calibration = "yes "  # Default behavior for automated mode

    if save_to_calibration not in ["yes", "y"]:
        print("Forecast results were not saved to calibration data.")
        return


    # Ask the user for the actual outcome
    while True:
        try:
            actual_result = float(input("What is the actual outcome of this scenario? Enter a value between 0 and 1: ").strip())
            if 0 <= actual_result <= 1:
                break
            else:
                print("Please enter a number between 0 and 1.")
        except ValueError:
            print("Invalid input. Please enter a valid float between 0 and 1.")

    # Ensure the folder and CSV file exist
    folder = "calibration_data"
    os.makedirs(folder, exist_ok=True)
    file_path = os.path.join(folder, "calibration_data.csv")
    if not os.path.exists(file_path):
        # Create the file with headers if it doesn't exist
        pd.DataFrame(columns=["data_set_name", "forecasted_result", "actual_result", "date_of_forecast", "version_number"]).to_csv(file_path, index=False)

    # Get the current date
    date_of_forecast = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Append the data to the CSV
    calibration_data = pd.read_csv(file_path)
    calibration_data = calibration_data.append({
        "data_set_name": data_set_name,
        "forecasted_result": forecasted_result,
        "actual_result": actual_result,
        "date_of_forecast": date_of_forecast,
        "version_number": version_number
    }, ignore_index=True)
    calibration_data.to_csv(file_path, index=False)

    print(f"Forecast results saved to {file_path}.")

# Prompt the user to save forecast results to calibration data
save_calibration_data(
    data_set_name=csv_base_name,  # Use the base name of the CSV as the dataset name
    forecasted_result=Model.status_quo  # Use the final status quo from the simulation
)

#------------------------------------------------------------------------------------------

# Save the updated DataFrame as a CSV in the subfolder
output_csv_name = f"{csv_base_name}_positions.csv"
output_csv_path = os.path.join(subfolder_path, output_csv_name)
df_output.to_csv(output_csv_path, index=False)

# Saving a plot of player's evolving positions
# Plot each actor's position over the rounds
df_plot = pd.DataFrame(position_recorder).T
plt.figure(figsize=(10, 6))  # Optional: adjust the figure size
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

# Save the plot to the subfolder
plot_file_name = f"{csv_base_name}_positions_plot.png"
plot_file_path = os.path.join(subfolder_path, plot_file_name)
plt.savefig(plot_file_path, bbox_inches='tight')  # Ensure nothing gets clipped in the saved file
plt.close()  # Close the plot to free memory

# Create an N x N matrix of players' beliefs
belief_matrix = pd.DataFrame(index=[player.name for player in players], columns=[player.name for player in players])

# Saving N x N matrix on player beliefs.
# Populate the matrix with beliefs
for player_a in players:
    for player_b in players:
        if player_a.name == player_b.name:
            belief_matrix.at[player_a.name, player_b.name] = 1.0  # Self-belief is always 1.0
        else:
            belief_matrix.at[player_a.name, player_b.name] = player_a.beliefs.get(player_b.name, 0.0)

# Save the beliefs matrix as a CSV file in the subfolder
beliefs_csv_name = f"{csv_base_name}_beliefs_matrix.csv"
beliefs_csv_path = os.path.join(subfolder_path, beliefs_csv_name)
belief_matrix.to_csv(beliefs_csv_path)

# Final notification of saved outputs
# Notify the user of results
print(f"Results saved to '{subfolder_path}':")
print(f"  - Chart: {plot_file_name}")
print(f"  - Data: {output_csv_name}")
print(f"  - Beliefs: {beliefs_csv_name}")