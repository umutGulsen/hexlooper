from typing import List
import pygame
import sys
import math
from Hex import Hex
from Player import Player
from Game import Game
import numpy as np

import time

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
initial_random_pop = 10
move_length = 100
display_interval = 1
generations = 10
pop_size = 5
mutation_chance = .01

import copy


def genetic_algorithm(initial_random_pop: int, move_length: int, display_interval: int, generations: int, pop_size: int,
                      mutation_chance: float):
    scores = np.array([])
    candidates = []
    for i in range(initial_random_pop):
        g = Game(player_count=1,
                 player_starting_positions="fixed",
                 board_config=board_config,
                 random_move_count=move_length,
                 colors=colors)
        g.run_game(fps=1024, display_interval=display_interval)
        cand, score = g.find_winner()
        scores = np.append(scores, score)
        candidates.append(cand)

    champion = candidates[np.argmax(scores)]
    champ_moves = champion.static_move_list

    # champ_moves = None
    best_scores = []
    champ_score = -1
    for i in range(generations):
        print(f"Started Generation {i}")
        scores = np.array([])
        # candidates = []
        cand_moves = []
        for j in range(pop_size):
            g = Game(player_count=1,
                     player_starting_positions="fixed",
                     board_config=board_config,
                     random_move_count=move_length,
                     colors=colors)
            move = copy.deepcopy(champ_moves)
            g.mutate_moves(move, mut_chance=mutation_chance)
            g.run_game(fps=1024, display_interval=display_interval)
            cand, score = g.find_winner()
            cand_moves.append(cand.static_move_list)
            scores = np.append(scores, score)
            # print(scores)
            # candidates.append(cand)
        best_scores.append(np.max(scores))
        if i > 0:
            if best_scores[-1] > champ_score:
                # champion = candidates[np.argmax(scores)]
                champ_score = best_scores[-1]
                champ_moves = cand_moves[np.argmax(scores)]
                # print("--change")
        else:
            # champion = candidates[np.argmax(scores)]
            champ_score = best_scores[0]
            # champ_moves = champion.static_move_list
            champ_moves = cand_moves[np.argmax(scores)]
            # print("----change")
        print(f"Finished Generation {i} with score: {np.max(scores)} / Last Champ: {champ_score}")
        # print(champ_moves)
    return champ_moves


best_moves = genetic_algorithm(initial_random_pop=40,
                               move_length=100,
                               display_interval=100,
                               generations=30,
                               pop_size=20,
                               mutation_chance=.03)
while True:
    g = Game(player_count=1,
             player_starting_positions="fixed",
             board_config=board_config,
             random_move_count=100,
             colors=colors)
    g.mutate_moves(best_moves, mut_chance=0)
    # time.sleep(10)
    g.run_game(fps=12, display_interval=1, wait_for_user=False)

pygame.quit()
# print(g.find_winner())
sys.exit()
