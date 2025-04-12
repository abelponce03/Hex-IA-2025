from typing import List, Tuple
from hex_board import HexBoard

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

