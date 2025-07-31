import random
#mortgage value = price/2

class Properties():

    def __init__(self):
        self.names = {
            "Mediterranean Ave": {
                "price": 60,
                "mortgaged": False,
                "base_rent": 2,
                "one_house_cost": 10,
                "two_house_cost": 30,
                "three_house_cost": 90,
                "four_house_cost": 160,
                "hotel_cost": 250,
                "num_houses": 0,
                "num_hotels": 0,
                "type": "brown",
                "build_cost": 50,
                "owner": None
            },
            "Baltic Ave": {
                "price": 60,
                "mortgaged": False,
                "base_rent": 4,
                "one_house_cost": 20,
                "two_house_cost": 60,
                "three_house_cost": 180,
                "four_house_cost": 320,
                "hotel_cost": 450,
                "num_houses": 0,
                "num_hotels": 0,
                "type": "brown",
                "build_cost": 50,
                "owner": None
            },
            "Oriental Ave": {
                "price": 100,
                "mortgaged": False,
                "base_rent": 6,
                "one_house_cost": 30,
                "two_house_cost": 90,
                "three_house_cost": 270,
                "four_house_cost": 400,
                "hotel_cost": 550,
                "num_houses": 0,
                "num_hotels": 0,
                "type": "turquoise",
                "build_cost": 50,
                "owner": None
            },
            "Vermont Ave": {
                "price": 100,
                "mortgaged": False,
                "base_rent": 6,
                "one_house_cost": 30,
                "two_house_cost": 90,
                "three_house_cost": 270,
                "four_house_cost": 400,
                "hotel_cost": 550,
                "num_houses": 0,
                "num_hotels": 0,
                "type": "turquoise",
                "build_cost": 50,
                "owner": None
            },
            "Connecticut Ave": {
                "price": 120,
                "mortgaged": False,
                "base_rent": 8,
                "one_house_cost": 40,
                "two_house_cost": 100,
                "three_house_cost": 300,
                "four_house_cost": 450,
                "hotel_cost": 600,
                "num_houses": 0,
                "num_hotels": 0,
                "type": "turquoise",
                "build_cost": 50,
                "owner": None
            },
            "St Charles Pl": {
                "price": 140,
                "mortgaged": False,
                "base_rent": 10,
                "one_house_cost": 50,
                "two_house_cost": 150,
                "three_house_cost": 450,
                "four_house_cost": 625,
                "hotel_cost": 750,
                "num_houses": 0,
                "num_hotels": 0,
                "type": "maroon",
                "build_cost": 100,
                "owner": None
            },
            "States Ave": {
                "price": 140,
                "mortgaged": False,
                "base_rent": 10,
                "one_house_cost": 50,
                "two_house_cost": 150,
                "three_house_cost": 450,
                "four_house_cost": 625,
                "hotel_cost": 750,
                "num_houses": 0,
                "num_hotels": 0,
                "type": "maroon",
                "build_cost": 100,
                "owner": None
            },
            "Virginia Ave": {
                "price": 160,
                "mortgaged": False,
                "base_rent": 12,
                "one_house_cost": 60,
                "two_house_cost": 180,
                "three_house_cost": 500,
                "four_house_cost": 700,
                "hotel_cost": 900,
                "num_houses": 0,
                "num_hotels": 0,
                "type": "maroon",
                "build_cost": 100,
                "owner": None
            },
            "St James Pl": {
                "price": 180,
                "mortgaged": False,
                "base_rent": 14,
                "one_house_cost": 70,
                "two_house_cost": 200,
                "three_house_cost": 550,
                "four_house_cost": 750,
                "hotel_cost": 950,
                "num_houses": 0,
                "num_hotels": 0,
                "type": "orange",
                "build_cost": 100,
                "owner": None
            },
            "Tennessee Ave": {
                "price": 180,
                "mortgaged": False,
                "base_rent": 14,
                "one_house_cost": 70,
                "two_house_cost": 200,
                "three_house_cost": 550,
                "four_house_cost": 750,
                "hotel_cost": 950,
                "num_houses": 0,
                "num_hotels": 0,
                "type": "orange",
                "build_cost": 100,
                "owner": None
            },
            "New York Ave": {
                "price": 200,
                "mortgaged": False,
                "base_rent": 16,
                "one_house_cost": 80,
                "two_house_cost": 220,
                "three_house_cost": 600,
                "four_house_cost": 800,
                "hotel_cost": 1000,
                "num_houses": 0,
                "num_hotels": 0,
                "type": "orange",
                "build_cost": 100,
                "owner": None
            },
            "Kentucky Ave": {
                "price": 220,
                "mortgaged": False,
                "base_rent": 18,
                "one_house_cost": 90,
                "two_house_cost": 250,
                "three_house_cost": 700,
                "four_house_cost": 875,
                "hotel_cost": 1050,
                "num_houses": 0,
                "num_hotels": 0,
                "type": "red",
                "build_cost": 150,
                "owner": None
            },
            "Indiana Ave": {
                "price": 220,
                "mortgaged": False,
                "base_rent": 18,
                "one_house_cost": 90,
                "two_house_cost": 250,
                "three_house_cost": 700,
                "four_house_cost": 875,
                "hotel_cost": 1050,
                "num_houses": 0,
                "num_hotels": 0,
                "type": "red",
                "build_cost": 150,
                "owner": None
            },
            "Illinois Ave": {
                "price": 240,
                "mortgaged": False,
                "base_rent": 20,
                "one_house_cost": 100,
                "two_house_cost": 300,
                "three_house_cost": 750,
                "four_house_cost": 925,
                "hotel_cost": 1100,
                "num_houses": 0,
                "num_hotels": 0,
                "type": "red",
                "build_cost": 150,
                "owner": None
            },
            "Atlantic Ave": {
                "price": 260,
                "mortgaged": False,
                "base_rent": 22,
                "one_house_cost": 110,
                "two_house_cost": 330,
                "three_house_cost": 800,
                "four_house_cost": 975,
                "hotel_cost": 1150,
                "num_houses": 0,
                "num_hotels": 0,
                "type": "yellow",
                "build_cost": 150,
                "owner": None
            },
            "Ventnor Ave": {
                "price": 260,
                "mortgaged": False,
                "base_rent": 22,
                "one_house_cost": 110,
                "two_house_cost": 330,
                "three_house_cost": 800,
                "four_house_cost": 975,
                "hotel_cost": 1150,
                "num_houses": 0,
                "num_hotels": 0,
                "type": "yellow",
                "build_cost": 150,
                "owner": None
            },
            "Marvin Gardens": {
                "price": 280,
                "mortgaged": False,
                "base_rent": 24,
                "one_house_cost": 120,
                "two_house_cost": 360,
                "three_house_cost": 850,
                "four_house_cost": 1025,
                "hotel_cost": 1200,
                "num_houses": 0,
                "num_hotels": 0,
                "type": "yellow",
                "build_cost": 150,
                "owner": None
            },
            "Pacific Ave": {
                "price": 300,
                "mortgaged": False,
                "base_rent": 26,
                "one_house_cost": 130,
                "two_house_cost": 390,
                "three_house_cost": 900,
                "four_house_cost": 1100,
                "hotel_cost": 1275,
                "num_houses": 0,
                "num_hotels": 0,
                "type": "green",
                "build_cost": 200,
                "owner": None
            },
            "N Carolina Ave": {
                "price": 300,
                "mortgaged": False,
                "base_rent": 26,
                "one_house_cost": 130,
                "two_house_cost": 390,
                "three_house_cost": 900,
                "four_house_cost": 1100,
                "hotel_cost": 1275,
                "num_houses": 0,
                "num_hotels": 0,
                "type": "green",
                "build_cost": 200,
                "owner": None
            },
            "Penn Ave": {
                "price": 320,
                "mortgaged": False,
                "base_rent": 28,
                "one_house_cost": 150,
                "two_house_cost": 450,
                "three_house_cost": 1000,
                "four_house_cost": 1200,
                "hotel_cost": 1400,
                "num_houses": 0,
                "num_hotels": 0,
                "type": "green",
                "build_cost": 200,
                "owner": None
            },
            "Park Pl": {
                "price": 350,
                "mortgaged": False,
                "base_rent": 35,
                "one_house_cost": 175,
                "two_house_cost": 500,
                "three_house_cost": 1100,
                "four_house_cost": 1300,
                "hotel_cost": 1500,
                "num_houses": 0,
                "num_hotels": 0,
                "type": "blue",
                "build_cost": 200,
                "owner": None
            },
            "Boardwalk": {
                "price": 400,
                "mortgaged": False,
                "base_rent": 50,
                "one_house_cost": 200,
                "two_house_cost": 600,
                "three_house_cost": 1400,
                "four_house_cost": 1700,
                "hotel_cost": 2000,
                "num_houses": 0,
                "num_hotels": 0,
                "type": "blue",
                "build_cost": 200,
                "owner": None
            },
            "Reading Railroad": {
                "price": 200,
                "mortgaged": False,
                "base_rent": 25,
                "one_house_cost": None,
                "two_house_cost": None,
                "three_house_cost": None,
                "four_house_cost": None,
                "hotel_cost": None,
                "num_houses": 0,
                "num_hotels": 0,
                "type": "railroad",
                "build_cost": None,
                "owner": None
            },
            "Penn Railroad": {
                "price": 200,
                "mortgaged": False,
                "base_rent": 25,
                "one_house_cost": None,
                "two_house_cost": None,
                "three_house_cost": None,
                "four_house_cost": None,
                "hotel_cost": None,
                "num_houses": 0,
                "num_hotels": 0,
                "type": "railroad",
                "build_cost": None,
                "owner": None
            },
            "B&O Railroad": {
                "price": 200,
                "mortgaged": False,
                "base_rent": 25,
                "one_house_cost": None,
                "two_house_cost": None,
                "three_house_cost": None,
                "four_house_cost": None,
                "hotel_cost": None,
                "num_houses": 0,
                "num_hotels": 0,
                "type": "railroad",
                "build_cost": None,
                "owner": None
            },
            "Short Line Railroad": {
                "price": 200,
                "mortgaged": False,
                "base_rent": 25,
                "one_house_cost": None,
                "two_house_cost": None,
                "three_house_cost": None,
                "four_house_cost": None,
                "hotel_cost": None,
                "num_houses": 0,
                "num_hotels": 0,
                "type": "railroad",
                "build_cost": None,
                "owner": None
            },
            "Electric Co": {
                "price": 150,
                "mortgaged": False,
                "base_rent": None,
                "one_house_cost": None,
                "two_house_cost": None,
                "three_house_cost": None,
                "four_house_cost": None,
                "hotel_cost": None,
                "num_houses": 0,
                "num_hotels": 0,
                "type": "utility",
                "build_cost": None,
                "owner": None
            },
            "Water Works": {
                "price": 150,
                "mortgaged": False,
                "base_rent": None,
                "one_house_cost": None,
                "two_house_cost": None,
                "three_house_cost": None,
                "four_house_cost": None,
                "hotel_cost": None,
                "num_houses": 0,
                "num_hotels": 0,
                "type": "utility",
                "build_cost": None,
                "owner": None
            },
        }

        self.chance_card_order = list(range(1, 17))
        self.cc_card_order = [9]
        #self.cc_card_order = list(range(1, 17))
        random.shuffle(self.chance_card_order)
        #random.shuffle(self.cc_card_order)

