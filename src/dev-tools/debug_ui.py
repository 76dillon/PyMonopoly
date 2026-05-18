# src-v2/debug_ui.py
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from ui import TerminalUI


class DebugUI(TerminalUI):
    """
    An extension of the TerminalUI that includes a "God Mode" menu for developers.
    """

    def play_turn(self, player):
        """
        Overrides the default play_turn to add a God Mode option while using
        the new engine-driven state for turn phases.
        """
        print(f"\n--- {player.name}'s Turn (Balance: ${player.balance}) ---")

        # Skip the forced jail prompt if they reloaded a save AFTER already failing their jail roll
        if player.is_in_jail and not self.game.has_rolled:
            print(f"🚨 You are in Jail! (Turn {player.jail_turns + 1} of 3)")
            input("Press Enter to attempt to roll for doubles...")

            move_data = self.handle_roll(player)

            if move_data.get("jail_status") == "escaped_with_doubles":
                print(f"✅ You escaped!")
            elif move_data.get("jail_status") == "paid_mandatory_bail":
                print("💰 You paid the mandatory $50 bail.")
            else:
                print(f"❌ Not doubles. You remain in jail.")

            return

        # --- NORMAL TURN LOGIC (No local can_roll/has_rolled variables) ---

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

            # Add the special developer options
            options["G"] = "God Mode"
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
            elif choice == "G":
                self.god_mode_menu(player)
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

    def god_mode_menu(self, current_player):
        """Displays a menu of debug commands to directly manipulate the game state."""
        print("\n" + "--- 👑 GOD MODE 👑 ---")
        options = {
            "1": "Jump a Player to Space",
            "2": "Force Pass Go",
            "3": "Force Bankruptcy",
            "4": "Claim Unowned Property",
            "5": "Claim Monopoly (No Houses)",
            "6": "Claim Monopoly (Max Hotels)",
            "7": "Set Player Balance",
            "q": "Exit God Mode",
        }

        for k, v in options.items():
            print(f"[{k}] {v}")

        choice = input("Enter command: ").strip().lower()

        if choice == "1":
            target_player = self._select_player("teleport")
            if not target_player:
                return
            try:
                space_idx = int(input("Enter space index (0-39): "))
                outcome = self.game.debug_teleport_player(target_player, space_idx)
                if outcome:
                    self.process_outcome(
                        target_player, self.game.board.get_space(space_idx), outcome
                    )
            except ValueError:
                print("Invalid index.")

        elif choice == "2":
            target_player = self._select_player("give money to")
            if target_player:
                target_player.add_balance(200)
                print(f"Gave {target_player.name} $200.")

        elif choice == "3":
            target_player = self._select_player("make bankrupt")
            if target_player:
                # For simplicity, this always makes them bankrupt to the Bank.
                print(self.game._execute_bankruptcy_to_bank(target_player))
                self._check_for_winner()

        elif choice == "4":
            unowned = [p for p, o in self.game.properties.owners.items() if o is None]
            for i, prop in enumerate(unowned):
                print(f"[{i}] {prop}")
            try:
                idx = int(input("Select property: "))
                print(
                    self.game.debug_force_acquire_property(current_player, unowned[idx])
                )
            except (ValueError, IndexError):
                print("Invalid selection.")

        elif choice == "5" or choice == "6":
            groups = sorted(
                list(
                    set(
                        [
                            d["group"]
                            for d in self.game.properties.property_data.values()
                        ]
                    )
                )
            )
            for i, grp in enumerate(groups):
                print(f"[{i}] {grp}")
            try:
                idx = int(input("Select group: "))
                max_houses = choice == "6"
                print(
                    self.game.debug_force_acquire_monopoly(
                        current_player, groups[idx], max_houses
                    )
                )
            except (ValueError, IndexError):
                print("Invalid selection.")

        elif choice == "7":
            target_player = self._select_player("set balance for")
            if not target_player:
                return
            try:
                new_bal = int(input(f"Enter new balance for {target_player.name}: $"))
                print(self.game.debug_set_player_balance(target_player, new_bal))
            except ValueError:
                print("Invalid number.")

    def _select_player(self, action_verb: str):
        """Helper to prompt the user to select any player in the game."""
        print(f"Select a player to {action_verb}:")
        for i, p in enumerate(self.game.players):
            print(f"[{i}] {p.name}")
        try:
            idx = int(input("Enter ID: "))
            return self.game.players[idx]
        except (ValueError, IndexError):
            print("Invalid selection.")
            return None
