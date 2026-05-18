# src/mechanics.py


def compute_rent(
    property_data: dict,
    houses: int = 0,
    is_monopoly: bool = False,
    owned_group_count: int = 1,
    dice_roll: int = 0,
) -> int:
    """
    Calculates the rent for a Monopoly property based on its type and current game state.

    Args:
        property_data (dict): The dictionary containing property rules (from properties.json).
        houses (int): Number of houses on the property (0-5, where 5 is a hotel).
        is_monopoly (bool): True if the owner owns all properties in the color group.
        owned_group_count (int): How many properties of this type the owner has (for Railroads/Utilities).
        dice_roll (int): The current dice roll (required only for Utilities).

    Returns:
        int: The calculated rent amount.
    """
    if not property_data:
        return 0

    prop_type = property_data.get("type")

    if prop_type == "street":
        if not (0 <= houses <= 5):
            raise ValueError("Houses must be between 0 and 5.")

        base_rent = property_data["rent"][houses]

        # Unimproved properties in a monopoly charge double rent
        if houses == 0 and is_monopoly:
            return base_rent * 2
        return base_rent

    elif prop_type == "railroad":
        if not (1 <= owned_group_count <= 4):
            raise ValueError("Owned railroads must be between 1 and 4.")

        # Arrays are 0-indexed, so 1 railroad owned = index 0
        return property_data["rent"][owned_group_count - 1]

    elif prop_type == "utility":
        if not (1 <= owned_group_count <= 2):
            raise ValueError("Owned utilities must be between 1 and 2.")
        if not (2 <= dice_roll <= 12):
            raise ValueError("Dice roll for utility rent must be between 2 and 12.")

        multiplier = property_data["rent_multipliers"][owned_group_count - 1]
        return dice_roll * multiplier

    else:
        raise ValueError(f"Unknown property type: {prop_type}")


def compute_repair_costs(
    houses_owned: int, hotels_owned: int, house_fee: int, hotel_fee: int
) -> int:
    """
    Calculates the total cost for property repairs (triggered by Chance/Community Chest cards).

    Args:
        houses_owned (int): Total number of houses the player owns across the board.
        hotels_owned (int): Total number of hotels the player owns across the board.
        house_fee (int): The penalty fee per house (e.g., $25 or $40 based on the card).
        hotel_fee (int): The penalty fee per hotel (e.g., $100 or $115 based on the card).

    Returns:
        int: The total penalty amount the player must pay to the bank.
    """
    if houses_owned < 0 or hotels_owned < 0:
        raise ValueError("Owned buildings cannot be negative.")

    return (houses_owned * house_fee) + (hotels_owned * hotel_fee)
