from collections import deque
import heapq
from config import COLORS
from win_condition import check_win, get_neighbors

def axial_distance(a, b):
    return (abs(a.q - b.q) + abs(a.q + a.r - b.q - b.r) + abs(a.r - b.r)) // 2

def a_star_path(game, player):
    board = game.board
    targets = []
    start_nodes = []
    
    # Configuración de bordes según jugador
    if player == 1:
        target_edge = lambda h: h.q + h.r == 5
        heuristic = lambda h: abs(h.q + h.r - 5)  # Distancia al borde derecho
        for hex in board.values():
            if hex.q + hex.r == -5 and hex.color == COLORS['player1']:
                start_nodes.append(hex)
    else:
        target_edge = lambda h: h.r == 0
        heuristic = lambda h: abs(h.r)  # Distancia vertical al borde inferior
        for hex in board.values():
            if hex.r == 10 and hex.color == COLORS['player2']:
                start_nodes.append(hex)

    # Estructuras para A*
    open_set = []
    came_from = {}
    g_score = {}
    f_score = {}
    
    # Inicialización
    for node in start_nodes:
        key = (node.q, node.r)
        g_score[key] = 0
        f_score[key] = heuristic(node)
        heapq.heappush(open_set, (f_score[key], key))
    
    while open_set:
        current_f, current_key = heapq.heappop(open_set)
        current = board[current_key]
        
        if target_edge(current):
            return g_score[current_key]  # Costo del camino mínimo
        
        for neighbor in get_neighbors(current, board):
            neighbor_key = (neighbor.q, neighbor.r)
            
            # Costo de movimiento: 0 si es del jugador, 1 si está vacío
            tentative_g = g_score[current_key] + (0 if neighbor.color == COLORS[f'player{player}'] else 1)
            
            if neighbor_key not in g_score or tentative_g < g_score[neighbor_key]:
                came_from[neighbor_key] = current_key
                g_score[neighbor_key] = tentative_g
                f_score[neighbor_key] = tentative_g + heuristic(neighbor)
                heapq.heappush(open_set, (f_score[neighbor_key], neighbor_key))
    
    return float('inf')

def heuristic(game, player=None):
    if player is None:
        player = game.current_player
    opponent = 3 - player

    player_path = a_star_path(game, player)
    opponent_path = a_star_path(game, opponent)

    # Balancear la prioridad para ambos jugadores
    return (opponent_path - player_path) * 100  # Simplificado y equilibrado