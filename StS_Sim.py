from itertools import permutations
import numpy as np
import matplotlib.pyplot as plt
import data
import StS_Enemies

plt.style.use(['ggplot'])

class Simulation:
    def __init__(self):
        """
        Used to simulate a StS encounter between a player and an enemy
            Attributes:
                all_cards -- A dictionary containing all cards currently implemented
                starting_deck -- A dictionary containing cards in the player's deck and discard combined
                hand -- The player's current hand
                current_deck -- A dictionary containing cards actively in the player's deck
                current_deck -- A dictionary containing cards actively in the player's discard
                max_hp -- The player's max health
                curr_hp -- The player's current health
                enemy_hp -- The enemy's current health
                states -- Any effects/statuses currently in effect
                play_type -- The player's current play type

            Methods:
                add_card(card) -- Adds the specified card to the starting deck
                draw_cards(num_draw) -- Draw random cards into the player's hand
                calc_playable(energy) -- Find which card(s) in hand are playable based on energy available
                pretty_print_cards(cards) -- Print the player's current hand
                pretty_print_permutations(perms) -- Prints a list of provided permutations
                card_pgf(card_name, x, y, states) -- Returns a PGF based on the provided card
                apply_card_to_state(card_name) -- Update states attribute based on card played
                plays_pgf(enemy_pgf, turn, energy, x, y) -- Create a PGF of all possible outcomes/plays
                shift(array, amt) -- Cycle a numpy array around
                sample_prob(p) -- Choose an element from an array of probabilities based on their values
                end_turn() -- End the simulated turn
                simulate(enemy_pgf) -- Run a full combat simulation

        """
        self.curr_turn = 1
        self.max_hp = 80

        self.dmg_center = 50
        self.dmg_max = 2 * 50 + 1
        self.blk_max = 2 * self.max_hp + 1
        self.dmg_vals = np.arange(self.dmg_max)
        self.blk_vals = np.arange(self.blk_max)

        self.dmg = np.exp(2*np.pi*1j*self.dmg_vals/self.dmg_max)
        self.blk = np.exp(2*np.pi*1j*self.blk_vals/self.blk_max)

        self.states = {'vulnerable':0, 'weakened': 0, 'strength':0}
        self.all_cards = data.all_cards
        self.enemy = StS_Enemies.Enemy()
        self.starting_deck = data.starting_deck.copy()
        self.hand = []
        self.current_deck = self.starting_deck.copy()
        self.current_discard = self.starting_deck.copy()
        for card in self.current_discard:
            self.current_discard[card] = 0

        
        self.curr_hp = self.max_hp
        self.enemy_hp = self.enemy.health
        

        self.play_type = 'random'

    def add_card(self, card):
        """
        Adds a card to the starting deck
        
            Keyword arguments:
                card -- name of the card being added
        """
        if card not in self.starting_deck:
            self.starting_deck.update({card: 1})
        else:
            self.starting_deck[card] = self.starting_deck[card]+1
        
        self.current_deck = self.starting_deck.copy()
        self.current_discard = self.starting_deck.copy()
        for card in self.current_discard:
            self.current_discard[card] = 0

    def draw_cards(self, num_draw):
        """
        Draws random cards into the player's simulated hand

            Keyword arguments:
                num_draw -- Number of cards to be drawn
            Returns: None
        """
        # Draw num_draw cards and add them to hand
        for n in range(0,num_draw):
            # Get how many cards are in the deck
            deck_count = sum(self.current_deck.values())
            
            # If the deck is empty, shuffle the discard pile into the draw pile
            if deck_count == 0:
                self.current_deck = self.current_discard.copy()
                self.current_discard = self.starting_deck.copy()
                for card in self.current_discard:
                    self.current_discard[card] = 0
                deck_count = sum(self.current_deck.values())

            # Get what types of cards can be drawn and at what probabilities
            types = list(self.current_deck.keys())
            probs = [self.current_deck[t] / deck_count for t in types]

            # Pick a card at random from deck and add it to hand
            card = np.random.choice(types, p=probs)
            self.hand.append({str(card): self.all_cards[card]})

            # Remove the drawn card from the deck
            self.current_deck[str(card)] -= 1

    def calc_playable(self, energy):
        """
        Find which card(s) in handare playable based on energy available

            Keyword arguments:
                energy -- How much energy is available to be spent to play cards
            Returns: A list of all possible card plays for the turn
        """
        all_possible_plays = []
        all_perms = list(permutations(self.hand))

        # for each permutation
        for p in all_perms:
            count = 0
            curr_played = []
            available_energy = energy
            # while there are still cards to check
            while count < len(p):
                # if the current card costs less than or has cost equal to
                # the current amount of energy available
                if list(p[count].values())[0][0] <= available_energy:
                    # "play" the card and move to the next card
                    curr_played.append(p[count])
                    available_energy = available_energy - list(p[count].values())[0][0]
                    count += 1
                else:
                    # otherwise, move to the next card
                    count += 1
            # once all cards are checked or energy runs out, add possible played cards to list
            # only add if not already present to save space
            if curr_played not in all_possible_plays:
                all_possible_plays.append(curr_played)

        return all_possible_plays

    def pretty_print_cards(self, cards):
        """
        Prints a list of provided cards

            Keyword arguments:
                cards -- A list of cards
            Returns: None
        """
        count = 1
        for c in cards:
            print(f'Card {count}: {list(c.keys())[0]} -- Cost: {list(c.values())[0][0]}' + 
                f' Effect: {list(c.values())[0][1]} {list(c.values())[0][2]}')
            count += 1
        print()


    def pretty_print_perms(self, perms):
        """
        Prints a list of provided permutations

            Keyword arguments:
                perms -- A list of card permutations
            Returns: None
        """
        for p in perms:
            self.pretty_print_cards(p)

    def card_pgf(self, card_name, x, y):
        """
        Returns a PGF based on the provided card

            Keyword arguments:
                card_name: The card the PGF is for
                x: Damage counting variable
                y: Block counting variable
                states: Any effects/statuses currently in effect
            Returns: None
        """
        vuln = self.states.get('vulnerable', 0)
        vuln_mult = 1.5 if vuln > 0 else 1.0

        match card_name:
            case 'Strike': return x**np.floor((6*vuln_mult))
            case 'Defend': return y**5
            case 'Bash': return x**np.floor((8*vuln_mult))
            case 'Bludgeon': return x**np.floor((32*vuln_mult))
            case 'Clothesline': return x**np.floor((12*vuln_mult))
            case _: raise ValueError(f"Invalid Card Name {card_name}")
        
    def apply_card_to_state(self, card_name):
        """
        Update states attribute based on card played

            Keyword arguments:
                card_name -- The card being played
            Returns: None
        """
        match card_name:
            case 'Bash': self.states['vulnerable'] = self.states['vulnerable'] + 2
            case 'Clothesline': self.states['weakened'] = self.states['weakened'] + 2
        # Add other state-modifying cards here
    
    def plays_pgf(self, energy, x, y):
        """
        Create a PGF of all possible outcomes/plays

            Keyword arguments:
                enemy_pgf -- The PGF for the enemy being faced
                turn -- The current turn
                energy -- How much energy the player has available
                x -- Damage counting variable
                y -- Block counting variable
            Returns: The PGF for all possible plays
        """
        all_possible_plays = self.calc_playable(energy)
        prob = [0 for i in range(len(all_possible_plays))]

        # all random -- each permutation has equal prob of being selected
        if self.play_type == 'random':
            prob = [1 / len(all_possible_plays) for i in range(len(all_possible_plays))]
        # more likely to play hands with rare cards
        elif self.play_type == 'shiny':
            total_weight = 0
            # for each "line" of card plays
            count = 0
            for p in all_possible_plays:
                weight = 0
                # for each card add a probability weight based on rarity
                for card in p:
                    if list(card.values())[0][3] == "S":
                        weight += 1
                        total_weight += 1
                    elif list(card.values())[0][3] == "C":
                        weight += 5
                        total_weight += 5
                    elif list(card.values())[0][3] == "U":
                        weight += 10
                        total_weight += 10
                    else:
                        weight += 25
                        total_weight += 25
                prob[count] = weight
                count += 1
            prob = [x/total_weight for x in prob]
            # print(prob)
        # more likely to play attacks/damage
        elif self.play_type == 'aggro':
            total_weight = 0
            # for each "line" of card plays
            count = 0
            for p in all_possible_plays:
                weight = 0
                # for each card add a probability weight based on if card does damage
                # more damage -> more likely
                for card in p:
                    if 'Damage' in list(card.values())[0][1]:
                        weight += 3*list(card.values())[0][2][0]
                        total_weight += 3*list(card.values())[0][2][0]

                    if 'Vulnerable' in list(card.values())[0][1]:
                        weight += 5
                        total_weight += 5
                    if weight == 0:
                        weight += 1
                        total_weight += 1
                prob[count] = weight
                count += 1
            prob = [x/total_weight for x in prob]
        # more likely to play blocks
        elif self.play_type == 'tank':
            total_weight = 0
            # for each "line" of card plays
            count = 0
            for p in all_possible_plays:
                weight = 0
                # for each card add a probability weight based on if card blocks
                # more block -> more likely
                for card in p:
                    if 'Block' in list(card.values())[0][1]:
                        weight += 3*list(card.values())[0][2][0]
                        total_weight += 3*list(card.values())[0][2][0]
                    if 'Weak' in list(card.values())[0][1]:
                        weight += 5
                        total_weight += 5
                    if weight == 0:
                        weight += 1
                        total_weight += 1
                prob[count] = weight
                count += 1
            prob = [x/total_weight for x in prob]
        
        total = 0
        count = 0
        for play in all_possible_plays:
            saved_states = self.states.copy()
            # Product of PGFs for each card played
            pgf = 1
            for card in play:
                pgf *= self.card_pgf(list(card.keys())[0], x, y)
                self.apply_card_to_state(list(card.keys())[0])
            self.states, temp_pgf = self.enemy.pgf(self.curr_turn, x, y, self.states)
            pgf *= temp_pgf
            total += prob[count] * pgf
            self.states = saved_states
            count += 1
        return total
    
    def shift_block(self, array, amt):
        """
        Cycle a numpy array around

        Keyword arguments:
            array: Array to be cycled
            amt: How far to cycle
        Returns: The cycled array
        """
        return np.roll(array, amt, 0)
    
    def shift_damage(self, array, amt):
        """
        Cycle a numpy array around

        Keyword arguments:
            array: Array to be cycled
            amt: How far to cycle
        Returns: The cycled array
        """
        return np.roll(array, amt, 1)

    def sample_prob(self, p):
        """
        Choose an element from an array of probabilities based on their values

            Keyword arguments:
                p -- Probability array
            Returns: An element from the array
        """
        p_array = np.array(p)
        i = np.random.choice(np.arange(p_array.size), p=p_array.ravel())
        return np.unravel_index(i, p_array.shape)


    def end_turn(self):
        """
        End the simulated turn
            Keyword arguments: None
            Returns: None
        """
        temporary_states = ['vulnerable', 'weakened']
        for card in range(len(self.hand)):
            card_name = list(self.hand[card].keys())[0]
            self.current_discard[card_name] = self.current_discard[card_name]+1
        for state in temporary_states:
            if self.states[state] > 0:
                self.states[state] -= 1
        self.hand = []

    def simulate(self):
        """
        Run a full combat simulation

            Keyword arguments:
                enemy_pgf -- The PGF for the enemy being faced
            Returns: 
                self.curr_turn -- The turn the combat ended on
                self.curr_hp -- The player's current health
                player_hp_change -- A list of the player's health after each turn
                enemy_hp_change -- A list of the enemy's health after each turn
        """
        player_hp_change = [self.curr_hp]
        enemy_hp_change = [self.enemy_hp]
        while self.curr_hp > 0 and self.enemy_hp > 0:
            self.draw_cards(5)

            # print(f'Hand: {self.hand}')
            # print(f'Deck: {self.current_deck}')
            # print(f'Discard: {self.current_discard}')

            # DMG, BLK = np.meshgrid(dmg, blk)

            # M evaluated pointwise over the grid
            M_grid = np.zeros((self.blk_max, self.dmg_max), dtype=complex)
            for i in range(self.blk_max):
                for j in range(self.dmg_max):
                    saved_states = self.states.copy()
                    saved_last_move = self.enemy.last_move
                    M_grid[i, j] = self.plays_pgf(energy=3, x=self.dmg[j], y=self.blk[i])
                    self.states = saved_states
                    self.enemy.last_move = saved_last_move

            # If jaw worm is acting, guess which move was last selected
            # IMPORTANT: This may not choose the same move as was actually done
            # Since our PGF returns a weighted sum of all possible moves,
            # we cannot "commit" to a single move. This will have to do for now
            if self.enemy.name == 'Jaw Worm' and self.curr_turn > 0:
                bellow_probs = {'Chomp': 0.59, 'Bellow': 0.0, 'Thrash': 0.45}
                thrash_probs = {'Chomp': 0.41, 'Bellow': 0.56, 'Thrash': 0.30}
                chomp_probs  = {'Chomp': 0.00, 'Bellow': 0.44, 'Thrash': 0.25}
                last = self.enemy.last_move if self.enemy.last_move else 'Thrash'
                self.enemy.last_move = np.random.choice(
                    ['Bellow', 'Thrash', 'Chomp'],
                    p=[bellow_probs[last], thrash_probs[last], chomp_probs[last]]
    )

            pn1n2 = abs(np.fft.fft2(M_grid)) / (self.blk_max * self.dmg_max)
            pn1n2_fixed = self.shift_block(pn1n2, self.max_hp)
            pn1n2_fixed = self.shift_damage(pn1n2_fixed, self.dmg_center)
            pn1n2_fixed /= np.sum(pn1n2_fixed) # normalize in case precision errors break numpy tolerance limits

            # plt.figure()
            # plt.imshow(pn1n2_fixed, origin='lower', extent=[-self.dmg_center - 0.5, self.dmg_center + 0.5,
            #                                                 -self.max_hp - 0.5, self.max_hp + 0.5])
            # plt.colorbar(label='Probability')
            # ax = plt.gca()
            # ax.set_xticks(range(-self.dmg_center, self.dmg_center + 1, 10))
            # ax.set_yticks(range(-self.max_hp,self.max_hp+1,10))
            # plt.ylabel('Net Block')
            # plt.xlabel('Damage')
            # plt.title("Probability spread of damage/block\nwith enemy implemented")
            # plt.savefig('PGF GRAPH')

            block, damage = self.sample_prob(pn1n2_fixed)
            block = block - self.max_hp
            damage = damage - self.dmg_center

            # print(f'Block: {block}')
            # print(f'Damage: {damage}')
            # print()

            if damage > 0:
                self.enemy_hp -= damage

            enemy_hp_change.append(self.enemy_hp)

            # If enemy dies, it does not attack
            if self.enemy_hp <= 0:
                break

            if block < 0:
                self.curr_hp += block
            
            player_hp_change.append(self.curr_hp)
        
            self.curr_turn += 1

            self.end_turn()

        return self.curr_turn, self.curr_hp, player_hp_change, enemy_hp_change