from itertools import combinations, permutations
import pygambit
from check_utility import *
from play_game import *
from update_game import *

def run_game_simulation(players, g, Model, args = False, cutoff = False, max_rounds=100):
    """
    Runs the Predictioneer's Game simulation. This is the meat of the simulation.

    Args:
        players (list): List of Player objects.
        g (pygambit.Game): Game structure object. Uses a pygambit file of .efg format (etf stands for extended form game).
        Model (object): The Model class contains the status quo. This class is documented in pg_players_class.py.
        args (argparse.Namespace): Parsed arguments from argparse. These argparse arguments are documented in main.py.
        max_rounds (int): Maximum number of rounds for the simulation. If you ever hit 100 there is probably an error since the alpha model currently converges very early on.

    Returns:
        dict: Results of the simulation, including final status quo, utility recorder,
              position recorder, status quo recorder, and number of rounds completed.
    """
    # Create dictionary of games. There are as many games as they are dyadic permutations of players.
    games_for_combinations = {}
    for combination in permutations(players, 2):
        key = tuple(player.name for player in combination)
        games_for_combinations[key] = g

    # Initialize status quo
    initial_status_quo = Model.status_quo
    #print(f"Initial status quo is {initial_status_quo}, {players[0].position} is {players[0].name}'s start position")

    # Initializing data structures for the game
    round_number = 0 # captures current round number 
    utility_recorder = {} # records utility of players in every round
    position_recorder = {} # records position of players in every round
    status_quo_recorder = []  # records status quo in every round

    Model.update_status_quo(players)

    # Main game loop
    finished_updating_positions = args.auto  # Skip position updates if in auto mode

    while round_number < max_rounds:
        utility_recorder[round_number] = {}
        position_recorder[round_number] = {}
        for player in players:
            utility_recorder[round_number][player.name] = player.utility(Model.status_quo)
            position_recorder[round_number][player.name] = player.position

        # Stores previous round positions. 
        # Players compare their utility in the current round to the utility in the previous round to determine if they want to continue playing the game.
        # That function check_utility_increasing uses these arguments to end the game if the sum of player utilities in the current round is greater than in the next round.
        for player in players:
            player.previous_position = player.position

        # Model each player pair
        for player_pair in combinations(players, 2):
            
            print(Model.status_quo, round_number, [player.position for player in players])

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
        
        #Update status quo after round (previously WIHIN the above for loop as of 12/3/24)
        Model.update_status_quo(players)
        # Record the status quo for this round
        status_quo_recorder.append(Model.status_quo)

        # Check end game rule
        if not cutoff:
            if check_utility_decreasing(round_number, utility_recorder):
                round_number += 1
                break

        round_number += 1

    print(f"Game finished with status quo {status_quo_recorder[-1]} after {round_number} rounds.")

    # Return results
    return {
        "final_status_quo": Model.status_quo,
        "utility_recorder": utility_recorder,
        "position_recorder": position_recorder,
        "status_quo_recorder": status_quo_recorder,
        "rounds_completed": round_number
    }
