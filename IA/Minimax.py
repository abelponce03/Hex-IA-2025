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
    
    # Primeros movimientos predefinidos para ahorrar tiempo
    if len(game_state.move_history) == 0:
        # Primer movimiento - tomar el centro
        return [(0, 0)]  # Centro del tablero
    
    # Casillas vacías
    empty_positions = [(hex.q, hex.r) for hex in board.values() if not hex.color]
    
    # Diccionario para clasificar y priorizar movimientos
    moves_by_type = {
        'winning': [],      # Movimientos que ganan directamente
        'blocking': [],     # Movimientos que bloquean victoria del oponente
        'blocking_path': [],# Movimientos que bloquean camino crítico del oponente
        'strategic': []     # Otros movimientos estratégicos
    }
    
    # Análisis de caminos críticos - detectar caminos del oponente
    opponent = 3 - current_player
    opponent_path = shortest_path_length(board, game_state.board_size, opponent)
    
    # Si el oponente tiene un camino "corto" (amenaza seria), priorizar bloqueo
    critical_path_threshold = min(game_state.board_size, 5)
    critical_blocking_needed = opponent_path <= critical_path_threshold
    
    # Evaluar cada movimiento posible
    for pos in empty_positions:
        q, r = pos
        
        # Verificar si es un movimiento ganador
        temp_game = game_state.clone()
        temp_game.play_move(q, r)
        if temp_game.game_over:
            moves_by_type['winning'].append(pos)
            continue
            
        # Verificar si bloquea una victoria del oponente
        temp_game = game_state.clone()
        temp_game.current_player = opponent
        temp_game.play_move(q, r)
        if temp_game.game_over:
            moves_by_type['blocking'].append(pos)
            continue
        
        # Verificar si bloquea un camino crítico del oponente
        if critical_blocking_needed:
            # Verificar si este movimiento aumenta la longitud del camino del oponente
            board_copy = board.copy()
            if (q, r) in board_copy:
                # Simulamos colocar nuestra ficha aquí
                board_copy[(q, r)].color = player_color
                new_path = shortest_path_length(board_copy, game_state.board_size, opponent)
                
                # Si aumentó la longitud del camino, es un buen bloqueo
                if new_path > opponent_path + 1:
                    moves_by_type['blocking_path'].append((pos, new_path - opponent_path))
                    continue
    
    # Ordenar los bloqueos de camino por efectividad
    if moves_by_type['blocking_path']:
        moves_by_type['blocking_path'].sort(key=lambda x: x[1], reverse=True)
        moves_by_type['blocking_path'] = [pos for pos, _ in moves_by_type['blocking_path']]
    
    # Unir todas las categorías por orden de prioridad
    all_moves = (
        moves_by_type['winning'] + 
        moves_by_type['blocking'] + 
        moves_by_type['blocking_path'] + 
        moves_by_type['strategic']
    )
    
    # Limitar el número de movimientos para mejorar velocidad
    max_moves = min(12, len(all_moves))
    return all_moves[:max_moves] if all_moves else empty_positions[:12]

def evaluate(game_state):
    # Comprobar victoria inmediata
    if game_state.game_over:
        winner = 3 - game_state.current_player  # El jugador que hizo el último movimiento
        return 10000 if winner == 2 else -10000
    
    # Para tableros con muy pocos movimientos, usar heurística sencilla
    if len(game_state.move_history) < 3:
        return evaluate_quick(game_state)
    
    # Calcular caminos más cortos (componente principal)
    p1_path = shortest_path_length(game_state.board, game_state.board_size, 1)
    p2_path = shortest_path_length(game_state.board, game_state.board_size, 2)
    
    # Distancia de caminos
    if p1_path == float('inf') and p2_path == float('inf'):
        path_score = 0
    elif p1_path == float('inf'):
        path_score = 2000  # Ventaja para jugador 2
    elif p2_path == float('inf'):
        path_score = -2000  # Ventaja para jugador 1
    else:
        # Enfatizar bloquear al jugador 1 (humano)
        if p1_path < game_state.board_size // 2:
            path_score = (p1_path**0.8) - (p2_path**1.5)
        else:
            path_score = p1_path - p2_path**1.2
    
    # Integrar evaluaciones avanzadas
    key_positions_score = evaluate_key_positions(game_state)
    
    # Contar grupos (menos grupos es mejor - significa mayor conectividad)
    p1_groups = count_groups(game_state.board, 1)
    p2_groups = count_groups(game_state.board, 2)
    group_score = (p1_groups - p2_groups) * 25
    
    # Analizar amenazas
    threat_score = analyze_threats_and_defenses(game_state)
    
    # Ajustar pesos según fase del juego
    move_count = len(game_state.move_history)
    
    if move_count < 8:  # Fase temprana
        path_weight = 0.5
        key_pos_weight = 0.3
        group_weight = 0.05
        threat_weight = 0.15
    else:  # Fase media y final
        path_weight = 0.6
        key_pos_weight = 0.15
        group_weight = 0.05
        threat_weight = 0.2
    
    # Combinar componentes con sus pesos
    final_score = (
        path_weight * path_score + 
        key_pos_weight * key_positions_score + 
        group_weight * group_score +
        threat_weight * threat_score
    )
    
    return final_score

