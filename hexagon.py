import math
from config import  HEX_SIZE

class Hexagon:
    def __init__(self, q, r):
        self.q = q
        self.r = r
        self.color = None
        self._pixel_pos = None  # Cachear posición

    def get_pixel_position(self):
        if not self._pixel_pos:  # Calcular solo una vez
            x = HEX_SIZE * (math.sqrt(3) * self.q + math.sqrt(3)/2 * self.r)
            y = HEX_SIZE * (3/2 * self.r)
            self._pixel_pos = (x + 750, y + 100)
        return self._pixel_pos