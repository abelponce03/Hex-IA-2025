import math
import time
from win_condition import shortest_path_length, count_groups
from config import COLORS

# Variable global para controlar el tiempo
MAX_TIME = 0.95  # segundos máximos permitidos
start_time = 0

def minimax(game_state, depth, alpha, beta, maximizing_player, time_limit=True):
    global start_time
    
    if time_limit and start_time == 0:
        start_time = time.time()
    
    # Verificar límite de tiempo
    if time_limit and time.time() - start_time > MAX_TIME:
        return None, None
    
    # Condiciones de terminación
    if depth == 0 or game_state.game_over:
        eval_score = evaluate(game_state)
        return eval_score, None
    
    # Usar la tabla de transposición
    state_hash = get_state_hash(game_state)
    if state_hash in game_state.transposition_table and game_state.transposition_table[state_hash][0] >= depth:
        return game_state.transposition_table[state_hash][1], game_state.transposition_table[state_hash][2]
    
    legal_moves = get_legal_moves(game_state)
    
    # Optimización: si solo hay un movimiento legal, hacerlo sin más análisis
    if len(legal_moves) == 1:
        return 0, legal_moves[0]
    
    # Caso sin movimientos disponibles
    if not legal_moves:
        return evaluate(game_state), None
    
    if maximizing_player:
        max_eval = -math.inf
        best_move = None
        for move in legal_moves:
            child = game_state.clone()
            child.play_move(*move)
            eval, _ = minimax(child, depth-1, alpha, beta, False, time_limit)
            
            # Si se excedió el tiempo, abortar
            if eval is None:
                return None, None
                
            if eval > max_eval:
                max_eval = eval
                best_move = move
            alpha = max(alpha, eval)
            if beta <= alpha:
                break
        
        # Guardar en la tabla de transposición
        game_state.transposition_table[state_hash] = (depth, max_eval, best_move)
        return max_eval, best_move
    else:
        min_eval = math.inf
        best_move = None
        for move in legal_moves:
            child = game_state.clone()
            child.play_move(*move)
            eval, _ = minimax(child, depth-1, alpha, beta, True, time_limit)
            
            # Si se excedió el tiempo, abortar
            if eval is None:
                return None, None
                
            if eval < min_eval:
                min_eval = eval
                best_move = move
            beta = min(beta, eval)
            if beta <= alpha:
                break
                
        # Guardar en la tabla de transposición
        game_state.transposition_table[state_hash] = (depth, min_eval, best_move)
        return min_eval, best_move

def get_state_hash(game_state):
    """Genera un hash único para el estado actual del tablero"""
    board_str = ""
    board_size = game_state.board_size
    offset = board_size // 2
    
    for r in range(-offset, offset + 1):
        for q in range(-offset, offset + 1):
            if (q, r) in game_state.board:
                hex = game_state.board[(q, r)]
                if hex.color == COLORS['player1']:
                    board_str += "1"
                elif hex.color == COLORS['player2']:
                    board_str += "2"
                else:
                    board_str += "0"
    
    return board_str + str(game_state.current_player)

def get_legal_moves(game_state):
    from config import COLORS
    
    board = game_state.board
    current_player = game_state.current_player
    player_color = COLORS[f'player{current_player}']
    enemy_color = COLORS[f'player{3-current_player}']
    
    # Primeros movimientos predefinidos para ahorrar tiempo
    if len(game_state.move_history) == 0:
        # Primer movimiento - tomar el centro
        offset = game_state.board_size // 2
        return [(0, 0)]  # Centro del tablero
    
    # Lista simple para movimientos (optimizado)
    winning_moves = []
    blocking_moves = []
    connecting_moves = []
    strategic_moves = []
    
    # Casillas vacías
    empty_positions = [(hex.q, hex.r) for hex in board.values() if not hex.color]
    
    # Evaluar cada movimiento posible de manera eficiente
    for pos in empty_positions:
        q, r = pos
        
        # Verificar si es un movimiento ganador
        temp_game = game_state.clone()
        temp_game.play_move(q, r)
        if temp_game.game_over:
            winning_moves.append(pos)
            continue
            
        # Verificar si bloquea una victoria del oponente
        temp_game = game_state.clone()
        temp_game.current_player = 3 - current_player  # Simular oponente
        temp_game.play_move(q, r)
        if temp_game.game_over:
            blocking_moves.append(pos)
            continue
        
        # Contar conexiones propias adyacentes
        own_adjacent = 0
        for dq, dr in [(1,0), (-1,0), (0,1), (0,-1), (1,-1), (-1,1)]:
            neighbor = (q + dq, r + dr)
            if neighbor in board and board[neighbor].color == player_color:
                own_adjacent += 1
        
        if own_adjacent >= 2:
            connecting_moves.append(pos)
        else:
            strategic_moves.append(pos)
    
    # Combinar por prioridad
    all_moves = winning_moves + blocking_moves + connecting_moves + strategic_moves
    
    # Limitar el número de movimientos a considerar para mejorar velocidad
    max_moves = min(10, len(all_moves))
    return all_moves[:max_moves]

def strategic_value(pos, board_size, player=2):
    q, r = pos
    offset = board_size // 2
    
    # La estrategia es diferente dependiendo del jugador
    if player == 1:  # Jugador 1 (horizontal)
        # Priorizar posiciones que ayuden a conectar horizontalmente
        horizontal_value = abs(r)  # Menor valor = mejor (cerca del eje horizontal)
        progress_value = q + offset  # Mayor valor = mejor (avance hacia la derecha)
        return horizontal_value * 2 - progress_value
    else:  # Jugador 2 (vertical)
        # Priorizar posiciones que ayuden a conectar verticalmente
        vertical_value = abs(q)  # Menor valor = mejor (cerca del eje vertical)
        progress_value = offset - r  # Mayor valor = mejor (avance hacia abajo)
        return vertical_value * 2 - progress_value

