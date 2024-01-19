class Player():
    def __init__(self, id, pos):
        self.id = id
        self.pos = pos
        self.nest = pos
        self.track = []
        self.score = 0
        self.track_score = 0

    def complete_loop(self):
        self.track = []
        self.score += self.track_score
        self.track_score = 0