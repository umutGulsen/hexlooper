from typing import List

import pygame
import sys
import math
from Hex import Hex
from Player import Player
import numpy as np
import time
# Constants
WIDTH, HEIGHT, HEX_RADIUS = 1000, 600, 10
FPS = 4000
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
GREEN = (0, 153, 51)
PLAYER_COLOR = (153, 0, 0)
HIGHLIGHT_COLOR = (255, 255, 0)  # Yellow for highlight
TRACK_COLOR = (102, 153, 255)
# Hexagon drawing function


def draw_track(p,hex_list):
    if len(p.track) > 1:
        points = []

        for hex_pos in p.track:
            hex=hex_list[hex_pos]
            x, y = hex.center_x, hex.center_y
            points.append((x,y))

        pygame.draw.polygon(screen, PLAYER_COLOR, points, 2)


def draw_hexagon(x, y, color=GRAY):
    angle = 0
    points = []
    for _ in range(6):
        x_i = x + HEX_RADIUS * math.cos(math.radians(angle))
        y_i = y + HEX_RADIUS * math.sin(math.radians(angle))
        points.append((int(x_i), int(y_i)))
        angle += 60

    pygame.draw.polygon(screen, color, points, 0)
    pygame.draw.polygon(screen, BLACK, points, 2)


def draw_hexgrid(height, width, hex_radius) -> list[Hex]:
    row_step = int((3 ** .5) * hex_radius * (2 / 4))
    col_step = int(3 * hex_radius)
    step = 0
    hex_list: list[Hex] = []
    for row in range(2 * row_step, height - 2 * row_step, row_step):
        step = (1 - step)
        for col in range(1*col_step, width-6*col_step, col_step):
            draw_hexagon(col + step * 1.5 * hex_radius, row)
            new_hex = Hex(ix=len(hex_list), r=hex_radius, center_x=col + step * 1.5 * HEX_RADIUS, center_y=row)
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
        draw_hexagon(hex_in_track.center_x, hex_in_track.center_y, TRACK_COLOR)
    draw_hexagon(hex_list[p.nest].center_x, hex_list[p.nest].center_y, GREEN)
    draw_hexagon(hex_list[p.pos].center_x, hex_list[p.pos].center_y, PLAYER_COLOR)
    draw_track(p, hex_list)



def display_game(players):
    screen.fill(BLACK)
    hex_list = draw_hexgrid(height=HEIGHT, width=WIDTH, hex_radius=HEX_RADIUS)


    for p in players:
        #text_area = pygame.Rect(500, 100, 30, 30)
        score_text = font.render(f"Score: P{p.id}: {p.score} ({p.track_score})", True, PLAYER_COLOR)
        draw_player_related_hexes(p, hex_list)
        screen.blit(score_text, (835, 10 + 20*p.id))
        id_text = font2.render(f"{p.id}", True, BLACK)
        screen.blit(id_text, (hex_list[p.pos].center_x - HEX_RADIUS/(2.2), hex_list[p.pos].center_y - (HEX_RADIUS*.8)))


    mouse_x, mouse_y = pygame.mouse.get_pos()
    closest_hex = find_closest_hex(mouse_x, mouse_y, hex_list)
    draw_hexagon(closest_hex.center_x, closest_hex.center_y, color=HIGHLIGHT_COLOR)
    return hex_list


def execute_move(move, hex_list, p, players):
    new_x, new_y = current_hex.generate_move_from_code(move)
    next_hex = find_closest_hex(new_x, new_y, hex_list)
    backtrack = any(next_hex.ix == hex_pos for hex_pos in p.track) and (next_hex.ix != p.nest)
    occupied = any(next_hex.ix == other_p.pos for other_p in players)
    if current_hex.is_neighbor(next_hex) and not backtrack and not occupied or False:
        p.move(next_hex.ix)
        #time.sleep(.001)
        #current_hex.find_move_code(next_hex)
        for other_p in players:
            if p.id != other_p.id and any(next_hex.ix == hex_pos for hex_pos in other_p.track):
                other_p.crash_track()
        p.consec_stalls = 0
    elif current_hex.is_neighbor(next_hex) and backtrack:
        p.consec_stalls += 1
    if p.consec_stalls > 20:
        p.crash_track()
pygame.init()
# Initialize the screen
FONT_SIZE = 25
FONT_COLOR = GRAY
# Initialize the screen and font

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Hexlooper")
clock = pygame.time.Clock()
font = pygame.font.Font(None, FONT_SIZE)
font2 = pygame.font.Font(None, 26)


# Main game loop

p1 = Player(id=0, pos=800)
p2 = Player(id=1, pos=1200)
p3 = Player(id=2, pos=1400)
p4 = Player(id=3, pos=1600)
out_of_the_nest = False
running = True
text_area = pygame.Rect(100, 100, 150, 30)
move_order = list((np.random.rand(2000)*6 + 1).astype(int))[::-1]


players = [p1,p2, p3, p4]
while running:

    hex_list = display_game(players=players)
    for p in players:
        current_hex = hex_list[p.pos]
        #draw_hexagon(current_hex.center_x, current_hex.center_y, PLAYER_COLOR)
        if len(move_order) > 0:
            execute_move(move_order.pop(), hex_list, p, players)

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
                        if current_hex.is_neighbor(next_hex) and (not backtrack or next_hex.ix == p_.nest) and not occupied:
                            p_.move(next_hex.ix)
                            current_hex.find_move_code(next_hex)
                            for other_p in players:
                                if p_.id != other_p.id and any(next_hex.ix == hex_pos for hex_pos in other_p.track):
                                    other_p.crash_track()
                            break
                        else:
                            print(f"Cannot move to that hex!(is neighbor:{current_hex.is_neighbor(next_hex)}   {backtrack=}")

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()
