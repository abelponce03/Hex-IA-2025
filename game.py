import math
from config import HEX_SIZE, COLORS
from board import init_board
from win_condition import check_win
from sounds.sounds import load_sounds
from hexagon import Hexagon
from IA.Minimax import Minimax


class HexagonGame:
    def __init__(self, vs_ai=True):
        self.board = init_board()
        self.current_player = 1
        self.sounds = load_sounds()
        self.game_over = False
        self.first_turn_blocked = True
        self.vs_ai = vs_ai
        self.move_history = []
    
    def ai_turn(self):
        if self.current_player != 2 or self.game_over or not self.vs_ai:
            return
        
        minimax = Minimax(self, depth=2)
        best_move = minimax.decision()
        if best_move:
            self.play_move(*best_move)
    
    
    def clone(self):
        cloned_game = HexagonGame(self.vs_ai)
        # Corregir la creación de hexágonos - ajustar según la definición de la clase Hexagon
        cloned_game.board = {}
        for (q, r), h in self.board.items():
            # Crear hexágonos con la cantidad correcta de parámetros
            # Opción 1: Si Hexagon recibe (q, r) y color es una propiedad
            new_hex = Hexagon(q, r)
            new_hex.color = h.color
            cloned_game.board[(q, r)] = new_hex
        
            # Opción 2: Si realmente el constructor recibe 3 argumentos
            # cloned_game.board[(q, r)] = Hexagon(q, r, h.color)
    
        # Copiar otros atributos necesarios
        cloned_game.current_player = self.current_player
        cloned_game.first_turn_blocked = self.first_turn_blocked
        cloned_game.game_over = self.game_over
    
        return cloned_game

    def play_move(self, q, r):
        hex = self.board.get((q, r))
        if hex and not hex.color:
            hex.color = COLORS[f'player{self.current_player}']
            self.move_history.append((q, r))
        
            if check_win(self.current_player, self.board):
                self.game_over = True
                self.sounds['win'].play()
            else:
                self.current_player = 3 - self.current_player  # Alternar turno
                self.first_turn_blocked = False  # Desbloquear después del primer turno
        
            return True
        return False
    
    
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
        if self.game_over or (self.vs_ai and self.current_player == 2):
            return
    
        hex = self.get_hex_at_position(pos)
        if not hex or hex.color:
            return
    
        # Validar bloqueo primer turno
        if self.first_turn_blocked and self.current_player == 1:
            if (hex.q, hex.r) == (-5, 5):
                return
    
        self.play_move(hex.q, hex.r)
                
                
