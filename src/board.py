class Board():

    #Initialize dictionary of board spaces. Board spaces have the following attributes:
        #id - unique numerical identifier
        #property - boolean value indicating if the space is associated with a property
        #Type - description of space type
        #players - list of players currently at the space
    def __init__(self):
        self.spaces = {
            "Go": {
                "id": 0,
                "property": False,
            },
            "Mediterranean Ave": {
                "id": 1,
                "property": True,
            },
            "Community Chest 1": {
                "id": 2,
                "property": False,
            },
            "Baltic Ave": {
                "id": 3,
                "property": True,
            },
            "Income Tax": {
                "id": 4,
                "property": False,
            },
            "Reading Railroad": {
                "id": 5,
                "property": True,
            },
            "Oriental Ave": {
                "id": 6,
                "property": True,
            },
            "Chance 1": {
                "id": 7,
                "property": False,
            },
            "Vermont Ave": {
                "id": 8,
                "property": True,
            },
            "Connecticut Ave": {
                "id": 9,
                "property": True,
            },
            "Jail": {
                "id": 10,
                "property": False,
            },
            "St Charles Pl": {
                "id": 11,
                "property": True,
            },
            "Electric Co": {
                "id": 12,
                "property": True,
            },
            "States Ave": {
                "id": 13,
                "property": True,
            },
            "Virginia Ave": {
                "id": 14,
                "property": True,
            },
            "Penn Railroad": {
                "id": 15,
                "property": True,
            },
            "St James Pl": {
                "id": 16,
                "property": True,
            },
            "Community Chest 2": {
                "id": 17,
                "property": False,
            },
            "Tennessee Ave": {
                "id": 18,
                "property": True,
            },
            "New York Ave": {
                "id": 19,
                "property": True,
            },
            "Free Parking": {
                "id": 20,
                "property": False,
            },
            "Kentucky Ave": {
                "id": 21,
                "property": True,
            },
            "Chance 2": {
                "id": 22,
                "property": False,
            },
            "Indiana Ave": {
                "id": 23,
                "property": True,
            },
            "Illinois Ave": {
                "id": 24,
                "property": True,
            },
            "B&O Railroad": {
                "id": 25,
                "property": True,
            },
            "Atlantic Ave": {
                "id": 26,
                "property": True,
            },
            "Ventnor Ave": {
                "id": 27,
                "property": True,
            },
            "Water Works": {
                "id": 28,
                "property": True,
            },
            "Marvin Gardens": {
                "id": 29,
                "property": True,
            },
            "Go To Jail": {
                "id": 30,
                "property": False,
            },
            "Pacific Ave": {
                "id": 31,
                "property": True,
            },
            "N Carolina Ave": {
                "id": 32,
                "property": True,
            },
            "Community Chest 3": {
                "id": 33,
                "property": False,
            },
            "Penn Ave": {
                "id": 34,
                "property": True,
            },
            "Short Line Railroad": {
                "id": 35,
                "property": True,
            },
            "Chance 3": {
                "id": 36,
                "property": False,
            },
            "Park Pl": {
                "id": 37,
                "property": True,
            },
            "Luxury Tax": {
                "id": 38,
                "property": False,
            },
            "Boardwalk": {
                "id": 39,
                "property": True,
            },
        }