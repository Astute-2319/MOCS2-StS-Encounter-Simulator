import StS_Sim
import matplotlib.pyplot as plt
import argparse
import numpy as np

"""Temp"""

if __name__ == '__main__':

    NUM_SIMS = 100
    types = ['random', 'shiny', 'aggro', 'tank']

    # define command line arguments
    parser = argparse.ArgumentParser(prog="StS Encounter Simulator",
                                     description='This program uses PGFs to simulate StS encounters with different play types')
    parser.add_argument('--single', help='Runs a single simulation on each player "type" and saves graphs showing health changes', action='store_true')
    parser.add_argument('--multi', help=f'Runs {NUM_SIMS} simulations on each player "type" and saves graphs showing distribution' +
                        ' of player health and turns taken', action='store_true')
    # make commands in group mutually exclusive
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--cultist', help='Selects cultist as the enemy for the encounter. Chosen by default', action='store_true')
    group.add_argument('--jawworm', help='Selects jaw worm as the enemy for the encounter', action='store_true')

    # parse command line arguments
    args = parser.parse_args()

    if not args.multi and not args.single:
        print("Did you forget an argument? Use -h flag for help")

    if args.multi:
        for t in types:
            player_hp_vals_std = [0 for x in range(NUM_SIMS)]
            turns_taken_vals_std = [0 for x in range(NUM_SIMS)]
            for i in range(NUM_SIMS):
                sim = StS_Sim.Simulation()
                if args.cultist:
                    sim.enemy.select_enemy('Cultist')
                    sim.enemy_hp = sim.enemy.health
                elif args.jawworm:
                    sim.enemy.select_enemy('Jaw Worm')
                    sim.enemy_hp = sim.enemy.health
                else:
                    sim.enemy.select_enemy('Cultist')
                    sim.enemy_hp = sim.enemy.health
                sim.play_type = t
                sim.add_card('Bludgeon')
                turns, curr_hp, player_hp_change, enemy_hp_change = sim.simulate()
                player_hp_vals_std[i] = curr_hp
                turns_taken_vals_std[i] = turns
            print(f'Average turns taken over {NUM_SIMS} simulations with {t} play type: {np.average(turns_taken_vals_std)}')
            print(f'Average player health over {NUM_SIMS} simulations with {t} play type: {np.average(player_hp_vals_std)}')
            plt.figure()
            plt.hist(turns_taken_vals_std)
            plt.title(f'Distribution of turns taken -- {t}')
            plt.savefig(f'Images/Multi_Player_Vs_{sim.enemy.name}_{t}_Turns')
            plt.figure()
            plt.hist(player_hp_vals_std)
            plt.title(f'Distribution of player health values -- {t}')
            plt.savefig(f'Images/Multi_Player_Vs_{sim.enemy.name}_{t}_Health')
    
    if args.single:
        for t in types:
            sim = StS_Sim.Simulation()
            if args.cultist:
                sim.enemy.select_enemy('Cultist')
            elif args.jawworm:
                sim.enemy.select_enemy('Jaw Worm')
            else:
                sim.enemy.select_enemy('Cultist')
            sim.play_type = t
            sim.add_card('Bludgeon') # add so rare testing can be seen

            turns, curr_hp, player_hp_change, enemy_hp_change = sim.simulate()

            plt.plot(range(turns), player_hp_change, color='g', label='Player HP', marker="o")
            try:
                plt.plot(range(turns), enemy_hp_change, color='r', label='Enemy HP', marker="o")
            except:
                plt.plot(range(turns+1), enemy_hp_change, color='r', label='Enemy HP', marker="o")

            # Health totals are what occurs at the end of the enemy's turn!
            # Ex: Player health total at the turn 1 point is what it was *after* the enemy acted

            plt.title(f'Player vs {sim.enemy.name} Health Totals -- {t}')
            plt.xlabel('Turn')
            plt.ylabel('Health Total')
            plt.legend()
            plt.savefig(f'Images/Player_Vs_{sim.enemy.name}_{t}')
            plt.clf()