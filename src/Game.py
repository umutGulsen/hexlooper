from Player import Player
import numpy as np
import pygame
from Board import Board
from utils import find_closest_hex
import logging
import copy


class Game(object):

    def __init__(self, player_count: int, board_config, generation="NA", player_starting_positions="random", move_count=0,
                 turn_limit=None, colors=None, move_generation_type="fixed", game_mode: str = "default",
                 random_player_colors=False, layer_sizes=None, base_network=None, network_update_variance=1, stagnant_network_update_variance=5,
                 layer_activation="", frozen_networks=[], ne_stagnancy=False, trial=0):

        row_step = int((3 ** .5) * board_config["hex_radius"] * (2 / 4))
        col_step = int(3 * board_config["hex_radius"])
        hex_count = 0
        for row in range(2 * row_step, board_config["height"] - 2 * row_step, row_step):
            for col in range(int(.6 * col_step), board_config["width"] - 240, col_step):
                hex_count += 1
        #hex_count = int((board_config["height"] / row_step) * (board_config["width"] / col_step))
        self.players = []
        self.generation = generation
        self.move_generation_type = move_generation_type
        #layer_sizes.append(6)
        random_hex = int(hex_count * trial / (trial + 1))
        #int(np.random.rand() * hex_count)#int(.5 * hex_count)
        for i in range(player_count):
            if game_mode == "coexist":
                pos = random_hex if player_starting_positions == "random" else int(.5 * hex_count)
            else:
                pos = int(np.random.rand() * hex_count) if player_starting_positions == "random" else int(
                    .5 * hex_count)
            new_player = Player(player_id=i, pos=pos, random_color=random_player_colors,
                                layer_activation=layer_activation)
            if self.move_generation_type == "list":
                new_player.generate_random_moves(move_count)
            else:
                self.layer_sizes = layer_sizes
                self.base_network = base_network
                if ne_stagnancy:
                    self.network_update_variance = stagnant_network_update_variance
                else:
                    self.network_update_variance = network_update_variance

            self.players.append(new_player)

        self.turn = 0
        self.turn_limit = turn_limit if move_generation_type != "list" else move_count
        self.game_mode = game_mode
        self.hex_list = []
        self.base_game_state = None
        self.frozen_networks = frozen_networks
        self.board = Board(board_config, colors)
        self.hex_radius = board_config["hex_radius"]

    def execute_move_from_candidates(self, possible_moves, p):
        change_happened = False
        current_hex = self.hex_list[p.pos]
        for move in possible_moves:
            new_x, new_y = current_hex.generate_move_from_code(move)
            next_hex = find_closest_hex(self.hex_list, new_x, new_y)

            if next_hex is not None:
                backtrack = p.player_game_state[next_hex.ix, 6] - p.player_game_state[next_hex.ix, 4]
                occupied = self.game_mode != "coexist" and (self.base_game_state[next_hex.ix, 2])
                neighbored = current_hex.is_neighbor(next_hex)

                if neighbored and not backtrack and not occupied:
                    p.move(next_hex.ix, self.hex_list, self.hex_radius)
                    change_happened = True
                    if self.game_mode != "coexist" and self.base_game_state[next_hex.ix, 3]:
                        for other_p in self.players:
                            if other_p.player_game_state[next_hex.ix, 6]:
                                other_p.crash_track()
                                break
                    break

        else:
            p.consec_stalls += 1
            if p.consec_stalls > 20:  # TODO parametrize this
                p.crash_track()
                change_happened = True
        return change_happened

    def execute_move(self, move: int, p):
        change_happened = False
        current_hex = self.hex_list[p.pos]
        new_x, new_y = current_hex.generate_move_from_code(move)
        next_hex = find_closest_hex(self.hex_list, new_x, new_y)

        if next_hex is not None:
            backtrack = p.player_game_state[next_hex.ix, 6] - p.player_game_state[next_hex.ix, 4]
            occupied = self.game_mode != "coexist" and (self.base_game_state[next_hex.ix, 2])
            neighbored = current_hex.is_neighbor(next_hex)

        else:
            neighbored, backtrack, occupied = False, False, False

        if neighbored:
            if not backtrack and not occupied:
                p.move(next_hex.ix, self.hex_list, self.hex_radius)
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

    def update_base_game_state(self, moved_player=None):
        self.base_game_state = np.zeros((len(self.hex_list), 7))
        if self.game_mode != "coexist" or moved_player is None:
            for p in self.players:
                self.base_game_state[p.nest, 1] = 1
                self.base_game_state[p.pos, 2] = 1
                self.base_game_state[p.track, 3] = 1
            self.base_game_state[:, 0] = (1 - np.sum(self.base_game_state[:, [1, 2, 3]], axis=1)).clip(min=0)

            for p in self.players:

                p.update_game_state(self.base_game_state, self.hex_list)

        else:
            moved_player.update_game_state(self.base_game_state, self.hex_list)

        # logging.debug(self.base_game_state)
        # logging.debug(f"{np.sum(self.base_game_state[:, 0])} hexes are empty")
        # logging.debug(f"{np.sum(self.base_game_state[:, 1])} hexes have nests")
        # logging.debug(f"{np.sum(self.base_game_state[:, 2])} hexes have players")
        # logging.debug(f"{np.sum(self.base_game_state[:, 3])} hexes are tracks")

    def set_up_networks(self):
        for i, p in enumerate(self.players):
            dims = {"n_hexes": len(self.hex_list),
                    "hex_state": 7,
                    "action_count": 6}
            if len(self.frozen_networks) == 0:
                p.initialize_network(dims, self.layer_sizes, self.game_mode)
                if self.base_network is not None:
                    p.network = copy.deepcopy(self.base_network)

                p.network.randomly_initialize_params(self.network_update_variance)
            else:
                p.network = copy.deepcopy(self.frozen_networks[i])

    def apply_manual_click_to_move(self, event, last_moved_player):
        mouse_x, mouse_y = event.pos
        next_hex = find_closest_hex(self.hex_list, mouse_x, mouse_y)
        if next_hex is None:
            return last_moved_player
        if last_moved_player != -1 or last_moved_player != len(self.players):
            order_check_list = self.players[last_moved_player + 1:] + self.players[
                                                                      :last_moved_player + 1]
        else:
            order_check_list = self.players
        for p_ in order_check_list:
            current_hex = self.hex_list[p_.pos]
            backtrack = any(next_hex.ix == hex_pos for hex_pos in p_.track)
            occupied = any(next_hex.ix == other_p.pos for other_p in self.players)
            if current_hex.is_neighbor(next_hex) and (
                    not backtrack or next_hex.ix == p_.nest) and not occupied:
                p_.move(next_hex.ix, self.hex_list, self.hex_radius)
                last_moved_player = p_.id
                self.update_base_game_state(p_)
                current_hex.find_move_code(next_hex)
                if self.base_game_state[next_hex.ix, 3] == 1:
                    for other_p in self.players:
                        if p_.id != other_p.id and any(
                                next_hex.ix == hex_pos for hex_pos in other_p.track):
                            other_p.crash_track()
                break
            else:
                logging.info(
                    f"Cannot move to that hex!(is neighbor:{current_hex.is_neighbor(next_hex)}  {backtrack=}")
        return last_moved_player

    def run_game(self, fps=64, display_interval: int = 1, wait_for_user=False, show_first_frame=True):
        pygame.init()
        running = True
        last_moved_player = -1
        pygame.display.set_caption("Hexlooper")
        if fps < 1000:
            clock = pygame.time.Clock()
        first = True

        while running:
            show_this_time = self.turn % display_interval == 0 or (first and show_first_frame)
            if show_this_time:
                self.hex_list = self.board.display_game(players=self.players, generation=self.generation, highlight=False)
                if first:
                    self.update_base_game_state()
                    if self.move_generation_type == "network":
                        self.set_up_networks()
                first = False

            for p in self.players:
                end_of_turn = (self.turn_limit is not None and self.turn >= self.turn_limit)
                next_move = p.generate_move(generation_type=self.move_generation_type, game_mode=self.game_mode)

                move_is_feasible = next_move is not None
                if not end_of_turn and move_is_feasible:
                    if self.move_generation_type == "network":
                        change_happened = self.execute_move_from_candidates(next_move, p)
                    else:
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
                                last_moved_player = self.apply_manual_click_to_move(event, last_moved_player)


            if show_this_time:
                pygame.display.flip()
            if fps < 1000:
                clock.tick(fps)
            self.turn = (self.turn + 1) % int(1e6)

        if self.game_mode == "just_play":
            self.display_scores()

    def find_winner(self, generation_rewards=[]):
        max_score = -1
        champion = None
        if len(generation_rewards) == 0:
            for p in self.players:
                if p.reward > max_score:
                    max_score = p.reward
                    champion = p
            return champion, max_score
        else:
            for i, p in enumerate(self.players):
                if generation_rewards[i] > max_score:
                    max_score = generation_rewards[i]
                    champion = p
            return champion, generation_rewards[i]

    def mutate_moves(self, move_list, mut_chance):
        for p in self.players:
            p.mutate_random_moves(move_list, per_move_mutation_chance=mut_chance)

    def display_scores(self):
        for p in self.players:
            print(f"{p.id}: {p.score} ({p.track_score})")
