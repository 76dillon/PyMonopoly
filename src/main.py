import random
import time
import ascii_magic

from config import AVAILABLE_PLAYERS, NUM_SPACES
from player import Player
from board import Board
from properties import Properties
from print_board import print_board
from turn import normal_turn, jail_turn


def check_victory_conditions(players):
    not_bankrupt = len(players)
    for player in players:
        if player.bankrupt == True:
            not_bankrupt -= 1
        else:
            cur_player = player.name
    if not_bankrupt == 1:
        return cur_player

def main():
    ascii_output = ascii_magic.from_image("./images/monopoly_logo.png")
    ascii_output.to_terminal(columns=100)
    print("\n======================= Welcome to PyMonopoly! =======================")

    #Configure number of players
    while True:
        try:
            num_players = int(input("How many players? (2-4): "))
            if 2 <= num_players <= 4:
                print(f"Nunber of players: {num_players}")
                break
            else:
                print("INVALID INPUT. Number must be between 2 and 4.")
        except ValueError:
            print("INVALID INPUT. Please enter an integer betweeb 2 and 4.")
    
    #Configure player names and initialize player objects for each
    players = []
    for i in range(0, num_players):
        print("\n======================= Available Player Names =======================")
        for j in range(0, len(AVAILABLE_PLAYERS)):
            print(f"{j+1}. {AVAILABLE_PLAYERS[j]}")
        print("======================================================================")
        while True:
            try:
                player_id = int(input(f"Player {i+1}, choose number between 1 - {len(AVAILABLE_PLAYERS)}: "))
                if 1 <= player_id <= len(AVAILABLE_PLAYERS):
                    player = Player(AVAILABLE_PLAYERS[player_id-1])
                    players.append(player)
                    AVAILABLE_PLAYERS.remove(AVAILABLE_PLAYERS[player_id-1])
                    break
                else:
                    print(f"INVALID INPUT. Please choose number between 1 - {len(AVAILABLE_PLAYERS)}.")
            except ValueError:
                print(f"INVALID INPUT. Please choose number between 1 - {len(AVAILABLE_PLAYERS)}.")

    random.shuffle(players) #Shuffle list of players to determine random order
    board = Board()
    spaces = board.spaces
    properties = Properties()
    #print_board(spaces, players, properties)

    #Main game loop
    try:
        while True:
            for player in players:
                #Check victory conditions at the start of each player's turn.
                winner = check_victory_conditions(players)
                if winner != None:
                    break

                #If player is not bankrupt, their turn proceeds, otherwise, skip them.
                if player.bankrupt == False:
                    if player.jail == False:
                        (players, properties) = normal_turn(player, players, spaces, properties)
                    else:
                        (players, properties) = jail_turn(player, players, spaces, properties)
            if winner != None:
                break
        print(f"Congratulations {winner}! You've won the game.")
    except KeyboardInterrupt:
        print("\nExiting Game!")


if __name__ == "__main__":
    main()