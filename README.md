# PyMonopoly

## Background

This is my CLI implementation of the popular Parker Brothers economic themed multiplayer board game. [Wikipedia Link](https://en.wikipedia.org/wiki/Monopoly_(game)).

## Usage

To execute this program, create a virtual environment as follows at the :

Clone the repository:

```bash
git clone https://github.com/76dillon/PyMonopoly
```

Create a virtual environment in at the root directory.

```bash
python3 -m venv venv
```

To activate the virtual environment

```bash
source venv/bin/activate
```

Download the following dependency:

```bash
pip install ascii-magic
```
## How to play

From the root path run the following command

```bash
./main.sh
```

You'll then be prompted the enter the number of players. Up to 4 players supported at this time. Then each player will pick their corresponding icon. Dog, Ship, Tophat, Ship.

Each player turn consists of rolling the dice at the start. When the player lands on the corresponding space, the associated space event will occur: Chance, Community Chest, Landing on a Property, or going to jail. After the associated space event, the player will have the option to build/bulldoze houses and hotels on eligible properties, morthage/unmortgage properties, and view the current player information and owned properties. 

## Debug Mode

In the folder ./config.py, modify the following line

```bash
DEBUG_MODE = TRUE
```

This enables the player to manually select the values on the dice in a given turn.

## Upcoming Features

Features to be added in future versions:

- Trade with other players
- GUI
- Players can use multiple devices for a single game session



