import numpy as np
from data import enemies

class Enemy:
    def __init__(self):
        """
        Used to hold enemy information in a StS encounter. Cultist by default.
        """
        self.name = 'Cultist'
        self.health = np.random.randint(enemies['Cultist'][0],enemies['Cultist'][1])

        self.pgf = self.cultist_pgf
        self.last_move = None

    def select_enemy(self, enemy):
        self.name = enemy
        self.health = np.random.randint(enemies[enemy][0], enemies[enemy][1])
        match enemy:
            case 'Cultist': self.pgf = self.cultist_pgf
            case 'Jaw Worm': self.pgf = self.jaw_worm_pgf

    def cultist_pgf(self, turn, x, y, states):
        # Turn 1 do nothing
        weak = states.get('weakened', 0)
        weak_mult = 0.75 if weak > 0 else 1.0
        if turn == 1:
            self.last_move = "Incantation"
            return states, 1
        # Every other turn deal 1 + multiple of 5
        # Use negative block to show enemy damage
        # In the end, negative block count -> player hp damage
        else:
            self.last_move = 'Dark Strike'
            return states, y**(np.floor(weak_mult*((-5)*(turn-1) - 1)))
        
    def jaw_worm_pgf(self, turn, x, y, states):
        
        strength = states['strength']
        weak = states.get('weakened', 0)
        weak_mult = 0.75 if weak > 0 else 1.0

        chomp_pgf  = y**int(np.floor(weak_mult * (-11 - strength)))
        thrash_pgf = x**(-5) * y**int(np.floor(weak_mult * (-7 - strength)))
        bellow_pgf = x**(-6)

        # Turn 1 use chomp
        if turn == 1:
            self.last_move = 'Chomp'
            return states, chomp_pgf
        
        # Otherwise do something based on last move
        if self.last_move == 'Chomp':
            return states, 0.59 * bellow_pgf + 0.41 * thrash_pgf
            # if np.random.random() <= 0.59:
            #     self.last_move = 'Bellow'
            #     states['strength'] = states['strength'] + 3
            #     return states, x**(-6)
            # else:
            #     self.last_move = 'Thrash'
            #     return states, x**(-5)*y**np.floor(weak_mult*(-7 - strength))
        
        elif self.last_move == 'Bellow':
            return states, 0.56 * thrash_pgf + 0.44 * chomp_pgf
            # if np.random.random() <= 0.56:
            #     self.last_move = 'Thrash'
            #     return states, x**(-5)*y**np.floor(weak_mult*(-7 - strength))
            # else:
            #     self.last_move = 'Chomp'
            #     return states, y**np.floor(weak_mult*(-11 - strength))
        
        else:
            return states, 0.45 * bellow_pgf + 0.30 * thrash_pgf + 0.25 * chomp_pgf
            # roll = np.random.random()
            # if roll <= 0.45:
            #     self.last_move = 'Bellow'
            #     states['strength'] = states['strength'] + 3
            #     return states, x**(-6)
            # elif roll > 0.45 and roll <= 0.75:
            #     self.last_move = 'Thrash'
            #     return states, x**(-5)*y**np.floor(weak_mult*(-7 - strength))
            # else:
            #     self.last_move = 'Chomp'
            #     return states, y**np.floor(weak_mult*(-11 - strength))