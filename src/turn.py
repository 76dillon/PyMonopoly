from player import Player
from print_board import print_board
from dice import roll_dice
from config import *
from events import process_space_event

def normal_turn(player, players, spaces, properties):
    print_board(spaces, players, properties)
    print(f"{player.name}'s (Bal: ${player.balance}) turn.")
    print("=" * 131)
    turn = input("Press Enter to roll dice: ")
    double_cnt = 0
    #Loop that breaks when no doubles or when 3 doubles
    while True:
        (dice1, dice2) = roll_dice(DEBUG_MODE)
        dice_total = dice1 + dice2
        #Update player position
        passgo = player.move_player(dice_total)
        #Check if doubles were rolled
        if dice1 == dice2:
            double_cnt += 1
            #If doubles were rolled MAX_DOUBLES times in a row, put the player in jail (ID )
            if double_cnt < MAX_DOUBLES:
                #If player lands on "Go to Jail - Space ID: 30, put player in jail (Space ID: 10)"
                print(f"{player.name} rolled a {dice1} and {dice2} for a total of {dice_total}.")
                print(f"{player.name} landed on {spaces[player.position]["name"]}.")
                if passgo == True:
                    player.add_balance(GO)
                    print(f"{player.name} passed Go and received $200.")
                (players, properties, break_flag) = process_space_event(player, players, spaces, properties, dice_total)
                if break_flag == True:
                    break
                print_board(spaces, players, properties)
                turn = input(f"{player.name} rolled doubles. Press enter to roll again: ")
            else:
                #print(f"{player.name} rolled a {dice1} and {dice2} for a total of {dice_total}")
                player.move_to_jail()
                print_board(spaces, players, properties)
                print(f"{player.name} rolled a {dice1} and {dice2} for a total of {dice_total}.")
                print(f"{player.name} is in jail for rolling doubles {MAX_DOUBLES} times in a row.")
                break
        else:
            
            print(f"{player.name} rolled a {dice1} and {dice2} for a total of {dice_total}.")
            if passgo == True:
                player.add_balance(GO)
                print(f"{player.name} passed Go and received $200.")
            print(f"{player.name} landed on {spaces[player.position]["name"]}.")
            (players, properties, break_flag) = process_space_event(player, players, spaces, properties, dice_total)
            if break_flag == True:
                break
            (players, properties) = player_actions(player, players, properties)
            break

    return (players, properties)

