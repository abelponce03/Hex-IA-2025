from hex_board import HexBoard
import random
import time
from sys import stderr
from typing import List, Tuple, Dict, Optional, Set

# Importar módulos nuevos
from utils.game_methods import play, adjust_search_depth, find_immediate_move, find_best_move
from utils.minimax_algorithm import minimax, get_board_key
from utils.board_evaluation import evaluate_board, evaluate_board_simplified, shortest_path_distance, evaluate_strategic_positions
from utils.move_selection import prioritize_moves_simplified

# Definición de la clase base Player
class Player:
    def __init__(self, player_id: int):
        self.player_id = player_id  # 1 (rojo) or 2 (azul)

    def play(self, board: "HexBoard") -> tuple:
        raise NotImplementedError("Implement this method!")

class IAPlayer(Player):
    """
    Agente de IA basado en Minimax con poda alfa-beta para jugar Hex.
    """
    def __init__(self, player_id: int):
        super().__init__(player_id)
        self.opponent_id = 2 if player_id == 1 else 1
        self.max_depth = 3  # Profundidad máxima de búsqueda
        self.transposition_table = {}  # Tabla de transposición
        
        
        # Direcciones adyacentes en tablero hexagonal
        self.directions = [
            (0, -1), (0, 1), (-1, 0), (1, 0), (-1, 1), (1, -1)
        ]
    
    # Métodos principales de juego
    def play(self, board: HexBoard) -> tuple:
        return play(self, board)
    
    def _adjust_search_depth(self, board: HexBoard) -> None:
        return adjust_search_depth(self, board)

    def _find_immediate_move(self, board: HexBoard) -> Optional[Tuple[int, int]]:
        return find_immediate_move(self, board)
    
    def _find_best_move(self, board: HexBoard) -> Optional[Tuple[int, int]]:
        return find_best_move(self, board)
    
    # Algoritmo Minimax
    def minimax(self, board: HexBoard, depth: int, alpha: float, beta: float, maximizing: bool) -> float:
        return minimax(self, board, depth, alpha, beta, maximizing)
    
    def get_board_key(self, board: HexBoard, maximizing: bool) -> tuple:
        return get_board_key(self, board, maximizing)
    
    # Evaluación del tablero
    def evaluate_board(self, board: HexBoard) -> float:
        return evaluate_board(self, board)
    
    def evaluate_board_simplified(self, board: HexBoard) -> float:
        return evaluate_board_simplified(self, board)
    
    def shortest_path_distance(self, board: HexBoard, player_id: int) -> float:
        return shortest_path_distance(self, board, player_id)
    
    def evaluate_strategic_positions(self, board: HexBoard, player_id: int) -> int:
        return evaluate_strategic_positions(self, board, player_id)
    

    def prioritize_moves_simplified(self, board: HexBoard, player_id: int) -> List[Tuple[int, int]]:
        return prioritize_moves_simplified(self, board, player_id)

    