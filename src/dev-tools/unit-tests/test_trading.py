import unittest
import sys
import os

# Look up TWO directories: unit-tests -> dev-tools -> src-v2
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from game import Game
from player import Player


class TestTrading(unittest.TestCase):

    def setUp(self):
        self.p1 = Player("Player 1", starting_balance=1000)
        self.p2 = Player("Player 2", starting_balance=1000)
        self.game = Game([self.p1, self.p2])

    def test_simple_cash_trade(self):
        """Tests a trade involving only cash."""
        success, msg = self.game.execute_trade(
            p1=self.p1,
            p1_offer_cash=200,
            p1_offer_props=[],
            p2=self.p2,
            p2_offer_cash=50,
            p2_offer_props=[],
        )
        self.assertTrue(success)
        self.assertEqual(self.p1.balance, 850)
        self.assertEqual(self.p2.balance, 1150)

    def test_insufficient_funds(self):
        """Tests that a trade fails if a player doesn't have enough cash."""
        success, msg = self.game.execute_trade(
            p1=self.p1,
            p1_offer_cash=1500,
            p1_offer_props=[],
            p2=self.p2,
            p2_offer_cash=0,
            p2_offer_props=[],
        )
        self.assertFalse(success)
        self.assertIn("does not have", msg)
        self.assertEqual(self.p1.balance, 1000)

    def test_simple_property_trade(self):
        """Tests a 1-for-1 property swap."""
        self.game.properties.set_owner("Boardwalk", self.p1)
        self.game.properties.set_owner("Park Place", self.p2)

        success, msg = self.game.execute_trade(
            p1=self.p1,
            p1_offer_cash=0,
            p1_offer_props=["Boardwalk"],
            p2=self.p2,
            p2_offer_cash=0,
            p2_offer_props=["Park Place"],
        )

        self.assertTrue(success)
        self.assertEqual(self.game.properties.get_owner("Boardwalk"), self.p2)
        self.assertEqual(self.game.properties.get_owner("Park Place"), self.p1)

    def test_complex_mixed_trade(self):
        """Tests trading multiple properties and cash simultaneously."""
        self.game.properties.set_owner("Baltic Avenue", self.p1)
        self.game.properties.set_owner("Mediterranean Avenue", self.p1)
        self.game.properties.set_owner("Reading Railroad", self.p2)

        success, msg = self.game.execute_trade(
            p1=self.p1,
            p1_offer_cash=100,
            p1_offer_props=["Baltic Avenue", "Mediterranean Avenue"],
            p2=self.p2,
            p2_offer_cash=0,
            p2_offer_props=["Reading Railroad"],
        )

        self.assertTrue(success)
        self.assertEqual(self.p1.balance, 900)
        self.assertEqual(self.p2.balance, 1100)
        self.assertEqual(self.game.properties.get_owner("Reading Railroad"), self.p1)
        self.assertEqual(self.game.properties.get_owner("Baltic Avenue"), self.p2)
        self.assertEqual(
            self.game.properties.get_owner("Mediterranean Avenue"), self.p2
        )

    def test_trade_fails_if_property_not_owned(self):
        """Tests that a trade fails if someone tries to trade a property they don't own."""
        self.game.properties.set_owner("Boardwalk", self.p1)
        # P2 does NOT own Park Place

        success, msg = self.game.execute_trade(
            p1=self.p1,
            p1_offer_cash=0,
            p1_offer_props=["Boardwalk"],
            p2=self.p2,
            p2_offer_cash=0,
            p2_offer_props=["Park Place"],
        )

        self.assertFalse(success)
        self.assertIn("no longer owns", msg)
        self.assertEqual(self.game.properties.get_owner("Boardwalk"), self.p1)

    def test_trade_fails_if_property_has_buildings(self):
        """Tests the official rule that properties with buildings cannot be traded."""
        self.game.properties.set_owner("Boardwalk", self.p1)
        self.game.properties.houses["Boardwalk"] = 1

        success, msg = self.game.execute_trade(
            p1=self.p1,
            p1_offer_cash=0,
            p1_offer_props=["Boardwalk"],
            p2=self.p2,
            p2_offer_cash=1000,
            p2_offer_props=[],
        )

        self.assertFalse(success)
        self.assertIn("has buildings", msg)
        self.assertEqual(self.game.properties.get_owner("Boardwalk"), self.p1)
        self.assertEqual(self.p2.balance, 1000)


if __name__ == "__main__":
    unittest.main()
