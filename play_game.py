from pygambit_gather_terminal_nodes import gather_terminal_nodes
import pygambit
from pg_player_class import Model
from math import sqrt
from statistics import mean

#Sript summary
#This script has game play functions that don't update the game itself.
#Get solution provides a solution object.
#Play game produces a list of all credible proposals.
#Bayesian updating provides the updated beliefs of the players.
#Update position actually changes the player's positions based on the credible proposals.

def clamp(value):
    '''Clamp the value between 0 and 1.'''
    return max(0, min(1, value))

def get_solution(game):
    equilibrium = pygambit.nash.logit_solve(game)[0]
    return equilibrium

def play_game(player_1, player_2, game, theta, solution):
    '''
    Play game function with first player being up the game tree and second player being down the game tree.
    Game object is loaded from local dictionary to allow game types to be written faster (avoids disk writing).
    Theta is entirely position based.
    Beta is entirely resolve based.

    Note to self on 3/27/24: Credible outcomes need to be weighted, eventually.
    '''
    #For more on Cobb-Douglass utility functions, see: https://en.wikipedia.org/wiki/Cobb-Douglas_production_function
    beta = 1 - theta

    #Instantiate empty list of credible proposals
    credible_proposals = []

    #Gather terminal nodes
    game_terminal_nodes = gather_terminal_nodes(game.root)

    #Credible proposal condition 1
    for node in game_terminal_nodes:
        if "coerce" in node.label and solution.realiz_prob(node) > 0:
            credible_proposals.append(node)  # Append the node to the list

    #Credible proposal condition 2
    player_1_condition_2_bound = player_1.utility(player_2.position) * ((1 - (player_1.position - player_2.position)**2)**theta) * ((1 - (player_1.resolve - player_2.resolve)**2)**beta)

    for node in game_terminal_nodes:
        if abs(float(node.outcome.__getitem__("Player 1")) - player_1.position) < player_1_condition_2_bound:
            credible_proposals.append(node)  # Append the node to the list

    if credible_proposals != []:
        return credible_proposals
    else:
        for node in game_terminal_nodes:
            credible_proposals.append(node)
        return credible_proposals
   
def Bayesian_updating(game, credible_proposals, solution, player_a, player_b):
    #Get all of the nodes in information sets
    player = game.players["Player 2"]
    nodes_in_information_sets = []
    for infoset in player.infosets:
        for node in infoset.members:
            nodes_in_information_sets.append(node)

    #2. Create a dictionary with terminal nodes as keys and values as parent nodes.
    terminal_nodes_information_nodes_dct = {}
    def terminal_nodes_information_nodes_assigner(node):
        # Check if the node's parent is not in the set of nodes within information sets
        if node.parent not in nodes_in_information_sets:
            #If not, recursively call this function with the parent node
            terminal_nodes_information_nodes_assigner(node.parent)
        else:
            #Assign the parent node to a unique key in the dictionary
            terminal_nodes_information_nodes_dct[node] = node.parent

    for credible_proposal in credible_proposals:
        terminal_nodes_information_nodes_assigner(credible_proposal)

    #3. Use the credible outcomes obtained from the play_game() function to get their parent node and check the belief.
    beliefs = []
    for key, value in terminal_nodes_information_nodes_dct.items():
        beliefs.append(solution.belief(value))
    average_belief = sum(beliefs) / len(beliefs) if beliefs else 0
    player_b.beliefs[player_a.name] = average_belief

#Update position function
def update_position(player_a, player_b, game, credible_proposals):
    '''Takes a player and utility of new position and returns a new position for them.
    The solution is a real solution to the inverse of the quadratic loss utility function.
    '''
    average_utility_a = mean([float(node.outcome["Player 1"]) for node in credible_proposals])
    average_utility_b = mean([float(node.outcome["Player 2"]) for node in credible_proposals])
    if player_a.position > player_b.position:
        player_a.position = clamp(Model.status_quo + sqrt(1 - average_utility_a) / 2)
    else:
        player_a.position = clamp(Model.status_quo - sqrt(1 - average_utility_a) / 2)
    if player_b.position > player_a.position:
        player_b.position = clamp(Model.status_quo + sqrt(1 - average_utility_b) / 2)
    else:
        player_b.position = clamp(Model.status_quo - sqrt(1 - average_utility_b) / 2)
    