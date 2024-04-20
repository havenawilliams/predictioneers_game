#This script updates the game tree according to the functions laid out in BdM 2011.
#It consists of a series of updater functions, a map of those functions to node names, and a final updater.

from pygambit_gather_terminal_nodes import gather_terminal_nodes
from pg_player_class import Model

#Updater functions (in pairs with A being player up the game tree and B being down the game tree)
#Outcome functions of different numbers never update the same node.
#For example, a terminal node might be outcome 1 and only outcome 1a or outcome 1b are used to update payoff.
def clamp(value):
    '''Clamp the value between 0 and 1.'''
    return max(0, min(1, value))

def outcome_1a(player_a, player_b, player_a_hawk, player_a_retaliatory, player_b_hawk, player_b_retaliatory):
    '''A's expected utility | B accept's A's proposal.'''
    return clamp(player_a.utility(player_a.position))

def outcome_1b(player_a, player_b, player_a_hawk, player_a_retaliatory, player_b_hawk, player_b_retaliatory):
    '''B's expected utility | B accept's A's proposal.'''
    return clamp(player_b.utility(player_a.position))

def outcome_2a(player_a, player_b, player_a_hawk, player_a_retaliatory, player_b_hawk, player_b_retaliatory):
    '''A's expected utility if A tries to coerce and B resits.'''
    return clamp(outcome_6a(player_a, player_b, player_a_hawk, player_a_retaliatory, player_b_hawk, player_b_retaliatory) - player_a.alpha(player_b, player_a_hawk, player_a_retaliatory, player_b_hawk, player_b_retaliatory) - player_a.phi(player_b, player_a_hawk, player_a_retaliatory, player_b_hawk, player_b_retaliatory))

def outcome_2b(player_a, player_b, player_a_hawk, player_a_retaliatory, player_b_hawk, player_b_retaliatory):
    '''B's expected utility if A tries to coerce and B resists.'''
    return clamp(outcome_6b(player_a, player_b, player_a_hawk, player_a_retaliatory, player_b_hawk, player_b_retaliatory) - player_b.tau(player_b, player_a_hawk, player_a_retaliatory, player_b_hawk, player_b_retaliatory))

def outcome_3a(player_a, player_b, player_a_hawk, player_a_retaliatory, player_b_hawk, player_b_retaliatory):
    '''A's expected utility if A coerces B and B gives in.'''
    return clamp(player_a.utility(player_a.position) - player_a.phi(player_b, player_a_hawk, player_a_retaliatory, player_b_hawk, player_b_retaliatory))

def outcome_3b(player_a, player_b, player_a_hawk, player_a_retaliatory, player_b_hawk, player_b_retaliatory):
    '''B's expected utility if A coerces B and B gives in.'''
    return clamp(player_b.utility(player_a.position) - player_b.gamma(player_b, player_a_hawk, player_a_retaliatory, player_b_hawk, player_b_retaliatory))

def outcome_4a(player_a, player_b, player_a_hawk, player_a_retaliatory, player_b_hawk, player_b_retaliatory):
    '''A's expected utility if B tries to coerce A and A resists.'''
    return clamp(outcome_6a(player_a, player_b, player_a_hawk, player_a_retaliatory, player_b_hawk, player_b_retaliatory) - player_a.gamma(player_b, player_a_hawk, player_a_retaliatory, player_b_hawk, player_b_retaliatory))

def outcome_4b(player_a, player_b, player_a_hawk, player_a_retaliatory, player_b_hawk, player_b_retaliatory):
    '''B's expected utility if B tries to coerce A and A resists.'''
    return clamp(outcome_6b(player_a, player_b, player_a_hawk, player_a_retaliatory, player_b_hawk, player_b_retaliatory) - player_b.alpha(player_b, player_a_hawk, player_a_retaliatory, player_b_hawk, player_b_retaliatory) - player_b.phi(player_b, player_a_hawk, player_a_retaliatory, player_b_hawk, player_b_retaliatory))

def outcome_5a(player_a, player_b, player_a_hawk, player_a_retaliatory, player_b_hawk, player_b_retaliatory):
    '''A's expected payoff if B coerces A and A gives in.'''
    return clamp(player_a.utility(player_b.position) - player_a.gamma(player_b, player_a_hawk, player_a_retaliatory, player_b_hawk, player_b_retaliatory))

