import math
from typing import Tuple
import functools
import logging


class Hex:
    """Class representing a hexagon.

    Attributes:
        ix (int): Index of the hexagon.
        r (float): Radius of the hexagon.
        center_x (float): x-coordinate of the center of the hexagon.
        center_y (float): y-coordinate of the center of the hexagon.
        visited (bool): Flag indicating whether the hexagon has been visited.
    """
    logging.basicConfig(level=logging.WARNING, format='%(asctime)s - %(levelname)s - %(message)s')

    def __init__(self, ix: int, r: float = None, center_x: float = None, center_y: float = None):
        """Initialize a Hex object.

        Args:
            ix (int): Index of the hexagon.
            r (float): Radius of the hexagon.
            center_x (float): x-coordinate of the center of the hexagon.
            center_y (float): y-coordinate of the center of the hexagon.
        """
        self.ix = ix
        self.r = r
        self.center_x = center_x
        self.center_y = center_y
        self.visited = False

    @functools.lru_cache(maxsize=None)
    def is_neighbor(self, other_hex: 'Hex') -> bool:
        """Check if another hexagon is a neighbor of the current hexagon.

        Args:
            other_hex (Hex): Another hexagon to check for neighbor relationship.

        Returns:
            bool: True if the hexagons are neighbors, False otherwise.
        """
        x1, y1 = self.center_x, self.center_y
        x2, y2 = other_hex.center_x, other_hex.center_y
        dist = ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5
        exp_dist = self.r * (3 ** 0.5)
        return abs(dist - exp_dist) < self.r / 3

    def find_move_code(self, other_hex: 'Hex') -> None:
        """Find the move code based on the relative position of another hexagon.

        Args:
            other_hex (Hex): Another hexagon to determine the move code for.
        """
        small_val = self.r / 10
        x_diff = other_hex.center_x - self.center_x
        y_diff = other_hex.center_y - self.center_y
        y_diff *= -1  # Correcting for consistency
        if abs(x_diff) < small_val:
            if y_diff > 0:
                code = 2
            else:
                code = 5
        elif x_diff > 0:
            if y_diff > 0:
                code = 1
            else:
                code = 6
        else:
            if y_diff > 0:
                code = 3
            else:
                code = 4

        logging.info(code)

    def generate_move_from_code(self, code: int) -> Tuple[float, float]:
        """Generate new coordinates based on the move code.

        Args:
            code (int): Move code indicating the direction.

        Returns:
            Tuple[float, float]: New x, y coordinates.
        """
        angle = -30 + code * 60
        new_x = self.center_x + 2 * self.r * math.cos(math.radians(angle))
        new_y = self.center_y - 2 * self.r * math.sin(math.radians(angle))
        return new_x, new_y
