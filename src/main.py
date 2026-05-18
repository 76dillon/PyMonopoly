# src-v2/main.py
import sys
from player import Player
from game import Game
from ui import TerminalUI
from save_manager import SaveManager  # <-- Import the manager


def main():
    game_engine = None

    # Check for an existing save file
    saved_snapshot = SaveManager.load_game()
    if saved_snapshot:
        print("\n💾 Found an existing save file.")
        choice = input("Would you like to load it? (y/n): ").strip().lower()
        if choice == "y":
            try:
                game_engine = Game.load_from_snapshot(saved_snapshot)
            except Exception as e:
                print(f"Could not load save file: {e}. Starting a new game.")

    # If no save was loaded, start a new game
    if game_engine is None:
        print("\n" + "=" * 50)
        print("🎲  WELCOME TO TERMINAL MONOPOLY  🎲")
        print("=" * 50)

        # (All the logic for setting up a new game: asking for player count and names)
        # ...
        num_players = 0
        while True:
            try:
                choice = input("How many players? (2-8): ").strip()
                num_players = int(choice)
                if 2 <= num_players <= 8:
                    break
                else:
                    print("❌ Invalid number. A game requires between 2 and 8 players.")
            except ValueError:
                print("❌ Invalid input. Please enter a number.")

        players = []
        print("\n--- Player Setup ---")
        for i in range(num_players):
            while True:
                name = input(f"Enter name for Player {i+1}: ").strip()
                if name:
                    if any(p.name.lower() == name.lower() for p in players):
                        print("❌ That name is already taken. Choose another.")
                    else:
                        players.append(Player(name=name))
                        break
                else:
                    print("❌ Name cannot be blank.")

        game_engine = Game(players=players)

    # Initialize the UI with the (either new or loaded) game engine
    ui = TerminalUI(game=game_engine)

    try:
        ui.start()
    except (KeyboardInterrupt, EOFError):
        # Save the game on a sudden exit (Ctrl+C or Ctrl+D)
        print("\n\n🛑 Game interrupted. Saving state...")
        SaveManager.save_game(game_engine)
        print("Exiting.")
        sys.exit(0)


if __name__ == "__main__":
    main()
