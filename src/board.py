class Board():

    #Initialize dictionary of board spaces. Board spaces have the following attributes:
        #id - unique numerical identifier
        #property - boolean value indicating if the space is associated with a property

    def __init__(self):
        self.spaces = {
            0: {
                "name": "Go",
                "property": False,
            },
            1: {
                "name": "Mediterranean Ave",
                "property": True,
            },
            2: {
                "name": "Community Chest 1",
                "property": False,
            },
            3: {
                "name": "Baltic Ave",
                "property": True,
            },
            4: {
                "name": "Income Tax",
                "property": False,
            },
            5: {
                "name": "Reading Railroad",
                "property": True,
            },
            6: {
                "name": "Oriental Ave",
                "property": True,
            },
            7: {
                "name": "Chance 1",
                "property": False,
            },
            8: {
                "name": "Vermont Ave",
                "property": True,
            },
            9: {
                "name": "Connecticut Ave",
                "property": True,
            },
            10: {
                "name": "Jail",
                "property": False,
            },
            11: {
                "name": "St Charles Pl",
                "property": True,
            },
            12: {
                "name": "Electric Co",
                "property": True,
            },
            13: {
                "name": "States Ave",
                "property": True,
            },
            14: {
                "name": "Virginia Ave",
                "property": True,
            },
            15: {
                "name": "Penn Railroad",
                "property": True,
            },
            16: {
                "name": "St James Pl",
                "property": True,
            },
            17: {
                "name": "Community Chest 2",
                "property": False,
            },
            18: {
                "name": "Tennessee Ave",
                "property": True,
            },
            19: {
                "name": "New York Ave",
                "property": True,
            },
            20: {
                "name": "Free Parking",
                "property": False,
            },
            21: {
                "name": "Kentucky Ave",
                "property": True,
            },
            22: {
                "name": "Chance 2",
                "property": False,
            },
            23: {
                "name": "Indiana Ave",
                "property": True,
            },
            24: {
                "name": "Illinois Ave",
                "property": True,
            },
            25: {
                "name": "B&O Railroad",
                "property": True,
            },
            26: {
                "name": "Atlantic Ave",
                "property": True,
            },
            27: {
                "name": "Ventnor Ave",
                "property": True,
            },
            28: {
                "name": "Water Works",
                "property": True,
            },
            29: {
                "name": "Marvin Gardens",
                "property": True,
            },
            30: {
                "name": "Go To Jail",
                "property": False,
            },
            31: {
                "name": "Pacific Ave",
                "property": True,
            },
            32: {
                "name": "N Carolina Ave",
                "property": True,
            },
            33: {
                "name": "Community Chest 3",
                "property": False,
            },
            34: {
                "name": "Penn Ave",
                "property": True,
            },
            35: {
                "name": "Short Line Railroad",
                "property": True,
            },
            36: {
                "name": "Chance 3",
                "property": False,
            },
            37: {
                "name": "Park Pl",
                "property": True,
            },
            38: {
                "name": "Luxury Tax",
                "property": False,
            },
            39: {
                "name": "Boardwalk",
                "property": True,
            },
        }