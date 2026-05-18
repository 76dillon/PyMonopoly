import unittest
import sys
import os

# Look up TWO directories: unit-tests -> dev-tools -> src-v2
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from game import Game
from player import Player


class TestBankruptcy(unittest.TestCase):

    def setUp(self):
        self.p1 = Player("Poor Player", starting_balance=100)
        self.p2 = Player("Rich Player", starting_balance=2000)
        self.game = Game([self.p1, self.p2])

    def test_liquid_worth_calculation(self):
        """Should correctly sum cash + mortgage value + half house value."""
        self.p1.balance = 50

        # Give P1 Boardwalk (Mortgage value: 200)
        self.game.properties.set_owner("Boardwalk", self.p1)

        # Give P1 Park Place with 2 houses (Mortgage value: 175, Houses: 200 each, sell value: 100 each)
        self.game.properties.set_owner("Park Place", self.p1)
        self.game.properties.houses["Park Place"] = 2

        # Total Liquid Worth should be:
        # Cash (50) + Boardwalk Mortgage (200) + Park Place Mortgage (175) + House Sell Value (2 * 100) = 625
        worth = self.game.get_player_liquid_worth(self.p1)
        self.assertEqual(worth, 625)

    def test_handle_payment_sufficient_funds(self):
        """Should succeed immediately if player has enough cash."""
        can_pay, msg = self.game.handle_payment(self.p1, 50, creditor=self.p2)

        self.assertTrue(can_pay)
        self.assertEqual(self.p1.balance, 50)
        self.assertEqual(self.p2.balance, 2050)

    def test_handle_payment_in_debt(self):
        """Should return IN_DEBT if player can't pay with cash, but CAN pay by liquidating."""
        self.p1.balance = 50
        self.game.properties.set_owner("Boardwalk", self.p1)  # Adds 200 liquid worth

        # P1 owes 100. They have 50 cash, but 250 liquid worth.
        can_pay, msg = self.game.handle_payment(self.p1, 100, creditor=self.p2)

        self.assertFalse(can_pay)
        self.assertEqual(msg, "IN_DEBT")
        self.assertFalse(self.p1.is_bankrupt)  # Not bankrupt yet!

    def test_bankruptcy_to_bank(self):
        """Should nullify ownership and buildings when bankrupt to bank."""
        self.p1.balance = 50
        self.game.properties.set_owner("Boardwalk", self.p1)
        self.game.properties.houses["Boardwalk"] = 1
        self.p1.chance_goojf_cards = 1  # Give the player a card

        # Owes 500 to the bank (e.g., taxes/cards). Total liquid worth is < 500.
        can_pay, msg = self.game.handle_payment(self.p1, 500)

        self.assertFalse(can_pay)
        self.assertTrue(self.p1.is_bankrupt)
        self.assertIn("Bank", msg)

        # Properties should be unowned and houses destroyed
        self.assertIsNone(self.game.properties.get_owner("Boardwalk"))
        self.assertEqual(self.game.properties.get_houses("Boardwalk"), 0)

        # Verify card was returned to the discard pile
        self.assertIn(
            "chance_07", [card["id"] for card in self.game.cards.chance_discard]
        )

    def test_bankruptcy_to_player(self):
        """Should transfer properties and cash when bankrupt to another player."""
        self.p1.balance = 100
        self.p1.get_out_of_jail_free_cards = 1
        self.game.properties.set_owner("Boardwalk", self.p1)
        self.game.properties.mortgaged["Boardwalk"] = True  # Test mortgage transfer
        self.p1.community_chest_goojf_cards = 1  # Give the player a card

        # Give P1 houses on a different property to test liquidation rule
        self.game.properties.set_owner("Baltic Avenue", self.p1)
        self.game.properties.houses["Baltic Avenue"] = 2

        # P1 owes 2000 to P2 (e.g., massive rent). Total liquid worth is < 2000.
        can_pay, msg = self.game.handle_payment(self.p1, 2000, creditor=self.p2)

        self.assertFalse(can_pay)
        self.assertTrue(self.p1.is_bankrupt)
        self.assertIn(self.p2.name, msg)

        # --- VERIFY CREDITOR GAINS ---

        # P2 should get P1's raw cash
        # AND P2 should get the cash from P1's houses (Baltic cost 50, sell for 25 * 2 = 50)
        # 2000 starting + 100 cash + 50 house sale = 2150
        self.assertEqual(self.p2.balance, 2150)

        # P2 should now own Boardwalk, and it should remain mortgaged
        self.assertEqual(self.game.properties.get_owner("Boardwalk"), self.p2)
        self.assertTrue(self.game.properties.is_mortgaged("Boardwalk"))

        # P2 should now own Baltic, but the houses were stripped
        self.assertEqual(self.game.properties.get_owner("Baltic Avenue"), self.p2)
        self.assertEqual(self.game.properties.get_houses("Baltic Avenue"), 0)

        # Verify creditor received the card
        self.assertEqual(self.p2.community_chest_goojf_cards, 1)


if __name__ == "__main__":
    unittest.main()
