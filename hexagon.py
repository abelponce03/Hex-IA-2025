import math
from config import WIDTH, HEIGHT

class Hexagon:
    HEX_SIZE = None  # Variable de clase compartida para todos los hexágonos

    def __init__(self, q, r):
        self.q = q
        self.r = r
        self.color = None
        self._pixel_pos = None
        
    @classmethod
    def reset_hex_size(cls):  
        cls.HEX_SIZE = None
        cls._pixel_pos = None
        
    @classmethod
    def calculate_hex_size(cls, hexagons):
        max_dim = max(max(abs(h.q), abs(h.r)) for h in hexagons)
        base_size = min(
            WIDTH / (max_dim * 1.05 * 2),
            HEIGHT / (max_dim * 1.05 * 2)
        )
        return max(int(base_size), 2)

    def get_pixel_position(self, board):
        if Hexagon.HEX_SIZE is None:
            max_dim = max(max(abs(h.q), abs(h.r)) for h in board.values())
            
            # Cálculo base con límite mínimo
            base_size = min(
                WIDTH / (max_dim * 1.05 * 2),
                HEIGHT / (max_dim * 1.05 * 2)
            )
            Hexagon.HEX_SIZE = max(int(base_size), 2)
        
        if not self._pixel_pos:
            center_x = WIDTH // 2
            center_y = HEIGHT // 2
            x = center_x + Hexagon.HEX_SIZE * math.sqrt(3) * (self.q + self.r / 2)
            y = center_y + Hexagon.HEX_SIZE * 1.5 * self.r
            self._pixel_pos = (x, y)
        return self._pixel_pos