import heapq
from hex_board import HexBoard

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
    """Busca el camino más corto entre bordes usando A* directamente sobre la matriz."""
    # Heurística de distancia al borde objetivo
    def heuristic(i, j):
        if player_id == 1:  # Rojo: izquierda a derecha
            return board.size - 1 - j
        else:  # Azul: arriba a abajo
            return board.size - 1 - i

    # Definir nodos de bordes según el jugador
    if player_id == 1:  # Rojo: izquierda a derecha
        start_positions = [(i, 0) for i in range(board.size) 
                           if board.board[i][0] == 0 or board.board[i][0] == player_id]
        is_end_position = lambda i, j: j == board.size - 1
    else:  # Azul: arriba a abajo
        start_positions = [(0, j) for j in range(board.size) 
                           if board.board[0][j] == 0 or board.board[0][j] == player_id]
        is_end_position = lambda i, j: i == board.size - 1
    
    if not start_positions:
        return float('inf')
    
    # Buscar el camino más corto desde cualquier posición inicial
    min_distance = float('inf')
    for start_i, start_j in start_positions:
        # Inicializar estructuras para A*
        open_set = [(heuristic(start_i, start_j), 0, start_i, start_j)]
        g_score = {}
        g_score[(start_i, start_j)] = 0
        visited = set()
        
        while open_set:
            _, g, current_i, current_j = heapq.heappop(open_set)
            current = (current_i, current_j)
            
            # Verificar si llegamos al borde objetivo
            if is_end_position(current_i, current_j):
                min_distance = min(min_distance, g)
                break
            
            if current in visited:
                continue
                
            visited.add(current)
            
            # Explorar vecinos directamente
            for dx, dy in self.directions:
                ni, nj = current_i + dx, current_j + dy
                
                # Verificar límites y si el nodo es transitable
                if 0 <= ni < board.size and 0 <= nj < board.size:
                    cell_value = board.board[ni][nj]
                    if cell_value == 0 or cell_value == player_id:
                        # Costo: 0 para casillas propias, 1 para casillas vacías
                        weight = 0 if cell_value == player_id else 1
                        neighbor = (ni, nj)
                        
                        tentative_g = g + weight
                        if tentative_g < g_score.get(neighbor, float('inf')):
                            g_score[neighbor] = tentative_g
                            f_score = tentative_g + heuristic(ni, nj)
                            heapq.heappush(open_set, (f_score, tentative_g, ni, nj))
    
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