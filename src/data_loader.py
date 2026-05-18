import json
import os


class DataLoader:
    """Utility class to load static game data from JSON files."""

    @staticmethod
    def load_json(filename: str):
        # Dynamically find the path to the src-v2/data directory
        base_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(base_dir, "data", filename)

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Could not find data file at: {file_path}")

        with open(file_path, "r", encoding="utf-8") as file:
            return json.load(file)
