#Import packages
import os
import pygambit
from itertools import combinations
import copy

#Get cwd
os.chdir("G:\\My Drive\\R\\ON Research Projects\\predictioneers_game\\predictioneers_mini_february_2024")

#Import functions
from pg_player_class import Player, Model, import_players_from_csv
from play_game import get_solution, play_game, Bayesian_updating
from update_game import *

#Load a game structure. Multiple copies will eventually be made.
g = pygambit.Game.read_game("pg_mini_2024_payoffs_0_1.gbt")

#Load players
players = import_players_from_csv("players.csv")

player_a = players[0]
player_b = players[1]


player_a.outcome_1a(player_b, 1, 1, 1, 1)
player_a.utility(player_b)
player_a.utility_point(0)

player_a_test_utility = []
for i in range(0, 20):
    player_a_test_utility.append(round(player_a.utility_point(i * 0.05), 3))
print(player_a_test_utility)


import matplotlib.pyplot as plt

# Assuming player_a.utility_point() is a method that takes a single argument and returns a value
# We'll simulate it with a mock function for the purpose of this example
def mock_utility_point(value):
    # This is a placeholder for the actual utility_point function of player_a
    return value * 2  # Example operation, replace with the actual logic

player_a_test_utility = []
x_values = [i * 0.05 for i in range(0, 20)]

for i in x_values:
    player_a_test_utility.append(round(player_a.utility_point(i), 3))

# Plotting
plt.figure(figsize=(10, 6))
plt.plot(x_values, player_a_test_utility, '-o', label='Utility')
plt.xlabel('X Values')
plt.ylabel('Utility Values')
plt.title('Utility Function Graph')
plt.legend()
plt.grid(True)
plt.show()