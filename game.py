import pygame
import math
from config import  HEX_SIZE, COLORS
from board import init_board
from win_condition import check_win

class HexagonGame:
    def __init__(self):
        self.board = init_board()
        self.current_player = 1
        self.sounds = self.load_sounds()
        self.game_over = False
        self.first_turn_blocked = True
        
    def load_sounds(self):
        pygame.mixer.init()
        return {
            'place': pygame.mixer.Sound('sounds/place.wav'),
            'hover': pygame.mixer.Sound('sounds/hover.wav'),
            'click': pygame.mixer.Sound('sounds/click.wav'),
            'win': pygame.mixer.Sound('sounds/win.wav')
        }
    
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
        if self.game_over:
            return
        
        hex = self.get_hex_at_position(pos)
        if not hex:
            return
        
         # Bloquear (-5, 5) solo en primer turno
        if self.first_turn_blocked and self.current_player == 1:
            if hex.q == -5 and hex.r == 5:
                return  # No permitir colocación
        
        
        if hex and not hex.color:
            self.sounds['click'].play()
            hex.color = COLORS[f'player{self.current_player}']
            self.sounds['place'].play()
            
            # Desactivar bloqueo después de primer turno
            self.first_turn_blocked = False
            
            if check_win(self.current_player, self.board):
                self.sounds['win'].play()
                self.game_over = True
            else:
                self.current_player = 2 if self.current_player == 1 else 1