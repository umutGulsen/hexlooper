import numpy as np
import seaborn as sns
import logging
from Network import Network
from utils import distance_between_hexes

class Player:
    def __init__(self, player_id, pos, random_color=False, layer_activation=""):
        self.id = player_id
        self.pos = pos
        self.nest = pos
        self.track = [pos]
        self.reward = 0
        self.score = 0
        self.track_score = 0
        self.consec_stalls = 0
        self.move_list = []
        self.network = None
        self.layer_activation = layer_activation
        self.static_move_list = []
        self.player_game_state = None
        if random_color:
            palette = sns.color_palette("Spectral", n_colors=200)
            color_val = palette[np.random.randint(0, 200)]
            self.player_color = [255 * val for val in color_val]
            self.track_color = tuple((x + y) / 2 for x, y in zip(self.player_color, (30, 30, 30)))
        else:
            self.player_color = (153, 0, 0)
            self.track_color = self.player_color

    def generate_random_moves(self, move_count: int):
        self.move_list = ((np.random.rand(move_count) * 6).astype(int))
        self.static_move_list = self.move_list

    def mutate_random_moves(self, move_list, per_move_mutation_chance: float = .001):
        new_move_list = []
        for i, move in enumerate(move_list):
            if np.random.rand() < per_move_mutation_chance:
                shift = np.random.randint(1, 6)
                new_move_list.append((move + shift) % 6)
            else:
                new_move_list.append(move)
        self.move_list = new_move_list
        self.static_move_list = new_move_list

    def initialize_network(self, dims: dict, layer_sizes=None, game_mode=""):
        if layer_sizes is None:
            layer_sizes = [1]
        if game_mode == "coexist":
            input_size = dims["n_hexes"] * (dims["hex_state"] - 5)
        else:
            input_size = dims["n_hexes"] * dims["hex_state"]
        layer_sizes.append(dims["action_count"])
        self.network = Network(layer_sizes, input_size, activator=self.layer_activation)

    def complete_loop(self):
        self.track = [self.nest]
        self.score += self.track_score
        self.track_score = 0

    def move(self, next_pos, hex_list):
        self.pos = next_pos
        if next_pos == self.nest:
            self.complete_loop()
        else:
            self.track_score += len(self.track)
            self.track.append(next_pos)
        self.consec_stalls = 0
        self.reward = self.score
        if not self.pos == self.nest:
            ...
            self.reward += .000001 * hex_list[self.pos].r * self.track_score / distance_between_hexes(hex_list[self.pos], hex_list[self.nest])

    def crash_track(self):
        self.nest = self.pos
        self.track = [self.nest]
        self.track_score = 0
        #self.reward /= 2

    def generate_move_from_fixed_list(self):
        if len(self.move_list) == 0:
            return None
        m = self.move_list[-1]
        self.move_list = self.move_list[:-1]
        return m

    def generate_move_from_network(self, x):
        output = self.network.forward_prop(x)
        logging.debug(f"{output=}")
        return np.argsort(-output.flatten())

    def generate_move(self, generation_type: str, game_mode):
        if generation_type == "list":
            return self.generate_move_from_fixed_list()
        # TODO give turn limit and count as inputs
        elif generation_type == "network":
            if game_mode == "coexist":
                relevant_game_state = self.player_game_state[:, [4, 6]]
            else:
                relevant_game_state = self.player_game_state
            input_x = relevant_game_state.reshape(relevant_game_state.shape[0] * relevant_game_state.shape[1], 1)
            return self.generate_move_from_network(x=input_x)

        elif generation_type == "fixed":
            return int(1)

    def update_game_state(self, base_game_state):
        self.player_game_state = base_game_state.copy()
        self.player_game_state[self.nest, 1] = 0
        self.player_game_state[self.pos, 2] = 0
        self.player_game_state[self.track, 3] = 0

        self.player_game_state[self.nest, 1 + 3] = 1
        self.player_game_state[self.pos, 2 + 3] = 1
        self.player_game_state[self.track, 3 + 3] = 1

        # logging.debug(self.id)
        # logging.debug(self.player_game_state)
        logging.debug(f"{np.sum(self.player_game_state[:, 0])} hexes are empty")
        logging.debug(f"{np.sum(self.player_game_state[:, 1])} hexes have nests")
        logging.debug(f"{np.sum(self.player_game_state[:, 2])} hexes have players")
        logging.debug(f"{np.sum(self.player_game_state[:, 3])} hexes are tracks")

        logging.debug(f"{np.sum(self.player_game_state[:, 4])} hexes are my nests")
        logging.debug(f"{np.sum(self.player_game_state[:, 5])} hexes my players")
        logging.debug(f"{np.sum(self.player_game_state[:, 6])} hexes my tracks")
