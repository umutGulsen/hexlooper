import math
class Hex():
    def __init__(self, ix, r=None, center_x=None, center_y=None):
        self.ix = ix
        self.r = r
        self.center_x = center_x
        self.center_y = center_y
        self.visited = False

    def is_neighbor(self, other_hex: object) -> bool:
        x1, y1 = self.center_x, self.center_y
        x2, y2 = other_hex.center_x, other_hex.center_y
        dist = ((x1 - x2)**2 + (y1 - y2)**2)**.5
        exp_dist = self.r * (3 ** .5)
        return abs(dist - exp_dist) < self.r / 3

    def find_move_code(self, other_hex: object):
        small_val = self.r / 10
        x_diff = other_hex.center_x - self.center_x
        y_diff = other_hex.center_y - self.center_y
        y_diff *= -1 # idk why this is negative, but I fix it for consistency
        if abs(x_diff) < small_val:
            if y_diff > 0:                code = 2
            else:                code = 5
        elif x_diff > 0:
            if y_diff > 0:                code = 1
            else:                code = 6
        else:
            if y_diff > 0:                code = 3
            else:                code = 4

        print(code)

    def generate_move_from_code(self, code):
        angle = -30 + code * 60
        new_x = self.center_x + 2 * self.r * math.cos(math.radians(angle))
        new_y = self.center_y - 2 * self.r * math.sin(math.radians(angle))
        return new_x, new_y
