# src-v2/save_manager.py
import os
import json


class SaveManager:
    SAVE_FILE_PATH = os.path.join(os.path.dirname(__file__), "..", "savegame.json")

    @classmethod
    def save_game(cls, game):
        """Saves the current game state to a file."""
        try:
            snapshot = game.snapshot()
            with open(cls.SAVE_FILE_PATH, "w", encoding="utf-8") as f:
                json.dump(snapshot, f, indent=4)
        except Exception as e:
            print(f"Error saving game: {e}")

    @classmethod
    def load_game(cls):
        """Loads a game state from a file, if it exists."""
        if not os.path.exists(cls.SAVE_FILE_PATH):
            return None

        try:
            with open(cls.SAVE_FILE_PATH, "r", encoding="utf-8") as f:
                snapshot = json.load(f)
            return snapshot
        except (json.JSONDecodeError, KeyError) as e:
            print(f"Error loading save file (it may be corrupted): {e}")
            return None

    @classmethod
    def delete_save(cls):
        """Deletes the save file, typically after a game concludes."""
        if os.path.exists(cls.SAVE_FILE_PATH):
            os.remove(cls.SAVE_FILE_PATH)
            print("Save file deleted.")
