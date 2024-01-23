from Player import Player
import numpy as np
import pygame
import sys
import math
from Hex import Hex


class Game(object):
    def __init__(self, player_count: int, board_config, player_starting_positions="random" ):
        row_step = int((3 ** .5) * board_config["hex_radius"] * (2 / 4))
        col_step = int(3 * board_config["hex_radius"])
        hex_count = int((board_config["height"] / row_step - 4) * (board_config["width"] / col_step -7))
        #print(hex_count)
        players = []
        for i in range(player_count):
            pos = int(np.random.rand()*hex_count)
            #print(pos)
            players.append(Player(id=i, pos=int(np.random.rand()*hex_count)))
        self.players = players


    def run_game(self, fps):
        pass


    def find_winner(self):
        pass
