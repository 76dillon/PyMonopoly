# src-v2/ui.py
import sys
from save_manager import SaveManager


class TerminalUI:
    """Handles all command-line interactions with the players."""

    def __init__(self, game):
        self.game = game

    def start(self):
        """The main game loop."""
        print("\n" + "=" * 50)
        print("🎲 WELCOME TO TERMINAL MONOPOLY 🎲")
        print("=" * 50)

        while True:
            current_player = self.game.get_current_player()

            if current_player.is_bankrupt:
                self.game.end_turn()
                continue

            self.play_turn(current_player)

            # Save the game after every completed turn.
            SaveManager.save_game(self.game)

            # Simple win condition check (only 1 player left)
            active_players = [p for p in self.game.players if not p.is_bankrupt]
            if len(active_players) == 1:
                print(f"\n🎉 {active_players[0].name} WINS THE GAME! 🎉")
                SaveManager.delete_save()  # Clean up the save file
                break

            self.game.end_turn()

    def play_turn(self, player):
        """Displays the menu for a single player's turn dynamically."""
        print(f"\n--- {player.name}'s Turn (Balance: ${player.balance}) ---")

        # Skip the forced jail prompt if they reloaded a save AFTER already failing their jail roll
        if player.is_in_jail and not self.game.has_rolled:
            print(f"🚨 You are in Jail! (Turn {player.jail_turns + 1} of 3)")
            input("Press Enter to attempt to roll for doubles...")

            # Use handle_roll instead of execute_move directly so we get the flashy dice output!
            move_data = self.handle_roll(player)

            if move_data.get("jail_status") == "escaped_with_doubles":
                print(f"✅ You escaped!")
            elif move_data.get("jail_status") == "paid_mandatory_bail":
                print("💰 You paid the mandatory $50 bail.")
            else:
                print(f"❌ Not doubles. You remain in jail.")

            # Game engine now tracks that they have rolled and cannot roll again
            return

        # --- NORMAL TURN LOGIC ---
        # Notice: can_roll and has_rolled local variables are GONE!

        while True:
            # 1. Dynamically build the available options using ENGINE state
            options = {}
            if self.game.can_roll:
                options["1"] = "Roll Dice"

            options["2"] = "View Player Status"
            options["3"] = "View Board"
            options["4"] = "Manage Mortgages"
            options["5"] = "Manage Buildings"

            if self.game.has_rolled and not self.game.can_roll:
                options["6"] = "Propose Trade"
                options["7"] = "End Turn"

            options["Q"] = "Quit Game"

            # 2. Display the menu
            print("\nOptions: " + "  ".join([f"[{k}] {v}" for k, v in options.items()]))
            choice = input("Select an option: ").strip().upper()

            # 3. Process valid choices
            if choice not in options:
                print("❌ Invalid option. Please choose a valid number.")
                continue

            if choice == "1":
                move_data = self.handle_roll(player)

                if move_data.get("game_over"):
                    break

                if move_data.get("sent_to_jail"):
                    print("Your turn is over because you were sent to jail.")
                    break

                # The engine tells us if we get to roll again!
                if self.game.can_roll:
                    print("🎲 You rolled doubles! You must roll again.")

            elif choice == "2":
                self.display_status(player)
            elif choice == "3":
                self.display_board()
            elif choice == "4":
                self.manage_mortgages(player)
            elif choice == "5":
                self.manage_buildings(player)
            elif choice == "6":
                self.manage_trading(player)
            elif choice == "7":
                print(f"Ending {player.name}'s turn.")
                break
            elif choice == "Q":
                confirm = (
                    input(
                        "Are you sure you want to quit? The game will be saved. (y/n): "
                    )
                    .strip()
                    .lower()
                )
                if confirm == "y":
                    raise KeyboardInterrupt

    def handle_roll(self, player) -> dict:
        """Executes a move and returns a dictionary with move data and game status."""
        print("\nRolling dice...")
        move_data = self.game.execute_move(player)

        # --- NEW: Highly visible dice output! ---
        d1, d2 = move_data["dice"]
        print(f"\n🎲 >>> ROLLED {d1} and {d2} (TOTAL: {d1+d2}) <<< 🎲\n")

        jail_status = move_data.get("jail_status")
        if jail_status == "failed_roll":
            return move_data
        elif jail_status == "mandatory_bail_debt":
            print(f"🚨 {player.name} hit debt trying to pay mandatory $50 bail!")
            self.force_liquidation_menu(player, 50, None)
            return move_data

        if move_data.get("sent_to_jail"):
            print("🚨 Rolled doubles 3 times in a row! Go to Jail!")
            return move_data

        if move_data.get("passed_go"):
            print("💵 You passed GO! Collected $200.")

        space = move_data["landed_space"]
        print(f"📍 Landed on: {space['name']}")

        outcome = self.game.resolve_space(player, space, sum(move_data["dice"]))

        if self.process_outcome(player, space, outcome):
            move_data["game_over"] = True

        return move_data

    def process_outcome(self, player, space, outcome):
        """
        Translates the engine's outcome into terminal text and returns True if the game is over.
        """
        # This is a failsafe for unexpected engine results
        if not outcome:
            return False

        # --- DEBT & BANKRUPTCY GATEKEEPER ---
        if "can_pay" in outcome and not outcome["can_pay"]:
            if outcome.get("message") == "IN_DEBT":
                creditor_name = outcome.get("owner") or outcome.get("creditor")
                creditor = next(
                    (p for p in self.game.players if p.name == creditor_name), None
                )
                self.force_liquidation_menu(player, outcome["amount"], creditor)
            else:
                # Bankruptcy was declared! Print the message and check for a winner.
                print(f"\n{outcome['message']}")
                return self._check_for_winner()  # Return True if the game is now over.
            return False

        action = outcome.get("action")

        # --- STANDARD ACTION PROCESSING ---

        if action == "paid_tax":
            print(
                f"🏛️ Paid ${outcome['amount']} in taxes. New balance: ${player.balance}"
            )

        elif action == "paid_rent":
            print(
                f"🏠 Paid ${outcome['amount']} rent to {outcome['owner']}. New balance: ${player.balance}"
            )

        elif action == "sent_to_jail":
            print("🚨 Go directly to Jail! Do not pass GO, do not collect $200.")

        # --- THIS IS THE MISSING BLOCK ---
        elif action == "offer_purchase":
            price = outcome["price"]
            print(f"🏢 {space['name']} is unowned. Price: ${price}")
            if player.balance >= price:
                buy = input(f"Do you want to buy it? (y/n): ").strip().lower()
                if buy == "y":
                    self.game.buy_property(player, space["name"])
                    print(f"✅ Bought {space['name']}! New balance: ${player.balance}")
                else:
                    print("Declined purchase. Initiating Auction...")
                    self.run_auction(space["name"])
            else:
                print(
                    "❌ You do not have enough money to buy this. Initiating Auction..."
                )
                self.run_auction(space["name"])
        # --- END OF MISSING BLOCK ---

        elif action == "nothing":
            # We can add the reason for clarity if the engine provides it.
            if outcome.get("reason"):
                print(f"ℹ️ {outcome['reason']}")
            else:
                print("Nothing happens here. Catch your breath!")

        elif action in ["drew_chance", "drew_community_chest"]:
            card_type = "Chance" if action == "drew_chance" else "Community Chest"
            print(f"🃏 Drew {card_type}: {outcome['card']['description']}")

            card_result = outcome.get("result", {})

            # Recursively process the outcome of the card's action
            if self.process_outcome(player, space, card_result):
                return True  # Pass the game-over signal up the chain

            # If the card also caused a move, process the new space
            if "follow_up" in card_result:
                print("...resolving new space...")
                new_space = self.game.board.get_space(player.position)
                if self.process_outcome(player, new_space, card_result["follow_up"]):
                    return True

        return False  # Return False if the game is not over

    def run_auction(self, property_name):
        """Handles the bidding war when a property is declined."""
        print(f"\n--- 🔨 AUCTION: {property_name} 🔨 ---")
        active_bidders = [p for p in self.game.players if not p.is_bankrupt]
        current_bid = 10
        highest_bidder = None

        while len(active_bidders) > 1:
            for bidder in list(active_bidders):  # Copy list to allow removal
                if len(active_bidders) == 1:
                    break

                print(
                    f"\nCurrent highest bid: ${current_bid} (by {highest_bidder.name if highest_bidder else 'None'})"
                )
                print(f"{bidder.name}'s turn to bid (Balance: ${bidder.balance}).")

                choice = (
                    input(f"Enter bid higher than ${current_bid} (or 'pass'): ")
                    .strip()
                    .lower()
                )

                if choice == "pass":
                    print(f"{bidder.name} drops out of the auction.")
                    active_bidders.remove(bidder)
                else:
                    try:
                        bid_amount = int(choice)
                        if bid_amount > current_bid and bid_amount <= bidder.balance:
                            current_bid = bid_amount
                            highest_bidder = bidder
                            print(f"✅ {bidder.name} bids ${current_bid}!")
                        else:
                            print(
                                f"❌ Invalid bid. Must be > ${current_bid} and <= your balance. You are out."
                            )
                            active_bidders.remove(bidder)
                    except ValueError:
                        print("❌ Invalid input. You are out of the auction.")
                        active_bidders.remove(bidder)

        if highest_bidder:
            print(
                f"\n🎉 {highest_bidder.name} wins the auction for {property_name} at ${current_bid}!"
            )
            self.game.win_auction(highest_bidder, property_name, current_bid)
        else:
            print("\n🤷 No one bid. The property remains unowned.")

    def display_status(self, player):
        """Prints the player's current stats and owned properties."""
        print("\n--- STATUS ---")
        print(f"Position: {self.game.board.get_space(player.position)['name']}")
        print(f"Balance: ${player.balance}")

        owned = []
        for prop_name, owner in self.game.properties.owners.items():
            if owner == player:
                owned.append(prop_name)

        if owned:
            print("Owned Properties:")
            for prop in owned:
                houses = self.game.properties.get_houses(prop)
                print(f" - {prop} (Houses: {houses})")
        else:
            print("Owned Properties: None")
        print("--------------\n")

    def display_board(self):
        """Prints the entire board state in a formatted table."""
        # Increased total width slightly to account for the wider Type column
        print("\n" + "=" * 110)
        print(f"{'--- CURRENT BOARD STATE ---':^110}")
        print("=" * 110)

        # Increased 'Type' column from <13 to <15
        print(
            f" {'Pos':<3} | {'Space Name':<26} | {'Type':<15} | {'Owner':<10} | {'Bldgs':<5} | {'Mrtg':<4} | Occupied By"
        )
        print("-" * 110)

        for i in range(40):
            space = self.game.board.get_space(i)
            name = space["name"]
            sp_type = space["type"]

            # Defaults for non-properties
            owner_str = "-"
            bldg_str = "-"
            mrtg_str = "-"

            # Fetch property data if applicable
            if sp_type in ["street", "railroad", "utility"]:
                owner = self.game.properties.get_owner(name)
                owner_str = owner.name if owner else "Unowned"

                if owner:
                    mrtg_str = (
                        "YES" if self.game.properties.is_mortgaged(name) else "No"
                    )

                if sp_type == "street":
                    houses = self.game.properties.get_houses(name)
                    if houses == 5:
                        bldg_str = "HOTEL"
                    elif houses > 0:
                        bldg_str = f"{houses}H"
                    else:
                        bldg_str = "0"

            # Determine occupants and Jail status
            occupants = []
            for p in self.game.players:
                if p.position == i and not p.is_bankrupt:
                    if i == 10:  # Special logic for Jail space
                        status = "(In Jail)" if p.is_in_jail else "(Visiting)"
                        occupants.append(f"{p.name} {status}")
                    else:
                        occupants.append(p.name)

            occ_str = ", ".join(occupants)

            # Updated string formatting: {sp_type:<15}
            print(
                f" {i:<3} | {name:<26} | {sp_type:<15} | {owner_str[:10]:<10} | {bldg_str:<5} | {mrtg_str:<4} | {occ_str}"
            )

        print("=" * 110 + "\n")

    def manage_mortgages(self, player):
        """Displays an interactive menu for toggling property mortgages."""
        while True:
            owned_props = self.game.properties.get_properties_owned_by(player)

            if not owned_props:
                print("\n❌ You don't own any properties yet.")
                return

            print(f"\n--- 🏦 MORTGAGE MANAGEMENT (Balance: ${player.balance}) ---")
            print(" ID | Property Name              | Status     | Action Value")
            print("-" * 65)

            for i, prop_name in enumerate(owned_props):
                is_mortgaged = self.game.properties.is_mortgaged(prop_name)
                prop_data = self.game.properties.get_property_data(prop_name)
                base_value = prop_data["mortgage_value"]

                if is_mortgaged:
                    status = "MORTGAGED"
                    cost = int(base_value * 1.1)
                    action_str = f"Pay ${cost} to Unmortgage"
                else:
                    status = "Active"
                    action_str = f"Receive ${base_value} to Mortgage"

                print(f" {i:<2} | {prop_name:<26} | {status:<10} | {action_str}")

            print("-" * 65)
            choice = (
                input("Enter property ID to toggle mortgage (or 'q' to go back): ")
                .strip()
                .lower()
            )

            if choice == "q":
                break

            try:
                idx = int(choice)
                if 0 <= idx < len(owned_props):
                    selected_prop = owned_props[idx]

                    # Toggle based on current state
                    if self.game.properties.is_mortgaged(selected_prop):
                        success, msg = self.game.unmortgage_property(
                            player, selected_prop
                        )
                    else:
                        success, msg = self.game.mortgage_property(
                            player, selected_prop
                        )

                    print(msg)
                else:
                    print("❌ Invalid ID.")
            except ValueError:
                print("❌ Please enter a valid number or 'q'.")

    def manage_buildings(self, player):
        """Displays an interactive menu for buying and selling houses/hotels."""
        while True:
            owned_props = self.game.properties.get_properties_owned_by(player)
            # Filter down to ONLY streets that are part of a completed Monopoly
            buildable_props = []
            for prop in owned_props:
                prop_data = self.game.properties.get_property_data(prop)
                if prop_data.get(
                    "type"
                ) == "street" and self.game.properties.has_monopoly(
                    player, prop_data["group"]
                ):
                    buildable_props.append(prop)

            if not buildable_props:
                print("\n❌ You do not have any full Monopolies to build on.")
                return

            print(f"\n--- 🏗️ BUILDING MANAGEMENT (Balance: ${player.balance}) ---")
            print(
                " ID | Property Name              | Grp   | Bldgs | Cost To Build | Bulldoze Value "
            )
            print("-" * 84)

            for i, prop_name in enumerate(buildable_props):
                prop_data = self.game.properties.get_property_data(prop_name)
                houses = self.game.properties.get_houses(prop_name)

                bldg_str = "HOTEL" if houses == 5 else f"{houses}H"
                cost = prop_data["house_cost"]
                sell = cost // 2
                grp = prop_data["group"][:3].upper()  # Shorten color group name

                print(
                    f" {i:<2} | {prop_name:<26} | {grp:<5} | {bldg_str:<5} | ${cost:<12} | ${sell}"
                )

            print("-" * 80)
            print(
                "Type '[ID] build' to build, '[ID] bulldoze' to remove, or 'q' to go back."
            )
            choice = input("Example: '0 build' -> ").strip().lower()

            if choice == "q":
                break

            parts = choice.split()
            if len(parts) == 2:
                try:
                    idx = int(parts[0])
                    action = parts[1]

                    if 0 <= idx < len(buildable_props):
                        selected_prop = buildable_props[idx]

                        if action == "build":
                            success, msg = self.game.build_house(player, selected_prop)
                        elif action == "bulldoze":
                            success, msg = self.game.sell_house(player, selected_prop)
                        else:
                            success, msg = False, "Action must be 'buy' or 'sell'."

                        print(msg)
                    else:
                        print("❌ Invalid ID.")
                except ValueError:
                    print("❌ Invalid format. Use format like '1 buy'.")
            else:
                print("❌ Invalid format. Please provide ID and action.")

    def force_liquidation_menu(self, player, amount_owed: int, creditor=None):
        """A special menu that forces a player to sell assets until they can pay a debt."""
        print(
            f"\n🚨 DEBT COLLECTION! You owe ${amount_owed} but only have ${player.balance}. 🚨"
        )
        print("You must sell buildings or mortgage properties to raise funds.")

        while player.balance < amount_owed:
            print("\nChoose an action:")
            print("[1] Sell Houses/Hotels")
            print("[2] Mortgage Properties")
            choice = input("Select an option: ").strip()

            if choice == "1":
                self.manage_buildings(player)
            elif choice == "2":
                self.manage_mortgages(player)
            else:
                print("Invalid choice. You must raise the funds.")

        # Once they have enough money, the game engine re-handles the payment
        can_pay, msg = self.game.handle_payment(player, amount_owed, creditor)
        print(f"\n✅ Debt paid. {msg}")

    def _check_for_winner(self) -> bool:
        """Checks if there is a single player left and declares them the winner."""
        active_players = [p for p in self.game.players if not p.is_bankrupt]
        if len(active_players) <= 1:
            winner = active_players[0] if active_players else None
            if winner:
                print(f"\n🎉 {winner.name} WINS THE GAME! 🎉")
            else:
                print("\nAll players went bankrupt simultaneously! No winner.")
            return True  # Game is over
        return False  # Game continues

    def manage_trading(self, player):
        """Guides the user through proposing a trade to another player."""
        print(f"\n--- 🤝 TRADE PROPOSAL (Your Balance: ${player.balance}) ---")

        # 1. Select Target Player
        active_opponents = [
            p for p in self.game.players if not p.is_bankrupt and p != player
        ]
        if not active_opponents:
            print("❌ There is no one left to trade with.")
            return

        print("Select a player to trade with:")
        for i, opp in enumerate(active_opponents):
            print(f"[{i}] {opp.name}")
        print("[q] Cancel")

        choice = input("Enter ID: ").strip().lower()
        if choice == "q":
            return

        try:
            target_idx = int(choice)
            if not (0 <= target_idx < len(active_opponents)):
                print("❌ Invalid ID.")
                return
            target_player = active_opponents[target_idx]
        except ValueError:
            print("❌ Invalid input.")
            return

        # 2. Build YOUR Offer (What you are giving up)
        print(f"\n--- What are YOU offering to {target_player.name}? ---")
        my_offer_cash, my_offer_props = self._build_trade_offer(player)
        if my_offer_cash is None:
            return  # Cancelled

        # 3. Build YOUR Request (What you want from them)
        print(f"\n--- What do you WANT from {target_player.name}? ---")
        their_offer_cash, their_offer_props = self._build_trade_offer(
            target_player, is_request=True
        )
        if their_offer_cash is None:
            return  # Cancelled

        # 4. Confirm before sending
        print("\n" + "=" * 50)
        print(f"📄 PROPOSED TRADE TO {target_player.name.upper()} 📄")
        print(
            f"YOU GIVE: ${my_offer_cash} and {my_offer_props if my_offer_props else 'No Properties'}"
        )
        print(
            f"YOU GET:  ${their_offer_cash} and {their_offer_props if their_offer_props else 'No Properties'}"
        )
        print("=" * 50)

        confirm = (
            input(f"Send this proposal to {target_player.name}? (y/n): ")
            .strip()
            .lower()
        )
        if confirm != "y":
            print("Trade cancelled.")
            return

        # 5. Target Player Approves/Denies
        print(f"\n🔔 HEY {target_player.name.upper()}! 🔔")
        print(f"{player.name} has proposed the trade above.")
        accept = input("Do you accept this trade? (y/n): ").strip().lower()

        if accept == "y":
            success, msg = self.game.execute_trade(
                player,
                my_offer_cash,
                my_offer_props,
                target_player,
                their_offer_cash,
                their_offer_props,
            )
            print(msg)
        else:
            print("❌ Trade rejected.")

    def _build_trade_offer(self, player, is_request=False):
        """Helper to let a user select cash and properties for a trade side.
        Returns (cash_amount, list_of_property_names), or (None, None) if cancelled.
        """
        offer_cash = 0
        offer_props = []

        # Filter properties: Can only trade properties with 0 houses.
        all_owned = self.game.properties.get_properties_owned_by(player)
        tradable_props = [
            p for p in all_owned if self.game.properties.get_houses(p) == 0
        ]

        while True:
            action_word = "request" if is_request else "offer"
            print(
                f"\nCurrent {action_word}: ${offer_cash} and {offer_props if offer_props else 'No Properties'}"
            )
            print("\nOptions:")
            print("[1] Set Cash Amount")
            print("[2] Add/Remove a Property")
            print("[3] Done (Move to next step)")
            print("[q] Cancel Entire Trade")

            choice = input("Select an option: ").strip().lower()

            if choice == "q":
                return None, None

            if choice == "3":
                if offer_cash == 0 and not offer_props:
                    confirm = input(
                        "Warning: This side of the trade is empty. Proceed? (y/n): "
                    ).lower()
                    if confirm != "y":
                        continue
                return offer_cash, offer_props

            elif choice == "1":
                # Determine max cash based on whose money we are looking at
                max_cash = (
                    player.balance if not is_request else "Any (You are requesting)"
                )
                amt_str = input(f"Enter cash amount (Max: {max_cash}): $")
                try:
                    amt = int(amt_str)
                    if amt < 0:
                        print("❌ Cannot offer negative cash.")
                    elif not is_request and amt > player.balance:
                        print(f"❌ You only have ${player.balance}.")
                    else:
                        offer_cash = amt
                except ValueError:
                    print("❌ Invalid number.")

            elif choice == "2":
                if not tradable_props:
                    print(
                        "❌ This player has no tradable properties (must have 0 houses)."
                    )
                    continue

                print(f"\nSelect a property to toggle in the {action_word}:")
                for i, prop in enumerate(tradable_props):
                    status = "[SELECTED]" if prop in offer_props else ""
                    print(f"[{i}] {prop} {status}")

                prop_choice = input("Enter ID (or 'b' to go back): ").strip().lower()
                if prop_choice == "b":
                    continue

                try:
                    idx = int(prop_choice)
                    if 0 <= idx < len(tradable_props):
                        selected = tradable_props[idx]
                        if selected in offer_props:
                            offer_props.remove(selected)
                        else:
                            offer_props.append(selected)
                    else:
                        print("❌ Invalid ID.")
                except ValueError:
                    print("❌ Invalid input.")
