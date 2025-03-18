import pygame
import math
from config import  HEX_SIZE, COLORS
from hexagon import Hexagon

class HexagonGame:
    def __init__(self):
        self.board = {}
        self.init_board()
        self.current_player = 1
        
    def load_sounds(self):
        pygame.mixer.init()
        return {
            'place': pygame.mixer.Sound('sounds/place.wav'),
            'hover': pygame.mixer.Sound('sounds/hover.wav'),
            'click': pygame.mixer.Sound('sounds/click.wav'),
            'win': pygame.mixer.Sound('sounds/win.wav')
        }
    
    def init_board(self):
        # Patrón hexagonal concéntrico
        radius = 4
        for q in range(-radius, radius + 1):
            for r in range(max(-radius, -q - radius), min(radius, -q + radius) + 1):
                self.board[(q, r)] = Hexagon(q, r)
    
    def get_hex_at_position(self, pos):
        closest_hex = None
        min_distance = float('inf')
        
        for hex in self.board.values():
            px, py = hex.get_pixel_position()
            distance = math.hypot(px - pos[0], py - pos[1])
            if distance < min_distance and distance < HEX_SIZE * 0.9:
                min_distance = distance
                closest_hex = hex
        return closest_hex
    
    def handle_click(self, pos):
        hex = self.get_hex_at_position(pos)
        if hex and not hex.color:
            hex.color = COLORS[f'player{self.current_player}']
            self.current_player = 2 if self.current_player == 1 else 1