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


def draw_track(p, hex_list):
    if len(p.track) > 1:
        points = []

        for hex_pos in p.track:
            hex = hex_list[hex_pos]
            x, y = hex.center_x, hex.center_y
            points.append((x, y))

        pygame.draw.polygon(screen, colors["PLAYER_COLOR"], points, 2)


def draw_hexagon(x, y, color=colors["GRAY"]):
    angle = 0
    points = []
    for _ in range(6):
        x_i = x + board_config["hex_radius"] * math.cos(math.radians(angle))
        y_i = y + board_config["hex_radius"] * math.sin(math.radians(angle))
        points.append((int(x_i), int(y_i)))
        angle += 60

    pygame.draw.polygon(screen, color, points, 0)
    pygame.draw.polygon(screen, colors["BLACK"], points, 2)


def draw_hexgrid(height, width, hex_radius) -> list[Hex]:
    row_step = int((3 ** .5) * hex_radius * (2 / 4))
    col_step = int(3 * hex_radius)
    step = 0
    hex_list: list[Hex] = []
    for row in range(2 * row_step, height - 2 * row_step, row_step):
        step = (1 - step)
        for col in range(1 * col_step, width - 6 * col_step, col_step):
            draw_hexagon(col + step * 1.5 * hex_radius, row)
            new_hex = Hex(ix=len(hex_list), r=hex_radius, center_x=col + step * 1.5 * board_config["hex_radius"],
                          center_y=row)
            hex_list.append(new_hex)
    return hex_list


def find_closest_hex(x, y, hex_list):
    dist_arr = []
    for hex in hex_list:
        dist = (x - hex.center_x) ** 2 + (y - hex.center_y) ** 2
        dist_arr.append(dist)
    dist_arr = np.array(dist_arr)
    closest_hex = hex_list[(np.argmin(dist_arr))]
    return closest_hex


def draw_player_related_hexes(p, hex_list):
    for hex_pos in p.track:
        hex_in_track = hex_list[hex_pos]
        draw_hexagon(hex_in_track.center_x, hex_in_track.center_y, colors["TRACK_COLOR"])
    draw_hexagon(hex_list[p.nest].center_x, hex_list[p.nest].center_y, colors["GREEN"])
    draw_hexagon(hex_list[p.pos].center_x, hex_list[p.pos].center_y, colors["PLAYER_COLOR"])
    draw_track(p, hex_list)


def display_game(players, highlight=False):
    screen.fill(colors["BLACK"])
    hex_list = draw_hexgrid(height=board_config["height"], width=board_config["width"],
                            hex_radius=board_config["hex_radius"])

    for p in players:
        # text_area = pygame.Rect(500, 100, 30, 30)
        score_text = font.render(f"Score: P{p.id}: {p.score} ({p.track_score})", True, colors["PLAYER_COLOR"])
        draw_player_related_hexes(p, hex_list)
        screen.blit(score_text, (835, 10 + 20 * p.id))
        id_text = font2.render(f"{p.id}", True, colors["BLACK"])
        screen.blit(id_text,
                    (hex_list[p.pos].center_x - board_config["hex_radius"] / (2.2),
                     hex_list[p.pos].center_y - (board_config["hex_radius"] * .8)))

    mouse_x, mouse_y = pygame.mouse.get_pos()
    closest_hex = find_closest_hex(mouse_x, mouse_y, hex_list)
    draw_hexagon(closest_hex.center_x, closest_hex.center_y, color=colors["HIGHLIGHT_COLOR"])
    return hex_list


def execute_move(move, hex_list, p, players):
    new_x, new_y = current_hex.generate_move_from_code(move)
    next_hex = find_closest_hex(new_x, new_y, hex_list)
    backtrack = any(next_hex.ix == hex_pos for hex_pos in p.track) and (next_hex.ix != p.nest)
    occupied = any(next_hex.ix == other_p.pos for other_p in players)
    if current_hex.is_neighbor(next_hex) and not backtrack and not occupied or False:
        p.move(next_hex.ix)
        # time.sleep(.001)
        # current_hex.find_move_code(next_hex)
        for other_p in players:
            if p.id != other_p.id and any(next_hex.ix == hex_pos for hex_pos in other_p.track):
                other_p.crash_track()
                break
        p.consec_stalls = 0
    elif current_hex.is_neighbor(next_hex) and backtrack:
        p.consec_stalls += 1
    if p.consec_stalls > 20:
        p.crash_track()


pygame.init()
# Initialize the screen
FONT_SIZE = 25
FONT_COLOR = colors["GRAY"]
# Initialize the screen and font

screen = pygame.display.set_mode((board_config["width"], board_config["height"]))
pygame.display.set_caption("Hexlooper")
clock = pygame.time.Clock()
font = pygame.font.Font(None, FONT_SIZE)
font2 = pygame.font.Font(None, 26)

# Main game loop

g = Game(player_count=2, player_starting_positions="random", board_config=board_config, random_move_count=100)
# p1 = Player(id=0, pos=800)

out_of_the_nest = False
running = True
text_area = pygame.Rect(100, 100, 150, 30)
move_order = list((np.random.rand(100) * 6 + 1).astype(int))[::-1]

players = g.players
first = True

while running:
    if len(players[0].move_list) % 1 == 0 or first:
        hex_list = display_game(players=players, highlight=len(players[0].move_list) == 0)
        first = False
    for p in players:
        current_hex = hex_list[p.pos]
        # draw_hexagon(current_hex.center_x, current_hex.center_y, PLAYER_COLOR)
        if len(p.move_list) > 0:
            next_move, p.move_list = p.move_list[-1], p.move_list[:-1]
            execute_move(next_move, hex_list, p, players)

        else:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Check for left mouse button click
                    mouse_x, mouse_y = event.pos
                    next_hex = find_closest_hex(mouse_x, mouse_y, hex_list)
                    for p_ in players:
                        current_hex = hex_list[p_.pos]
                        backtrack = any(next_hex.ix == hex_pos for hex_pos in p_.track)
                        occupied = any(next_hex.ix == other_p.pos for other_p in players)
                        if current_hex.is_neighbor(next_hex) and (
                                not backtrack or next_hex.ix == p_.nest) and not occupied:
                            p_.move(next_hex.ix)
                            current_hex.find_move_code(next_hex)
                            for other_p in players:
                                if p_.id != other_p.id and any(next_hex.ix == hex_pos for hex_pos in other_p.track):
                                    other_p.crash_track()
                            break
                        else:
                            print(
                                f"Cannot move to that hex!(is neighbor:{current_hex.is_neighbor(next_hex)}   {backtrack=}")

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()
