import unittest
import sys
import os

# Look up TWO directories: unit-tests -> dev-tools -> src-v2
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from game import Game
from player import Player


class TestHandlePayment(unittest.TestCase):

    def setUp(self):
        self.p1 = Player("P1", starting_balance=100)
        self.p2 = Player("P2", starting_balance=2000)
        self.p3 = Player("P3", starting_balance=2000)
        self.game = Game([self.p1, self.p2, self.p3])

    def test_direct_payment_success(self):
        """Standard payment that the player can afford in cash."""
        can_pay, msg = self.game.handle_payment(self.p1, 50, creditor=self.p2)

        self.assertTrue(can_pay)
        self.assertEqual(self.p1.balance, 50)
        self.assertEqual(self.p2.balance, 2050)

    def test_payment_triggers_in_debt_signal(self):
        """Player has assets but not enough raw cash."""
        self.p1.balance = 50
        # Give them an asset so their liquid worth is > 100
        self.game.properties.set_owner("Boardwalk", self.p1)

        can_pay, msg = self.game.handle_payment(self.p1, 100, creditor=self.p2)

        self.assertFalse(can_pay)
        self.assertEqual(msg, "IN_DEBT")
        # Balances should NOT have changed yet, waiting for UI liquidation
        self.assertEqual(self.p1.balance, 50)
        self.assertEqual(self.p2.balance, 2000)

    def test_card_pay_players_returns_transactions(self):
        """Testing that a group payout card returns the correct transaction list."""
        card = {"action": "pay_players", "amount": 50}
        result = self.game.execute_card(self.p1, card)

        self.assertEqual(result["status"], "multi_transaction")
        self.assertEqual(len(result["transactions"]), 2)

        # P1 must pay P2 and P3
        self.assertEqual(result["transactions"][0]["debtor"], "P1")
        self.assertEqual(result["transactions"][0]["creditor"], "P2")
        self.assertEqual(result["transactions"][1]["debtor"], "P1")
        self.assertEqual(result["transactions"][1]["creditor"], "P3")

    def test_card_collect_from_players_returns_transactions(self):
        """Testing that a group collection card returns the correct transaction list."""
        card = {"action": "collect_from_players", "amount": 50}
        result = self.game.execute_card(self.p1, card)

        self.assertEqual(result["status"], "multi_transaction")
        self.assertEqual(len(result["transactions"]), 2)

        # P2 and P3 must pay P1
        self.assertEqual(result["transactions"][0]["debtor"], "P2")
        self.assertEqual(result["transactions"][0]["creditor"], "P1")
        self.assertEqual(result["transactions"][1]["debtor"], "P3")
        self.assertEqual(result["transactions"][1]["creditor"], "P1")


if __name__ == "__main__":
    unittest.main()
