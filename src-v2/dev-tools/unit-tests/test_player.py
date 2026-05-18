# src-v2/unit-tests/test_player.py
import unittest
import sys
import os

# Look up TWO directories: unit-tests -> dev-tools -> src-v2
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from player import Player


class TestPlayer(unittest.TestCase):

    def setUp(self):
        self.player = Player(name="Battleship", token="battleship")

    def test_initial_state(self):
        self.assertEqual(self.player.balance, 1500)
        self.assertEqual(self.player.position, 0)
        self.assertFalse(self.player.is_in_jail)

    def test_add_and_pay_balance(self):
        self.player.add_balance(200)
        self.assertEqual(self.player.balance, 1700)

        self.player.pay_balance(500)
        self.assertEqual(self.player.balance, 1200)

    def test_move_forward_passing_go(self):
        self.player.set_position(38)  # Park Place
        passed_go = self.player.move_forward(4)  # Roll a 4

        self.assertTrue(passed_go)
        self.assertEqual(self.player.position, 2)  # Community Chest

    def test_jail_mechanics(self):
        self.player.go_to_jail()
        self.assertTrue(self.player.is_in_jail)
        self.assertEqual(self.player.position, 10)

        self.player.release_from_jail()
        self.assertFalse(self.player.is_in_jail)

    def test_serialization(self):
        self.player.add_balance(100)
        self.player.set_position(5)

        data = self.player.to_dict()
        self.assertEqual(data["balance"], 1600)
        self.assertEqual(data["position"], 5)
        self.assertEqual(data["name"], "Battleship")


if __name__ == "__main__":
    unittest.main()
