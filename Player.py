import numpy as np

class Player():
    def __init__(self, id, pos):
        self.id = id
        self.pos = pos
        self.nest = pos
        self.track = [pos]
        self.score = 0
        self.track_score = 0
        self.consec_stalls = 0
        self.move_list = []

    def generate_random_moves(self, move_count: int):
        self.move_list = ((np.random.rand(move_count) * 6 + 1).astype(int))

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
