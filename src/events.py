from board import Board
from player import Player
from properties import compute_rent
from config import LUXURY_TAX, INCOME_TAX

from config import *

class Chance():
    def __init__(self):
        self.chance_cards = {
            1: {
                "description": "Advance to Boardwalk.",
                "function": move_to_space,
                "input": 39
            },
            2: {
                "description": "Advance to Go (Collect $200).",
                "function": move_to_space,
                "input": 0
            },
            3: {
                "description": "Advance to Illinois Avenue.\n If you pass Go, collect $200.",
                "function": move_to_space,
                "input": 24
            },
            4: {
                "description": "Advance to St. Charles Place.\n If you pass Go, collect $200.",
                "function": move_to_space,
                "input": 11
            },
            5: {
                "description": "Advance to the nearest Railroad.\n If unowned, you mzy buy it from the Bank.\n If owned, pay owner twice the rental price.",
                "function": move_nearest_rlrd,
                "input": None
            },
            6: {
                "description": "Advance to the nearest Railroad.\n If unowned, you mzy buy it from the Bank.\n If owned, pay owner twice the rental price.",
                "function": move_nearest_rlrd,
                "input": None
            },
            7: {
                "description": "Advance to the nearest Utility.\n If unowned, you may buy it from the Bank.\n If owned, throw dice and pay owner ten times the amount shown on the dice.",
                "function": move_nearest_util,
                "input": None
            },
            8: {
                "description": "Bank pays you dividend of $50.",
                "function": reward_player,
                "input": 50
            },
            9: {
                "description": "Get Out of Jail Free.",
                "function": add_jail_free_card,
                "input": "chance"
            },
            10: {
                "description": "Go Back 3 Spaces.",
                "function": back_three_spaces,
                "input": None
            },
            11: {
                "description": "Go to Jail.",
                "function": handle_jail_event,
                "input": None
            },
            12: {
                "description": "Make general repairs on all your property.\n For each house, pay $25. For each hotel, pay $100.",
                "function": prop_repair,
                "input": [25, 100]
            },
            13: {
                "description": "Speeding fine $15.",
                "function": penalize_player,
                "input": 15
            },
            14: {
                "description": "Take a trip to Reading Railroad.\n If you pass Go, collect $200.",
                "function": move_to_space,
                "input": 5
            },
            15: {
                "description": "You have been elected Chairman of the Board. Pay each player $50.",
                "function": pay_each_player,
                "input": 50
            },
            16: {
                "description": "Your building loan matures. Collet $150.",
                "function": reward_player,
                "input": 150
            },
        }

class CommChest():
    def __init__(self):
        self.cc_cards = {
            1: {
                "description": "Advance to Go (Collect $200).",
                "function": move_to_space,
                "input": 0
            },
            2: {
                "description": "Bank error in your favor. Collect $200.",
                "function": reward_player,
                "input": 200
            },
            3: {
                "description": "Doctor's fee. Pay $50.",
                "function": penalize_player,
                "input": 50
            },
            4: {
                "description": "From sale of stock, you get $50.",
                "function": reward_player,
                "input": 50
            },
            5: {
                "description": "Get Out of Jail Free.",
                "function": add_jail_free_card,
                "input": "cc"
            },
            6: {
                "description": "Go to Jail.",
                "function": handle_jail_event,
                "input": None
            },
            7: {
                "description": "Holiday fund matures. Receive $100.",
                "function": reward_player,
                "input": 100
            },
            8: {
                "description": "Income tax refund. Collect $20.",
                "function": reward_player,
                "input": 20
            },
            9: {
                "description": "It's your birthday. Collect $10 from every player.",
                "function": birthday,
                "input": 10
            },
            10: {
                "description": "Life insurance matures. Collect $100.",
                "function": reward_player,
                "input": 100
            },
            11: {
                "description": "Pay hospital fees of $100.",
                "function": penalize_player,
                "input": 100
            },
            12: {
                "description": "Pay school fees of $50.",
                "function": penalize_player,
                "input": 50
            },
            13: {
                "description": "Receive $25 consultancy fee.",
                "function": reward_player,
                "input": 25
            },
            14: {
                "description": "You are assessed for street repair. $40 per house. $115 per hotel.",
                "function": prop_repair,
                "input": [40, 115]
            },
            15: {
                "description": "You have won second prize in a beauty contest. Collect $10.",
                "function": reward_player,
                "input": 10
            },
            16: {
                "description": "You inherit $100.",
                "function": reward_player,
                "input": 100
            },
        }

