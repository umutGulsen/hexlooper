import numpy as np
import seaborn as sns
import logging
logging.basicConfig(level=logging.INFO)

class Player():
    def __init__(self, id, pos, random_color=False):
        self.id = id
        self.pos = pos
        self.nest = pos
        self.track = [pos]
        self.score = 0
        self.track_score = 0
        self.consec_stalls = 0
        self.move_list = []
        self.static_move_list = []
        self.player_game_state = None
        if random_color:
            palette = sns.color_palette("Spectral", n_colors=200)
            color_val = palette[np.random.randint(0, 200)]
            self.player_color = [255*val for val in color_val]
            #tuple(np.random.randint(1, 256, size=3))
            self.track_color = tuple((x + y) / 2 for x, y in zip(self.player_color, (30, 30, 30)))
        else:
            self.player_color = (153, 0, 0)
            self.track_color = self.player_color#tuple((x + y) / 2 for x, y in zip(self.player_color, (80, 80, 80)))#(102, 153, 255)

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

    def complete_loop(self):
        self.track = [self.nest]
        self.score += self.track_score
        self.track_score = 0

    def move(self, next_pos):
        self.pos = next_pos
        if next_pos == self.nest:
            self.complete_loop()
        else:
            self.track_score += len(self.track)
            self.track.append(next_pos)
        self.consec_stalls = 0

    def crash_track(self):
        self.nest = self.pos
        self.track = [self.nest]
        self.track_score = 0

    def generate_move(self, generation_type: str):
        if generation_type == "list":
            if len(self.move_list) == 0:
                return None
            m = self.move_list[-1]
            self.move_list = self.move_list[:-1]
            return m
        if generation_type == "fixed":
            return int(1)

    def update_game_state(self, base_game_state):
        self.player_game_state = base_game_state.copy()
        self.player_game_state[self.nest, 1] = 0
        self.player_game_state[self.pos, 2] = 0
        self.player_game_state[self.track, 3] = 0

        self.player_game_state[self.nest, 1+3] = 1
        self.player_game_state[self.pos, 2+3] = 1
        self.player_game_state[self.track, 3+3] = 1

        logging.debug(self.id)
        logging.debug(self.player_game_state)
        logging.debug(f"{np.sum(self.player_game_state[:,0])} hexes are empty")
        logging.debug(f"{np.sum(self.player_game_state[:, 1])} hexes have nests")
        logging.debug(f"{np.sum(self.player_game_state[:, 2])} hexes have players")
        logging.debug(f"{np.sum(self.player_game_state[:, 3])} hexes are tracks")

        logging.debug(f"{np.sum(self.player_game_state[:, 4])} hexes are my nests")
        logging.debug(f"{np.sum(self.player_game_state[:, 5])} hexes my players")
        logging.debug(f"{np.sum(self.player_game_state[:, 6])} hexes my tracks")