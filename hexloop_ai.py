import pygame
import sys
import math
from Hex import Hex
import numpy as np

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
HEX_RADIUS = 20
FPS = 10
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
PLAYER_COLOR = (0, 128, 255)
HIGHLIGHT_COLOR = (255, 255, 0)  # Yellow for highlight

# Initialize the screen
FONT_SIZE = 100
FONT_COLOR = BLACK
# Initialize the screen and font

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Hexlooper")
clock = pygame.time.Clock()
font = pygame.font.Font(None, FONT_SIZE)

# Define the dedicated area for the text
text_area = pygame.Rect(100, 100, 150, 30)
# Hexagon drawing function


def draw_hexagon(x, y, color=GRAY):
    angle = 0
    points = []
    for _ in range(6):
        x_i = x + HEX_RADIUS * math.cos(math.radians(angle))
        y_i = y + HEX_RADIUS * math.sin(math.radians(angle))
        points.append((int(x_i), int(y_i)))
        angle += 60

    pygame.draw.polygon(screen, color, points, 2)


def find_closest_hex(x,y, hex_list):
    dist_arr = []
    for hex in hex_list:
        dist = (x - hex.center_x)**2 + (y - hex.center_y)**2
        dist_arr.append(dist)
    dist_arr = np.array(dist_arr)
    closest_hex = hex_list[(np.argmin(dist_arr))]
    return closest_hex

# Main game loop
player_position = 100
hex_track = []
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Check for left mouse button click
            mouse_x, mouse_y = event.pos
            next_hex = find_closest_hex(mouse_x, mouse_y, hex_list)
            if current_hex.is_neighbor(next_hex):
                player_position = next_hex.ix
            else:
                draw_hexagon(next_hex.center_x, next_hex.center_y, color=GRAY)
    # Draw the hexagonal grid

    #screen.fill(BLACK)
    row_step = ((3**.5)*(HEX_RADIUS)*(2/4))
    col_step = 3*HEX_RADIUS
    step = 0
    hex_list = []
    for row in range(0, HEIGHT, int(row_step)):
        step=(1-step)
        for col in range(0, WIDTH, int(col_step)):
            draw_hexagon(col + step * 1.5*(HEX_RADIUS), row)
            new_hex = Hex(ix =len(hex_list), r=HEX_RADIUS, center_x=col + step * 1.5 * HEX_RADIUS, center_y=row)
            hex_list.append(new_hex)


    text_area = pygame.Rect(100, 100, 150, 30)
    score_text = font.render(f"Score: {len(hex_track)}", True, HIGHLIGHT_COLOR)
    screen.blit(score_text, (100, 100))


    # Highlight the selected hexagon
    current_hex = hex_list[player_position]
    current_hex.visited = True
    track_step = True
    for past_hex in hex_track:
        if past_hex.ix == current_hex.ix:
            track_step = False; continue
    if track_step:
        hex_track.append(current_hex)
    print(len(hex_track))



    mouse_x, mouse_y = pygame.mouse.get_pos()
    closest_hex = find_closest_hex(mouse_x, mouse_y, hex_list)
    draw_hexagon(closest_hex.center_x, closest_hex.center_y, color=HIGHLIGHT_COLOR)

    # Update and draw player position
    draw_hexagon(current_hex.center_x, current_hex.center_y, PLAYER_COLOR)


    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()
