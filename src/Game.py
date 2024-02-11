from Player import Player
import numpy as np
import pygame
import math
from Hex import Hex
import functools
import logging

class Game(object):

    def __init__(self, player_count: int, board_config, player_starting_positions="random", random_move_count=0,
                 turn_limit=None, colors=None, move_generation_type="fixed", game_mode: str = "default",
                 random_player_colors=False, layer_sizes=[1]):
        if colors is None:
            colors = {}
        row_step = int((3 ** .5) * board_config["hex_radius"] * (2 / 4))
        col_step = int(3 * board_config["hex_radius"])
        hex_count = int((board_config["height"] / row_step - 4) * (board_config["width"] / col_step - 7))
        self.players = []
        self.move_generation_type = move_generation_type
        for i in range(player_count):
            pos = int(np.random.rand() * hex_count) if player_starting_positions == "random" else int(.5 * hex_count)
            new_player = Player(id=i, pos=pos, random_color=random_player_colors)
            if self.move_generation_type == "list":
                new_player.generate_random_moves(random_move_count)
            else:
                self.layer_sizes = layer_sizes
            self.players.append(new_player)

        self.turn = 0
        self.turn_limit = turn_limit if move_generation_type != "list" else random_move_count
        self.game_mode = game_mode
        self.hex_list = []
        self.base_game_state = None
        self.board_config = board_config
        self.colors = colors
        self.screen = pygame.display.set_mode((self.board_config["width"], self.board_config["height"]))
        pygame.init()
        self.player_num_font = pygame.font.Font(None, 25)
        self.scoreboard_font = pygame.font.Font(None, 26)

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
        self.hex_list: list[Hex] = []
        for row in range(2 * row_step, height - 2 * row_step, row_step):
            step = (1 - step)
            for col in range(1 * col_step, width - 6 * col_step, col_step):
                self.draw_hexagon(col + step * 1.5 * hex_radius, row, r=self.board_config["hex_radius"],
                                  edge_color=self.colors["GRAY"], fill_color=self.colors["BLACK"])
                new_hex = Hex(ix=len(self.hex_list), r=hex_radius,
                              center_x=col + step * 1.5 * self.board_config["hex_radius"],
                              center_y=row)
                self.hex_list.append(new_hex)
        return self.hex_list

    def draw_track(self, p):
        if len(p.track) > 1:
            points = []

            for hex_pos in p.track:
                hex_in_track = self.hex_list[hex_pos]
                x, y = hex_in_track.center_x, hex_in_track.center_y
                points.append((x, y))

            pygame.draw.polygon(self.screen, p.player_color, points, 2)

    def draw_player_related_hexes(self, p):
        track_len = len(p.track)
        for i, hex_pos in enumerate(p.track):
            hex_in_track = self.hex_list[hex_pos]
            self.draw_hexagon(hex_in_track.center_x, hex_in_track.center_y,
                              self.board_config["hex_radius"] / 3,
                              edge_color=self.colors["GRAY"], fill_color=p.track_color)

        self.draw_hexagon(self.hex_list[p.nest].center_x, self.hex_list[p.nest].center_y,
                          self.board_config["hex_radius"], edge_color=self.colors["GRAY"],
                          fill_color=self.colors["BLACK"])

        self.draw_hexagon(self.hex_list[p.nest].center_x, self.hex_list[p.nest].center_y,
                          self.board_config["hex_radius"] / 2, edge_color=self.colors["GRAY"],
                          fill_color=self.colors["GREEN"])

        self.draw_hexagon(self.hex_list[p.pos].center_x, self.hex_list[p.pos].center_y, self.board_config["hex_radius"],
                          edge_color=self.colors["GRAY"], fill_color=p.player_color)
        self.draw_track(p)

    def display_game(self, players, highlight=False):
        self.screen.fill(self.colors["BLACK"])
        self.hex_list = self.draw_hexgrid(height=self.board_config["height"], width=self.board_config["width"],
                                          hex_radius=self.board_config["hex_radius"])

        for p in players:
            # text_area = pygame.Rect(500, 100, 30, 30)
            score_text = self.scoreboard_font.render(f"Score: P{p.id}: {p.score} ({p.track_score})", True,
                                                     p.player_color)
            self.draw_player_related_hexes(p)
            self.screen.blit(score_text, (835, 10 + 20 * p.id))
            id_text = self.player_num_font.render(f"{p.id}", True, self.colors["BLACK"])
            self.screen.blit(id_text,
                             (self.hex_list[p.pos].center_x - self.board_config["hex_radius"] / 2.2,
                              self.hex_list[p.pos].center_y - (self.board_config["hex_radius"] * .8)))

        if highlight:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            closest_hex = self.find_closest_hex(mouse_x, mouse_y)
            self.draw_hexagon(closest_hex.center_x, closest_hex.center_y, self.board_config["hex_radius"],
                              edge_color=self.colors["HIGHLIGHT_COLOR"], fill_color=self.colors["HIGHLIGHT_COLOR"])
        return self.hex_list

    @functools.lru_cache(maxsize=None)
    def find_closest_hex(self, x, y):
        for hex in self.hex_list:
            dist = (x - hex.center_x) ** 2 + (y - hex.center_y) ** 2
            if dist < hex.r ** 2 / 3:
                return hex
        return None

    def execute_move(self, move: int, p):
        change_happened = False
        current_hex = self.hex_list[p.pos]
        new_x, new_y = current_hex.generate_move_from_code(move)
        next_hex = self.find_closest_hex(new_x, new_y)
        if next_hex is not None:
            backtrack = p.player_game_state[next_hex.ix, 6] - p.player_game_state[next_hex.ix, 4]
            occupied = self.game_mode != "coexist" and (self.base_game_state[next_hex.ix, 2])
            neighbored = current_hex.is_neighbor(next_hex)
        else:
            neighbored, backtrack, occupied = False, False, False
        if neighbored:
            if not backtrack and not occupied:
                p.move(next_hex.ix)
                change_happened = True
                if self.game_mode != "coexist" and self.base_game_state[next_hex.ix, 3]:
                    for other_p in self.players:
                        if other_p.player_game_state[next_hex.ix, 6]:
                            other_p.crash_track()
                            break
            elif backtrack:
                p.consec_stalls += 1
        if p.consec_stalls > 20:  # TODO parametrize this
            p.crash_track()
            change_happened = True
        return change_happened

    def update_base_game_state(self):
        self.base_game_state = np.zeros((len(self.hex_list), 7))
        for p in self.players:
            self.base_game_state[p.nest, 1] = 1
            self.base_game_state[p.pos, 2] = 1
            self.base_game_state[p.track, 3] = 1
        self.base_game_state[:, 0] = (1 - np.sum(self.base_game_state[:, [1, 2, 3]], axis=1)).clip(min=0)
        for p in self.players:
            p.update_game_state(self.base_game_state)

        #logging.debug(self.base_game_state)
        #logging.debug(f"{np.sum(self.base_game_state[:, 0])} hexes are empty")
        #logging.debug(f"{np.sum(self.base_game_state[:, 1])} hexes have nests")
        #logging.debug(f"{np.sum(self.base_game_state[:, 2])} hexes have players")
        #ogging.debug(f"{np.sum(self.base_game_state[:, 3])} hexes are tracks")

    def run_game(self, fps=64, display_interval: int = 1, wait_for_user=False, show_first_frame=True):
        pygame.init()
        running = True
        pygame.display.set_caption("Hexlooper")
        clock = pygame.time.Clock()
        first = True

        while running:
            show_this_time = self.turn % display_interval == 0 or (first and show_first_frame)
            if show_this_time:
                self.hex_list = self.display_game(players=self.players, highlight=False)
                if first:
                    self.update_base_game_state()
                    if self.move_generation_type == "network":
                        for p in self.players:
                            dims = {"n_hexes": len(self.hex_list),
                                    "hex_state": 7,
                                    "action_count": 6}
                            p.initialize_network(dims, self.layer_sizes)
                first = False

            for p in self.players:
                end_of_turn = (self.turn_limit is not None and self.turn >= self.turn_limit)
                next_move = p.generate_move(generation_type=self.move_generation_type)
                move_is_feasible = next_move is not None
                if not end_of_turn and move_is_feasible:
                    change_happened = self.execute_move(next_move, p)
                    if change_happened:
                        self.update_base_game_state()
                else:
                    if not wait_for_user:
                        if end_of_turn:
                            running = False
                    else:
                        for event in pygame.event.get():
                            if event.type == pygame.QUIT:
                                running = False
                            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                                mouse_x, mouse_y = event.pos
                                next_hex = self.find_closest_hex(mouse_x, mouse_y)
                                if next_hex is None:
                                    continue
                                for p_ in self.players:
                                    current_hex = self.hex_list[p_.pos]
                                    backtrack = any(next_hex.ix == hex_pos for hex_pos in p_.track)
                                    occupied = any(next_hex.ix == other_p.pos for other_p in self.players)
                                    if current_hex.is_neighbor(next_hex) and (
                                            not backtrack or next_hex.ix == p_.nest) and not occupied:
                                        p_.move(next_hex.ix)
                                        self.update_base_game_state()
                                        current_hex.find_move_code(next_hex)
                                        if self.base_game_state[next_hex.ix, 3] == 1:
                                            for other_p in self.players:
                                                if p_.id != other_p.id and any(
                                                        next_hex.ix == hex_pos for hex_pos in other_p.track):
                                                    other_p.crash_track()
                                        break
                                    else:
                                        logging.info(
                                            f"Cannot move to that hex!(is neighbor:{current_hex.is_neighbor(next_hex)}   {backtrack=}")
            if show_this_time:
                pygame.display.flip()
            clock.tick(fps)
            self.turn = (self.turn + 1) % int(1e6)

    def find_winner(self):
        max_score = -1
        champion = None
        for p in self.players:
            if p.score > max_score:
                max_score = p.score
                champion = p
        return champion, max_score

    def mutate_moves(self, move_list, mut_chance):
        for p in self.players:
            p.mutate_random_moves(move_list, per_move_mutation_chance=mut_chance)
