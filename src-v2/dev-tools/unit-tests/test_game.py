# src-v2/unit-tests/test_game.py
import unittest
import sys
import os

# Look up TWO directories: unit-tests -> dev-tools -> src-v2
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from game import Game
from player import Player


class TestGame(unittest.TestCase):

    def setUp(self):
        self.p1 = Player("Iron")
        self.p2 = Player("Hat")
        self.game = Game([self.p1, self.p2])

    def test_initialization(self):
        self.assertEqual(len(self.game.players), 2)
        self.assertIs(self.game.get_current_player(), self.p1)

    def test_end_turn_cycling(self):
        self.game.end_turn()
        self.assertIs(self.game.get_current_player(), self.p2)
        self.game.end_turn()
        self.assertIs(self.game.get_current_player(), self.p1)

    def test_buy_property(self):
        # P1 has $1500. Boardwalk costs $400.
        success = self.game.buy_property(self.p1, "Boardwalk")
        self.assertTrue(success)
        self.assertEqual(self.p1.balance, 1100)
        self.assertIs(self.game.properties.get_owner("Boardwalk"), self.p1)

    def test_resolve_space_tax(self):
        # Income Tax is $200
        tax_space = {"name": "Income Tax", "type": "tax", "amount": 200}
        outcome = self.game.resolve_space(self.p1, tax_space, dice_total=5)

        self.assertEqual(outcome["action"], "paid_tax")
        self.assertEqual(self.p1.balance, 1300)

    def test_resolve_space_rent(self):
        # P2 owns Boardwalk
        self.game.buy_property(self.p2, "Boardwalk")

        boardwalk_space = self.game.board.get_space(39)  # Boardwalk
        outcome = self.game.resolve_space(self.p1, boardwalk_space, dice_total=6)

        # P1 pays rent ($50 base rent for Boardwalk)
        self.assertEqual(outcome["action"], "paid_rent")
        self.assertEqual(outcome["amount"], 50)
        self.assertEqual(self.p1.balance, 1450)

        # P2 receives rent (Started 1500 - 400 cost + 50 rent = 1150)
        self.assertEqual(self.p2.balance, 1150)


if __name__ == "__main__":
    unittest.main()
