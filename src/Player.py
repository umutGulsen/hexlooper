import numpy as np
import seaborn as sns


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
        if random_color:
            palette = sns.color_palette("gist_rainbow", n_colors=1000)
            color_val = palette[np.random.randint(0, 1000)]
            self.player_color = [255*val for val in color_val]
            #tuple(np.random.randint(1, 256, size=3))
            self.track_color = tuple((x + y) / 2 for x, y in zip(self.player_color, (30, 30, 30)))
        else:
            self.player_color = (153, 0, 0)
            self.track_color = self.player_color#tuple((x + y) / 2 for x, y in zip(self.player_color, (80, 80, 80)))#(102, 153, 255)


    def generate_random_moves(self, move_count: int):
        self.move_list = ((np.random.rand(move_count) * 6 + 1).astype(int))
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
