import unittest
import pygambit
from statistics import mean
from pg_player_class import Player, Model, import_players_from_csv
from play_game import get_solution, play_game, Bayesian_updating
from update_game import update_game, update_position

class TestPredictioneersGame(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Load a game structure and players
        cls.g = pygambit.Game.read_game("game_alpha_0.0_game_1.gbt")
        cls.players = import_players_from_csv("./data/fake_data_unit_test.csv")
        cls.player_a = cls.players[0]
        cls.player_b = cls.players[1]

    def test_player_names(self):
        # Test player name assignments
        self.assertEqual(self.player_a.name, "Player 1")
        self.assertEqual(self.player_b.name, "Player 2")

    def test_conflict_probabilities(self):
        # Test conflict probabilities
        self.player_a.conflict_probabilities(self.player_b, self.players)
        self.player_b.conflict_probabilities(self.player_a, self.players)
        self.assertGreaterEqual(self.player_a.victory_probability, 0)
        self.assertLessEqual(self.player_a.victory_probability, 1)
        self.assertGreaterEqual(self.player_b.victory_probability, 0)
        self.assertLessEqual(self.player_b.victory_probability, 1)

    def test_get_solution(self):
        # Test solution generation
        solution = get_solution(self.g)
        self.assertIsInstance(solution, pygambit.Game)

    def test_play_game(self):
        # Test credible proposals
        solution = get_solution(self.g)
        credible_proposals = play_game(self.player_a, self.player_b, self.g, 1, solution)
        self.assertTrue(len(credible_proposals) > 0)

    def test_bayesian_updating(self):
        # Test Bayesian updating
        solution = get_solution(self.g)
        credible_proposals = play_game(self.player_a, self.player_b, self.g, 1, solution)
        Bayesian_updating(self.g, credible_proposals, solution, self.player_a, self.player_b)
        self.assertIn(self.player_b.name, self.player_a.beliefs)

    def test_update_game(self):
        # Test game updates
        update_game(self.player_a, self.player_b, self.g)
        self.assertIsInstance(self.g, pygambit.Game)

    def test_update_position(self):
        # Test position updates
        solution = get_solution(self.g)
        credible_proposals = play_game(self.player_a, self.player_b, self.g, 1, solution)
        update_position(self.player_a, self.player_b, self.g, credible_proposals)
        self.assertNotEqual(self.player_a.position, 0)
        self.assertNotEqual(self.player_b.position, 0)

    def test_cost_functions(self):
        # Test individual cost functions
        tau_value = self.player_a.tau(self.player_b, 1, 1, 1, 1)
        self.assertGreater(tau_value, 0)

    def test_outcome_functions(self):
        # Test individual outcome functions
        outcome_1a_result = outcome_1a(self.player_a, self.player_b, 1, 1, 1, 1)
        self.assertIsInstance(outcome_1a_result, float)

if __name__ == "__main__":
    unittest.main()
