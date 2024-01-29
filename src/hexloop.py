import pygame
import sys
from Game import Game
import numpy as np
import copy

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

    g = Game(player_count=initial_random_pop,
             player_starting_positions="fixed",
             board_config=board_config,
             random_move_count=move_length,
             move_generation_type="list",
             game_mode="coexist",
             colors=colors)
    g.run_game(fps=train_fps, display_interval=display_interval)

    champion, champ_score = g.find_winner()
    champ_moves = champion.static_move_list

    best_scores = []
    for i in range(generations):
        print(f"Started Generation {i}")
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
        gen_champ, score = g.find_winner()

        best_scores.append(score)
        if i > 0:
            if best_scores[-1] > champ_score:
                champ_score = best_scores[-1]
                champ_moves = gen_champ.static_move_list

        print(f"Finished Generation {i} with score: {score} / Last Champ: {champ_score}")
    return champ_moves


def display_ga_champion():
    move_length = 30
    best_moves = genetic_algorithm(initial_random_pop=20,
                                   move_length=move_length,
                                   display_interval=1,
                                   generations=40,
                                   pop_size=40,
                                   mutation_chance=.15,
                                   train_fps=48)
    while True:
        g = Game(player_count=1,
                 player_starting_positions="fixed",
                 board_config=board_config,
                 random_move_count=move_length,
                 move_generation_type="list",
                 colors=colors)

        g.mutate_moves(best_moves, mut_chance=0)
        # time.sleep(10)
        g.run_game(fps=12, display_interval=1, wait_for_user=False)


display_ga_champion()

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
pygame.quit()
# print(g.find_winner())
sys.exit()
