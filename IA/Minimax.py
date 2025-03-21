from IA.Astar import heuristic

class Minimax:
    def __init__(self, game, depth):
        self.original_game = game
        self.depth = depth
        
    def decision(self):
        best_move = None
        best_value = float('-inf')
        alpha = float('-inf')
        beta = float('inf')
        
        for move in self.get_possible_moves(self.original_game, 2):
            cloned = self.original_game.clone()
            cloned.play_move(*move)
            value = self.minimize(cloned, self.depth-1, alpha, beta)
            if value > best_value:
                best_value = value
                best_move = move
            alpha = max(alpha, best_value)
            if alpha >= beta:
                break
        return best_move

    def maximize(self, game, depth, alpha, beta):
        if depth == 0 or game.game_over:
            return heuristic(game, 2)
        
        max_value = float('-inf')
        for move in self.get_possible_moves(game, 2):
            cloned = game.clone()
            cloned.play_move(*move)
            value = self.minimize(cloned, depth-1, alpha, beta)
            max_value = max(max_value, value)
            alpha = max(alpha, max_value)
            if alpha >= beta:
                break
        return max_value

    def minimize(self, game, depth, alpha, beta):
        if depth == 0 or game.game_over:
            return heuristic(game, 1)
        
        min_value = float('inf')
        for move in self.get_possible_moves(game, 1):
            cloned = game.clone()
            cloned.play_move(*move)
            value = self.maximize(cloned, depth-1, alpha, beta)
            min_value = min(min_value, value)
            beta = min(beta, min_value)
            if beta <= alpha:
                break
        return min_value

    
    def get_possible_moves(self, game, player):
        moves = [(h.q, h.r) for h in game.board.values() 
             if not h.color and not self.is_blocked(h, player, game)]
        print(f"Movimientos posibles para jugador {player}: {moves}")  # Depuración
        return moves

    def is_blocked(self, hex, player, game):
    # Solo bloquea al jugador 1 (humano) en su primer turno
        return player == 1 and game.first_turn_blocked and hex.q == -5 and hex.r == 5
