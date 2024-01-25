from typing import List

import pygame
import sys
import math
from Hex import Hex
from Player import Player
from Game import Game
import numpy as np

import time

# Constants
board_config = {"height": 600,
                "width": 1000,
                "hex_radius": 10
                }
FPS = 10

colors = {
    "BLACK": (0, 0, 0),
    "WHITE": (255, 255, 255),
    "GRAY": (200, 200, 200),
    "GREEN": (0, 153, 51),
    "PLAYER_COLOR": (153, 0, 0),
    "HIGHLIGHT_COLOR": (255, 255, 0),  # Yellow for highlight
    "TRACK_COLOR": (102, 153, 255)
}

g = Game(player_count=1,
         player_starting_positions="random",
         board_config=board_config,
         random_move_count=1000,
         colors=colors)
g.run_game(fps=512, display_interval=10)
#text_area = pygame.Rect(100, 100, 150, 30)
#move_order = list((np.random.rand(100) * 6 + 1).astype(int))[::-1]
