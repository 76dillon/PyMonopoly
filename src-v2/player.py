# src-v2/player.py


class Player:
    """
    A pure state container representing a Monopoly player.
    Contains no UI logic or terminal prompts, making it network-ready.
    """

    def __init__(self, name: str, token: str = "", starting_balance: int = 1500):
        self.name = name
        self.token = token
        self.balance = starting_balance
        self.position = 0

        # Jail state
        self.is_in_jail = False
        self.jail_turns = 0
        self.get_out_of_jail_free_cards = 0

        # --- UPDATED: Specific GOOJF card tracking ---
        self.chance_goojf_cards = 0
        self.community_chest_goojf_cards = 0

        # Game state
        self.is_bankrupt = False

    def add_balance(self, amount: int):
        """Adds funds to the player's account."""
        if amount < 0:
            raise ValueError("Amount to add must be positive.")
        self.balance += amount

    def pay_balance(self, amount: int):
        """
        Deducts funds from the player's account.
        Note: This does not automatically trigger bankruptcy. The Game engine
        should check if the player can afford this, or force them to mortgage/trade.
        """
        if amount < 0:
            raise ValueError("Amount to pay must be positive.")
        self.balance -= amount

    def move_forward(self, spaces: int) -> bool:
        """
        Moves the player forward by a set number of spaces.
        Returns True if the player passed or landed on Go.
        """
        new_position = self.position + spaces
        passed_go = new_position >= 40
        self.position = new_position % 40
        return passed_go

    def set_position(self, target_position: int):
        """
        Instantly teleports the player to a specific index (used for cards).
        The Game engine is responsible for deciding if this triggers passing Go.
        """
        if not (0 <= target_position <= 39):
            raise ValueError("Position must be between 0 and 39.")
        self.position = target_position

    def go_to_jail(self):
        """Updates state to place the player in jail."""
        self.is_in_jail = True
        self.position = 10
        self.jail_turns = 0

    def release_from_jail(self):
        """Clears the player's jail status."""
        self.is_in_jail = False
        self.jail_turns = 0

    def declare_bankruptcy(self):
        """Marks the player as out of the game."""
        self.is_bankrupt = True
        self.balance = 0

    def to_dict(self) -> dict:
        """
        Serializes the player state into a dictionary.
        This is perfect for sending the player's state over a multiplayer network.
        """
        return {
            "name": self.name,
            "token": self.token,
            "balance": self.balance,
            "position": self.position,
            "is_in_jail": self.is_in_jail,
            "jail_turns": self.jail_turns,
            "chance_goojf_cards": self.chance_goojf_cards,
            "community_chest_goojf_cards": self.community_chest_goojf_cards,
            "is_bankrupt": self.is_bankrupt,
        }