def evaluate_quick(game_state):
    """Evaluación rápida para primeros movimientos"""
    score = 0
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
    for (q, r), hex in game_state.board.items():
        # Posiciones que forman "rutas naturales"
        if hex.color == COLORS['player1']:
            # Para jugador 1 (horizontal), las casillas con r cercano a 0 son valiosas
            score -= 15 * (1.0 / (abs(r) + 1))
        elif hex.color == COLORS['player2']:
            # Para jugador 2 (vertical), las casillas con q cercano a 0 son valiosas
            score += 15 * (1.0 / (abs(q) + 1))
    
    return score

def analyze_threats_and_defenses(game_state):
    """Analiza amenazas específicas y defensas en el tablero"""
    score = 0
    board = game_state.board
    board_size = game_state.board_size
    
    # Detectar si el jugador humano tiene piezas cerca de conectar
    human_positions = [(hex.q, hex.r) for hex in board.values() 
                       if hex.color == COLORS['player1']]
    
    # Buscar pares de piezas del humano que estén casi conectadas
    for i, pos1 in enumerate(human_positions):
        q1, r1 = pos1
        
        # Verificar horizontalmente (conexión potencial del jugador 1)
        horizontal_pieces = [pos for pos in human_positions if pos[1] == r1]
        horizontal_pieces.sort()  # Ordenar por q
        
        if len(horizontal_pieces) >= 2:
            # Verificar si hay espacios pequeños entre piezas horizontales
            for j in range(len(horizontal_pieces) - 1):
                q_gap = horizontal_pieces[j+1][0] - horizontal_pieces[j][0]
                if 1 < q_gap <= 3:  # Espacio pequeño entre piezas
                    # ¡Amenaza detectada! Priorizar bloquear
                    score += 100 * (4 - q_gap)
    
    # Contar piezas en zonas de conexión críticas
    central_zone = [(q, r) for q in range(-2, 3) for r in range(-2, 3) 
                    if (q, r) in board and abs(q + r) <= 3]
    
    ai_pieces_in_center = sum(1 for pos in central_zone 
                             if pos in board and board[pos].color == COLORS['player2'])
    human_pieces_in_center = sum(1 for pos in central_zone 
                                if pos in board and board[pos].color == COLORS['player1'])
    
    # Más piezas en el centro = más control
    score += (ai_pieces_in_center - human_pieces_in_center) * 30
    
    # Analizar potencial de bloqueo en áreas críticas
    horizontal_axis = [(q, 0) for q in range(-board_size//2, board_size//2 + 1) 
                       if (q, 0) in board]
    vertical_axis = [(0, r) for r in range(-board_size//2, board_size//2 + 1) 
                     if (0, r) in board]
    
    # Contar control de ejes
    ai_h_control = sum(1 for pos in horizontal_axis 
                       if board[pos].color == COLORS['player2'])
    human_h_control = sum(1 for pos in horizontal_axis 
                          if board[pos].color == COLORS['player1'])
    
    ai_v_control = sum(1 for pos in vertical_axis 
                       if board[pos].color == COLORS['player2'])
    human_v_control = sum(1 for pos in vertical_axis 
                          if board[pos].color == COLORS['player1'])
    
    # En Hex, controlar el eje contrario al propio es crucial para bloquear
    score += (ai_h_control * 40) - (human_h_control * 20)
    
    return score