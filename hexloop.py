from typing import List

import pygame
import sys
import math
from Hex import Hex
from Player import Player
import numpy as np
import time
# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT, HEX_RADIUS = 800, 600, 20
FPS = 10
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
GREEN = (0, 153, 51)
PLAYER_COLOR = (153, 0, 0)
HIGHLIGHT_COLOR = (255, 255, 0)  # Yellow for highlight
TRACK_COLOR = (102, 153, 255)

# Initialize the screen
FONT_SIZE = 30
FONT_COLOR = BLACK
# Initialize the screen and font

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Hexlooper")
clock = pygame.time.Clock()
font = pygame.font.Font(None, FONT_SIZE)

# Hexagon drawing function
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
    row_step = ((3 ** .5) * hex_radius * (2 / 4))
    col_step = 3 * hex_radius
    step = 0
    hex_list: list[Hex] = []
    for row in range(0, height, int(row_step)):
        step = (1 - step)
        for col in range(0, width, int(col_step)):
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


# Main game loop

p = Player(id=0, pos=100)
out_of_the_nest = False
running = True
text_area = pygame.Rect(100, 100, 150, 30)
move_order = [6,6,6,6,6,6,6,6]
move_order = move_order[::-1]
while running:
    screen.fill(BLACK)

    hex_list = draw_hexgrid(height=HEIGHT, width=WIDTH, hex_radius=HEX_RADIUS)
    current_hex = hex_list[p.pos]
    text_area = pygame.Rect(100, 100, 30, 30)
    score_text = font.render(f"Score: {p.score} ({p.track_score})", True, FONT_COLOR)

    if current_hex.ix == p.nest:
        hex_track = []

    for hex_pos in p.track:
        hex_in_track = hex_list[hex_pos]
        draw_hexagon(hex_in_track.center_x, hex_in_track.center_y, TRACK_COLOR)
    draw_hexagon(hex_list[p.nest].center_x, hex_list[p.nest].center_y, GREEN)
    screen.blit(score_text, (10, 10))
    mouse_x, mouse_y = pygame.mouse.get_pos()
    closest_hex = find_closest_hex(mouse_x, mouse_y, hex_list)
    draw_hexagon(closest_hex.center_x, closest_hex.center_y, color=HIGHLIGHT_COLOR)

    current_hex = hex_list[p.pos]
    draw_hexagon(current_hex.center_x, current_hex.center_y, PLAYER_COLOR)
    
    if len(move_order) > 0:
        new_x, new_y = current_hex.generate_move_from_code(move_order.pop()) 
        next_hex = find_closest_hex(new_x, new_y, hex_list)
        p.move(next_hex.ix)
        time.sleep(1)
    else:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Check for left mouse button click
                mouse_x, mouse_y = event.pos
                next_hex = find_closest_hex(mouse_x, mouse_y, hex_list)
                backtrack = any(next_hex.ix == hex_pos for hex_pos in p.track)
                if current_hex.is_neighbor(next_hex) and (not backtrack or next_hex.ix == p.nest):
                    p.move(next_hex.ix)
                    current_hex.find_move_code(next_hex)
                else:
                    print("Cannot move to that hex!")

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()
