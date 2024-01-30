import pygame
import sys
from Game import Game
import numpy as np
import copy
import matplotlib.pyplot as plt

board_config = {"height": 600,
                "width": 1000,
                "hex_radius": 10
                }

colors = {
    "BLACK": (0, 0, 0),
    "WHITE": (255, 255, 255),
    "GRAY": (200, 200, 200),
    "GREEN": (0, 153, 51),
    "PLAYER_COLOR": (153, 0, 0),
    "HIGHLIGHT_COLOR": (255, 255, 0),  # Yellow for highlight
    "TRACK_COLOR": (102, 153, 255)
}


# import cProfile
# cProfile.run("g.run_game(fps=40960, display_interval=10000)", sort="tottime")


def genetic_algorithm(initial_random_pop: int, move_length: int, display_interval: int, generations: int, pop_size: int,
                      mutation_chance: float, train_fps: int = 4096):
    record = {}
    generation_scores = np.zeros((generations+1, max(initial_random_pop, pop_size)))
    champion_scores = np.zeros(generations+1)
    g = Game(player_count=initial_random_pop,
             player_starting_positions="fixed",
             board_config=board_config,
             random_move_count=move_length,
             move_generation_type="list",
             game_mode="coexist",
             colors=colors)
    g.run_game(fps=train_fps, display_interval=display_interval)

    generation_scores[0, :] = [p.score for p in g.players]
    champion, champ_score = g.find_winner()
    champion_scores[0] = champ_score
    champ_moves = champion.static_move_list

    best_scores = []
    for gen in range(generations):
        print(f"Started Generation {gen}")
        g = Game(player_count=pop_size,
                 player_starting_positions="fixed",
                 board_config=board_config,
                 random_move_count=move_length,
                 move_generation_type="list",
                 game_mode="coexist",
                 colors=colors)

        move = copy.deepcopy(champ_moves)
        g.mutate_moves(move, mut_chance=mutation_chance)

        g.run_game(fps=train_fps, display_interval=display_interval)
        generation_scores[gen+1, :] = [p.score for p in g.players]
        gen_champ, score = g.find_winner()

        best_scores.append(score)
        if gen > 0:
            if best_scores[-1] > champ_score:
                champ_score = best_scores[-1]
                champ_moves = gen_champ.static_move_list
        champion_scores[gen + 1] = champ_score
        print(f"Finished Generation {gen} with score: {score} / Last Champ: {champ_score}")
        record["champion_scores"] = champion_scores
        record["generation_scores"] = generation_scores
    return champ_moves, record


def visualize_scores(record):
    plt.plot(record["champion_scores"])
    for g, gen_score_list in enumerate(record["generation_scores"]):
        [plt.scatter(g, gen_score_list[i]) for i in range(gen_score_list.shape[0])]
    plt.show()


def display_ga_champion(champ_disp_count=1):
    move_length = 20
    best_moves, record = genetic_algorithm(initial_random_pop=20,
                                           move_length=move_length,
                                           display_interval=1,
                                           generations=10,
                                           pop_size=20,
                                           mutation_chance=.01,
                                           train_fps=56)
    for _ in range(champ_disp_count):
        g = Game(player_count=1,
                 player_starting_positions="fixed",
                 board_config=board_config,
                 random_move_count=move_length,
                 move_generation_type="list",
                 colors=colors)

        g.mutate_moves(best_moves, mut_chance=0)
        g.run_game(fps=12, display_interval=1, wait_for_user=False)
    pygame.quit()
    visualize_scores(record)


display_ga_champion(champ_disp_count=2)

"""
g = Game(player_count=5,
         player_starting_positions="fixed",
         board_config=board_config,
         turn_limit=500,
         move_generation_type="fixed",
         game_mode="coexist",
         colors=colors)
g.run_game(fps=50, display_interval=1, wait_for_user=True)
"""
#pygame.quit()
# print(g.find_winner())
sys.exit()
