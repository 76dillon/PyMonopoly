# src-v2/unit-tests/test_cards.py
import unittest
import sys
import os

# Look up TWO directories: unit-tests -> dev-tools -> src-v2
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from game import Game
from player import Player


class TestCards(unittest.TestCase):

    def setUp(self):
        self.p1 = Player("P1")
        self.p2 = Player("P2")
        self.game = Game([self.p1, self.p2])

    def test_receive_from_bank(self):
        card = {"action": "receive_from_bank", "amount": 200}
        self.game.execute_card(self.p1, card)
        self.assertEqual(self.p1.balance, 1700)  # Started with 1500

    def test_advance_to_go_passes_go(self):
        self.p1.set_position(30)  # Start near the end
        card = {"action": "advance_to_space", "target": "Go"}

        self.game.execute_card(self.p1, card)

        self.assertEqual(self.p1.position, 0)
        # 1500 + 200 for passing/landing on Go
        self.assertEqual(self.p1.balance, 1700)

    def test_pay_players(self):
        card = {"action": "pay_players", "amount": 50}
        result = self.game.execute_card(self.p1, card)

        # In our decoupled architecture, execute_card returns the transactions,
        # and the UI actually processes them. We simulate the UI processing here:
        self.assertEqual(result["status"], "multi_transaction")

        for t in result["transactions"]:
            debtor = next(p for p in self.game.players if p.name == t["debtor"])
            creditor = next(p for p in self.game.players if p.name == t["creditor"])
            self.game.handle_payment(debtor, t["amount"], creditor)

        self.assertEqual(self.p1.balance, 1450)  # Paid $50 to P2
        self.assertEqual(self.p2.balance, 1550)  # Received
