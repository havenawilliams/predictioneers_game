#Import packages
import pygambit
from statistics import mean
from math import sqrt

#Import functions
from pg_player_class import Player, Model, import_players_from_csv
from play_game import get_solution, play_game, Bayesian_updating, update_position
from update_game import *

#Load a game structure
g = pygambit.Game.read_game("game_alpha_0.0_game_1.gbt")

#Test pg_player_class functions
#Load players
players = import_players_from_csv(".\data\\fake_data_unit_test.csv")

#Create players as objects
player_a = players[0]
player_b = players[1]
player_a.name
player_b.name

#Examine conflict probabilities
player_a.conflict_probabilities(player_b, players)
player_b.conflict_probabilities(player_a, players)
player_a.victory_probability
player_b.victory_probability

#Test play_game functions
solution = get_solution(g)
solution

credible_proposals = play_game(player_a, player_b, g, 1, solution)
credible_proposals

#Bayesian updating function test
Bayesian_updating(g, credible_proposals, solution, player_a, player_b)
player_b.beliefs #.795 for pg_alpha_00_game_unit_test

#Inspect average positions (component in update position function)
average_utility_a = mean([float(node.outcome["Player 1"]) for node in credible_proposals])
average_utility_b = mean([float(node.outcome["Player 2"]) for node in credible_proposals])
average_utility_a
average_utility_b

#Check that game updates payoffs
update_game(player_a, player_b, g)
g

#Update position function
credible_proposals
update_position(player_a, player_b, g, credible_proposals)
player_a.position
player_b.position

#Inspect player cost functions
player_a.tau(player_b, 1, 1, 1, 1)
player_a.tau.__doc__
player_a.alpha(player_b, 1, 1, 1, 1)
player_a.alpha.__doc__
player_a.phi(player_b, 1, 1, 1, 1)
player_a.phi.__doc__
player_a.gamma(player_b, 1, 1, 1, 1)
player_a.gamma.__doc__

player_a.position

#Inspect individual outcome functions
outcome_1a(player_a, player_b, 1, 1, 1, 1)
outcome_1a.__doc__
outcome_1b(player_a, player_b, 1, 1, 1, 1)
outcome_1b.__doc__

outcome_2a(player_a, player_b, 1, 1, 1, 1)
outcome_2a.__doc__
outcome_2b(player_a, player_b, 1, 1, 1, 1)
outcome_2b.__doc__

outcome_3a(player_a, player_b, 1, 1, 1, 1)
outcome_3a.__doc__
outcome_3b(player_a, player_b, 1, 1, 1, 1)
outcome_3b.__doc__

outcome_4a(player_a, player_b, 1, 1, 1, 1)
outcome_4a.__doc__
outcome_4b(player_a, player_b, 1, 1, 1, 1)
outcome_4b.__doc__

outcome_5a(player_a, player_b, 1, 1, 1, 1)
outcome_5a.__doc__
outcome_5b(player_a, player_b, 1, 1, 1, 1)
outcome_5b.__doc__

outcome_6a(player_a, player_b, 1, 1, 1, 1)
outcome_6a.__doc__
outcome_6b(player_a, player_b, 1, 1, 1, 1)
outcome_6b.__doc__

outcome_7a(player_a, player_b, 1, 1, 1, 1)
outcome_7a.__doc__
outcome_7b(player_a, player_b, 1, 1, 1, 1)
outcome_7b.__doc__

outcome_8a(player_a, player_b, 1, 1, 1, 1)
outcome_8a.__doc__
outcome_8b(player_a, player_b, 1, 1, 1, 1)
outcome_8b.__doc__

