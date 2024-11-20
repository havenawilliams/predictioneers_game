#Predictioneer's Game
import csv
from dataclasses import dataclass
from typing import List

'''
This document introduces three key elements:
1. Player class, the individual unit of analysis for the predictioneer's game.
2. Model class, a classmethod used to store the values of the status quo and other global parameters.
3. The import_players_from_csv function that imports a dataset from the working directory, turns them
into intances of the player class, retains those instances in a list, and updates the Model class.
'''

@dataclass
class Player:
    name: str
    position: float #Between 0 and 1
    capabilities: float #Any number, normalized on import
    salience: float #Between 0 and 1
    resolve: float #Between 0 and 1, even though BdM uses 0 and 100. There's no way, with the way he's written it, that he isn't normalizing it later.
    true_hawk_type: int #Not implemented as of 3/26/24
    true_retaliatory_type: int #Not implemented as of 3/26/24
    
    def __post_init__(self):
        self.beliefs = {}
        self.votes = self.capabilities * self.salience #This is used to calculate clout in the model's probability space in the Model class
        self.ideal_point = self.position #unused, for now, but might be useful for resolve
        self.strategy = "unknown" #Initialization value is a placeholder. This is updated after players interact. This is used to check if all players have converged to universal position. There is currently no implementation of this as of 3/26/24.

    #The basic utility that a player attaches to another player's position
    def utility(self, other_player_position):
        '''Utility is one minus the squared difference between the positions, weighted by resolve.'''
        theta = self.resolve
        beta = 1 - theta
        return ((1 - (self.position - other_player_position) ** 2) ** theta) * ((1 - (self.position - Model.status_quo) ** 2) ** beta)
    
    def utility_point(self, input_position):
        '''This function is the same as the utility function but takes an arbitrary point as an argument.'''
        theta = self.resolve
        beta = 1 - theta
        return ((1 - (self.position - input_position) ** 2) ** theta) * ((1 - (self.position - input_position) ** 2) ** beta)

    def conflict_probabilities(self, other_player, players):
        '''Takes self, other_player, and players as arguments and returns the 
        odds of player self prevailing over other_player in the space defined by all players.
        It runs every time the players interact dyadically.'''
        numerator = sum([player.salience * player.capabilities * (player.utility(self.position) - player.utility(other_player.position)) for player in players if (player.utility(self.position) - player.utility(other_player.position)) > 0])
        denominator = sum([player.salience * player.capabilities * abs(player.utility(self.position) - player.utility(other_player.position)) for player in players])
        if denominator == 0:
            self.victory_probability = 1
            other_player.victory_probability = 1
        else:
            self.victory_probability = numerator / denominator
            other_player.victory_probability = 1 - (numerator / denominator)

    #Cost variables
    def alpha(self, other_player, player_a_hawk, player_a_retaliatory, player_b_hawk, player_b_retaliatory): #hawk influenced
        '''The heuristic cost of trying to coerce and meeting resistance.
        Hawks pay lower cost alpha because they perceive resistance as less of a threat.
        Associated with outcome 2.'''
        if player_a_hawk == 1:
            return (other_player.capabilities * .01 / self.capabilities) #cost is lower for hawk players
        elif player_a_hawk == 0:
            return (other_player.capabilities * .02 / self.capabilities) #cost is larger for not hawk players

    def gamma(self, other_player, player_a_hawk, player_a_retaliatory, player_b_hawk, player_b_retaliatory): #retaliatory influenced
        '''The heuristic cost of being coerced and not resisting.
        If other player is retaliatory then costs to player are higher.
        Associated with outcome 5.'''
        if player_b_retaliatory == 1:
            return (other_player.capabilities * .02 / self.capabilities) #cost is higher with retaliatory opponent
        elif player_b_retaliatory == 0:
            return (other_player.capabilities * .01 / self.capabilities) #cost is lower for not retaliatory opponent

    def tau(self, other_player, player_a_hawk, player_a_retaliatory, player_b_hawk, player_b_retaliatory): #retaliatory influenced
        '''The heuristic cost of being coerced and resisting.
        If other player is retaliatory then costs to player are higher.
        Associated with outcome 4.'''
        if player_b_retaliatory == 1:
            return (other_player.capabilities * .02 / self.capabilities) #cost is higher with retaliatory opponent
        elif player_b_retaliatory == 0:
            return (other_player.capabilities * .01 / self.capabilities) #cost is lower for not retaliatory opponent

    def phi(self, other_player, player_a_hawk, player_a_retaliatory, player_b_hawk, player_b_retaliatory): #hawk influenced
        '''The heuristic cost of cost of coercing.
        If type is hawk, player pays lower cost.
        Associated with outcomes 2, 3, 4.'''
        if player_a_hawk == 1:
            return (other_player.capabilities * .01 / self.capabilities)
        elif player_a_hawk == 0:
            return (other_player.capabilities * .02 / self.capabilities)

@dataclass
class Model:
    status_quo = 0

    @classmethod
    def update_status_quo(self, players):
        '''update_status_quo() function is invoked in import_players_from_csv().'''
        policy_vote = sum([player.capabilities * player.salience * player.position for player in players])
        total_votes = sum([player.capabilities * player.salience for player in players])
        self.status_quo = policy_vote / total_votes

#Import players
def import_players_from_csv(file_path: str) -> List[Player]:
    '''
    This is a very complex function that does more than it's name suggests.
    First, it imports players from a compatible CSV and then normalizes player positions, salience, resolve, and capabilities.
    Next, it updates the status quo.
    It also introduces a new player attribute of uncertainty via a dictionary so that all players have uncertainty for each player.
    It returns all of the newly imported player objects in a list.
    '''
    #Empty list of players
    players = []

    #Import csv object into class
    expected_fieldnames = ['name', 'position', 'capabilities', 'salience', 'resolve', 'true_hawk_type', 'true_retaliatory_type']
    with open(file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        if reader.fieldnames != expected_fieldnames:
            raise ValueError(f"Expected field names: {expected_fieldnames}. Found: {reader.fieldnames}")
        for row in reader:
            players.append(Player(row['name'], float(row['position']), float(row['capabilities']), float(row['salience']), float(row['resolve']), float(row['true_hawk_type']), float(row['true_retaliatory_type'])))

    #If positions are out of 100 return them out of 1
    if max([player.position for player in players]) > 1:
        print("WARNING: non-recommended position range detected. Values should range between 1 to 0, inclusive. Values were automatically divided by 100.")
        for player in players:
            player.position = player.position / 100
    
    #If salience is out of 100 return them out of 1
    if max([player.salience for player in players]) > 1:
        print("WARNING: non-recommended salience range detected. Values should range between 1 to 0, inclusive. Values were automatically divided by 100.")
        for player in players:
            player.salience = player.salience / 100
    
    #If resolve is out of 100 return them out of 1
    if max([player.resolve for player in players]) > 1:
        print("WARNING: non-recommended resolve range detected. Values should range between 1 to 0, inclusive. Values were automatically divided by 100.")
        for player in players:
            player.resolve = player.resolve / 100

    #Normalize capabilities
    total_capabilities = sum([player.capabilities for player in players])
    print("WARNING: capbilities were normalized.")
    for player in players:
        player.capabilities = player.capabilities / total_capabilities
    
    #Update status quo
    Model.update_status_quo(players)

    #Add status quo attribute to all players
    for player in players:
        player.status_quo = Model.status_quo
    
    #Instantiate uncertainty of beliefs for each player
    for player in players:
        player.beliefs = {other_player.name: 0.5 for other_player in players if other_player != player}
    
    #Returns all players as a list object :)
    return players