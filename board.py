from hexagon import Hexagon

def init_board(size):
    board = {}
    offset = size // 2
    for r in range(-offset, size - offset):
        q_start = -offset - r
        q_end = size - offset - r
        for q in range(q_start, q_end):
            board[(q, r)] = Hexagon(q, r)
            
    # Calcular HEX_SIZE después de crear todos los hexágonos
    Hexagon.HEX_SIZE = Hexagon.calculate_hex_size(board.values())
    return board
    