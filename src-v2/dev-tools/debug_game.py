import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from game import Game


class DebugGame(Game):
    """
    Inherits from the standard Game engine and adds powerful methods
    for debugging and testing purposes.
    """

    def __init__(self, players: list):
        # Initialize the parent Game class normally
        super().__init__(players)

    # --- GOD MODE METHODS ---

    def debug_set_player_balance(self, player, amount: int):
        """God Mode: Directly sets a player's balance."""
        if amount < 0:
            amount = 0
        player.balance = amount
        return f"Set {player.name}'s balance to ${amount}."

    def debug_teleport_player(self, player, space_index: int, resolve_space=True):
        """God Mode: Teleports a player to a space and optionally resolves the landing."""
        if not (0 <= space_index <= 39):
            return "Invalid space index."

        player.set_position(space_index)

        if resolve_space:
            space = self.board.get_space(space_index)
            # We need a dummy dice roll for rent calculation if it's a utility
            outcome = self.resolve_space(player, space, dice_total=7)
            return outcome
        return None

    def debug_force_acquire_property(self, player, property_name: str):
        """God Mode: Gives a player ownership of an unowned property for free."""
        if self.properties.get_owner(property_name) is None:
            self.properties.set_owner(property_name, player)
            return f"{player.name} acquired {property_name}."
        return f"{property_name} is already owned."

    def debug_force_acquire_monopoly(self, player, group: str, max_houses=False):
        """God Mode: Gives a player a full monopoly, optionally with max buildings."""
        group_props = [
            p
            for p, d in self.properties.property_data.items()
            if d.get("group") == group
        ]
        if not group_props:
            return f"No properties found for group '{group}'."

        for prop in group_props:
            # Clear current ownership and buildings first
            current_owner = self.properties.get_owner(prop)
            if current_owner and current_owner != player:
                self.properties.set_owner(prop, None)  # Make it unowned first

            self.properties.set_owner(prop, player)
            if (
                max_houses
                and self.properties.get_property_data(prop).get("type") == "street"
            ):
                self.properties.houses[prop] = 5  # 5 houses = Hotel

        return f"{player.name} acquired the {group} monopoly, with max buildings: {max_houses}."
