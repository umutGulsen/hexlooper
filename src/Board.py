import pygame
from Hex import Hex
import math
from utils import find_closest_hex

class Board:

    def __init__(self, board_config, colors):
        self.board_config = board_config
        self.colors = colors
        self.screen = pygame.display.set_mode((board_config["width"], board_config["height"]))
        pygame.init()
        self.player_num_font = pygame.font.Font(None, board_config["player_num_fontisze"])
        self.scoreboard_font = pygame.font.Font(None, board_config["score_board_font"])

    def draw_hexagon(self, x, y, r=1, edge_color=(30, 30, 30), fill_color=(200, 200, 200)):
        angle = 0
        points = []
        for _ in range(6):
            x_i = x + r * math.cos(math.radians(angle))
            y_i = y + r * math.sin(math.radians(angle))
            points.append((int(x_i), int(y_i)))
            angle += 60

        pygame.draw.polygon(self.screen, fill_color, points, 0)
        pygame.draw.polygon(self.screen, edge_color, points, max(1, int(r / 5)))

    def draw_hexgrid(self, height, width, hex_radius) -> list[Hex]:
        row_step = int((3 ** .5) * hex_radius * (2 / 4))
        col_step = int(3 * hex_radius)
        step = 0
        hex_list: list[Hex] = []
        for row in range(2 * row_step, height - 2 * row_step, row_step):
            step = (1 - step)
            for col in range(1 * col_step, width - 6 * col_step, col_step):
                self.draw_hexagon(col + step * 1.5 * hex_radius, row, r=self.board_config["hex_radius"],
                                  edge_color=self.colors["GRAY"], fill_color=self.colors["BLACK"])
                new_hex = Hex(ix=len(hex_list), r=hex_radius,
                              center_x=col + step * 1.5 * self.board_config["hex_radius"],
                              center_y=row)
                hex_list.append(new_hex)
        return hex_list

    def draw_track(self, p, hex_list):
        if len(p.track) > 1:
            points = []

            for hex_pos in p.track:
                hex_in_track = hex_list[hex_pos]
                x, y = hex_in_track.center_x, hex_in_track.center_y
                points.append((x, y))

            pygame.draw.polygon(self.screen, p.player_color, points, 2)

    def draw_player_related_hexes(self, hex_list, p):
        for i, hex_pos in enumerate(p.track):
            hex_in_track = hex_list[hex_pos]
            self.draw_hexagon(hex_in_track.center_x, hex_in_track.center_y,
                              self.board_config["hex_radius"] / 3,
                              edge_color=self.colors["GRAY"], fill_color=p.track_color)

        self.draw_hexagon(hex_list[p.nest].center_x, hex_list[p.nest].center_y,
                          self.board_config["hex_radius"], edge_color=self.colors["GRAY"],
                          fill_color=self.colors["BLACK"])

        self.draw_hexagon(hex_list[p.nest].center_x, hex_list[p.nest].center_y,
                          self.board_config["hex_radius"] / 2, edge_color=self.colors["GRAY"],
                          fill_color=self.colors["GREEN"])

        self.draw_hexagon(hex_list[p.pos].center_x, hex_list[p.pos].center_y, self.board_config["hex_radius"],
                          edge_color=self.colors["GRAY"], fill_color=p.player_color)
        self.draw_track(p, hex_list)

    def display_game(self, players, highlight=False):
        self.screen.fill(self.colors["BLACK"])
        hex_list = self.draw_hexgrid(height=self.board_config["height"], width=self.board_config["width"],
                                     hex_radius=self.board_config["hex_radius"])

        for p in players:
            # text_area = pygame.Rect(500, 100, 30, 30)
            score_text = self.scoreboard_font.render(f"Score: P{p.id}: {p.score} ({p.track_score})", True,
                                                     p.player_color)
            self.draw_player_related_hexes(hex_list, p)
            self.screen.blit(score_text, (835, 10 + 20 * p.id))
            id_text = self.player_num_font.render(f"{p.id}", True, self.colors["BLACK"])
            self.screen.blit(id_text,
                             (hex_list[p.pos].center_x - self.board_config["hex_radius"] / 2.2,
                              hex_list[p.pos].center_y - (self.board_config["hex_radius"] * .8)))

        if highlight:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            closest_hex = find_closest_hex(mouse_x, mouse_y)
            self.draw_hexagon(closest_hex.center_x, closest_hex.center_y, self.board_config["hex_radius"],
                              edge_color=self.colors["HIGHLIGHT_COLOR"], fill_color=self.colors["HIGHLIGHT_COLOR"])
        return tuple(hex_list)
