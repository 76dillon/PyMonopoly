import unittest
import sys
import os

# Look up TWO directories: unit-tests -> dev-tools -> src-v2
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))


# Now we can import the classes from the src-v2 directory
from board import Board
from properties import Properties


# Mock Player class for testing ownership
class MockPlayer:
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return f"Player({self.name})"


class TestBoard(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Load the Board instance once for all tests in this class."""
        cls.board = Board()

    def test_board_loads_correct_number_of_spaces(self):
        """Should load exactly 40 spaces from the JSON file."""
        self.assertEqual(len(self.board.spaces), 40)

    def test_get_space_by_index(self):
        """Should return the correct space data for a given index."""
        go_space = self.board.get_space(0)
        boardwalk_space = self.board.get_space(39)

        self.assertEqual(go_space["name"], "Go")
        self.assertEqual(go_space["type"], "go")
        self.assertEqual(boardwalk_space["name"], "Boardwalk")
        self.assertEqual(boardwalk_space["type"], "street")

    def test_find_space_index_by_name(self):
        """Should find the correct position index for a given property name."""
        illinois_index = self.board.find_space_index("Illinois Avenue")
        go_index = self.board.find_space_index("Go")

        self.assertEqual(illinois_index, 24)
        self.assertEqual(go_index, 0)

    def test_find_space_is_case_insensitive(self):
        """The name lookup should work regardless of casing."""
        boardwalk_index = self.board.find_space_index("bOaRdWaLk")
        self.assertEqual(boardwalk_index, 39)

    def test_find_nonexistent_space_raises_error(self):
        """Should raise a ValueError if the space name doesn't exist."""
        with self.assertRaises(ValueError):
            self.board.find_space_index("Moon Base")


class TestProperties(unittest.TestCase):

    def setUp(self):
        """Create a new Properties instance and mock players for each test."""
        self.properties = Properties()
        self.player_one = MockPlayer("Tophat")
        self.player_two = MockPlayer("Car")

    def test_properties_load_and_initialize_state(self):
        """Should load all properties and initialize owner/house/mortgage dictionaries."""
        self.assertIn("Reading Railroad", self.properties.property_data)
        self.assertIn("Marvin Gardens", self.properties.owners)
        self.assertIsNone(self.properties.owners["Marvin Gardens"])
        self.assertFalse(self.properties.mortgaged["Marvin Gardens"])

    def test_get_and_set_owner(self):
        """Should correctly assign a player object as the owner of a property."""
        self.assertIsNone(self.properties.get_owner("Boardwalk"))
        self.properties.set_owner("Boardwalk", self.player_one)
        self.assertIs(self.properties.get_owner("Boardwalk"), self.player_one)

    def test_get_owned_group_count(self):
        """Should correctly count owned properties within a specific group."""
        # Player one buys one railroad
        self.properties.set_owner("Reading Railroad", self.player_one)
        count = self.properties.get_owned_group_count(self.player_one, "Railroad")
        self.assertEqual(count, 1)

        # Player one buys a second railroad
        self.properties.set_owner("B. & O. Railroad", self.player_one)
        count = self.properties.get_owned_group_count(self.player_one, "Railroad")
        self.assertEqual(count, 2)

        # Player two buys a railroad, shouldn't affect player one's count
        self.properties.set_owner("Short Line", self.player_two)
        count = self.properties.get_owned_group_count(self.player_one, "Railroad")
        self.assertEqual(count, 2)

    def test_has_monopoly(self):
        """Should correctly identify when a player completes a color group."""
        # Test with the Brown group (Mediterranean, Baltic)
        self.assertFalse(self.properties.has_monopoly(self.player_one, "Brown"))

        # Player one buys the first Brown property
        self.properties.set_owner("Mediterranean Avenue", self.player_one)
        self.assertFalse(self.properties.has_monopoly(self.player_one, "Brown"))

        # Player two buys the second one (no monopoly for player one)
        self.properties.set_owner("Baltic Avenue", self.player_two)
        self.assertFalse(self.properties.has_monopoly(self.player_one, "Brown"))

        # Player one also buys the second one (now has monopoly)
        self.properties.set_owner("Baltic Avenue", self.player_one)
        self.assertTrue(self.properties.has_monopoly(self.player_one, "Brown"))


if __name__ == "__main__":
    unittest.main()
