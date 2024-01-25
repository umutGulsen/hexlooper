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
scores = np.array([])
candidates = []
for i in range(initial_random_pop):
    g = Game(player_count=1,
             player_starting_positions="random",
             board_config=board_config,
             random_move_count=100,
             colors=colors)
    g.run_game(fps=40960, display_interval=100)
    cand, score = g.find_winner()
    scores = np.append(scores, score)
    candidates.append(cand)

champion = candidates[np.argmax(scores)]

generations = 40
pop_size = 50
best_scores = []
for i in range(generations):
    print(f"Started Generation {i}")
    scores = np.array([])
    for j in range(pop_size):
        g = Game(player_count=1,
                 player_starting_positions="random",
                 board_config=board_config,
                 random_move_count=100,
                 colors=colors)
        g.mutate_moves(champion.static_move_list, mut_chance=.01)
        g.run_game(fps=40960, display_interval=100)
        cand, score = g.find_winner()
        scores = np.append(scores, score)
        candidates.append(cand)
    best_scores.append(np.max(scores))
    if i > 1:
        if best_scores[-1] > best_scores[-2]:
            champion = candidates[np.argmax(scores)]
    else:
        champion = candidates[np.argmax(scores)]
    print(f"Finished Generation {i} with score: {np.max(scores)}")
print(best_scores)

g = Game(player_count=1,
         player_starting_positions="random",
         board_config=board_config,
         random_move_count=100,
         colors=colors)
g.mutate_moves(champion.static_move_list, mut_chance=0)
g.run_game(fps=5, display_interval=1, wait_for_user=True)
# print(g.find_winner())
sys.exit()
