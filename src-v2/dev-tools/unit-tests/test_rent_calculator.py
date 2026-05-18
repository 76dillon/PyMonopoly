import unittest
import sys
import os

# Look up TWO directories: unit-tests -> dev-tools -> src-v2
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))


from mechanics import compute_rent, compute_repair_costs


class TestRentCalculation(unittest.TestCase):

    def setUp(self):
        """Set up mock property data based on our properties.json structure."""
        self.street_prop = {
            "type": "street",
            "group": "Dark Blue",
            "rent": [50, 200, 600, 1400, 1700, 2000],  # Boardwalk
        }
        self.railroad_prop = {
            "type": "railroad",
            "group": "Railroad",
            "rent": [25, 50, 100, 200],
        }
        self.utility_prop = {
            "type": "utility",
            "group": "Utility",
            "rent_multipliers": [4, 10],
        }

    # --- STREET TESTS ---
    def test_street_base_rent(self):
        rent = compute_rent(self.street_prop, houses=0, is_monopoly=False)
        self.assertEqual(rent, 50)

    def test_street_monopoly_double_rent(self):
        rent = compute_rent(self.street_prop, houses=0, is_monopoly=True)
        self.assertEqual(rent, 100)

    def test_street_with_houses(self):
        # 3 houses. Monopoly status shouldn't double it if there are houses.
        rent = compute_rent(self.street_prop, houses=3, is_monopoly=True)
        self.assertEqual(rent, 1400)

    def test_street_with_hotel(self):
        # 5 houses represents a hotel
        rent = compute_rent(self.street_prop, houses=5)
        self.assertEqual(rent, 2000)

    def test_street_invalid_houses(self):
        with self.assertRaises(ValueError):
            compute_rent(self.street_prop, houses=6)

    # --- RAILROAD TESTS ---
    def test_railroad_one_owned(self):
        rent = compute_rent(self.railroad_prop, owned_group_count=1)
        self.assertEqual(rent, 25)

    def test_railroad_three_owned(self):
        rent = compute_rent(self.railroad_prop, owned_group_count=3)
        self.assertEqual(rent, 100)

    def test_railroad_invalid_count(self):
        with self.assertRaises(ValueError):
            compute_rent(self.railroad_prop, owned_group_count=5)

    # --- UTILITY TESTS ---
    def test_utility_one_owned(self):
        # Multiplier is 4, dice roll is 7 -> 28
        rent = compute_rent(self.utility_prop, owned_group_count=1, dice_roll=7)
        self.assertEqual(rent, 28)

    def test_utility_two_owned(self):
        # Multiplier is 10, dice roll is 11 -> 110
        rent = compute_rent(self.utility_prop, owned_group_count=2, dice_roll=11)
        self.assertEqual(rent, 110)

    def test_utility_invalid_dice_roll(self):
        with self.assertRaises(ValueError):
            # Impossible dice roll for 2d6
            compute_rent(self.utility_prop, owned_group_count=1, dice_roll=1)

    def test_utility_invalid_count(self):
        with self.assertRaises(ValueError):
            compute_rent(self.utility_prop, owned_group_count=3, dice_roll=7)

    # --- ERROR HANDLING ---
    def test_unknown_property_type(self):
        bad_prop = {"type": "spaceship"}
        with self.assertRaises(ValueError):
            compute_rent(bad_prop)


class TestRepairCosts(unittest.TestCase):

    def test_standard_repair_costs(self):
        # E.g., Card says $25 per house, $100 per hotel. Player has 3 houses, 1 hotel.
        # (3 * 25) + (1 * 100) = 175
        cost = compute_repair_costs(
            houses_owned=3, hotels_owned=1, house_fee=25, hotel_fee=100
        )
        self.assertEqual(cost, 175)

    def test_no_buildings(self):
        cost = compute_repair_costs(
            houses_owned=0, hotels_owned=0, house_fee=40, hotel_fee=115
        )
        self.assertEqual(cost, 0)

    def test_negative_buildings(self):
        with self.assertRaises(ValueError):
            compute_repair_costs(
                houses_owned=-1, hotels_owned=0, house_fee=25, hotel_fee=100
            )


if __name__ == "__main__":
    unittest.main()