'''
-Jail turn works different from a normal turn. Player has option of attempting to roll doubles or pay $50 bail. They may also use their Get out of Jail Free card if they have one.
-If on the third turn in jail, they are released automatically and pay $50 bail.
-While in jail, players can buy property, build houses and hotels, and collect rent from other players.
-When they are released, they roll and proceed with their turn as normal except their turn ends regardless of if they rolled doubles or not.
'''
def jail_turn(player, players, spaces, properties):
    print_board(spaces, players, properties)
    turn = print(f"{player.name}'s (Bal: ${player.balance}) turn.")
    print("=" * 131)
    while True:
        if player.num_jail_turns == 3:
            print(f"{player.name} has reached their maximum allotted jail turns and must pay ${BAIL}.")
            player.release_from_jail()
            #Deduct bail. Check if sufficient funds
            (pos_balance, properties) = player.pay_bank(BAIL, properties, optional=False)
            if pos_balance == False:
                break
            else:
                print(f"{player.name} paid ${BAIL} and is released from jail.")
                turn = input(f"It is {player.name}'s (Bal: ${player.balance}) turn. Press Enter to roll dice: ")
                (dice1, dice2) = roll_dice(DEBUG_MODE)
                dice_total = dice1+dice2
                player.move_player(dice_total)
                print(f"{player.name} rolled a {dice1} and {dice2} for a total of {dice_total}.")
                print(f"{player.name} landed on {spaces[player.position]["name"]}.")
                (players, properties, break_flag) = process_space_event(player, players, spaces, properties, dice_total)
                if break_flag == True:
                    break
                (players, properties) = player_actions(player, properties)
                break
        else:
            num_options = 1
            print(f"{player.name} (Bal: ${player.balance}) is in jail.")
            print("\n======================= Available Options =======================")
            print("1. Attempt to roll doubles")
            if player.balance > BAIL:
                print("2. Pay Bail")
                num_options += 1
            if player.num_jail_free_cards > 0:
                num_options += 1
                print("3. Use Get Out of Jail Free Card")
            print("=================================================================")
            while True:
                try:
                    choice = int(input(f"Enter the number corresponding to the above options 1 - {num_options}: "))
                    if 1 <= choice <= num_options:
                        break
                    else:
                        print(f"INVALID INPUT. Please choose a number between 1 and {num_options}.")
                except ValueError:
                    print(f"INVALID INPUT. Please choose a number between 1 and {num_options}.")

            if choice == 1:
                print(choice)
                (dice1, dice2) = roll_dice(DEBUG_MODE)
                dice_total = dice1+dice2
                if dice1 == dice2:
                    player.release_from_jail()
                    player.move_player(dice_total)
                    print(f"{player.name} rolled a {dice1} and {dice2} for a total of {dice_total}.")
                    print(f"{player.name} rolled doubles.")
                    print(f"{player.name} is released from jail!")
                    print(f"{player.name} landed on {spaces[player.position]["name"]}.")
                    (players, properties, break_flag) = process_space_event(player, players, spaces, properties, dice_total)
                    if break_flag == True:
                        break
                    
                else:
                    player.num_jail_turns += 1
                    print(f"{player.name} rolled a {dice1} and {dice2} for a total of {dice_total}.")
                    print(f"{player.name} remains in jail.")
            if choice == 2:
                player.release_from_jail()
                player.deduct_balance(BAIL)
                print(f"{player.name} paid ${BAIL} for bail.")
                print(f"{player.name} is released from jail!")
                turn = input(f"It is {player.name}'s turn. Press Enter to roll dice: ")
                (dice1, dice2) = roll_dice(DEBUG_MODE)
                dice_total = dice1+dice2
                player.move_player(dice_total)
                print(f"{player.name} rolled a {dice1} and {dice2} for a total of {dice_total}.")
                print(f"{player.name} landed on {spaces[player.position]["name"]}.")
                (players, properties, break_flag) = process_space_event(player, players, spaces, properties, dice_total)
                if break_flag == True:
                    break
            if choice == 3:
                player.num_jail_free_cards -= 1
                if (player.has_chance_jf_card == True) and (player.has_cc_jf_card == True):
                    properties.chance_card_order.append(9)
                    player.has_chance_jf_card = False
                elif (player.has_chance_jf_card == True) and (player.has_cc_jf_card == False):
                    player.has_chance_jf_card = False
                    properties.chance_card_order.append(9)
                else:
                    player.has_cc_jf_card = False
                    properties.cc_card_order.append(5)
                player.release_from_jail()
                print(f"{player.name} used their Get Out of Jail Free Card.")
                print(f"{player.name} is released from jail!")
                turn = input(f"It is {player.name}'s turn. Press Enter to roll dice: ")
                (dice1, dice2) = roll_dice(DEBUG_MODE)
                dice_total = dice1+dice2
                player.move_player(dice_total)
                print(f"{player.name} rolled a {dice1} and {dice2} for a total of {dice_total}.")
                print(f"{player.name} landed on {spaces[player.position]["name"]}.")
                (players, properties, break_flag) = process_space_event(player, players, spaces, properties, dice_total)
                if break_flag == True:
                    break
            (players, properties) = player_actions(player, players, properties)
            break

    return (players, properties)

#Handles actions a player can take after they roll the dice and after the initial turn events occur.
#Players in jail still have the option to purchase houses or mortgage/unmortgage property
def player_actions(player, players, properties):
    num_options = 8
    while True:
        print("\n======================= Available Options =======================")
        print("1. View General Player Stats")
        print("2. View Property Asset Info")
        print("3. Mortgage")
        print("4. Unmortgage")
        print("5. Build")
        print("6. Bulldoze")
        print("7. Trade (Not yet supported...)")
        print("8. End Turn")
        print("=================================================================")
        while True:
            try:
                choice = int(input(f"Enter the number corresponding to the above options 1 - {num_options}: ") or num_options)
                if 1 <= choice <= num_options:
                    break
                else:
                    print(f"INVALID INPUT. Please choose a number between 1 and {num_options}.")
            except ValueError:
                print(f"INVALID INPUT. Please choose a number between 1 and {num_options}.")
        #Query Player Info
        if choice == 1:
            player.query_player_info(properties)
        #View Property Asset Info
        elif choice == 2:
            player.query_prop_info(properties)
        #Mortgage
        elif choice == 3:
            properties = player.mortgage_select(properties)
        #Unmortgage
        elif choice == 4:
            properties = player.unmortgage_select(properties)
        #Build houses and hotels on eligible properties
        elif choice == 5:
            properties = player.build_select(properties)
        #bulldoze
        elif choice == 6:
            properties = player.bulldoze_select(properties)
        #Trade
        elif choice == 7:
            print("Not supported yet.")
            #TODO in v2: add trade functionality
        #End turn
        else:
            print(f"{player.name}'s (Balance: ${player.balance}) turn has ended.")
            break

    return (players, properties)
