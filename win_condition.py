from collections import deque
from config import COLORS

def check_win(player, board):
    player_color = COLORS[f'player{player}']
    
    # Definir bordes según el jugador
    if player == 1:
        # Borde izquierdo: q + r = -5 (desde r=0 hasta r=10)
        edge_hexes = [hex for hex in board.values() if hex.q + hex.r == -5]
        # Borde derecho: q + r = 5 (desde r=0 hasta r=10)
        target_edge = lambda h: h.q + h.r == 5
    else:
        # Borde superior: r = 10 (desde q=-15 hasta q=-5)
        edge_hexes = [hex for hex in board.values() if hex.r == 10]
        # Borde inferior: r = 0 (desde q=-5 hasta q=5)
        target_edge = lambda h: h.r == 0

    # BFS para encontrar camino continuo
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