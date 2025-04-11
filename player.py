from hex_board import HexBoard
import random
import math
import time
import heapq
from sys import stderr
from copy import deepcopy
from typing import List, Tuple, Dict, Optional, Set

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
        self.max_depth = 5  # Profundidad máxima de búsqueda
        self.transposition_table = {}  # Tabla de transposición para almacenar evaluaciones
        
        # Direcciones adyacentes en tablero hexagonal
        self.directions = [
            (0, -1),   # Izquierda
            (0, 1),    # Derecha
            (-1, 0),   # Arriba
            (1, 0),    # Abajo
            (-1, 1),   # Arriba derecha
            (1, -1)    # Abajo izquierda
        ]
        
    def play(self, board: HexBoard) -> tuple:
        # Primera jugada: centro del tablero
        if len(board.get_possible_moves()) == board.size * board.size:
            return (board.size // 2, board.size // 2)
        
        # Ajustar profundidad según tamaño del tablero
        if board.size <= 5:
            self.max_depth = 3
        elif board.size <= 7:
            self.max_depth = 2
        else:
            self.max_depth = 1
        
        # Calcular movimientos restantes para posible ajuste de profundidad
        moves_remaining = len(board.get_possible_moves())
        if moves_remaining < 15:
            self.max_depth += 1
        
        # Limpiar tabla de transposición si está muy grande
        if len(self.transposition_table) > 10000:
            self.transposition_table = {}
        
        start_time = time.time()
        
        # Buscar movimiento ganador inmediato
        for move in board.get_possible_moves():
            temp_board = board.clone()
            temp_board.place_piece(move[0], move[1], self.player_id)
            if temp_board.check_connection(self.player_id):
                return move
        
        # Buscar movimiento bloqueante de victoria del oponente
        for move in board.get_possible_moves():
            temp_board = board.clone()
            temp_board.place_piece(move[0], move[1], self.opponent_id)
            if temp_board.check_connection(self.opponent_id):
                return move
        
        # Ejecutar minimax con poda alfa-beta
        best_score = float('-inf')
        best_move = None
        alpha = float('-inf')
        beta = float('inf')
        
        # Ordenar movimientos para mejorar la poda
        moves = self.prioritize_moves(board)
        
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
        
        elapsed = time.time() - start_time
        stderr.write(f"Minimax completado en {elapsed:.2f} segundos. Profundidad: {self.max_depth}\n")
        
        return best_move if best_move else random.choice(board.get_possible_moves())
    
    def minimax(self, board: HexBoard, depth: int, alpha: float, beta: float, maximizing: bool) -> float:
        """
        Algoritmo minimax con poda alfa-beta.
        """
        # Generar clave para la tabla de transposición
        board_key = self.get_board_key(board, maximizing)
        
        # Verificar si ya hemos evaluado esta posición a esta profundidad o mayor
        if board_key in self.transposition_table and self.transposition_table[board_key][1] >= depth:
            return self.transposition_table[board_key][0]
        
        # Verificar si el juego ha terminado o si hemos alcanzado la profundidad máxima
        if depth == 0 or board.check_connection(self.player_id) or board.check_connection(self.opponent_id):
            score = self.evaluate_board(board)
            self.transposition_table[board_key] = (score, depth)
            return score
        
        # No hay más movimientos disponibles
        possible_moves = board.get_possible_moves()
        if not possible_moves:
            score = self.evaluate_board(board)
            self.transposition_table[board_key] = (score, depth)
            return score
        
        # Ordenar movimientos para mejorar la poda
        moves = self.prioritize_moves(board) if maximizing else self.prioritize_moves(board, for_opponent=True)
        
        if maximizing:
            value = float('-inf')
            for move in moves:
                new_board = board.clone()
                new_board.place_piece(move[0], move[1], self.player_id)
                
                value = max(value, self.minimax(new_board, depth-1, alpha, beta, False))
                alpha = max(alpha, value)
                
                if beta <= alpha:
                    break  # Poda beta
            
            self.transposition_table[board_key] = (value, depth)
            return value
        else:
            value = float('inf')
            for move in moves:
                new_board = board.clone()
                new_board.place_piece(move[0], move[1], self.opponent_id)
                
                value = min(value, self.minimax(new_board, depth-1, alpha, beta, True))
                beta = min(beta, value)
                
                if beta <= alpha:
                    break  # Poda alfa
            
            self.transposition_table[board_key] = (value, depth)
            return value
    
    def get_board_key(self, board: HexBoard, maximizing: bool) -> str:
        """
        Genera una clave única para el tablero actual y el jugador que mueve.
        """
        # Crear una representación de cadena del tablero y el jugador actual
        board_str = ''.join(''.join(str(cell) for cell in row) for row in board.board)
        return board_str + ('1' if maximizing else '0')
    
    def evaluate_board(self, board: HexBoard) -> float:
        """
        Función de evaluación heurística basada en Dijkstra.
        """
        # Si hay un ganador, retornar un valor alto (positivo o negativo)
        if board.check_connection(self.player_id):
            return 10000
        if board.check_connection(self.opponent_id):
            return -10000
        
        # Calcular distancia más corta entre los bordes para ambos jugadores
        player_distance = self.shortest_path_distance(board, self.player_id)
        opponent_distance = self.shortest_path_distance(board, self.opponent_id)
        
        # Si no hay camino, asignar un valor alto
        if player_distance == float('inf'):
            player_distance = board.size * board.size
        if opponent_distance == float('inf'):
            opponent_distance = board.size * board.size
        
        # Calcular puntuación de puentes
        #player_bridges = self.count_bridges(board, self.player_id)
        #opponent_bridges = self.count_bridges(board, self.opponent_id)
        
        # Evaluar control de casillas estratégicas (centro y laterales)
        player_strategic = self.evaluate_strategic_positions(board, self.player_id)
        opponent_strategic = self.evaluate_strategic_positions(board, self.opponent_id)
        
        # Calcular la puntuación final
        # Menos distancia es mejor, más puentes es mejor
        # Más posiciones estratégicas es mejor
        score = (opponent_distance - player_distance) * 10 + \
            (player_strategic - opponent_strategic) * 2
        
        return score
    
    def shortest_path_distance(self, board: HexBoard, player_id: int) -> float:
        """
        Implementa el algoritmo de Dijkstra para encontrar el camino más corto entre los bordes.
        Para jugador 1: conectar izquierda con derecha
        Para jugador 2: conectar arriba con abajo
        """
        # Crear un grafo a partir del tablero
        graph = {}
        for i in range(board.size):
            for j in range(board.size):
                if board.board[i][j] == 0 or board.board[i][j] == player_id:
                    # Costo 1 para celdas vacías, 0 para celdas propias
                    cost = 0 if board.board[i][j] == player_id else 1
                    neighbors = []
                    for dx, dy in self.directions:
                        ni, nj = i + dx, j + dy
                        if 0 <= ni < board.size and 0 <= nj < board.size:
                            if board.board[ni][nj] == 0 or board.board[ni][nj] == player_id:
                                neighbors.append(((ni, nj), 0 if board.board[ni][nj] == player_id else 1))
                    graph[(i, j)] = neighbors
        
        # Nodos de los bordes
        if player_id == 1:  # Rojo: izquierda a derecha
            start_nodes = [(i, 0) for i in range(board.size)]
            end_nodes = [(i, board.size-1) for i in range(board.size)]
        else:  # Azul: arriba a abajo
            start_nodes = [(0, j) for j in range(board.size)]
            end_nodes = [(board.size-1, j) for j in range(board.size)]
        
        # Filtrar nodos de bordes que no estén en el grafo
        start_nodes = [node for node in start_nodes if node in graph]
        end_nodes = [node for node in end_nodes if node in graph]
        
        if not start_nodes or not end_nodes:
            return float('inf')
        
        # Ejecutar Dijkstra desde cada nodo de inicio y encontrar el camino más corto
        min_distance = float('inf')
        for start in start_nodes:
            # Inicializar distancias
            distances = {node: float('inf') for node in graph}
            distances[start] = 0
            priority_queue = [(0, start)]
            
            while priority_queue:
                current_distance, current_node = heapq.heappop(priority_queue)
                
                if current_distance > distances[current_node]:
                    continue
                
                for neighbor, weight in graph[current_node]:
                    distance = current_distance + weight
                    if distance < distances.get(neighbor, float('inf')):
                        distances[neighbor] = distance
                        heapq.heappush(priority_queue, (distance, neighbor))
            
            # Encontrar el camino más corto a cualquier nodo final
            for end in end_nodes:
                if end in distances and distances[end] < min_distance:
                    min_distance = distances[end]
        
        return min_distance
    
    def count_bridges(self, board: HexBoard, player_id: int) -> int:
        """
        Cuenta el número de puentes (configuraciones que garantizan una conexión) para un jugador.
        """
        count = 0
        for i in range(board.size):
            for j in range(board.size):
                if board.board[i][j] == player_id:
                    # Verificar patrones de puente
                    for k in range(len(self.directions)):
                        # Verificar patrones de puente en dos direcciones
                        dx1, dy1 = self.directions[k]
                        dx2, dy2 = self.directions[(k+2) % len(self.directions)]
                        
                        # Verificar si los dos extremos del puente son del mismo jugador
                        i1, j1 = i + dx1, j + dy1
                        i2, j2 = i + dx2, j + dy2
                        
                        if (0 <= i1 < board.size and 0 <= j1 < board.size and
                            0 <= i2 < board.size and 0 <= j2 < board.size and
                            board.board[i1][j1] == player_id and board.board[i2][j2] == player_id):
                            
                            # Verificar si el espacio intermedio está vacío
                            mid_i, mid_j = i + dx1 + dx2, j + dy1 + dy2
                            if (0 <= mid_i < board.size and 0 <= mid_j < board.size and
                                board.board[mid_i][mid_j] == 0):
                                count += 1
        
        return count
    
    def evaluate_strategic_positions(self, board: HexBoard, player_id: int) -> int:
        """
        Evalúa el control de posiciones estratégicas como el centro y los bordes.
        """
        score = 0
        center = board.size // 2
        
        # Valorar más las posiciones cercanas al centro
        for i in range(board.size):
            for j in range(board.size):
                if board.board[i][j] == player_id:
                    # Distancia al centro
                    distance_to_center = abs(i - center) + abs(j - center)
                    score += max(0, board.size - distance_to_center)
                    
                    # Bonus por estar en los bordes relevantes
                    if player_id == 1:  # Rojo: izquierda-derecha
                        if j == 0 or j == board.size - 1:
                            score += 3
                    else:  # Azul: arriba-abajo
                        if i == 0 or i == board.size - 1:
                            score += 3
        
        return score
    
    def prioritize_moves(self, board: HexBoard, for_opponent=False) -> List[Tuple[int, int]]:
        """
        Ordena los movimientos dando prioridad a los más prometedores.
        """
        player = self.opponent_id if for_opponent else self.player_id
        moves = board.get_possible_moves()
        if not moves:
            return []
        
        # Evaluar cada movimiento y asignarle una puntuación
        move_scores = []
        for move in moves:
            # Crear tablero temporal con este movimiento
            temp_board = board.clone()
            temp_board.place_piece(move[0], move[1], player)
            
            # Asignar puntuación basada en varios factores
            score = 0
            
            # Factor 1: ¿El movimiento gana?
            if temp_board.check_connection(player):
                score += 1000
            
            # Factor 2: ¿Crea un puente?
            score += self.count_bridges(temp_board, player) * 10
            
            # Factor 3: ¿Mejora la distancia mínima?
            prev_distance = self.shortest_path_distance(board, player)
            new_distance = self.shortest_path_distance(temp_board, player)
            if prev_distance != float('inf') and new_distance != float('inf'):
                score += (prev_distance - new_distance) * 5
            
            # Factor 4: Proximidad a piezas propias
            player_positions = board.player_positions[player]
            if player_positions:
                min_distance = min(abs(move[0] - p[0]) + abs(move[1] - p[1]) for p in player_positions)
                score += (board.size - min_distance)
            
            # Factor 5: Proximidad al centro
            center = board.size // 2
            distance_to_center = abs(move[0] - center) + abs(move[1] - center)
            score += (board.size - distance_to_center)
            
            move_scores.append((score, move))
        
        # Ordenar movimientos por puntuación en orden descendente
        move_scores.sort(reverse=True)
        
        # Retornar solo los movimientos
        return [move for _, move in move_scores]