def evaluate(game_state):
    # Comprobar victoria inmediata (prioridad máxima)
    if game_state.game_over:
        winner = 3 - game_state.current_player  # El jugador que hizo el último movimiento
        return 10000 if winner == 2 else -10000
    
    # Versión simplificada - evaluar solo caminos cuando es necesario
    # Para tableros con pocos movimientos, usar heurística sencilla
    if len(game_state.move_history) < 5:
        return evaluate_quick(game_state)
    
    # Calcular caminos más cortos
    p1_path = shortest_path_length(game_state.board, game_state.board_size, 1)
    p2_path = shortest_path_length(game_state.board, game_state.board_size, 2)
    
    # Distancia de caminos
    if p1_path == float('inf') and p2_path == float('inf'):
        path_diff = 0
    elif p1_path == float('inf'):
        path_diff = 1000  # Ventaja para jugador 2
    elif p2_path == float('inf'):
        path_diff = -1000  # Ventaja para jugador 1
    else:
        # Simplificado para mayor velocidad
        path_diff = p1_path - p2_path
    
    # Simplificar la evaluación para mayor velocidad
    return path_diff * 10

def evaluate_quick(game_state):
    """Evaluación rápida para primeros movimientos"""
    from config import COLORS
    
    score = 0
    center_q, center_r = 0, 0  # Centro del tablero
    player1_pieces = 0
    player2_pieces = 0
    
    for (q, r), hex in game_state.board.items():
        if hex.color == COLORS['player1']:
            player1_pieces += 1
            # Bonificación por cercanía al eje horizontal
            score -= (5 - abs(r)) * 5
        elif hex.color == COLORS['player2']:
            player2_pieces += 1
            # Bonificación por cercanía al eje vertical
            score += (5 - abs(q)) * 5
    
    # Equilibrar para el primer jugador
    score += (player1_pieces - player2_pieces) * 5
    
    return score

def evaluate_key_positions(game_state):
    """Evalúa el control de posiciones estratégicas en el tablero"""
    board_size = game_state.board_size
    offset = board_size // 2
    score = 0
    
    # Casillas centrales son muy valiosas en Hex
    center_pos = []
    for q in range(-1, 2):
        for r in range(-1, 2):
            if abs(q + r) <= 1:  # Limitar a región central
                center_pos.append((q, r))
    
    # Evaluar control del centro
    for pos in center_pos:
        if pos in game_state.board:
            hex = game_state.board[pos]
            if hex.color == COLORS['player1']:
                score -= 30
            elif hex.color == COLORS['player2']:
                score += 30
    
    # Evaluar casillas que forman parte de los caminos más cortos
    # (Simulación simplificada)
    for (q, r), hex in game_state.board.items():
        # Posiciones que forman "rutas naturales"
        if hex.color == COLORS['player1']:
            # Para jugador 1 (horizontal), las casillas con r cercano a 0 son valiosas
            score -= 15 * (1.0 / (abs(r) + 1))
        elif hex.color == COLORS['player2']:
            # Para jugador 2 (vertical), las casillas con q cercano a 0 son valiosas
            score += 15 * (1.0 / (abs(q) + 1))
    
    return score

def evaluate_bridges(game_state):
    """Evalúa la presencia de puentes y conexiones virtuales"""
    score = 0
    
    # Patrones de puente (simplificado)
    # Un puente es un patrón donde dos fichas del mismo color pueden
    # conectarse indirectamente aunque el oponente juegue una ficha entre ellas
    bridge_patterns = [
        [(0,0), (1,-1), (2,0)],  # Patrón horizontal
        [(0,0), (0,2), (1,1)],   # Patrón vertical
        [(0,0), (2,-1), (1,1)]   # Patrón diagonal
    ]
    
    for (q, r), hex in game_state.board.items():
        if not hex.color:
            continue
            
        for pattern in bridge_patterns:
            for rotation in range(6):  # 6 posibles rotaciones en hex
                valid_bridge = True
                player_color = None
                
                # Rotar el patrón
                rotated_pattern = rotate_pattern(pattern, rotation)
                
                # Verificar si el patrón existe con el mismo color
                for dq, dr in rotated_pattern:
                    check_pos = (q + dq, r + dr)
                    if check_pos not in game_state.board:
                        valid_bridge = False
                        break
                        
                    check_hex = game_state.board[check_pos]
                    if player_color is None and check_hex.color:
                        player_color = check_hex.color
                    elif check_hex.color != player_color:
                        valid_bridge = False
                        break
                
                if valid_bridge and player_color:
                    if player_color == COLORS['player1']:
                        score -= 40
                    else:
                        score += 40
    
    return score

def rotate_pattern(pattern, rotation):
    """Rota un patrón de coordenadas axiales en hexágonos"""
    # Matrices de rotación para coordenadas axiales (60° por rotación)
    rotation_matrices = [
        [[1, 0], [0, 1]],                # 0°
        [[1, -1], [1, 0]],               # 60°
        [[0, -1], [1, -1]],              # 120°
        [[-1, 0], [0, -1]],              # 180°
        [[-1, 1], [-1, 0]],              # 240°
        [[0, 1], [-1, 1]]                # 300°
    ]
    
    matrix = rotation_matrices[rotation % 6]
    rotated = []
    
    for q, r in pattern:
        new_q = matrix[0][0] * q + matrix[0][1] * r
        new_r = matrix[1][0] * q + matrix[1][1] * r
        rotated.append((new_q, new_r))
    
    return rotated