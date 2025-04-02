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
    