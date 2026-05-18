from data_loader import DataLoader


class Properties:
    """
    Manages both the static property rules and the dynamic state
    (ownership, buildings, mortgages) during a game session.
    """

    def __init__(self):
        # Load the static configurations
        self.property_data = DataLoader.load_json("properties.json")

        # Initialize dynamic game state trackers for every property
        self.owners = {name: None for name in self.property_data.keys()}
        self.houses = {name: 0 for name in self.property_data.keys()}
        self.mortgaged = {name: False for name in self.property_data.keys()}

    def get_property_data(self, property_name: str) -> dict:
        """Returns the static JSON data for a property."""
        return self.property_data.get(property_name)

    # --- OWNERSHIP & STATE METHODS ---

    def get_owner(self, property_name: str):
        return self.owners.get(property_name)

    def set_owner(self, property_name: str, player):
        self.owners[property_name] = player

    def get_houses(self, property_name: str) -> int:
        return self.houses.get(property_name, 0)

    def is_mortgaged(self, property_name: str) -> bool:
        return self.mortgaged.get(property_name, False)

    # --- GAME LOGIC HELPERS ---

    def get_owned_group_count(self, player, group_name: str) -> int:
        """Counts how many properties of a specific group a player owns."""
        count = 0
        for prop_name, data in self.property_data.items():
            if data.get("group") == group_name and self.owners.get(prop_name) == player:
                count += 1
        return count

    def has_monopoly(self, player, group_name: str) -> bool:
        """Checks if a player owns all properties in a given color group."""
        # Find all properties that belong to this group
        group_properties = [
            name
            for name, data in self.property_data.items()
            if data.get("group") == group_name
        ]

        # Find how many of those are owned by the player
        owned_by_player = [
            name for name in group_properties if self.owners.get(name) == player
        ]

        # If the lists match in length, they own the whole group
        return len(group_properties) > 0 and len(group_properties) == len(
            owned_by_player
        )

    def get_properties_owned_by(self, player) -> list:
        """Returns a list of property names owned by the specified player."""
        return [name for name, owner in self.owners.items() if owner == player]

    def to_dict(self) -> dict:
        """Serializes the current board ownership and buildings for debugging."""
        state = {}
        for prop in self.property_data.keys():
            owner = self.owners[prop]
            if owner:
                state[prop] = {
                    "owner": owner.name,
                    "houses": self.houses[prop],
                    "mortgaged": self.mortgaged[prop],
                }
        return state