'''
This function handles events associated with various board spaces.
- If space is property, check to see if owned by anyone. If owned by someone other than current player, pay the corresponding property rent.
- If space is not a property, handle accordingly.
'''
def process_space_event(player, players, spaces, properties, dice_val):
    chance = Chance()
    comm_chest = CommChest()
    space_name = spaces[player.position]["name"]
    break_flag = False
    #Space is a property
    if space_name in properties.names.keys():
        (players, properties, break_flag) = property_event(player, players, properties, dice_val, space_name, break_flag)

    #Space is not a property  
    elif space_name == "Go To Jail":
        (players, properties, break_flag) = handle_jail_event(player, players, properties, spaces, dice_val, break_flag)
        break_flag = True
        print(f"{player.name} is in jail.")
    elif space_name == "Luxury Tax":
        print(f"{player.name} landed on Luxury Tax and owes ${LUXURY_TAX}.")
        (pos_bal, properties) = player.pay_bank(LUXURY_TAX, properties, optional=False)
        if pos_bal == False:
            break_flag = True
    elif space_name == "Income Tax":
        print(f"{player.name} landed on Income Tax and owes ${INCOME_TAX}.")
        (pos_bal, properties) = player.pay_bank(INCOME_TAX, properties, optional=False)
        if pos_bal == False:
            break_flag = True
    elif "Chance" in space_name:
        print(f"{player.name} drew a Chance Card.")
        card_id = properties.chance_card_order.pop(0)
        print(chance.chance_cards[card_id]["description"])
        (players, properties, break_flag) = process_chance_event(player, players, properties, spaces, dice_val, break_flag, card_id, chance)
        #Don't append Get out of Jail Free card (ID 9) to the back of the card_order as card is with player until used.
        if card_id != 9:
            properties.chance_card_order.append(card_id)
    elif "Community Chest" in space_name:
        print(f"{player.name} drew a Community Chest Card.")
        card_id = properties.cc_card_order.pop(0)
        print(comm_chest.cc_cards[card_id]["description"])
        (players, properties, break_flag) = process_cc_event(player, players, properties, spaces, dice_val, break_flag, card_id, comm_chest)
        #Don't append Get out of Jail Free card (ID 5) to the back of the card_order as card is with player until used.
        if card_id != 5:
            properties.cc_card_order.append(card_id)
    else:
        pass
    #Chance
    #Community Chest

    
    return (players, properties, break_flag)

#Checks property ownership. If owned, player must pay rent. If  not owned, either buy or auction property
def property_event(player, players, properties, dice_val, space_name, break_flag):
    owner = properties.names[space_name]["owner"]
    rent = compute_rent(space_name, properties, dice_val)
    mortgaged = properties.names[space_name]["mortgaged"]
    if owner != None:
        print(f"{owner.name} owns this property.")
        if (owner != player) and (mortgaged == False):
            print(f"{player.name} owes {owner.name} ${rent} in rent.")
            (pos_bal, properties) = player.pay_player(owner, rent, properties, optional=False)
            if pos_bal == False:
                break_flag = True
        if (owner != player) and (mortgaged == True):
            print("This property is currently mortgaged.")
    else:
        price = properties.names[space_name]["price"]
        print(f"{space_name} costs ${price}.")
        print(f"You have ${player.balance}.")

        if price < player.balance:
            print("\n======================= Available Options =======================")
            print("1. Purchase Property")
            print("2. Auction Property")
            print("======================= Available Options =======================")
            while True:
                prompt = input("Would you line to buy this property? Enter the number corresponding to the above options [Default=2]: ") or 2
                if (int(prompt) == 2):
                    auction(players, space_name, properties)
                    break
                elif (int(prompt) == 1):
                    properties = player.buy_property(space_name, properties)
                    break
                else:
                    print("INVALID INPUT. Enter '1' or '2'.")
        else:
            print("You don't have enough money to buy this property.")
            auction(players, space_name, properties)
    return (players, properties, break_flag)

