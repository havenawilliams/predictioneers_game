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
players = import_players_from_csv("data/israel_hamas_war.csv")

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