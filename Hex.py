class Hex():
    def __init__(self, ix, r=None, center_x=None, center_y=None, bottom_left_x=None, bottom_left_y=None):
        self.ix = ix
        self.r = r
        self.center_x = center_x
        self.center_y = center_y
        self.visited = False
        #self.bottom_left_x = bottom_left_x
        #self.bottom_left_y = bottom_left_y

    def derive_centerpoint(self):
        self.center_x = self.bottom_left_x #+ self.r / 2
        self.center_y = self.bottom_left_y #+ self.r * (3 ** .5) * .5

    def is_neighbor(self, other_hex: object) -> bool:
        x1, y1 = self.center_x, self.center_y
        x2, y2 = other_hex.center_x, other_hex.center_y
        dist = ((x1 - x2)**2 + (y1 - y2)**2)**.5
        exp_dist = self.r * (3 ** .5)
        #print(dist, exp_dist)
        return abs(dist - exp_dist) < self.r / 10
