class Player():
    def __init__(self, id, pos):
        self.id = id
        self.pos = pos
        self.nest = pos
        self.track = [pos]
        self.score = 0
        self.track_score = 0

    def complete_loop(self):
        self.track = [self.nest]
        self.score += self.track_score
        self.track_score = 0

    def move(self, next_pos):
        self.pos = next_pos
        if next_pos == self.nest:
            self.complete_loop()
        else:
            self.track_score += len(self.track)-1
            self.track.append(next_pos)

