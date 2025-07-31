def print_board(spaces, players, properties):
    prop_names = properties.names
    #Print the current board state
    print("=" * 131)
    print("       Board Location         |                Players                 | Houses | Hotels |     Owned by       |    Prop. Type    |")
    print("----------------------------------------------------------------------------------------------------------------------------------")
    for space in spaces.keys():
        players_in_space = []
        space_name = spaces[space]["name"]
        #Determine property type, number of houses and hotels, and property owner if applicable
        if space_name in prop_names.keys():
            prop_type = str(prop_names[space_name]["type"])
            num_houses = str(prop_names[space_name]["num_houses"])
            num_hotels = str(prop_names[space_name]["num_hotels"])
            owner = prop_names[space_name]["owner"]
            if owner != None:
                owner = owner.name
            else:
                owner = str(owner)
        else:
            prop_type = "NA"
            num_houses = "0"
            num_hotels = "0"
            owner = "None"
        #prop_type = spaces[space]["type"]

        #Determine which players occupy the space
        player_list_str = ""
        for player in players:
            if player.position == space and player.bankrupt == False:
                players_in_space.append(player)
        for i in range(0, len(players_in_space)):
            if i != len(players_in_space) - 1:
                player_list_str = player_list_str + players_in_space[i].name + ","
            else:
                player_list_str = player_list_str + players_in_space[i].name
        if len(player_list_str) > 40:
            player_list_str = player_list_str[0:39]
        print(space_name.rjust(30) + "|" + player_list_str.rjust(40) + "|" + num_houses.rjust(8) + "|" + num_hotels.rjust(8) + "|" + owner.rjust(20) + "|" + prop_type.rjust(18) + "|")
    print("=" * 131)