from data_loader import DataLoader


class Board:
    """Manages the static layout of the Monopoly board."""

    def __init__(self):
        # Loads the list of 40 spaces from board-spaces.json
        self.spaces = DataLoader.load_json("board-spaces.json")

    def get_space(self, index: int) -> dict:
        """Returns the data for a space at the given index, wrapping around the board."""
        return self.spaces[index % 40]

    def find_space_index(self, name: str) -> int:
        """
        Finds the board index of a space by its exact name.
        Useful for cards like 'Advance to Boardwalk'.
        """
        for space in self.spaces:
            if space["name"].lower() == name.lower():
                return space["position"]
        raise ValueError(f"Space '{name}' not found on the board.")
