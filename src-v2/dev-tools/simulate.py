import json
import random
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from player import Player
from game import Game


class BotSimulation:
    """Runs a headless Monopoly game with basic AI bots."""

    def __init__(self, num_players=4, max_turns=1000):
        self.players = [Player(f"Bot_{i+1}") for i in range(num_players)]
        self.game = Game(self.players)
        self.max_turns = max_turns
        self.turn_count = 0
        self.log = []

    def log_event(self, message):
        """Saves an event to the game log."""
        self.log.append(f"[Turn {self.turn_count}] {message}")

    def run(self):
        """Executes the game loop until someone wins or max_turns is reached."""
        self.log_event("Simulation started.")

        while self.turn_count < self.max_turns:
            current_player = self.game.get_current_player()

            if not current_player.is_bankrupt:
                self.take_bot_turn(current_player)

            # --- UPDATED WIN CONDITION CHECK ---
            # Check for a winner AFTER every player's turn or bankruptcy event.
            active_players = [p for p in self.game.players if not p.is_bankrupt]
            if len(active_players) <= 1:
                winner = active_players[0] if active_players else None
                if winner:
                    self.log_event(f"🎉 {winner.name} WINS THE GAME! 🎉")
                else:
                    self.log_event(
                        "All players went bankrupt simultaneously! No winner."
                    )
                break  # End the simulation immediately.

            self.game.end_turn()
            self.turn_count += 1

        self.export_logs()

    def take_bot_turn(self, bot):
        """Executes automated logic for a bot's turn with proper logging and immediate exits."""

        # --- PRE-ROLL STRATEGY ---
        # The bot first decides to trade or build before rolling.
        self.auto_trade(bot)
        self.auto_build(bot)

        while True:  # This loop handles doubles.
            if bot.is_bankrupt:
                break

            move_data = self.game.execute_move(bot)

            # --- UPDATED JAIL LOGGING ---
            jail_status = move_data.get("jail_status")
            if jail_status == "failed_roll":
                self.log_event(
                    f"🎲 {bot.name} is in jail and failed to roll doubles {move_data['dice']}."
                )
                break  # Turn is over.
            elif jail_status == "escaped_with_doubles":
                self.log_event(
                    f"🎲 {bot.name} rolled doubles {move_data['dice']} to escape jail!"
                )
            elif jail_status == "paid_mandatory_bail":
                self.log_event(
                    f"💰 {bot.name} paid $50 mandatory bail and is out of jail."
                )

            # Did they go to jail for speeding?
            if move_data["sent_to_jail"]:
                self.log_event(f"🚨 {bot.name} went to jail for speeding (3 doubles).")
                break

            # Process the outcome of landing on the space.
            space = move_data["landed_space"]
            self.log_event(f"{bot.name} landed on {space['name']}.")
            outcome = self.game.resolve_space(bot, space, sum(move_data["dice"]))
            self.process_bot_outcome(bot, space, outcome)

            # If the bot went bankrupt resolving the space, end its turn immediately.
            if bot.is_bankrupt:
                break

            # Standard end-of-roll logic
            if not move_data["is_doubles"] or jail_status == "escaped_with_doubles":
                break
            else:
                self.log_event(f"🎲 {bot.name} rolled doubles! Taking another turn.")

    def process_bot_outcome(self, bot, space, outcome):
        """Automates the responses to game engine prompts."""
        if "can_pay" in outcome and not outcome["can_pay"]:
            if outcome.get("message") == "IN_DEBT":
                creditor_name = outcome.get("owner") or outcome.get("creditor")
                creditor = next(
                    (p for p in self.game.players if p.name == creditor_name), None
                )
                self.auto_liquidate(bot, outcome["amount"], creditor)
            else:
                self.log_event(f"💥 {outcome['message']}")
            return

        action = outcome.get("action")

        if action == "offer_purchase":
            price = outcome["price"]
            # Basic AI: Buy it if we have at least $100 left over after purchase
            if bot.balance >= price + 100:
                self.game.buy_property(bot, space["name"])
                self.log_event(f"✅ {bot.name} bought {space['name']} for ${price}.")
            else:
                self.log_event(
                    f"🔄 {bot.name} declined {space['name']}. (Auction Skipped for Simplicity)"
                )
                # *Note: We skip auction logic in this basic bot sim to keep it fast,
                # but you could add a random bidding loop here!*

        elif action in ["drew_chance", "drew_community_chest"]:
            self.log_event(
                f"🃏 {bot.name} drew a card: {outcome['card']['description']}"
            )
            card_result = outcome.get("result", {})

            if card_result.get("status") == "multi_transaction":
                # Handle group payouts automatically
                for t in card_result["transactions"]:
                    debtor = next(
                        (p for p in self.game.players if p.name == t["debtor"]), None
                    )
                    creditor = next(
                        (p for p in self.game.players if p.name == t["creditor"]), None
                    )
                    if debtor and not debtor.is_bankrupt:
                        can_pay, msg = self.game.handle_payment(
                            debtor, t["amount"], creditor
                        )
                        if not can_pay and msg == "IN_DEBT":
                            self.auto_liquidate(debtor, t["amount"], creditor)
            else:
                self.process_bot_outcome(bot, space, card_result)

            if "follow_up" in card_result:
                new_space = self.game.board.get_space(bot.position)
                self.process_bot_outcome(bot, new_space, card_result["follow_up"])

    def auto_liquidate(self, bot, amount, creditor):
        """Forces a bot to sell houses or mortgage properties until debt is paid."""
        self.log_event(f"🚨 {bot.name} is in debt for ${amount}!")

        while bot.balance < amount:
            owned = self.game.properties.get_properties_owned_by(bot)

            # 1. Try to sell houses first
            properties_with_houses = [
                p for p in owned if self.game.properties.get_houses(p) > 0
            ]
            if properties_with_houses:
                sold_something = False
                for prop in properties_with_houses:
                    success, msg = self.game.sell_house(bot, prop)
                    if success:
                        self.log_event(f"🏚️ {bot.name} {msg}")
                        sold_something = True
                        break  # Break the inner loop, re-evaluate balance in the while loop

                if sold_something:
                    continue  # We raised some cash, check if it's enough yet!

            # 2. If no houses left to sell, resort to mortgaging
            unmortgaged = [p for p in owned if not self.game.properties.is_mortgaged(p)]
            if not unmortgaged:
                break  # Can't raise any more money, out of assets!

            prop_to_mortgage = unmortgaged[0]
            success, msg = self.game.mortgage_property(bot, prop_to_mortgage)
            if success:
                self.log_event(
                    f"🏦 {bot.name} mortgaged {prop_to_mortgage} to raise funds."
                )
            else:
                # Failsafe against infinite loops if the engine rejects the mortgage for any reason
                self.log_event(f"❌ Bot failed to liquidate {prop_to_mortgage}: {msg}")
                break

        # Re-attempt payment
        can_pay, msg = self.game.handle_payment(bot, amount, creditor)
        self.log_event(msg)

    def export_logs(self):
        """Writes the turn-by-turn history and the final game snapshot to a 'logs' directory."""

        # Define the logs directory path relative to this script's location
        base_dir = os.path.dirname(os.path.abspath(__file__))
        logs_dir = os.path.join(base_dir, "logs")

        # Create the directory if it doesn't exist.
        os.makedirs(logs_dir, exist_ok=True)

        log_file_path = os.path.join(logs_dir, "simulation_log.txt")
        snapshot_file_path = os.path.join(logs_dir, "simulation_snapshot.json")

        # 1. Write the text log
        self.log_event("Exporting final snapshot and logs.")
        with open(log_file_path, "w", encoding="utf-8") as f:
            f.write("\n".join(self.log))

        # 2. Write the JSON state snapshot
        with open(snapshot_file_path, "w", encoding="utf-8") as f:
            json.dump(self.game.snapshot(), f, indent=4)

        print(f"Simulation complete after {self.turn_count} turns.")
        print(f"Outputs saved to '{logs_dir}'")

    def auto_trade(self, bot):
        """Simple AI to try and complete Monopolies by buying missing properties."""
        owned = self.game.properties.get_properties_owned_by(bot)

        # Group properties by color
        groups = {}
        for prop in owned:
            data = self.game.properties.get_property_data(prop)
            if data.get("type") == "street":
                grp = data["group"]
                groups[grp] = groups.get(grp, []) + [prop]

        for grp, props in groups.items():
            # Find all properties that belong to this color group
            all_in_grp = [
                p
                for p, d in self.game.properties.property_data.items()
                if d.get("group") == grp
            ]

            # If we are missing exactly 1 property to finish the set
            if len(props) == len(all_in_grp) - 1:
                missing = [p for p in all_in_grp if p not in props][0]
                owner = self.game.properties.get_owner(missing)

                # If someone else owns it, offer them 2.5x the price
                if owner and owner != bot:
                    price = self.game.properties.get_property_data(missing)["price"]
                    offer = int(price * 2.5)

                    # If the bot has the cash, and the other owner isn't actively building a monopoly themselves
                    if bot.balance >= offer:
                        # (A smart bot would refuse, but our simple bots will accept the cash!)
                        bot.pay_balance(offer)
                        owner.add_balance(offer)
                        self.game.properties.set_owner(missing, bot)
                        self.log_event(
                            f"🤝 TRADE: {bot.name} bought {missing} from {owner.name} for ${offer} to complete a Monopoly!"
                        )

    def auto_build(self, bot):
        """Simple AI to build houses on completed Monopolies."""
        owned = self.game.properties.get_properties_owned_by(bot)

        for prop in owned:
            data = self.game.properties.get_property_data(prop)
            if data.get("type") == "street" and self.game.properties.has_monopoly(
                bot, data["group"]
            ):
                house_cost = data["house_cost"]

                # Try to build if we have enough cash buffer ($500 safety net)
                while bot.balance >= house_cost + 500:
                    success, msg = self.game.build_house(bot, prop)
                    if success:
                        self.log_event(msg)
                    else:
                        break  # Stop trying if it fails (e.g., hit the even-build rule limit or max hotels)


if __name__ == "__main__":
    sim = BotSimulation(num_players=4)
    sim.run()