#Computes the rent for a player landing on someone else's property.
def compute_rent(property_name, properties, dice_val):
    prop_type = properties.names[property_name]["type"]
    base_rent = properties.names[property_name]["base_rent"]
    owner = properties.names[property_name]["owner"]
    if prop_type == "railroad":
        num_owned = 0
        for item in properties.names.keys():
            if properties.names[item]["type"] == prop_type:
                if properties.names[item]["owner"] == owner:
                    num_owned += 1
        if num_owned == 1:
            rent = 25
        elif num_owned == 2:
            rent = 50
        elif num_owned == 3:
            rent = 100
        elif num_owned == 4:
            rent = 200
        else:
            raise Exception("Something went wrong. Should own at least 1 and at most 4")
    elif prop_type == "utility":
        if properties.names["Electric Co"]["owner"] == properties.names["Water Works"]["owner"]:
            rent = 10*dice_val
        else:
            rent = 4*dice_val
    else:
        num_houses = properties.names[property_name]["num_houses"]
        num_hotels = properties.names[property_name]["num_hotels"]
        if (num_houses == 0) and (num_hotels == 0):
            is_complete = complete_set(property_name, properties)
            if is_complete == True:
                rent = base_rent * 2
            else:
                rent = base_rent
        elif (num_houses == 1) and (num_hotels == 0):
            rent = properties.names[property_name]["one_house_cost"]
        elif (num_houses == 2) and (num_hotels == 0):
            rent = properties.names[property_name]["two_house_cost"]
        elif (num_houses == 3) and (num_hotels == 0):
            rent = properties.names[property_name]["three_house_cost"]
        elif (num_houses == 4) and (num_hotels == 0):
            rent = properties.names[property_name]["four_house_cost"]
        elif (num_houses == 0) and (num_hotels == 1):
            rent = properties.names[property_name]["hotel_cost"]
        else: 
            raise Exception("Invalid number of houses and hotels. Something went wrong.")
    return rent

