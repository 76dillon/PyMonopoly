import random

def roll_dice(cheat=False):
    if cheat==False:
        dice1 = random.randint(1, 6)
        dice2 = random.randint(1, 6)
    else:
        dice_seq = input("Enter dice numbers: 'dice1,dice2': ")
        try:
            dice1 = int(dice_seq.split(",")[0])
            dice2 = int(dice_seq.split(",")[1])
        except ValueError:
            dice1 = random.randint(1, 6)
            dice2 = random.randint(1, 6)
    return (dice1, dice2)


