from hexagon import Hexagon

def init_board():
       
        board = {}
        # Patron competitivo 
        for r in range(0, 11):
            for q in range(-5, 6):
                board[(q - r, r)] = Hexagon(q - r, r)
                
        return board