#Use this function for handling property events from chance cards such as advancing to railroads
def property_event_special(player, players, properties, dice_val, space_name, break_flag):
    owner = properties.names[space_name]["owner"]
    prop_type = properties.names[space_name]["type"]
    if prop_type == "utility":
        rent = 10*dice_val
    elif prop_type == "railroad":
        rent = 2*compute_rent(space_name, properties, dice_val)
    else:
        compute_rent(space_name, properties, dice_val)
    mortgaged = properties.names[space_name]["mortgaged"]
    if owner != None:
        print(f"{owner.name} owns this property.")
        if (owner != player) and (mortgaged == False):
            print(f"{player.name} owes {owner.name} ${rent} in rent.")
            (pos_bal, properties) = player.pay_player(owner, rent, properties, optional=False)
            if pos_bal == False:
                break_flag = True
        if (owner != player) and (mortgaged == True):
            print("This property is currently mortgaged.")
    else:
        price = properties.names[space_name]["price"]
        print(f"{space_name} costs ${price}.")
        print(f"You have ${player.balance}.")

        if price < player.balance:
            print("\n======================= Available Options =======================")
            print("1. Purchase Property")
            print("2. Auction Property")
            print("======================= Available Options =======================")
            while True:
                prompt = input("Would you line to buy this property? Enter the number corresponding to the above options [Default=2]: ") or 2
                if (int(prompt) == 2):
                    auction(players, space_name, properties)
                    break
                elif (int(prompt) == 1):
                    properties = player.buy_property(space_name, properties)
                    break
                else:
                    print("INVALID INPUT. Enter '1' or '2'.")
        else:
            print("You don't have enough money to buy this property.")
            auction(players, space_name, properties)
    return (players, properties, break_flag)


def auction(players, property_name, properties):
    print("=" * 131)
    print(f"Commencing Auction for {property_name}.")
    print("=" * 131)
    auction_winner = None
    folded = [] #Keep track of players who fold
    min_bid = 1
    while len(folded) < len(players) - 1:
        for player in players:
            if (len(folded) >= len(players) - 1) and (min_bid > 1):
                break
            if player not in folded:
                print("\n======================= Available Options =======================")
                print("1. Bid")
                print("2. Fold")
                print("======================= Available Options =======================")
                print(f"{player.name}'s turn to bid.")
                while True:
                    if (min_bid < player.balance) and (player.bankrupt == False):
                        prompt = input(f"Would you like to increase your bid? (Minimum Bid: ${min_bid}) [Default=2]: ") or 2
                        if (int(prompt) == 2):
                            print(f"{player.name} has folded.")
                            folded.append(player)
                            break
                        elif (int(prompt) == 1):
                            while True:
                                prompt = input(f"Enter bid amount >={min_bid}. [Default={min_bid}]: ") or min_bid
                                try:
                                    bid = int(prompt)
                                    if min_bid <= bid < player.balance:
                                        print(f"{player.name} has bid ${bid} on {property_name}.")
                                        min_bid = bid + 1
                                        break
                                    elif bid >= player.balance:
                                        print(f"You only have {player.balance}. Enter an amount smaller than this.")
                                    else:
                                        print(f"INVALID INPUT. Please enter a number >= {min_bid}")
                                except ValueError:
                                    print(f"INVALID INPUT. Please enter a number >= {min_bid}")
                            break
                        else:
                            print("INVALID INPUT. Enter '1' or '2'.")
                    else:
                        folded.append(player)
                        break
    #Find winner
    for player in players:
        if player not in folded:
            auction_winner = player
            sold_price = min_bid - 1
            player.buy_property(property_name, properties, sold_price)
            print(f"Congratulations {player.name}. You've purchased {property_name} for ${sold_price}.")
    if auction_winner == None:
        print(f"No one bidded on the property. {property_name} remains unsold.")

#Handles chance event of moving player to the nearest railroad
def move_nearest_rlrd(player, players, properties, spaces, dice_val, break_flag, placeholder):
    player_pos = player.position
    for space in spaces.keys():
        if player_pos == space:
            passgo = player.move_player(1)
            space_name = spaces[player_pos]["name"]
            while "Railroad" not in space_name:
                passgo = player.move_player(1)
                player_pos = player.position
                space_name = spaces[player_pos]["name"]
            if passgo == True:
                player.add_balance(GO)
            (players, properties, break_flag) = property_event_special(player, players, properties, dice_val, space_name, break_flag)
            break
    return (players, properties, break_flag)

