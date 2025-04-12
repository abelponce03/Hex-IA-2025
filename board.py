import copy
from utils.check_conections import dfs
from hex_board import HexBoard

class BoardAbel(HexBoard):
    def __init__(self, size: int):
        self.size = size  # Tamaño N del tablero (NxN)
        self.board = [[0] * size for _ in range(size)]  # Matriz NxN (0=vacío, 1=Jugador1, 2=Jugador2)
        self.player_positions = {1: set(), 2: set()}  # Registro de fichas por jugador


    def clone(self) -> "HexBoard":
        cloned = self.__class__(self.size) 
        cloned.board = copy.deepcopy(self.board)
        cloned.player_positions = {
            1: copy.deepcopy(self.player_positions[1]),
            2: copy.deepcopy(self.player_positions[2])
        }
        return cloned    

    def place_piece(self, row: int, col: int, player_id: int) -> bool:
        if self.board[row][col] != 0:
            return False
        self.board[row][col] = player_id
        self.player_positions[player_id].add((row,col))
        return True

    def get_possible_center_moves(self, max_radius=None) -> list:

        # Determinar el centro del tablero
        center_row = center_col = self.size // 2
        
        # Obtener casillas vacías
        empty_cells = []
        for i in range(self.size):
            for j in range(self.size):
                if self.board[i][j] == 0:
                    # Calcular distancia hexagonal al centro
                    distance = max(abs(i - center_row), abs(j - center_col), 
                                abs((i - center_row) - (j - center_col)))
                    
                    # Solo incluir si está dentro del radio máximo (si se especificó)
                    if max_radius is None or distance <= max_radius:
                        empty_cells.append((distance, (i, j)))
        
        # Ordenar por distancia al centro y devolver solo las coordenadas
        empty_cells.sort()  # Ordena por el primer elemento de cada tupla (la distancia)
        
        return [cell[1] for cell in empty_cells]


    def get_possible_moves(self) -> list:
        # Si no hay fichas en el tablero
        if not self.player_positions[1] and not self.player_positions[2]:
            return self.get_possible_center_moves(max_radius=2)
        
        # Si hay fichas, encontramos posiciones ocupadas por ambos jugadores
        occupied_positions = self.player_positions[1].union(self.player_positions[2])
        
        # Buscar posiciones vacías a radio 2 de cualquier ficha
        result = []
        for i in range(self.size):
            for j in range(self.size):
                if self.board[i][j] == 0:  # Si la posición está vacía
                    # Verificar si está a distancia <= 2 de alguna ficha
                    is_within_radius = False
                    for pos_r, pos_c in occupied_positions:
                        # Cálculo de distancia en tablero hexagonal
                        distance = max(abs(i - pos_r), abs(j - pos_c), 
                                    abs((i - pos_r) - (j - pos_c)))
                        if distance <= 2:
                            is_within_radius = True
                            break
                    if is_within_radius:
                        result.append((i, j))
        
        return result
    
    def check_connection(self, player_id: int) -> bool:
        return dfs(self.player_positions[player_id],player_id,self.size)
    
    def print_board(self):
        space = ""
        print(space , end="     ")
        for i in range(self.size):
            print(f"\033[34m{i}  \033[0m", end=" ")  # Cambiado a azul (columnas)
        print("\n")
        for i in range(self.size):
            print(space , end=" ")
            print(f"\033[31m{i}  \033[0m",end=" ")  # Cambiado a rojo (filas)
            for j in range(self.size):
                if self.board[i][j] == 0:
                    print("⬜ ",end=" ")
                if self.board[i][j] == 1:
                    print("🟥 ",end=" ")
                if self.board[i][j] == 2:
                    print("🟦 ",end=" ")
                if j == self.size -1:
                    print(f"\033[31m {i} \033[0m",end=" ")  # Cambiado a rojo (filas)
            space += "  "
            print("\n")
        print(space,end="    ")
        for i in range(self.size):
            print(f"\033[34m{i}  \033[0m", end=" ")  # Cambiado a azul (columnas)