#This function returns a boolean to check if the properties of a certain type are owned by same player.
#Returns True if single owner has the complete set of the given property type, otherwise, returns false.
def complete_set(property_name, properties):
    owner = properties.names[property_name]["owner"]
    prop_type = properties.names[property_name]["type"]
    for item in properties.names.keys():
        if properties.names[item]["type"] == prop_type:
            if properties.names[item]["owner"] != owner:
                return False
    return True

#Determines mortgage eligibility
#Property must not be in mortgage status and if player owns the set, there must not be houses and hotels on any of the props in the set
def check_mortgage_eligibility(property_name, properties):
    owner = properties.names[property_name]["owner"]
    prop_type = properties.names[property_name]["type"]
    if properties.names[property_name]["mortgaged"] == True:
        return False
    if complete_set(property_name, properties):
        props = set_list(prop_type, properties)
        for prop in props:
            num_houses = properties.names[prop]["num_houses"]
            num_hotels = properties.names[prop]["num_hotels"]
            if (num_houses != 0) or (num_hotels != 0):
                return False
                break
    return True

    
#Determines build eligibility. Properties of set must have same owner and none of them must be mortgaged
#If hotel, can't build further
def check_build_eligibility(property_name, properties):
    num_houses = properties.names[property_name]["num_houses"]
    num_hotels = properties.names[property_name]["num_hotels"]
    prop_type = properties.names[property_name]["type"]
    num_built = num_houses + num_hotels*5
    if (prop_type == "railroad") or (prop_type == "utility"):
        return False
    if complete_set(property_name, properties) == False:
        return False
    else:
        props = set_list(prop_type, properties)
        for prop in props:
            num_built_other = properties.names[prop]["num_houses"] + 5*properties.names[prop]["num_hotels"]
            if properties.names[prop]["mortgaged"] == True:
                return False
            #Houses and hotels must be built evenly across set. Cannot build further until every prop has same amt of houses
            if num_built > num_built_other:
                return False
    if num_hotels > 0:
        return False
    return True

#Determines bulldoze eligibility. Properties must have houses or hotels and must be bulldozed evenly across the set before bulldozing another prop on the same set
def check_bulldoze_eligibility(property_name, properties):
    num_houses = properties.names[property_name]["num_houses"]
    num_hotels = properties.names[property_name]["num_hotels"]
    prop_type = properties.names[property_name]["type"]
    num_built = num_houses + num_hotels*5
    if (num_houses == 0) and (num_hotels == 0):
        return False
    else:
        props = set_list(prop_type, properties)
        for prop in props:
            num_built_other = properties.names[prop]["num_houses"] + 5*properties.names[prop]["num_hotels"]
            if num_built < num_built_other:
                return False
    return True
    
#Given an input property type, this function returns a list of all properties of that set.
def set_list(prop_type, properties):
    props = []
    for prop in properties.names.keys():
        if properties.names[prop]["type"] == prop_type:
            props.append(prop)
    return props

