import functools


@functools.lru_cache(maxsize=None)
def distance(x1, y1, x2, y2):
    return ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** .5


@functools.lru_cache(maxsize=None)
def distance_between_hexes(hex1, hex2):
    x1, y1 = hex1.center_x, hex1.center_y
    x2, y2 = hex2.center_x, hex2.center_y
    return distance(x1, y1, x2, y2)


@functools.lru_cache(maxsize=None)
def find_closest_hex(hex_list, x, y):
    for hex1 in hex_list:
        dist = distance(x, y, hex1.center_x, hex1.center_y)
        if dist < hex1.r ** 2 / 3:
            return hex1
    return None
