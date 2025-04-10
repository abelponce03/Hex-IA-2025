from collections import deque
from config import COLORS

def check_win(player, board, board_size):
    offset = board_size // 2
    player_color = COLORS[f'player{player}']
    
    if player == 1:
        edge_hexes = [hex for hex in board.values() if hex.q + hex.r == -offset]
        target_edge = lambda h: (h.q + h.r) == offset
    else:
        edge_hexes = [hex for hex in board.values() if hex.r == offset]
        target_edge = lambda h: h.r == -offset
    
    visited = set()
    queue = deque()
    
    for hex in edge_hexes:
        if hex.color == player_color:
            queue.append(hex)
            visited.add(hex)
    
    while queue:
        current = queue.popleft()
        if target_edge(current):
            return True
        for neighbor in get_neighbors(current, board):
            if neighbor.color == player_color and neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)
    
    return False

def get_neighbors(hex, board):
    directions = [(1, 0), (-1, 0), (0, 1), (0, -1), (1, -1), (-1, 1)]
    neighbors = []
    for dq, dr in directions:
        neighbor_pos = (hex.q + dq, hex.r + dr)
        if neighbor_pos in board:
            neighbors.append(board[neighbor_pos])
    return neighbors
    
def shortest_path_length(board, board_size, player):
    offset = board_size // 2
    start_nodes = []
    target_edge = None
    player_color = COLORS[f'player{player}']

    # Definir bordes iniciales y objetivo según el jugador
    if player == 1:
        # Jugador 1 (horizontal): de izquierda (-q-r=offset) a derecha (q+r=offset)
        start_nodes = [hex for hex in board.values() if hex.q + hex.r == -offset]
        target_edge = lambda h: h.q + h.r == offset  # Corregido: ahora usa h.r
    else:
        # Jugador 2 (vertical): de arriba (r=offset) a abajo (r=-offset)
        start_nodes = [hex for hex in board.values() if hex.r == offset]
        target_edge = lambda h: h.r == -offset

    visited = {}
    queue = deque()

    # Inicializar BFS desde nodos de inicio válidos (del color del jugador)
    for hex in start_nodes:
        if hex.color == player_color:
            queue.append((hex, 1))  # (hex, distancia)
            visited[hex] = True

    # Búsqueda de camino más corto
    while queue:
        current_hex, dist = queue.popleft()

        # Verificar si alcanzó el borde objetivo
        if target_edge(current_hex):
            return dist

        # Explorar vecinos
        for neighbor in get_neighbors(current_hex, board):
            if neighbor.color == player_color and neighbor not in visited:
                visited[neighbor] = True
                queue.append((neighbor, dist + 1))

    # Si no se encontró camino, retornar infinito
    return float('inf')


def count_groups(board, player):
    visited = set()
    group_count = 0
    color = COLORS[f'player{player}']
    
    for hex in board.values():
        if hex.color == color and hex not in visited:
            # Encontrar todos los hexágonos conectados usando BFS
            queue = deque([hex])
            visited.add(hex)
            
            while queue:
                current = queue.popleft()
                for neighbor in get_neighbors(current, board):
                    if neighbor.color == color and neighbor not in visited:
                        visited.add(neighbor)
                        queue.append(neighbor)
            
            group_count += 1
    
    return group_count