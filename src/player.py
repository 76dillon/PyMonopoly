from config import NUM_SPACES

class Player():
    def __init__(self, name):
        self.name = name
        self.balance = 1500
        self.worth = 1500
        self.position = 0
        self.owned = {}
        self.num_jail_free_cards = 0
        self.jail = False
        self.board_location_id = 0
        self.bankrupt = False
    '''
    This function moves player position down the board by a specified number of spaces.
    Board has spaces with IDs between 0 and 39. If after adding to the current position, pos > 39,
    subtract the number of spaces from it to obtain the new player position.
    '''
    def move_player(self, move_spaces):
        if (self.position + move_spaces <= NUM_SPACES - 1):
            self.position += move_spaces
        else:
            self.position = (self.position+move_spaces) - NUM_SPACES
        return self.position
    
    '''
    This function simply updates the player position to a desired space anywhere on the board between 0 and 39.
    '''
    def update_position(space):
        self.position = space
        return self.position