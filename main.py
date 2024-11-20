#Import packages
import os
import pygambit
import pandas as pd
from itertools import combinations
import matplotlib.pyplot as plt

#Get cwd
os.chdir("C:\\Users\\haw27\Documents\\Haven_Code_Projects\\predictioneers_game\\predictioneers_game_alpha_00")

#Import functions
from pg_player_class import Player, Model, import_players_from_csv
from play_game import get_solution, play_game, Bayesian_updating, update_position
from update_game import *
from check_utility import check_utility_decreasing

#Load a game structure. Multiple copies will eventually be made.
g = pygambit.Game.read_game("game_alpha_0.0_game_1.gbt")

#Load players
players = import_players_from_csv("israel_hamas_war.csv")


#Create dictionary for games per player
games_for_combinations = {}
for combination in combinations(players, 2):
    key = tuple(player.name for player in combination)
    games_for_combinations[key] = g

#Initialize status quo
initial_status_quo = Model.status_quo

#Initialize round number, which increments by single integers and keeps track of the current round being played
round_number = 0

#Initialize data structure to capture intra-round data
utility_recorder = {}
position_recorder = {}

#Main function
#Main for loop plays the whole game
for number in range(0, 10):

    #Create new key in round recorder to record round values
    utility_recorder[round_number] = {}
    position_recorder[round_number] = {}

    #Populate round values with a nested dictionary
    for player in players:
        utility_recorder[round_number][player.name] = player.utility(Model.status_quo)
        position_recorder[round_number][player.name] = player.position
    
    #Store previous round positions
    for player in players:
        player.previous_position = player.position

    #Model each player pair
    for player_pair in combinations(players, 2):
        
        #Update the status quo
        Model.update_status_quo(players)

        #Update the player probabilities of victory over another
        player_pair[0].conflict_probabilities(player_pair[1], players)
        player_pair[1].conflict_probabilities(player_pair[0], players)

        #Update the game
        #Access player names as a tuple to access game dictionary
        players_for_round = tuple(player.name for player in combination)
        #Update beliefs
        #Update game probabilities
        games_for_combinations[players_for_round].set_chance_probs(games_for_combinations[players_for_round].root.infoset, [player_pair[0].beliefs[player_pair[1].name], 1 - player_pair[0].beliefs[player_pair[1].name]])
        #Update the game so that the game has values relevant to the players for the specific round
        update_game(player_pair[0], player_pair[1], games_for_combinations[players_for_round])
        
        #Compute the solution of the updated game
        solution = get_solution(g)
        
        #From the solution, get the credible outcomes as described in BdM 2011
        credible_proposals = play_game(player_pair[0], player_pair[1], g, 1, solution)
        
        #Implement Bayesian updating function to have Player B learn Plaer A's type
        Bayesian_updating(g, credible_proposals, solution, player_pair[0], player_pair[1])
        
        #Update position functions
        update_position(player_pair[0], player_pair[1], games_for_combinations[players_for_round], credible_proposals)

    #Check end game rule
    if check_utility_decreasing(round_number, utility_recorder) == True:
        #Revert to previous round's positions
        for player in players:
            player.position = player.previous_position
        break
    else:
        print(f"Game continues past round {round_number}.")

        #Update round number
        round_number += 1
        continue

#Game conclusion summary statements
print(f"Game is finished with status quo {Model.status_quo} after round {round_number}.")

#Export positions
df = pd.DataFrame(position_recorder)
df_transposed = df.T
df_transposed.to_csv('output.csv')

# Plot each actor's position over the rounds
for actor in df.index:
    plt.plot(df.columns, df.loc[actor], marker='o', label=actor)
    
    # Label each actor at the last position in their line
    plt.annotate(actor, (df.columns[-1], df.loc[actor].iloc[-1]), 
                 textcoords="offset points", xytext=(5,0), ha='left', rotation = 45, fontsize = 5)

# Add title and labels
plt.title('Change in Position per Actor Over Rounds')
plt.xlabel('Rounds')
plt.ylabel('Position')

# Show the plot
plt.show()

players

Model.status_quo