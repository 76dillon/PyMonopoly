import random
from board import Board
from properties import Properties
from cards import CardManager
from player import Player
from mechanics import compute_rent, compute_repair_costs


class Game:
    """
    The core Game Engine. Manages the turn loop and enforces the rules of Monopoly.
    Contains strictly zero UI interactions.
    """

    def __init__(self, players: list):
        if not players or len(players) < 2:
            raise ValueError("A game requires at least 2 players.")

        self.players = players
        self.board = Board()
        self.properties = Properties()
        self.cards = CardManager()

        self.current_player_index = 0
        self.consecutive_doubles = 0

        self.has_rolled = False
        self.can_roll = True

    @classmethod
    def load_from_snapshot(cls, snapshot: dict):
        """Creates a new Game instance from a saved state snapshot."""

        # 1. Re-create Player objects from the snapshot data
        players = []
        for p_data in snapshot.get("players", []):
            player = Player(name=p_data["name"])
            # Manually set all state attributes
            player.balance = p_data.get("balance", 1500)
            player.position = p_data.get("position", 0)
            player.is_in_jail = p_data.get("is_in_jail", False)
            player.jail_turns = p_data.get("jail_turns", 0)
            player.chance_goojf_cards = p_data.get("chance_goojf_cards", 0)
            player.community_chest_goojf_cards = p_data.get(
                "community_chest_goojf_cards", 0
            )
            player.is_bankrupt = p_data.get("is_bankrupt", False)
            players.append(player)

        if not players:
            raise ValueError("Snapshot is missing player data.")

        # 2. Create the Game instance with the re-created players
        game_instance = cls(players)

        # 3. Restore Game-level state
        current_player_name = snapshot.get("current_player")
        if current_player_name:
            game_instance.current_player_index = next(
                (i for i, p in enumerate(players) if p.name == current_player_name), 0
            )

        game_instance.consecutive_doubles = snapshot.get("consecutive_doubles", 0)
        game_instance.has_rolled = snapshot.get("has_rolled", False)
        game_instance.can_roll = snapshot.get("can_roll", True)

        # 4. Restore Property ownership and state
        property_states = snapshot.get("properties", {})
        for prop_name, state in property_states.items():
            owner_name = state.get("owner")
            owner = next((p for p in players if p.name == owner_name), None)
            if owner:
                game_instance.properties.set_owner(prop_name, owner)
                game_instance.properties.houses[prop_name] = state.get("houses", 0)
                game_instance.properties.mortgaged[prop_name] = state.get(
                    "mortgaged", False
                )

        print("\n✅ Game state successfully loaded from save file.")
        return game_instance

    def get_current_player(self):
        return self.players[self.current_player_index]

    def end_turn(self):
        """Advances the game to the next player's turn."""
        self.consecutive_doubles = 0

        self.has_rolled = False
        self.can_roll = True

        # Advance index, skipping bankrupt players
        while True:
            self.current_player_index = (self.current_player_index + 1) % len(
                self.players
            )
            if not self.get_current_player().is_bankrupt:
                break

    def roll_dice(self) -> tuple:
        """Simulates rolling two 6-sided dice."""
        return random.randint(1, 6), random.randint(1, 6)

    def execute_move(self, player) -> dict:
        """
        Rolls dice, moves the player, checks for 3-doubles-jail rule,
        handles mandatory jail bail, and identifies the space landed on.
        """
        self.has_rolled = True
        d1, d2 = self.roll_dice()
        is_doubles = d1 == d2
        total_roll = d1 + d2
        self.can_roll = is_doubles

        outcome = {
            "dice": (d1, d2),
            "is_doubles": is_doubles,
            "sent_to_jail": False,
            "passed_go": False,
            "landed_space": None,
            "jail_status": "free",  # New tracker for UI clarity
        }

        # --- JAIL LOGIC ---
        if player.is_in_jail:
            if is_doubles:
                player.release_from_jail()
                outcome["jail_status"] = "escaped_with_doubles"
                # They move normally, but they do NOT get to roll again.
                self.consecutive_doubles = 0
                self.can_roll = False
            else:
                player.jail_turns += 1
                if player.jail_turns >= 3:
                    # Mandatory Bail! Force the payment.
                    can_pay, msg = self.handle_payment(player, 50)

                    # If they can't pay (or hit IN_DEBT), we must stop their turn
                    if not can_pay:
                        outcome["jail_status"] = "mandatory_bail_debt"
                        outcome["debt_message"] = msg
                        return outcome

                    # If they paid successfully, release them and let them move!
                    player.release_from_jail()
                    outcome["jail_status"] = "paid_mandatory_bail"
                else:
                    # Failed to roll doubles on turn 1 or 2, turn is over.
                    outcome["jail_status"] = "failed_roll"
                    return outcome

        # --- NORMAL MOVEMENT LOGIC ---
        if is_doubles and outcome["jail_status"] == "free":
            self.consecutive_doubles += 1
            if self.consecutive_doubles == 3:
                player.go_to_jail()
                outcome["sent_to_jail"] = True
                self.consecutive_doubles = 0
                self.can_roll = False
                return outcome

        # Move the player
        passed_go = player.move_forward(total_roll)
        if passed_go:
            player.add_balance(200)
            outcome["passed_go"] = True

        # Identify the space
        landed_space = self.board.get_space(player.position)
        outcome["landed_space"] = landed_space

        return outcome

    def buy_property(self, player, property_name: str) -> bool:
        """Attempts to buy the property. Returns True if successful."""
        prop_data = self.properties.get_property_data(property_name)
        if not prop_data:
            return False

        price = prop_data["price"]

        # Verify ownership is none and player has enough money
        if self.properties.get_owner(property_name) is None and player.balance >= price:
            player.pay_balance(price)
            self.properties.set_owner(property_name, player)
            return True

        return False

    def resolve_space(self, player, space: dict, dice_total: int) -> dict:
        """
        Determines the automatic consequences of landing on a space
        (e.g., drawing cards, paying rent, taxes, or offering a property for purchase).
        """
        space_type = space["type"]
        space_name = space["name"]

        # --- Handle Non-Property Spaces First ---

        if space_type == "chance":
            card = self.cards.draw_chance()
            result = self.execute_card(player, card)
            return {"action": "drew_chance", "card": card, "result": result}

        elif space_type == "community_chest":
            card = self.cards.draw_community_chest()
            result = self.execute_card(player, card)
            return {"action": "drew_community_chest", "card": card, "result": result}

        elif space_type == "tax":
            tax_amount = space["amount"]
            can_pay, msg = self.handle_payment(player, tax_amount)
            return {
                "action": "paid_tax",
                "amount": tax_amount,
                "can_pay": can_pay,
                "message": msg,
            }

        elif space_type == "go_to_jail":
            player.go_to_jail()
            return {"action": "sent_to_jail"}

        # --- Handle All Purchasable Properties ---

        elif space_type in ["street", "railroad", "utility"]:
            prop_data = self.properties.get_property_data(space_name)
            owner = self.properties.get_owner(space_name)

            # Scenario 1: Property is unowned
            if not owner:
                return {"action": "offer_purchase", "price": prop_data["price"]}

            # Scenario 2: Property is owned by the current player
            elif owner == player:
                return {"action": "nothing", "reason": "Landed on own property."}

            # Scenario 3: Property is owned by another player
            else:  # owner != player
                if self.properties.is_mortgaged(space_name):
                    return {
                        "action": "nothing",
                        "reason": f"{space_name} is mortgaged.",
                    }
                else:
                    # Pay Rent
                    houses = self.properties.get_houses(space_name)
                    is_monopoly = self.properties.has_monopoly(
                        owner, prop_data["group"]
                    )
                    owned_count = self.properties.get_owned_group_count(
                        owner, prop_data["group"]
                    )

                    rent_due = compute_rent(
                        property_data=prop_data,
                        houses=houses,
                        is_monopoly=is_monopoly,
                        owned_group_count=owned_count,
                        dice_roll=dice_total,
                    )

                    can_pay, msg = self.handle_payment(player, rent_due, creditor=owner)
                    return {
                        "action": "paid_rent",
                        "amount": rent_due,
                        "owner": owner.name,
                        "can_pay": can_pay,
                        "message": msg,
                    }

        # --- Fallback for all other spaces (Go, Free Parking, Jail/Visiting) ---
        else:
            return {"action": "nothing"}

    def execute_card(self, player, card: dict) -> dict:
        """Parses a card's JSON action and applies the effect to the game state."""
        action = card["action"]

        if action == "receive_from_bank":
            player.add_balance(card["amount"])
            return {"status": "received_money", "amount": card["amount"]}

        elif action == "pay_bank":
            can_pay, msg = self.handle_payment(player, card["amount"])
            return {
                "status": "paid_money",
                "amount": card["amount"],
                "can_pay": can_pay,
                "message": msg,
            }

        elif action == "advance_to_space":
            target_index = self.board.find_space_index(card["target"])

            # Check if they pass Go (if target is behind them on the board array)
            if target_index < player.position:
                player.add_balance(200)

            player.set_position(target_index)

            # Since they moved to a new space, we must resolve what that space does!
            new_space = self.board.get_space(target_index)
            follow_up = self.resolve_space(player, new_space, dice_total=0)
            return {
                "status": "moved",
                "new_position": target_index,
                "follow_up": follow_up,
            }

        elif action == "move_relative":
            # e.g., "Go back 3 spaces"
            new_position = (player.position + card["spaces"]) % 40
            player.set_position(new_position)

            new_space = self.board.get_space(new_position)
            follow_up = self.resolve_space(player, new_space, dice_total=0)
            return {"status": "moved_relative", "follow_up": follow_up}

        elif action == "go_to_jail":
            player.go_to_jail()
            return {"status": "jailed"}

        elif action == "get_out_of_jail_free":
            # Identify which deck the card came from by its ID
            if "chance" in card["id"]:
                player.chance_goojf_cards += 1
            elif "cc" in card["id"]:
                player.community_chest_goojf_cards += 1
            return {"status": "kept_card"}

        elif action == "pay_players":
            # The player draws a card forcing them to pay everyone else.
            # We return a list of transactions to the UI so it can process them sequentially.
            transactions = []
            for other_player in self.players:
                if other_player != player and not other_player.is_bankrupt:
                    transactions.append(
                        {
                            "debtor": player.name,
                            "creditor": other_player.name,
                            "amount": card["amount"],
                        }
                    )
            return {"status": "multi_transaction", "transactions": transactions}

        elif action == "collect_from_players":
            # The player draws a card forcing everyone else to pay them.
            transactions = []
            for other_player in self.players:
                if other_player != player and not other_player.is_bankrupt:
                    transactions.append(
                        {
                            "debtor": other_player.name,
                            "creditor": player.name,
                            "amount": card["amount"],
                        }
                    )
            return {"status": "multi_transaction", "transactions": transactions}

        elif action == "property_repairs":
            total_houses, total_hotels = 0, 0
            # Count the buildings the player owns across all properties
            for prop_name, owner in self.properties.owners.items():
                if owner == player:
                    houses = self.properties.get_houses(prop_name)
                    if houses == 5:
                        total_hotels += 1
                    else:
                        total_houses += houses

            repair_cost = compute_repair_costs(
                total_houses, total_hotels, card["house_cost"], card["hotel_cost"]
            )
            can_pay, msg = self.handle_payment(player, repair_cost)
            return {
                "status": "paid_repairs",
                "amount": repair_cost,
                "can_pay": can_pay,
                "message": msg,
            }

        return {"status": "unknown_action"}

    def win_auction(self, winning_player, property_name: str, winning_bid: int) -> bool:
        """
        Awards an unowned property to the winner of an auction at their bid price.
        Returns True if successful.
        """
        if winning_bid < 0:
            raise ValueError("Bid cannot be negative.")

        # Verify the property is unowned
        if self.properties.get_owner(property_name) is not None:
            return False

        # Verify the player has enough money
        if winning_player.balance >= winning_bid:
            winning_player.pay_balance(winning_bid)
            self.properties.set_owner(property_name, winning_player)
            return True

        return False

    def mortgage_property(self, player, property_name: str) -> tuple[bool, str]:
        """Attempts to mortgage a property. Returns (Success_Boolean, Message_String)."""
        if self.properties.get_owner(property_name) != player:
            return False, "You do not own this property."

        if self.properties.is_mortgaged(property_name):
            return False, "This property is already mortgaged."

        if self.properties.get_houses(property_name) > 0:
            return False, "You must sell all houses before mortgaging."

        prop_data = self.properties.get_property_data(property_name)
        mortgage_value = prop_data["mortgage_value"]

        self.properties.mortgaged[property_name] = True
        player.add_balance(mortgage_value)

        return True, f"✅ Mortgaged {property_name} for ${mortgage_value}."

    def unmortgage_property(self, player, property_name: str) -> tuple[bool, str]:
        """Attempts to unmortgage a property (costs value + 10%). Returns (Success, Message)."""
        if self.properties.get_owner(property_name) != player:
            return False, "You do not own this property."

        if not self.properties.is_mortgaged(property_name):
            return False, "This property is not currently mortgaged."

        prop_data = self.properties.get_property_data(property_name)
        mortgage_value = prop_data["mortgage_value"]

        # Unmortgaging costs the mortgage value + 10% interest
        cost = int(mortgage_value * 1.1)

        if player.balance < cost:
            return False, f"Insufficient funds. You need ${cost} to unmortgage this."

        player.pay_balance(cost)
        self.properties.mortgaged[property_name] = False

        return True, f"✅ Unmortgaged {property_name} for ${cost}."

    def build_house(self, player, property_name: str) -> tuple[bool, str]:
        """Attempts to build a house/hotel. Enforces monopoly and even-build rules."""
        if self.properties.get_owner(property_name) != player:
            return False, "You do not own this property."

        prop_data = self.properties.get_property_data(property_name)
        if prop_data.get("type") != "street":
            return False, "You can only build on streets."

        group = prop_data["group"]
        if not self.properties.has_monopoly(player, group):
            return False, "You need a full Monopoly to build."

        # Find all properties in this group to check mortgages and even-build
        group_props = [
            name
            for name, data in self.properties.property_data.items()
            if data.get("group") == group
        ]

        for name in group_props:
            if self.properties.is_mortgaged(name):
                return False, "Cannot build. A property in this group is mortgaged."

        current_houses = self.properties.get_houses(property_name)
        if current_houses >= 5:
            return False, "This property already has a hotel."

        # Even build rule: You can only build if this property is tied for the least houses in the group
        min_houses_in_group = min(
            [self.properties.get_houses(name) for name in group_props]
        )
        if current_houses > min_houses_in_group:
            return (
                False,
                "You must build evenly. Build on other properties in this group first.",
            )

        house_cost = prop_data["house_cost"]
        if player.balance < house_cost:
            return False, f"Insufficient funds. A house here costs ${house_cost}."

        # Execute transaction
        player.pay_balance(house_cost)
        self.properties.houses[property_name] += 1

        bldg_type = "Hotel" if current_houses + 1 == 5 else "House"
        return True, f"✅ Built a {bldg_type} on {property_name} for ${house_cost}."

    def sell_house(self, player, property_name: str) -> tuple[bool, str]:
        """Attempts to sell a house/hotel for half price. Enforces even-sell rule."""
        if self.properties.get_owner(property_name) != player:
            return False, "You do not own this property."

        current_houses = self.properties.get_houses(property_name)
        if current_houses == 0:
            return False, "There are no buildings here to sell."

        prop_data = self.properties.get_property_data(property_name)
        group = prop_data["group"]
        group_props = [
            name
            for name, data in self.properties.property_data.items()
            if data.get("group") == group
        ]

        # Even sell rule: You can only sell if this property is tied for the most houses in the group
        max_houses_in_group = max(
            [self.properties.get_houses(name) for name in group_props]
        )
        if current_houses < max_houses_in_group:
            return (
                False,
                "You must sell evenly. Sell from other properties in this group first.",
            )

        # Sell price is always exactly half of the buy price
        sell_value = prop_data["house_cost"] // 2

        # Execute transaction
        self.properties.houses[property_name] -= 1
        player.add_balance(sell_value)

        bldg_type = "Hotel" if current_houses == 5 else "House"
        return True, f"✅ Sold a {bldg_type} on {property_name} for ${sell_value}."

    # Add these methods to your Game class in src-v2/game.py

    def get_player_liquid_worth(self, player) -> int:
        """Calculates the total cash a player could raise by selling everything."""
        cash = player.balance

        owned_props = self.properties.get_properties_owned_by(player)
        for prop_name in owned_props:
            prop_data = self.properties.get_property_data(prop_name)

            # Add value from selling houses/hotels
            houses = self.properties.get_houses(prop_name)
            if houses > 0:
                sell_value = prop_data["house_cost"] // 2
                cash += houses * sell_value

            # Add value from mortgaging unmortgaged properties
            if not self.properties.is_mortgaged(prop_name):
                cash += prop_data["mortgage_value"]

        return cash

    def _execute_bankruptcy_to_bank(self, player):
        """Handles asset transfer when a player goes bankrupt to the bank."""
        player.declare_bankruptcy()

        # Return all properties to the bank
        owned_props = self.properties.get_properties_owned_by(player)
        for prop_name in owned_props:
            self.properties.owners[prop_name] = None
            self.properties.houses[prop_name] = 0
            self.properties.mortgaged[prop_name] = False

        # Return Get Out of Jail Free cards to the deck
        for _ in range(player.chance_goojf_cards):
            # Find any chance goojf card to return it.
            self.cards.return_card_to_deck("chance_07")  # ID from cards.json
        for _ in range(player.community_chest_goojf_cards):
            self.cards.return_card_to_deck("cc_05")  # ID from cards.json

        return f"💥 {player.name} went bankrupt to the Bank! Their assets are returned."

    def _execute_bankruptcy_to_player(self, debtor, creditor):
        """Handles asset transfer when a player goes bankrupt to another player."""

        # 1. Give the creditor all the debtor's current cash
        creditor.add_balance(debtor.balance)
        debtor.declare_bankruptcy()

        # 2. Handle Properties and Buildings
        owned_props = self.properties.get_properties_owned_by(debtor)
        for prop_name in owned_props:
            # Rule: Buildings are sold to the bank at half price, cash goes to creditor
            houses = self.properties.get_houses(prop_name)
            if houses > 0:
                prop_data = self.properties.get_property_data(prop_name)
                sell_value = (prop_data["house_cost"] // 2) * houses
                creditor.add_balance(sell_value)

                # Strip the buildings from the property
                self.properties.houses[prop_name] = 0

            # Transfer the deed to the creditor (mortgage status transfers as-is)
            self.properties.set_owner(prop_name, creditor)

        # 3. Transfer Get Out of Jail Free cards
        creditor.chance_goojf_cards += debtor.chance_goojf_cards
        creditor.community_chest_goojf_cards += debtor.community_chest_goojf_cards

        return f"💥 {debtor.name} went bankrupt to {creditor.name}! Buildings liquidated and assets transferred."

    def handle_payment(self, player, amount: int, creditor=None) -> tuple[bool, str]:
        """
        Central payment function. Determines if a player can pay or must liquidate/go bankrupt.
        Args:
            player: The player who needs to pay.
            amount: The amount owed.
            creditor: The player owed (or None if paying the Bank).

        Returns:
            (can_afford_boolean, message_string)
        """
        if player.balance >= amount:
            player.pay_balance(amount)
            if creditor:
                creditor.add_balance(amount)
            return True, f"{player.name} paid ${amount}."

        # If they can't afford it with cash, check their total liquid worth
        liquid_worth = self.get_player_liquid_worth(player)
        if liquid_worth < amount:
            # Bankruptcy is inevitable
            if creditor:
                msg = self._execute_bankruptcy_to_player(player, creditor)
            else:
                msg = self._execute_bankruptcy_to_bank(player)
            return False, msg  # False signifies they couldn't pay

        # If they can afford it but need to sell things, signal to the UI
        return False, "IN_DEBT"

    def snapshot(self) -> dict:
        """Returns a complete JSON-ready snapshot of the current game state."""
        return {
            "current_player": self.get_current_player().name,
            "consecutive_doubles": self.consecutive_doubles,
            "has_rolled": getattr(self, "has_rolled", False),
            "can_roll": getattr(self, "can_roll", True),
            "players": [p.to_dict() for p in self.players],
            "properties": self.properties.to_dict(),
        }

    def execute_trade(
        self,
        p1,
        p1_offer_cash: int,
        p1_offer_props: list,
        p2,
        p2_offer_cash: int,
        p2_offer_props: list,
    ) -> tuple[bool, str]:
        """Executes a complex trade between two players. Returns (Success, Message)."""

        # 1. Verify Cash
        if p1.balance < p1_offer_cash:
            return False, f"Trade failed. {p1.name} does not have ${p1_offer_cash}."
        if p2.balance < p2_offer_cash:
            return False, f"Trade failed. {p2.name} does not have ${p2_offer_cash}."

        # 2. Verify Properties
        for prop in p1_offer_props:
            if self.properties.get_owner(prop) != p1:
                return False, f"Trade failed. {p1.name} no longer owns {prop}."
            if self.properties.get_houses(prop) > 0:
                return (
                    False,
                    f"Trade failed. Cannot trade {prop} because it has buildings.",
                )

        for prop in p2_offer_props:
            if self.properties.get_owner(prop) != p2:
                return False, f"Trade failed. {p2.name} no longer owns {prop}."
            if self.properties.get_houses(prop) > 0:
                return (
                    False,
                    f"Trade failed. Cannot trade {prop} because it has buildings.",
                )

        # 3. Execute Trade - Cash
        if p1_offer_cash > 0:
            p1.pay_balance(p1_offer_cash)
            p2.add_balance(p1_offer_cash)
        if p2_offer_cash > 0:
            p2.pay_balance(p2_offer_cash)
            p1.add_balance(p2_offer_cash)

        # 4. Execute Trade - Properties
        for prop in p1_offer_props:
            self.properties.set_owner(prop, p2)
        for prop in p2_offer_props:
            self.properties.set_owner(prop, p1)

        return True, "✅ Trade successfully executed!"
