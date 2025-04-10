import math
from config import COLORS
from board import init_board
from win_condition import check_win
from sounds.sounds import load_sounds
from hexagon import Hexagon
from IA.Minimax import minimax
import threading
import queue


class HexagonGame:
    def __init__(self, vs_ai=True, board_size = 11):
        Hexagon.reset_hex_size()
        self.board_size = board_size
        self.board = init_board(self.board_size)
        self.current_player = 1
        self.sounds = load_sounds()
        self.game_over = False
        self.vs_ai = vs_ai
        self.move_history = []
        self.ai_queue = queue.Queue()
        self.ai_thinking = False
        self.transposition_table = {}  # Tabla de transposición
        
    def clone(self):
        cloned_game = HexagonGame(self.vs_ai, self.board_size)
        cloned_game.board = {pos: Hexagon(hex.q, hex.r) for pos, hex in self.board.items()}
        for pos, hex in self.board.items():
            cloned_game.board[pos].color = hex.color
        cloned_game.current_player = self.current_player
        cloned_game.game_over = self.game_over
        cloned_game.move_history = self.move_history.copy()
        return cloned_game

    def play_move(self, q, r):
        hex = self.board.get((q, r))
        if hex and not hex.color:
            hex.color = COLORS[f'player{self.current_player}']
            self.move_history.append((q, r))
            self.sounds['place'].play()
             
            if check_win(self.current_player, self.board, self.board_size):  # Pasamos board_size aquí
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
            px, py = hex.get_pixel_position(self.board)
            distance = math.hypot(px - pos[0], py - pos[1])
            if distance < min_distance and distance < hex.HEX_SIZE * 0.9:
                min_distance = distance
                closest_hex = hex
        return closest_hex
    
    def handle_click(self, pos):
        if self.game_over or (self.vs_ai and self.current_player == 2):
            return
    
        hex = self.get_hex_at_position(pos)
        if not hex or hex.color:
            return
        
        self.play_move(hex.q, hex.r)


def ai_turn(game):
    if game.ai_thinking or game.current_player != 2 or game.game_over or not game.vs_ai:
        return
    
    def ai_worker():
        try:
            import time
            global start_time
            from IA.Minimax import start_time, MAX_TIME
            
            # Reiniciar el tiempo
            start_time = time.time()
            
            # Iterative deepening con límite de tiempo
            best_move = None
            for depth in range(1, 4):  # Empezar con profundidad 1, incrementar hasta 3
                # Si ya gastamos más de la mitad del tiempo, usar el mejor movimiento encontrado
                if time.time() - start_time > MAX_TIME * 0.5 and best_move is not None:
                    break
                    
                # Intentar con la profundidad actual
                _, move = minimax(
                    game.clone(), 
                    depth=depth,
                    alpha=-float('inf'),
                    beta=float('inf'),
                    maximizing_player=True
                )
                
                # Si se encontró un movimiento válido, actualizar el mejor
                if move is not None:
                    best_move = move
                
                # Si nos estamos acercando al límite de tiempo, salir
                if time.time() - start_time > MAX_TIME * 0.8:
                    break
            
            # Si no se encontró ningún movimiento, seleccionar uno disponible
            if best_move is None:
                from random import choice
                empty_hexes = [(hex.q, hex.r) for hex in game.board.values() if not hex.color]
                if empty_hexes:
                    best_move = choice(empty_hexes)
            
            game.ai_queue.put(best_move)
        except Exception as e:
            print(f"Error en IA: {e}")
            game.ai_queue.put(None)
        finally:
            game.ai_thinking = False
    
    game.ai_thinking = True
    threading.Thread(target=ai_worker, daemon=True).start()