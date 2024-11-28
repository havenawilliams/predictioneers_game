from itertools import combinations
import pygambit
from check_utility import *
from play_game import *
from update_game import *

def run_game_simulation(players, g, Model, args, max_rounds=100):
    """
    Run the Predictioneer's Game simulation.

    Args:
        players (list): List of Player objects.
        g (pygambit.Game): Game structure object.
        Model (object): The Model class or instance with status quo and methods.
        args (argparse.Namespace): Parsed arguments from argparse.
        max_rounds (int): Maximum number of rounds for the simulation.

    Returns:
        dict: Results of the simulation, including final status quo, utility recorder,
              position recorder, status quo recorder, and number of rounds completed.
    """
    # Create dictionary for games per player
    games_for_combinations = {}
    for combination in combinations(players, 2):
        key = tuple(player.name for player in combination)
        games_for_combinations[key] = g

    # Initialize status quo
    initial_status_quo = Model.status_quo

    # Initialize round number
    round_number = 0

    # Initialize data structures to capture intra-round data
    utility_recorder = {}
    position_recorder = {}
    status_quo_recorder = []  # New recorder for status quo

    # Main game loop
    finished_updating_positions = args.auto  # Skip position updates if in auto mode

    while round_number < max_rounds:
        # Record initial round data
        utility_recorder[round_number] = {}
        position_recorder[round_number] = {}
        for player in players:
            utility_recorder[round_number][player.name] = player.utility(Model.status_quo)
            position_recorder[round_number][player.name] = player.position

        # Record the status quo for this round
        status_quo_recorder.append(Model.status_quo)

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

    # Return results
    return {
        "final_status_quo": Model.status_quo,
        "utility_recorder": utility_recorder,
        "position_recorder": position_recorder,
        "status_quo_recorder": status_quo_recorder,
        "rounds_completed": round_number
    }
