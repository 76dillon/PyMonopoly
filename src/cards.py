# src-v2/cards.py
import random
from data_loader import DataLoader


class CardManager:
    """Manages the Chance and Community Chest decks, including shuffling and drawing."""

    def __init__(self):
        # Load the raw card data
        decks = DataLoader.load_json("cards.json")

        self.chance_deck = decks.get("chance", [])
        self.chest_deck = decks.get("community_chest", [])

        # Shuffle both decks initially
        random.shuffle(self.chance_deck)
        random.shuffle(self.chest_deck)

        self.chance_discard = []
        self.chest_discard = []

    def draw_chance(self) -> dict:
        """Draws a Chance card, reshuffling the discard pile if empty."""
        if not self.chance_deck:
            self.chance_deck = self.chance_discard
            self.chance_discard = []
            random.shuffle(self.chance_deck)

        card = self.chance_deck.pop(0)

        # Keep 'Get Out of Jail Free' out of the discard pile until used
        if card["action"] != "get_out_of_jail_free":
            self.chance_discard.append(card)

        return card

    def draw_community_chest(self) -> dict:
        """Draws a Community Chest card, reshuffling the discard pile if empty."""
        if not self.chest_deck:
            self.chest_deck = self.chest_discard
            self.chest_discard = []
            random.shuffle(self.chest_deck)

        card = self.chest_deck.pop(0)

        if card["action"] != "get_out_of_jail_free":
            self.chest_discard.append(card)

        return card

    def return_card_to_deck(self, card_id: str):
        """Returns a GOOJF card to the appropriate discard pile."""
        if "chance" in card_id:
            # Find the original card data from the master list
            card = next(
                (
                    c
                    for c in self.chance_deck + self.chance_discard
                    if c["id"] == card_id
                ),
                None,
            )
            if card:
                self.chance_discard.append(card)
        elif "cc" in card_id:
            card = next(
                (c for c in self.chest_deck + self.chest_discard if c["id"] == card_id),
                None,
            )
            if card:
                self.chest_discard.append(card)
