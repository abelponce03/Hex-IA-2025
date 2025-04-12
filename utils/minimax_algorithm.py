from hex_board import HexBoard

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