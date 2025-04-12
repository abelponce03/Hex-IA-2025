import time
import random
from sys import stderr
from typing import Tuple, Optional
from hex_board import HexBoard

def play(self, board: HexBoard) -> tuple:
    # Primera jugada: intenta el centro o una posición cercana
    if len(board.get_possible_center_moves()) >= board.size * board.size - 1:
        center = (board.size // 2, board.size // 2)
        possible_moves = board.get_possible_center_moves()
        
        # Si el centro está disponible, jugar ahí
        if center in possible_moves:
            return center
        
        # Si no, encontrar la posición más cercana al centro
        closest_move = None
        min_distance = float('inf')
        
        for move in possible_moves:
            # Calcular distancia Manhattan al centro
            distance = abs(move[0] - center[0]) + abs(move[1] - center[1])
            if distance < min_distance:
                min_distance = distance
                closest_move = move
                
        return closest_move
    
    # Ajustar profundidad según el estado del juego
    self._adjust_search_depth(board)
    
    start_time = time.time()
    
    # Buscar movimientos inmediatos (victoria o bloqueo)
    immediate_move = self._find_immediate_move(board)
    if immediate_move:
        return immediate_move
    
    # Ejecutar minimax con poda alfa-beta
    best_move = self._find_best_move(board)
    
    elapsed = time.time() - start_time
    stderr.write(f"Minimax completado en {elapsed:.2f} segundos. Profundidad: {self.max_depth}\n")
    
    return best_move if best_move else random.choice(board.get_possible_moves())

def adjust_search_depth(self, board: HexBoard) -> None:
    """Ajusta la profundidad de búsqueda según el estado del juego"""
    # Base según tamaño del tablero
    
    if board.size <= 7:
        self.max_depth = 3
    else:
        self.max_depth = 2
    
    # Ajuste por movimientos restantes
    moves_remaining = len(board.get_possible_moves())
    if moves_remaining < 20:
        self.max_depth += 1
    
    # Ajuste por situación crítica
    quick_eval = self.evaluate_board(board)
    if abs(quick_eval) > 5000:
        self.max_depth += 1
        stderr.write(f"¡Situación crítica detectada! Aumentando profundidad a {self.max_depth}\n")
    
    # Limpiar tabla de transposición si es necesario
    if len(self.transposition_table) > 10000:
        self.transposition_table = {}

def find_immediate_move(self, board: HexBoard) -> Optional[Tuple[int, int]]:
    """Busca movimientos inmediatos de victoria o bloqueo"""
   
    for move in board.get_possible_moves():
        temp_board_opponent = board.clone()
        temp_board_player = board.clone()
        
        temp_board_opponent.place_piece(move[0], move[1], self.opponent_id)
        temp_board_player.place_piece(move[0], move[1], self.player_id)
        
        # Buscar movimiento ganador inmediato
        if temp_board_player.check_connection(self.player_id):
            return move
        
        # Buscar movimiento bloqueante de victoria del oponente
        elif temp_board_opponent.check_connection(self.opponent_id):
            return move       
    
    return None

def find_best_move(self, board: HexBoard) -> Optional[Tuple[int, int]]:
    """Encuentra el mejor movimiento usando minimax y evaluación de amenazas."""
    best_score = float('-inf')
    best_move = None
    alpha = float('-inf')
    beta = float('inf')
    
    # Ordenar movimientos para mejorar la poda
    moves = self.prioritize_moves_simplified(board, self.player_id)
    
    
    for move in moves:
        # Aplicar movimiento
        new_board = board.clone()
        new_board.place_piece(move[0], move[1], self.player_id)
        
        # Evaluar movimiento
        score = self.minimax(new_board, self.max_depth-1, alpha, beta, False)
        
        if score > best_score:
            best_score = score
            best_move = move
            
        alpha = max(alpha, best_score)
    
    return best_move