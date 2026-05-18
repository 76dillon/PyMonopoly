# Terminal Monopoly (V2)

A fully decoupled, network-ready Python implementation of the classic board game Monopoly.

## 🚀 Overview

Version 2 represents a complete architectural overhaul of the original script. The core objective was to separate the game's mathematical rules (the "Engine") from the user interface (the "UI"). 

This decoupled design ensures that the game state is purely data-driven, mathematically sound, and easily serializable, paving the way for future integrations like client-server multiplayer (V3) or a 3D graphical frontend.

## 🏗️ Architecture

The project is divided into distinct, isolated layers:

*   **Data Layer (`src-v2/data/`):** All static game information (board layout, property prices, card logic) is stored in JSON format. The game logic relies entirely on these files, making it incredibly easy to create custom boards or tweak rent values without touching Python code.
*   **Math Layer (`src-v2/mechanics.py`):** Pure, stateless functions that handle the complex Monopoly math (e.g., dynamic rent calculation based on dice rolls and monopolies, repair costs).
*   **State Managers (`src-v2/board.py`, `src-v2/properties.py`, `src-v2/cards.py`):** Classes that ingest the JSON data and manage the dynamic, mid-game state (e.g., who owns what, how many houses are built, deck shuffling).
*   **The Engine (`src-v2/game.py`):** The central orchestrator. It enforces the rules, moves players, and handles atomic transactions. **It contains zero UI prompts (`print` or `input`).**
*   **The UI (`src-v2/ui.py`):** A "dumb" terminal interface. It simply displays the engine's state, asks the user for decisions, and passes those decisions back to the engine.

## 🎮 How to Play

Run the main entry script from the root directory:

```bash
python src-v2/main.py
```

*   Supports 2 to 8 players.

*   Features a dynamic, responsive command-line menu.

*   Includes a fully featured Trading System allowing players to negotiate complex, multi-asset deals.

*   **Auto-Save:** The game automatically saves after every turn. You can safely `Quit Game` from the menu or press `Ctrl+C`, and your progress will be restored the next time you boot up.

## 🛠️ Developer Tools

This project includes a dedicated suite of tools for debugging and game balance analysis, safely isolated from the production code.

### The Developer Console (`main-dev.py`)

Run the developer entry point:

```bash
python src-v2/dev-tools/main-dev.py
```

This loads a `DebugGame` engine which unlocks "God Mode" (`[G]`) in the turn menu. Developers can use this to:

*   Teleport players to specific spaces.

*   Instantly claim properties or full monopolies (with or without max hotels).

*   Arbitrarily adjust player bank balances.

*   Force bankruptcies.

### The Simulation Engine (`simulate.py`)

A headless bot runner designed to stress-test the game logic and economy.

```bash
python src-v2/dev-tools/simulate.py

```

This script will instantly play a full game of Monopoly using basic AI bots. It generates two files in the `src-v2/logs/` directory:

1. `simulation_log.txt`: A chronological, turn-by-turn history of every action taken in the game.

2. `simulation_snapshot.json`: A complete JSON dump of the board and player states at the moment the game ended (useful for debugging stalemates or crashes).

## 🧪 Testing

The core engine is backed by a robust suite of unit tests, verifying everything from rent calculations to complex bankruptcy asset transfers.

To run the test suite:

```bash
python -m unittest discover -s src-v2/unit-tests
```

## 🗺️ Roadmap (V3)

The decoupled nature of V2 was specifically designed to support the following upgrades:

*   Multiplayer Server: Converting `game.py` into a headless server (e.g., using FastAPI or WebSockets) that broadcasts the state snapshot to remote clients.

*   Graphical Interface: Replacing the `TerminalUI` with a web-based frontend or a 3D engine (like Unity/Godot) that reads the JSON state and animates the board accordingly.