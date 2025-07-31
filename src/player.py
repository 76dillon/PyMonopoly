from config import NUM_SPACES
from properties import (
    compute_rent, 
    complete_set, 
    check_mortgage_eligibility, 
    check_build_eligibility, 
    check_bulldoze_eligibility,
)

class Player():
    def __init__(self, name):
        self.name = name
        self.balance = 1500
        self.asset_worth = 0
        self.position = 0
        self.owned = []
        self.num_jail_free_cards = 0
        self.num_jail_turns = 0
        self.has_chance_jf_card = False
        self.has_cc_jf_card = False
        self.jail = False
        self.board_location_id = 0
        self.bankrupt = False

    '''
    This method moves player position down the board by a specified number of spaces.
    Board has spaces with IDs between 0 and 39. If after adding to the current position, pos > 39,
    subtract the number of spaces from it to obtain the new player position.
    '''
    def move_player(self, move_spaces):
        passgo = False
        if (self.position + move_spaces <= NUM_SPACES - 1):
            self.position += move_spaces
        else:
            #This means the player passed Go
            self.position = (self.position+move_spaces) - NUM_SPACES
            passgo = True
        return passgo
    
    #This method simply updates the player position to a desired space anywhere on the board between 0 and 39.
    def update_position(self, space):
        self.position = space

    #This method moves a player into jail and sets the applicable jail status flags for the player object
    def move_to_jail(self):
        prompt = input("Go directly to Jail. Do not stop. Do not pass Go, do not collect $200. Press Enter to continue: ")
        self.position = 10
        self.jail = True
        self.num_jail_turns = 1
    
    def release_from_jail(self):
        self.jail = False
        self.num_jail_turns = 0
    
    def add_balance(self, amt):
        self.balance += amt

    def deduct_balance(self, amt, optional=True):
        if (amt < self.balance):
            self.balance -= amt
            return True
        else:
            if optional == False:
                return False
            else:
                print(f"TRANSACTION DECLINED! Insufficient funds.")
                return True
    
    def bankruptcy_status(self, amt_owed):
        if self.balance + self.asset_worth <= amt_owed:
            print(f"{self.name} doesn't have sufficient funds or assets to pay their debt.")
            print(f"{self.name} is bankrupt!")
            return True
        else:
            return False

    def handle_bankruptcy_by_player(self, other, amt_owed, properties):
        self.bankrupt = True
        print(f"{self.name} doesn't have sufficient funds or assets to pay their debt.")
        print(f"{self.name} is bankrupt!")
        #Transfer assets to other player
        cash_transfer = self.balance
        for prop in self.owned:
            num_houses = properties.names[prop]["num_houses"]
            num_hotels = properties.names[prop]["num_hotels"]
            build_cost = properties.names[prop]["build_cost"]
            base_price = properties.names[prop]["price"]
            prop_type = properties.names[prop]["type"]
            mortgage_val = base_price // 2
            if (prop_type != "railroad") and (prop_type != "utility"):
                house_val = build_cost // 2
                cash_transfer += num_houses + (5*num_hotels)
                cash_transfer += mortgage_val
                properties.names[prop]["num_houses"] = 0
                properties.names[prop]["num_hotels"] = 0
            properties.names[prop]["mortgaged"] = True
            properties.names[prop]["owner"] = other
            other.owned.append(prop)
            if self.num_jail_free_cards > 0:
                other.num_jail_free_cards += self.num_jail_free_cards
                print(f"{other.name} received {self.num_jail_free_cards} Get Out of Jail Free card(s).")
                self.num_jail_free_cards = 0
                if (self.has_chance_jf_card == True) and (self.has_cc_jf_card == True):
                    self.has_chance_jf_card = False
                    self.has_cc_jf_card = False
                    other.has_chance_jf_card = True
                    other.has_cc_jf_card = True
                elif (self.has_chance_jf_card == True) and (self.has_cc_jf_card == False):
                    self.has_chance_jf_card = False
                    other.has_chance_jf_card = True
                else:
                    self.has_cc_jf_card = False
                    other.has_cc_jf_card = True
            other.add_balance(cash_transfer)
            self.balance = 0
            print(f"{prop} transferred to {other.name}.")
        self.owned = []
        self.asset_worth = 0
        print(f"${cash_transfer} transferred to {other.name}.")
    
        return properties

    def handle_bankruptcy_by_bank(self, amt_owed, properties):
        self.bankrupt = True
        print(f"{self.name} doesn't have sufficient funds or assets to pay their debt.")
        print(f"{self.name} is bankrupt!")
        #Place player property assets back on market. Reset mortgage status, owner, num_houses, and num_hotels to initial values
        #TODO in v2, implement auction-off of players assets to remaining players if more than one remaining player
        for prop in self.owned:
            properties.names[prop]["num_houses"] = 0
            properties.names[prop]["num_hotels"] = 0
            properties.names[prop]["mortgaged"] = False
            properties.names[prop]["owner"] = None
            print(f"{prop} is back on the market.")
        self.owned = []
        self.asset_worth = 0
        self.num_jail_free_cards = 0
        if (self.has_chance_jf_card == True) and (self.has_cc_jf_card == True):
            properties.chance_card_order.append(9)
            properties.cc_card_order.append(5)
            self.has_chance_jf_card = False
            self.has_cc_jf_card = False
        elif (player.has_chance_jf_card == True) and (self.has_cc_jf_card == False):
            self.has_chance_jf_card = False
            properties.chance_card_order.append(9)
        else:
            self.has_cc_jf_card = False
            properties.cc_card_order.append(5)
        return properties

    def handle_debt_to_player(self, other, amt_owed, properties):
        #Prompt player to sell off assets via mortgage or bulldozing until debt paid.
        num_options = 2
        while self.balance <= amt_owed:
            print("\n======================= Available Options =======================")
            print("1. Mortgage Property")
            print("2. Bulldoze")
            print("=================================================================")
            print(f"{self.name} owes {other.name} ${amt_owed}, but {self.name} only has ${self.balance}.")
            print(f"{self.name} must mortgage or bulldoze property to pay debt.")
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
                properties = self.mortgage_select(properties)
            elif choice == 2:
                properties = self.bulldoze_select(properties)
            else:
                print("Something went wrong.")
        self.deduct_balance(amt_owed)
        other.add_balance(amt_owed)
        print(f"{self.name} paid {other.name} ${amt_owed}.")

        return properties

    def handle_debt_to_bank(self, amt_owed, properties):
        #Prompt player to sell off assets via mortgage or bulldozing until debt paid.
        num_options = 2
        while self.balance <= amt_owed:
            print("\n======================= Available Options =======================")
            print("1. Mortgage Property")
            print("2. Bulldoze")
            print("=================================================================")
            print(f"{self.name} owes the bank ${amt_owed}, but {self.name} only has ${self.balance}.")
            print(f"{self.name} must mortgage or bulldoze property to pay debt.")
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
                properties = self.mortgage_select(properties)
            elif choice == 2:
                properties = self.bulldoze_select(properties)
            else:
                print("Something went wrong.")
        self.deduct_balance(amt_owed)
        print(f"{self.name} paid the bank ${amt_owed}.")

        return properties

    def buy_property(self, property_name, properties, auction_price=None):
        base_price = properties.names[property_name]["price"]
        if auction_price == None:
            price = base_price
        else:
            price = auction_price
        enough_funds = self.deduct_balance(price)
        if enough_funds == True:
            properties.names[property_name]["owner"] = self
            self.owned.append(property_name)
            self.asset_worth += base_price // 2
            print(f"{self.name} has successfully purchased {property_name}.")
        return properties
    
    def mortgage_property(self, property_name, properties):
        base_price = properties.names[property_name]["price"]
        properties.names[property_name]["mortgaged"] = True
        mortgage_val = base_price // 2
        self.add_balance(mortgage_val)
        self.asset_worth -= mortgage_val
        print(f"{self.name} mortgaged {property_name} and received ${mortgage_val}.")
        return properties
    
    #Unmortgage price = mortgage_price + 10%
    def unmortgage_property(self, property_name, properties):
        base_price = properties.names[property_name]["price"]
        mortgage_val = base_price // 2
        unmortgage_price = mortgage_val + int(0.10*mortgage_val)
        if self.balance > unmortgage_price:
            self.deduct_balance(unmortgage_price)
            properties.names[property_name]["mortgaged"] = False
            self.asset_worth += unmortgage_price
            print(f"{self.name} paid ${unmortgage_price} to unmortgage {property_name}.")
        else:
            print(f"TRANSACTION DECLINED! Insufficient funds.")
        return properties
    
    def build(self, property_name, properties):
        num_houses = properties.names[property_name]["num_houses"]
        num_hotels = properties.names[property_name]["num_hotels"]
        build_cost = properties.names[property_name]["build_cost"]
        house_val = build_cost // 2
        if self.balance > build_cost:
            self.deduct_balance(build_cost)
            self.asset_worth += house_val
            if (num_houses < 4) and (num_hotels == 0):
                properties.names[property_name]["num_houses"] += 1
                print(f"{self.name} paid ${build_cost} to build a house on {property_name}.")
            else:
                properties.names[property_name]["num_hotels"] += 1
                properties.names[property_name]["num_houses"] = 0
                print(f"{self.name} paid ${build_cost} to build a hotel on {property_name}.")
        else:
            print(f"TRANSACTION DECLINED! Insufficient funds.")
        return properties
            
    def bulldoze(self, property_name, properties):
        num_houses = properties.names[property_name]["num_houses"]
        num_hotels = properties.names[property_name]["num_hotels"]
        build_cost = properties.names[property_name]["build_cost"]
        house_val = build_cost // 2
        self.add_balance(house_val)
        self.asset_worth -= house_val
        if (num_hotels) == 1:
            properties.names[property_name]["num_houses"] = 4
            properties.names[property_name]["num_hotels"] = 0
            print(f"{self.name} bulldozed a hotel and received ${house_val}.")
        if (num_houses) > 0:
            properties.names[property_name]["num_houses"] -= 1
            print(f"{self.name} bulldozed a house and received ${house_val}.")
        return properties

    def pay_player(self, other, amt, properties, optional=True):
        if optional == True:
            bal_before = self.balance
            pos_bal = self.deduct_balance(amt, optional=True)
            bal_after = self.balance
            if bal_before > bal_after:
                print(f"{self.name} paid {other.name} ${amt}.")
        else:
            pos_bal = self.deduct_balance(amt, optional=False)
            if pos_bal == True:
                other.add_balance(amt)
                print(f"{self.name} paid {other.name} ${amt}.")
            else:
                if pos_bal == False:
                    is_bankrupt = self.bankruptcy_status(amt)
                    if is_bankrupt == False:
                        properties = self.handle_debt_to_player(other, amt, properties)
                        pos_bal = True
                    else:
                        properties = self.handle_bankruptcy_by_player(other, amt, properties)
        return (pos_bal, properties)

    def pay_bank(self, amt, properties, optional=True):
        if optional == True:
            bal_before = self.balance
            pos_bal = self.deduct_balance(amt, optional=True)
            bal_after = self.balance
            if bal_before > bal_after:
                print(f"{self.name} paid the bank ${amt}.")
        else:
            pos_bal = self.deduct_balance(amt, optional=False)
            if pos_bal == True:
                print(f"{self.name} paid the bank ${amt}.")
            else:
                if pos_bal == False:
                    is_bankrupt = self.bankruptcy_status(amt)
                    if is_bankrupt == False:
                        properties = self.handle_debt_to_bank(amt, properties)
                        pos_bal = True
                    else:
                        properties = self.handle_bankruptcy_by_bank(amt, properties)

        return (pos_bal, properties)
    
    def query_player_info(self, properties):
        owned_prop_str = ""
        for prop in self.owned:
            owned_prop_str += "- " + prop
            mortgage_status = properties.names[prop]["mortgaged"]
            if mortgage_status == True:
                owned_prop_str += " (mortgaged)"
            owned_prop_str += "\n"
        print("\n======================= Player Info =======================")
        print(f"Player Name: {self.name}")
        print(f"Balance: ${self.balance}")
        print(f"Number of Get Out of Jail Free Cards: {self.num_jail_free_cards}")
        print("Properties Owned: ")
        print(owned_prop_str)
        print("===========================================================")
        prompt = input("Press Enter to go back: ")

    def query_prop_info(self, properties):
        print("=" * 90)
        print("       Property Name         | Houses | Hotels |  Prop. Type  |  Mortgaged  | Rent Cost |")
        print("-" * 90)
        for prop in self.owned:
            num_houses = str(properties.names[prop]["num_houses"])
            num_hotels = str(properties.names[prop]["num_hotels"])
            prop_type = str(properties.names[prop]["type"])
            mortgaged = str(properties.names[prop]["mortgaged"])
            rent_cost = "$" + str(compute_rent(prop, properties, 10)) #dummy dice_val of 10 here
            if prop_type == "utility":
                if complete_set(prop, properties) == True:
                    rent_cost = "10xdice"
                else:
                    rent_cost = "4xdice"
            print(prop.rjust(29) + "|" +  num_houses.rjust(8) + "|" + num_hotels.rjust(8) + "|" + prop_type.rjust(14) + "|" + mortgaged.rjust(13) + "|" + rent_cost.rjust(11) + "|")
        print("=" * 90)
        prompt = input("Press Enter to go back: ")
    
    #List properties eligible for mortgage and prompt user to make selection.
    def mortgage_select(self, properties):
        while True:
            num_options = 1
            print("\n======================= Properties to Mortgage =======================")
            mortgage_props = []
            for prop in self.owned:
                eligible = check_mortgage_eligibility(prop, properties)
                if eligible == True:
                    base_price = properties.names[prop]["price"]
                    mortgage_val = base_price // 2
                    print(f"{num_options}. {prop} (Mortgage Value: ${mortgage_val})")
                    mortgage_props.append(prop)
                    num_options += 1
            print(f"{num_options}. Go Back")
            print("======================================================================")
            try:
                choice = int(input(f"Enter the number corresponding to the above options 1 - {num_options}: ") or num_options)
                if 1 <= choice < num_options:
                    properties = self.mortgage_property(mortgage_props[choice - 1], properties)
                elif choice == num_options:
                    break
                else:
                    print(f"INVALID INPUT. Please choose a number between 1 and {num_options}.")
            except ValueError:
                print(f"INVALID INPUT. Please choose a number between 1 and {num_options}.")

        return properties


    #List properties eligible for unmortgage and prompt user to make selection.
    def unmortgage_select(self, properties):
        while True:
            num_options = 1
            print("\n======================= Properties to Unmortgage =======================")
            unmortgage_props = []
            for prop in self.owned:
                if (properties.names[prop]["mortgaged"] == True):
                    base_price = properties.names[prop]["price"]
                    mortgage_val = base_price // 2
                    unmortgage_price = mortgage_val + int(0.10*mortgage_val)
                    if self.balance > unmortgage_price:
                        print(f"{num_options}. {prop} (Unmortgage Price: ${unmortgage_price})")
                        num_options += 1
                        unmortgage_props.append(prop)
            print(f"{num_options}. Go Back")
            print("======================================================================")
            try:
                choice = int(input(f"Enter the number corresponding to the above options 1 - {num_options}: ") or num_options)
                if 1 <= choice < num_options:
                    properties = self.unmortgage_property(unmortgage_props[choice - 1], properties)
                elif choice == num_options:
                    break
                else:
                    print(f"INVALID INPUT. Please choose a number between 1 and {num_options}.")
            except ValueError:
                print(f"INVALID INPUT. Please choose a number between 1 and {num_options}.")

        return properties

    def build_select(self, properties):
        while True:
            num_options = 1
            print("\n=============================== Properties to Build ===============================")
            build_props = []
            for prop in self.owned:
                eligible = check_build_eligibility(prop, properties)
                build_cost = properties.names[prop]["build_cost"]
                if (eligible == True) and (self.balance > build_cost):
                    num_houses = properties.names[prop]["num_houses"]
                    num_hotels = properties.names[prop]["num_hotels"]
                    print(f"{num_options}. {prop} (Build Cost: ${build_cost}, Houses: {num_houses}, Hotels: {num_hotels})")
                    build_props.append(prop)
                    num_options += 1
            print(f"{num_options}. Go Back")
            print("====================================================================================")

            try:
                choice = int(input(f"Enter the number corresponding to the above options 1 - {num_options}: ") or num_options)
                if 1 <= choice < num_options:
                    properties = self.build(build_props[choice - 1], properties)
                elif choice == num_options:
                    break
                else:
                    print(f"INVALID INPUT. Please choose a number between 1 and {num_options}.")
            except ValueError:
                print(f"INVALID INPUT. Please choose a number between 1 and {num_options}.")
            
        return properties

    def bulldoze_select(self, properties):
        while True:
            num_options = 1
            print("\n=============================== Properties to Bulldoze ===============================")
            bulldoze_props = []
            for prop in self.owned:
                eligible = check_bulldoze_eligibility(prop, properties)
                build_cost = properties.names[prop]["build_cost"]
                house_val = build_cost // 2
                if (eligible == True):
                    num_houses = properties.names[prop]["num_houses"]
                    num_hotels = properties.names[prop]["num_hotels"]
                    print(f"{num_options}. {prop} (Return Value: ${house_val}, Houses: {num_houses}, Hotels: {num_hotels})")
                    bulldoze_props.append(prop)
                    num_options += 1
            print(f"{num_options}. Go Back")
            print("====================================================================================")

            try:
                choice = int(input(f"Enter the number corresponding to the above options 1 - {num_options}: ") or num_options)
                if 1 <= choice < num_options:
                    properties = self.bulldoze(bulldoze_props[choice - 1], properties)
                elif choice == num_options:
                    break
                else:
                    print(f"INVALID INPUT. Please choose a number between 1 and {num_options}.")
            except ValueError:
                print(f"INVALID INPUT. Please choose a number between 1 and {num_options}.")
            
        return properties



    

