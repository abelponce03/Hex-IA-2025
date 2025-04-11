adj = [
    (0, -1),   # Izquierda
    (0, 1),    # Derecha
    (-1, 0),   # Arriba
    (1, 0),    # Abajo
    (-1, 1),   # Arriba derecha
    (1, -1)    # Abajo izquierda
]


def dfs(positions, player_id, size):
    """
    Verifica si existe un camino conectando los bordes correspondientes al jugador
    
    positions: conjunto de posiciones (tuplas) ocupadas por el jugador
    player_id: id del jugador (1: rojo, 2: azul)
    size: tamaño del tablero
    """
    if not positions:
        return False
        
    # Definir los bordes de inicio y fin según el jugador
    if player_id == 1:  # Rojo: izquierda a derecha
        start_border = [(i, 0) for i in range(size)]
        end_border = [(i, size-1) for i in range(size)]
    else:  # Azul: arriba a abajo
        start_border = [(0, j) for j in range(size)]
        end_border = [(size-1, j) for j in range(size)]
    
    # Filtrar posiciones en el borde de inicio
    start_positions = [pos for pos in positions if pos in start_border]
    
    if not start_positions:
        return False
    
    # Realizar DFS desde cada posición en el borde de inicio
    visited = set()
    for start in start_positions:
        if dfs_visit_new(positions, start, visited, end_border):
            return True
    
    return False

def dfs_visit_new(positions, current, visited, end_border):
    """
    Visita recursivamente las posiciones adyacentes en el DFS
    """
    visited.add(current)
    
    # Si llegamos al borde final, hemos encontrado una conexión
    if current in end_border:
        return True
    
    # Direcciones adyacentes
    directions = [(0, -1), (0, 1), (-1, 0), (1, 0), (-1, 1), (1, -1)]
    
    # Visitar vecinos
    for dx, dy in directions:
        neighbor = (current[0] + dx, current[1] + dy)
        if neighbor in positions and neighbor not in visited:
            if dfs_visit_new(positions, neighbor, visited, end_border):
                return True
    
    return False