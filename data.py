# Define the cards
# Data is stored as (Cost, (Effect Types), (Effect Values), Rarity)
all_cards = {'Strike': (1, ('Damage'), (6,), 'S'),
             'Defend': (1, ('Block'), (5,), 'S'),
             'Bash': (2, ('Damage', 'Vulnerable'), (8, 2), 'S'),
             'Bludgeon': (3, ('Damage'), (32,), 'R'),
             'Clothesline': (2, ('Damage', 'Weak'), (12, 2), 'C')}

# Define the enemies
# Data is stored as (Health range),
enemies = {'Cultist': ((48,55)), 'Jaw Worm': ((40,45))}

starting_deck = {'Strike': 5, 'Defend': 4, 'Bash': 1}