from collections import deque
from config import COLORS

def check_win(player, board):
        player_color = COLORS[f'player{player}']
        edge_hexes = []
        target_edge = []
        
        # Definir bordes objetivo
        if player == 1:
            edge_hexes = [hex for hex in board.values() if hex.q == 4]
            target_edge = lambda h: h.q == -4
        else:
            edge_hexes = [hex for hex in board.values() if hex.r == 4]
            target_edge = lambda h: h.r == -4
        
        # BFS desde todos los hexágonos del borde inicial
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