def outcome_5b(player_a, player_b, player_a_hawk, player_a_retaliatory, player_b_hawk, player_b_retaliatory):
    '''B's expected payoff if B coerces A and A gives in.'''
    return clamp(player_b.utility(player_b.position) - player_b.phi(player_b, player_a_hawk, player_a_retaliatory, player_b_hawk, player_b_retaliatory))

def outcome_6a(player_a, player_b, player_a_hawk, player_a_retaliatory, player_b_hawk, player_b_retaliatory):
    '''A's expected utility if A and B compromise.'''
    return clamp(player_a.victory_probability * (1 - player_a.utility(player_a.position)) + (1 - player_a.victory_probability) * (1 - player_a.utility(player_b.position)))

def outcome_6b(player_a, player_b, player_a_hawk, player_a_retaliatory, player_b_hawk, player_b_retaliatory):
    '''B's expected utility if A and B compromise.'''
    return clamp(player_a.victory_probability * (1 - player_b.utility(player_a.position)) + (1 - player_a.victory_probability) * (1 - player_b.utility(player_b.position)))

def outcome_7a(player_a, player_b, player_a_hawk, player_a_retaliatory, player_b_hawk, player_b_retaliatory):
    '''A's utility for status quo.'''
    return clamp(((1 - (player_a.position - Model.status_quo) ** 2) * player_a.salience))

def outcome_7b(player_a, player_b, player_a_hawk, player_a_retaliatory, player_b_hawk, player_b_retaliatory):
    '''B's utility for status quo.'''
    return clamp(((1 - (player_b.position - Model.status_quo) ** 2) * player_b.salience))

def outcome_8a(player_a, player_b, player_a_hawk, player_a_retaliatory, player_b_hawk, player_b_retaliatory):
    '''A's expected utility | A offers to compromise.'''
    return clamp(player_a.utility(player_b.position))

def outcome_8b(player_a, player_b, player_a_hawk, player_a_retaliatory, player_b_hawk, player_b_retaliatory):
    '''B's expected utility | A offers to compromise.'''
    return clamp(player_b.utility(player_b.position))

#"Connecting dicitonaries" used later for mapping the name of the node to the payoff function, by player
#Player A, up the tree
node_function_map_a = {
    f'outcome_{i}': globals()[f'outcome_{i}a'] for i in range(1, 9) if f'outcome_{i}a' in globals()
}

#Player B, down the tree
node_function_map_b = {
    f'outcome_{i}': globals()[f'outcome_{i}b'] for i in range(1, 9) if f'outcome_{i}b' in globals()
}

#Function to update the game tree that maps the names of the terminal nodes to the connecting dictionaries and, thus, the utility values
def update_game(player_a, player_b, game):
    terminal_nodes_hawk = gather_terminal_nodes(game.root.children[0])
    terminal_nodes_dove = gather_terminal_nodes(game.root.children[1])
    
    for node in terminal_nodes_hawk:
        # For player_a
        if node.label in node_function_map_a:
            # Retrieve and call the function for player_a
            function_to_execute_a = node_function_map_a[node.label]
            payoff_a = function_to_execute_a(player_a, player_b, 1, 1, 1, 1) #1's are placeholder values for retaliatory parts not programmed
            node.outcome["Player 1"] = payoff_a
            
        # For player_b
        if node.label in node_function_map_b:
            # Retrieve and call the function for player_b
            function_to_execute_b = node_function_map_b[node.label]
            payoff_b = function_to_execute_b(player_a, player_b, 1, 1, 1, 1)
            node.outcome["Player 2"] = payoff_b
    
    for node in terminal_nodes_dove:
            # For player_a
        if node.label in node_function_map_a:
            # Retrieve and call the function for player_a
            function_to_execute_a = node_function_map_a[node.label]
            payoff_a = function_to_execute_a(player_a, player_b, 0, 1, 1, 1) #1's are placeholder values for retaliatory parts not programmed
            node.outcome["Player 1"] = payoff_a
            
        # For player_b
        if node.label in node_function_map_b:
            # Retrieve and call the function for player_b
            function_to_execute_b = node_function_map_b[node.label]
            payoff_b = function_to_execute_b(player_a, player_b, 0, 1, 1, 1)
            node.outcome["Player 2"] = payoff_b
            
        else:
            print(f"No function mapped or missing player in outcomes for node: {node.label}")