from hex_board import HexBoard
import random
import time
import heapq
from sys import stderr
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
        self.max_depth = 2  # Profundidad máxima de búsqueda
        self.transposition_table = {}  # Tabla de transposición
        
        # Direcciones adyacentes en tablero hexagonal
        self.directions = [
            (0, -1), (0, 1), (-1, 0), (1, 0), (-1, 1), (1, -1)
        ]
        
    #--------------------------------
    # Métodos principales de juego
    #--------------------------------
    def play(self, board: HexBoard) -> tuple:
        # Primera jugada: intenta el centro o una posición cercana
        if len(board.get_possible_moves()) >= board.size * board.size - 1:
            center = (board.size // 2, board.size // 2)
            possible_moves = board.get_possible_moves()
            
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
        #self._adjust_search_depth(board)
        
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
    
    def _adjust_search_depth(self, board: HexBoard) -> None:
        """Ajusta la profundidad de búsqueda según el estado del juego"""
        # Base según tamaño del tablero
        if board.size <= 5:
            self.max_depth = 3
        elif board.size <= 7:
            self.max_depth = 2
        else:
            self.max_depth = 1
        
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

    def _find_immediate_move(self, board: HexBoard) -> Optional[Tuple[int, int]]:
        """Busca movimientos inmediatos de victoria o bloqueo"""
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
        
        return None
    
    def _find_best_move(self, board: HexBoard) -> Optional[Tuple[int, int]]:
        """Encuentra el mejor movimiento usando minimax y evaluación de amenazas."""
        best_score = float('-inf')
        best_move = None
        alpha = float('-inf')
        beta = float('inf')
        
        # Ordenar movimientos para mejorar la poda
        moves = self.prioritize_moves(board)
        
        # Para debugging, mostrar amenazas de los mejores movimientos
        debug_top_moves = 3
        stderr.write("Análisis de las mejores jugadas:\n")
        for i, move in enumerate(moves[:debug_top_moves]):
            threats = self.detect_threats(board, move, self.player_id)
            stderr.write(f"Movimiento {move}: {len(threats)} amenazas {threats}\n")
        
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
    
    #--------------------------------
    # Algoritmo Minimax
    #--------------------------------
    def minimax(self, board: HexBoard, depth: int, alpha: float, beta: float, maximizing: bool) -> float:
        """Algoritmo minimax con poda alfa-beta."""
        # Verificar condiciones de terminación
        if depth == 0 or board.check_connection(self.player_id) or board.check_connection(self.opponent_id):
            score = self.evaluate_board(board)
            return score
        
        # Generar clave para la tabla de transposición
        board_key = self.get_board_key(board, maximizing)
        
        # Verificar tabla de transposición
        if board_key in self.transposition_table and self.transposition_table[board_key][1] >= depth:
            return self.transposition_table[board_key][0]
        
        # No hay más movimientos disponibles
        possible_moves = board.get_possible_moves()
        if not possible_moves:
            score = self.evaluate_board(board)
            self.transposition_table[board_key] = (score, depth)
            return score
        
        # Ordenar movimientos para mejorar la poda
        player = self.player_id if maximizing else self.opponent_id
        moves = self.prioritize_moves_simplified(board, player)
        
        if maximizing:
            value = float('-inf')
            for move in moves:
                # Hacer movimiento
                i, j = move
                old_value = board.board[i][j]
                board.board[i][j] = self.player_id
                
                # Evaluar recursivamente
                value = max(value, self.minimax(board, depth-1, alpha, beta, False))
                alpha = max(alpha, value)
                
                # Deshacer movimiento
                board.board[i][j] = old_value
                
                if beta <= alpha:
                    break  # Poda beta
        else:
            value = float('inf')
            for move in moves:
                # Hacer movimiento
                i, j = move
                old_value = board.board[i][j]
                board.board[i][j] = self.opponent_id
                
                # Evaluar recursivamente
                value = min(value, self.minimax(board, depth-1, alpha, beta, True))
                beta = min(beta, value)
                
                # Deshacer movimiento
                board.board[i][j] = old_value
                
                if beta <= alpha:
                    break  # Poda alfa
        
        self.transposition_table[board_key] = (value, depth)
        return value
    
    def get_board_key(self, board: HexBoard, maximizing: bool) -> tuple:
        """Genera una clave eficiente para el tablero."""
        # Usar una representación más eficiente que convertir a string
        compressed = []
        for i in range(0, len(board.board), 2):
            if i+1 < len(board.board):
                # Comprimir dos filas en un solo número
                row = 0
                for j in range(board.size):
                    row = (row << 2) | board.board[i][j]
                    if i+1 < len(board.board):
                        row = (row << 2) | board.board[i+1][j]
                compressed.append(row)
            else:
                # Última fila si el número de filas es impar
                row = 0
                for j in range(board.size):
                    row = (row << 2) | board.board[i][j]
                compressed.append(row)
        
        return tuple(compressed + [1 if maximizing else 0])
    
    #--------------------------------
    # Evaluación del tablero
    #--------------------------------
    def evaluate_board(self, board: HexBoard) -> float:
        """Función de evaluación heurística."""
        # Si hay un ganador, retornar un valor alto
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
        
        # Evaluar control de casillas estratégicas
        player_strategic = self.evaluate_strategic_positions(board, self.player_id)
        opponent_strategic = self.evaluate_strategic_positions(board, self.opponent_id)
        
        # Calcular la puntuación final
        score = (opponent_distance - player_distance) * 10 + \
            (player_strategic - opponent_strategic) * 2
        
        return score
    
    def evaluate_board_simplified(self, board: HexBoard) -> float:
        """Versión simplificada para evaluación rápida."""
        # Victoria/derrota
        if board.check_connection(self.player_id):
            return 10000
        if board.check_connection(self.opponent_id):
            return -10000
        
        # Puntuación basada en posición
        player_score = 0
        opponent_score = 0
        center = board.size // 2
        
        for i in range(board.size):
            for j in range(board.size):
                if board.board[i][j] == self.player_id:
                    # Valorar avance según dirección del jugador
                    if self.player_id == 1:  # Rojo (izq->der)
                        player_score += j * 2  # Valor por proximidad al borde derecho
                    else:  # Azul (arriba->abajo)
                        player_score += i * 2  # Valor por proximidad al borde inferior
                    
                    # Valor por posiciones centrales (más estratégicas)
                    distance_to_center = abs(i - center) + abs(j - center)
                    player_score += max(0, board.size - distance_to_center)
                    
                elif board.board[i][j] == self.opponent_id:
                    # Similar para el oponente
                    if self.opponent_id == 1:
                        opponent_score += j * 2
                    else:
                        opponent_score += i * 2
                        
                    distance_to_center = abs(i - center) + abs(j - center)
                    opponent_score += max(0, board.size - distance_to_center)
        
        return player_score - opponent_score
    
    def shortest_path_distance(self, board: HexBoard, player_id: int) -> float:
        """Busca el camino más corto entre bordes usando A*."""
        # Heurística de distancia al borde objetivo
        def heuristic(node):
            i, j = node
            if player_id == 1:  # Rojo: izquierda a derecha
                return board.size - 1 - j
            else:  # Azul: arriba a abajo
                return board.size - 1 - i

        # Crear un grafo a partir del tablero
        graph = {}
        for i in range(board.size):
            for j in range(board.size):
                if board.board[i][j] == 0 or board.board[i][j] == player_id:
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
        
        # Filtrar nodos de bordes
        start_nodes = [node for node in start_nodes if node in graph]
        end_nodes = set(node for node in end_nodes if node in graph)
        
        if not start_nodes or not end_nodes:
            return float('inf')
        
        # Buscar el camino más corto
        min_distance = float('inf')
        for start in start_nodes:
            g_score = {node: float('inf') for node in graph}
            g_score[start] = 0
            
            open_set = [(heuristic(start), 0, start)]
            visited = set()
            
            while open_set:
                f, g, current = heapq.heappop(open_set)
                
                if current in end_nodes:
                    min_distance = min(min_distance, g)
                    break
                
                if current in visited:
                    continue
                    
                visited.add(current)
                
                for neighbor, weight in graph[current]:
                    tentative_g = g + weight
                    if tentative_g < g_score.get(neighbor, float('inf')):
                        g_score[neighbor] = tentative_g
                        f_score = tentative_g + heuristic(neighbor)
                        heapq.heappush(open_set, (f_score, tentative_g, neighbor))
        
        return min_distance
    
    def evaluate_strategic_positions(self, board: HexBoard, player_id: int) -> int:
        """Evalúa el control de posiciones estratégicas."""
        score = 0
        center = board.size // 2
        
        for i in range(board.size):
            for j in range(board.size):
                if board.board[i][j] == player_id:
                    # Valorar proximidad al centro
                    distance_to_center = abs(i - center) + abs(j - center)
                    score += max(0, board.size - distance_to_center)
                    
                    # Bonus por estar en los bordes relevantes
                    if player_id == 1 and (j == 0 or j == board.size - 1):
                        score += 3
                    elif player_id == 2 and (i == 0 or i == board.size - 1):
                        score += 3
        
        return score
    
    #--------------------------------
    # Funciones auxiliares
    #--------------------------------
    def prioritize_moves(self, board: HexBoard, for_opponent=False) -> List[Tuple[int, int]]:
        """Ordena los movimientos por prioridad, valorando múltiples amenazas."""
        player = self.opponent_id if for_opponent else self.player_id
        moves = board.get_possible_moves()
        if not moves:
            return []
        
        move_scores = []
        for move in moves:
            # Detectar amenazas creadas por este movimiento
            threats = self.detect_threats(board, move, player)
            
            # Base score = número de amenazas * 100 (valoramos altamente los movimientos multi-amenaza)
            score = len(threats) * 100
            
            # Puntuación adicional según tipos específicos de amenazas
            if "winning_move" in threats:
                score += 1000  # Victoria inmediata es prioritaria
            if "fork_creation" in threats:
                score += 200   # Crear bifurcaciones es muy valioso
            if "path_reduction" in threats:
                score += 150
            if "block_opponent" in threats:
                score += 120
            if "strategic_position" in threats:
                score += 80
            
            # Añadir criterios existentes de evaluación
            # Proximidad a piezas propias
            player_positions = board.player_positions[player]
            if player_positions:
                min_distance = min(abs(move[0] - p[0]) + abs(move[1] - p[1]) for p in player_positions)
                score += (board.size - min_distance)
            
            # Proximidad al centro
            center = board.size // 2
            distance_to_center = abs(move[0] - center) + abs(move[1] - center)
            score += (board.size - distance_to_center)
            
            # Almacenar puntuación del movimiento
            move_scores.append((score, move))
        
        # Ordenar por puntuación (mayor primero)
        move_scores.sort(reverse=True)
        return [move for _, move in move_scores]
    
    def detect_threats(self, board: HexBoard, move: Tuple[int, int], player_id: int) -> List[str]:
        """
        Identifica las diferentes amenazas que crea un movimiento específico.
        Retorna una lista con los tipos de amenazas detectadas.
        """
        threats = []
        temp_board = board.clone()
        temp_board.place_piece(move[0], move[1], player_id)
        
        # Amenaza 1: Movimiento ganador directo
        if temp_board.check_connection(player_id):
            threats.append("winning_move")
            return threats  # Si es movimiento ganador, es prioritario
        
        # Amenaza 2: Reducción significativa del camino mínimo
        prev_distance = self.shortest_path_distance(board, player_id)
        new_distance = self.shortest_path_distance(temp_board, player_id)
        if prev_distance != float('inf') and new_distance != float('inf'):
            if prev_distance - new_distance >= 2:
                threats.append("path_reduction")
        
        # Amenaza 3: Creación de bifurcación (múltiples caminos potenciales)
        if self.creates_fork(temp_board, move, player_id):
            threats.append("fork_creation")
        
        # Amenaza 4: Bloqueo de camino del oponente
        opponent = 3 - player_id  # Obtiene el ID del oponente (1→2, 2→1)
        prev_opp_distance = self.shortest_path_distance(board, opponent)
        new_opp_distance = self.shortest_path_distance(temp_board, opponent)
        if prev_opp_distance != float('inf') and new_opp_distance != float('inf'):
            if new_opp_distance > prev_opp_distance + 1:
                threats.append("block_opponent")
        
        # Amenaza 5: Ocupación de posición estratégica
        if self.is_strategic_position(board, move):
            threats.append("strategic_position")
        
        return threats

    def creates_fork(self, board: HexBoard, move: Tuple[int, int], player_id: int) -> bool:
        """
        Determina si un movimiento crea una bifurcación (múltiples caminos).
        """
        # Contar cuántos caminos potenciales diferentes existen desde este punto
        paths = 0
        i, j = move
        
        # Para el jugador rojo (1), buscamos caminos horizontales
        if player_id == 1:
            # Contar caminos potenciales hacia la izquierda
            if j > 0:
                for di, dj in [(-1, 0), (0, -1), (-1, 1)]:
                    ni, nj = i + di, j + dj
                    if 0 <= ni < board.size and 0 <= nj < board.size:
                        if board.board[ni][nj] == player_id:
                            paths += 1
            
            # Contar caminos potenciales hacia la derecha
            if j < board.size - 1:
                for di, dj in [(1, 0), (0, 1), (1, -1)]:
                    ni, nj = i + di, j + dj
                    if 0 <= ni < board.size and 0 <= nj < board.size:
                        if board.board[ni][nj] == player_id:
                            paths += 1
        
        # Para el jugador azul (2), buscamos caminos verticales
        else:
            # Contar caminos potenciales hacia arriba
            if i > 0:
                for di, dj in [(-1, 0), (0, -1), (-1, 1)]:
                    ni, nj = i + di, j + dj
                    if 0 <= ni < board.size and 0 <= nj < board.size:
                        if board.board[ni][nj] == player_id:
                            paths += 1
            
            # Contar caminos potenciales hacia abajo
            if i < board.size - 1:
                for di, dj in [(1, 0), (0, 1), (1, -1)]:
                    ni, nj = i + di, j + dj
                    if 0 <= ni < board.size and 0 <= nj < board.size:
                        if board.board[ni][nj] == player_id:
                            paths += 1
        
        # Si hay más de un camino potencial, es una bifurcación
        return paths >= 2

    def is_strategic_position(self, board: HexBoard, move: Tuple[int, int]) -> bool:
        """
        Determina si una posición es estratégica (centro o puntos clave).
        """
        i, j = move
        center = board.size // 2
        
        # Posiciones centrales
        if abs(i - center) <= 1 and abs(j - center) <= 1:
            return True
        
        # Posiciones en los bordes relevantes según el jugador
        if (i == 0 or i == board.size - 1) and (j == 0 or j == board.size - 1):
            return True
        
        return False

    def prioritize_moves_simplified(self, board: HexBoard, player_id: int) -> List[Tuple[int, int]]:
        """Versión optimizada para ordenar movimientos."""
        moves = board.get_possible_moves()
        if not moves:
            return []
        
        center = board.size // 2
        move_scores = []
        opponent_id = 3 - player_id  # Alternar entre 1 y 2
        
        for move in moves:
            i, j = move
            score = 0
            
            # Verificar victoria inmediata (máxima prioridad)
            board.board[i][j] = player_id
            if board.check_connection(player_id):
                board.board[i][j] = 0
                return [move]  # Si hay victoria inmediata, solo devolver ese movimiento
            board.board[i][j] = 0
            
            # Verificar bloqueo de victoria del oponente
            board.board[i][j] = opponent_id
            if board.check_connection(opponent_id):
                score += 1000
            board.board[i][j] = 0
            
            # Contar piezas adyacentes propias
            adjacent_own = 0
            for di, dj in self.directions:
                ni, nj = i + di, j + dj
                if 0 <= ni < board.size and 0 <= nj < board.size:
                    if board.board[ni][nj] == player_id:
                        adjacent_own += 1
                        score += 20
            
            # Bonificación por posible bifurcación
            if adjacent_own >= 2:
                score += 100
            
            # Proximidad al centro
            distance_to_center = abs(i - center) + abs(j - center)
            score += (board.size - distance_to_center) * 2
            
            # Avance en la dirección relevante
            if player_id == 1:  # Rojo (horizontal)
                score += j * 5  # Valor por avance hacia la derecha
            else:  # Azul (vertical)
                score += i * 5  # Valor por avance hacia abajo
            
            move_scores.append((score, move))
        
        # Ordenar por puntuación (mayor primero)
        move_scores.sort(reverse=True)
        return [move for _, move in move_scores]
