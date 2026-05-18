# src-v2/dev-tools/main-dev.py

import sys
import os

# Add the parent directory (src-v2/) to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from player import Player
from debug_game import DebugGame
from debug_ui import DebugUI
from save_manager import SaveManager  # <-- Import the save manager


def main():
    print("\n" + "=" * 50)
    print("🛠️  MONOPOLY DEVELOPER CONSOLE 🛠️")
    print("=" * 50)

    game_engine = None

    # 1. Check for an existing save file
    saved_snapshot = SaveManager.load_game()
    if saved_snapshot:
        print("\n💾 Found an existing save file.")
        choice = input("Would you like to load it? (y/n): ").strip().lower()
        if choice == "y":
            try:
                # Use DebugGame's load method (which it inherits from Game)
                game_engine = DebugGame.load_from_snapshot(saved_snapshot)
                print(
                    "✅ Game state successfully loaded from save file into DEBUG Engine."
                )
            except Exception as e:
                print(f"Could not load save file: {e}. Starting a new game.")

    # 2. If no save was loaded, start a new game setup
    if game_engine is None:
        fast_boot = (
            input("\nFast-boot with dummy players (P1, P2)? (y/n): ").strip().lower()
        )

        if fast_boot == "y":
            players = [Player("P1"), Player("P2")]
            print("Initialized dummy players: P1, P2")
        else:
            players = []
            try:
                num_players = int(input("How many players? (2-8): "))
                num_players = max(2, min(8, num_players))

                for i in range(num_players):
                    name = input(f"Enter Player {i+1} name: ").strip()
                    if not name:
                        name = f"Player_{i+1}"
                    players.append(Player(name=name))
            except ValueError:
                print("Invalid input. Defaulting to 2 players.")
                players = [Player("P1"), Player("P2")]

        # Initialize the Debug Engine
        game_engine = DebugGame(players=players)

    # 3. Initialize the Debug UI
    ui = DebugUI(game=game_engine)
    print("\n👑 God Mode UI Initialized. Access via option [G] in the main menu.")

    # 4. Start the game loop
    try:
        ui.start()
    except (KeyboardInterrupt, EOFError):
        # Save the game on a sudden exit (Ctrl+C or Ctrl+D)
        print("\n\n🛑 Developer Console interrupted. Saving state...")
        SaveManager.save_game(game_engine)
        print("Exiting.")
        sys.exit(0)


if __name__ == "__main__":
    main()
