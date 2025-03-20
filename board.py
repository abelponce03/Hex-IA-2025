from hexagon import Hexagon

def init_board():
        # Patrón hexagonal concéntrico
        #radius = 4
        board = {}
        #for q in range(-radius, radius + 1):
        #    for r in range(max(-radius, -q - radius), min(radius, -q + radius) + 1):
        #        board[(q, r)] = Hexagon(q, r)
        
        # Patron competitivo 
        for r in range(0, 11):
            for q in range(-5, 6):
                board[(q - r, r)] = Hexagon(q - r, r)
                
        return board