def move_nearest_util(player, players, properties, spaces, dice_val, break_flag, placeholder):
    player_pos = player.position
    for space in spaces.keys():
        if player_pos == space:
            passgo = player.move_player(1)
            space_name = spaces[player_pos]["name"]
            while ("Electric" not in space_name) and ("Water" not in space_name):
                print(space_name)
                passgo = player.move_player(1)
                player_pos = player.position
                space_name = spaces[player_pos]["name"]
            if passgo == True:
                player.add_balance(GO)
            (players, properties, break_flag) = property_event_special(player, players, properties, dice_val, space_name, break_flag)
            break
    return (players, properties, break_flag)

def reward_player(player, players, properties, spaces, dice_val, break_flag, reward):
    player.add_balance(reward)
    return (players, properties, break_flag)

def move_to_space(player, players, properties, spaces, dice_val, break_flag, space_id):
    if player.position >= space_id:
        player.add_balance(GO)
        print(f"{player.name} passed Go and received $200.")
    player.position = space_id
    (players, properties, break_flag) = process_space_event(player, players, spaces, properties, dice_val)
    return (players, properties, break_flag)

def back_three_spaces(player, players, properties, spaces, dice_val, break_flag, placeholder):
    player.position -= 3
    (players, properties, break_flag) = process_space_event(player, players, spaces, properties, dice_val)
    return (players, properties, break_flag)

def prop_repair(player, players, properties, spaces, dice_val, break_flag, amts):
    num_houses = 0
    num_hotels = 0
    for prop in player.owned:
        num_houses += properties.names[prop]["num_houses"]
        num_hotels += properties.names[prop]["num_hotels"]
    amt = amts[0]*num_houses + amts[1]*num_hotels
    print(f"{player.name} owes ${amt} to the bank for property repairs.")
    if amt > 0:
        (pos_bal, properties) = player.pay_bank(amt, properties, optional=False)
        if pos_bal == False:
            break_flag = True
    return (players, properties, break_flag)

def penalize_player(player, players, properties, spaces, dice_val, break_flag, penalty):
    print(f"{player.name} owes ${penalty} to the bank.")
    (pos_bal, properties) = player.pay_bank(penalty, properties, optional=False)
    if pos_bal == False:
        break_flag = True
    return (players, properties, break_flag)

def pay_each_player(player, players, properties, spaces, dice_val, break_flag, amt):
    amt_owed = 0
    for sub_player in players:
        if (sub_player != player) and (sub_player.bankrupt == False):
            print(f"{sub_player.name} received ${amt}.")
            sub_player.add_balance(amt)
            amt_owed += 50
    print(f"{player.name} owes ${amt_owed} to the bank.")
    #While there's more nuanced rules on how to handle the event of a bankruptcy from this event, for now I handle it as a bankruptcy by the bank, hence the pay_bank call instead of pay_player
    (pos_bal, properties) = player.pay_bank(amt_owed, properties, optional=False)
    if pos_bal == False:
        break_flag = True
    return (players, properties, break_flag)

def birthday(player, players, properties, spaces, dice_val, break_flag, amt):
    for sub_player in players:
        if (sub_player != player) and (sub_player.bankrupt == False):
            print(f"{sub_player.name} owes {player.name} ${amt}.")
            (pos_bal, properties) = sub_player.pay_player(player, amt, properties, optional=False)
            if pos_bal == False:
                break_flag = True
    return (players, properties, break_flag)

def handle_jail_event(player, players, properties, spaces, dice_val, break_flag, placeholder=None):
    player.move_to_jail()
    return (players, properties, break_flag)

def add_jail_free_card(player, players, properties, spaces, dice_val, break_flag, group):
    player.num_jail_free_cards += 1
    if group == "chance":
        player.has_chance_jf_card = True
    if group == "cc":
        player.has_cc_jf_card = True
    return (players, properties, break_flag)

def process_chance_event(player, players, properties, spaces, dice_val, break_flag, card_id, chance):
    optional_input = chance.chance_cards[card_id]["input"]
    (players, properties, break_flag) = chance.chance_cards[card_id]["function"](player, players, properties, spaces, dice_val, break_flag, optional_input)
    return (players, properties, break_flag)

def process_cc_event(player, players, properties, spaces, dice_val, break_flag, card_id, comm_chest):
    optional_input = comm_chest.cc_cards[card_id]["input"]
    (players, properties, break_flag) = comm_chest.cc_cards[card_id]["function"](player, players, properties, spaces, dice_val, break_flag, optional_input)
    return (players, properties, break_flag)
