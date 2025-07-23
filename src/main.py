import random
import time

from config import AVAILABLE_PLAYERS, NUM_SPACES
from player import Player
from board import Board
from properties import Properties
from print_board import print_board
from dice import roll_dice

available_players = ["Dog", "Ship", "Tophat", "Car"]

def main():
    print("Welcome to PyMonopoly!")

    #Configure number of players
    while True:
        try:
            num_players = int(input("How many players? (2-4): "))
            if 2 <= num_players <= 4:
                print(f"Nunber of players: {num_players}")
                break
            else:
                print("Invalid input. Number must be between 2 and 4.")
        except ValueError:
            print("Invalid input. Please enter an integer betweeb 2 and 4.")
    
    #Configure player names and initialize player objects for each
    players = []
    for i in range(0, num_players):
        for j in range(0, len(AVAILABLE_PLAYERS)):
            print(f"{j+1}. {AVAILABLE_PLAYERS[j]}")
        while True:
            try:
                player_id = int(input(f"Choose number between 1 - {len(AVAILABLE_PLAYERS)}: "))
                if 1 <= player_id <= len(AVAILABLE_PLAYERS):
                    player = Player(AVAILABLE_PLAYERS[player_id-1])
                    players.append(player)
                    AVAILABLE_PLAYERS.remove(AVAILABLE_PLAYERS[player_id-1])
                    break
                else:
                    print(f"Invalid input. Please choose number between 1 - {len(AVAILABLE_PLAYERS)}:")
            except ValueError:
                print(f"Invalid input. Please choose number between 1 - {len(AVAILABLE_PLAYERS)}:")

    random.shuffle(players) #Shuffle list of players to determine random order
    print(players)
    board = Board()
    spaces = board.spaces
    properties = Properties()
    print_board(spaces, players, properties)

    #Main game loop
    try:
        while True: 
            for player in players:
                turn = input(f"It is {player.name}'s turn. Press Enter to roll dice: ")
                double_cnt = 0
                #Loop that breaks when no doubles or when 3 doubles
                while True:
                    (dice1, dice2) = roll_dice()
                    dice_total = dice1 + dice2
                    print(f"{player.name} rolled a {dice1} and {dice2} for a total of {dice_total}")
                    #Update player position
                    player.move_player(dice_total)
                    #Check if doubles were rolled
                    if dice1 == dice2:
                        double_cnt += 1
                        if double_cnt < 3:
                            print_board(spaces, players, properties)
                            turn = input(f"{player.name} rolled doubles. Press enter to roll again: ")
                        else:
                            print(f"{player.name} rolled a {dice1} and {dice2} for a total of {dice_total}")
                            print(f"{player.name} is in jail for rolling doubles three times in a row.")
                            player.position = 10 #Space ID of 10 is jail
                            print_board(spaces, players, properties)
                            break
                    else:
                        print_board(spaces, players, properties)
                        break
    except KeyboardInterrupt:
        print("\nExiting Game!")



if __name__ == "__main__":
    main()