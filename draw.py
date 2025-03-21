import math
import pygame
from config import HEX_SIZE, COLORS, WIDTH, HEIGHT
from hexagon import Hexagon


def draw_hexagon(screen, hex, hover=False):
    center = hex.get_pixel_position()
    corners = []
    for i in range(6):
        angle = math.radians(60 * i + 30)  # +30 para alinear vértices
        x = center[0] + HEX_SIZE * math.cos(angle)
        y = center[1] + HEX_SIZE * math.sin(angle)
        corners.append((x, y))
    
    # Sombras
    shadow_offset = 5
    shadow_corners = [(x + shadow_offset, y + shadow_offset) for (x, y) in corners]
    pygame.gfxdraw.filled_polygon(screen, shadow_corners, (*COLORS['shadow'][:3],))
    
    # Color base
    color = hex.color if hex.color else (50, 50, 50)
    if hover:
        color = tuple(min(c + 40, 255) for c in color)
    
    # Relleno con anti-aliasing
    pygame.gfxdraw.filled_polygon(screen, corners, color)
    pygame.gfxdraw.aapolygon(screen, corners, color)
    
    # Borde
    pygame.gfxdraw.aapolygon(screen, corners, COLORS['hex_border'])
    
    
def draw_win_message(screen, player):
    font = pygame.font.Font(None, 74)
    text = font.render(f"¡Jugador {player} gana!", True, COLORS['text'])
    text_rect = text.get_rect(center=(WIDTH//2, HEIGHT//2))
    screen.blit(text, text_rect)
    
    
def draw_edges(screen):
    
    
    #Esquinas donde ambos pueden conectar
    pygame.draw.circle(screen, (255, 255, 255), Hexagon(-5,0).get_pixel_position(), 8)  # Círculos más grandes
    pygame.draw.circle(screen, (255, 255, 255), Hexagon(-15,10).get_pixel_position(), 8)  # Círculos más grandes
    pygame.draw.circle(screen, (255, 255, 255), Hexagon(-5,10).get_pixel_position(), 8)  # Círculos más grandes
    pygame.draw.circle(screen, (255, 255, 255), Hexagon(5,0).get_pixel_position(), 8)  # Círculos más grandes
    
    #Centro donde no se puede poner ficha el primer turno
    pygame.draw.circle(screen, (200, 10, 47), Hexagon(-5,5).get_pixel_position(), 8)  # Círculos más grandes
    pygame.draw.circle(screen, (255, 255, 255), Hexagon(-5,5).get_pixel_position(), 8, 2)  # Borde blanco
    
    for player in [1, 2]:
        color = COLORS[f'player{player}']
        start_hexes = []
        end_hexes = []
        
        # Dibujar borde inicial
        if player == 2:
            for i in range(-4, 5) :
                start_hexes.append(Hexagon(i, 0))
                end_hexes.append(Hexagon(i - 10, 10))
        else:
            j = 0
            for i in range(-14, -5):
                start_hexes.append(Hexagon(i, 9 - j))
                end_hexes.append(Hexagon(i + 10, 9 - j))
                j = j + 1
                
        # Dibujar ambos bordes
        for hex in start_hexes + end_hexes:
            pygame.draw.circle(screen, color, hex.get_pixel_position(), 8)  # Círculos más grandes
            pygame.draw.circle(screen, (255, 255, 255), hex.get_pixel_position(), 8, 2)  # Borde blanco
            
    
    
def draw_menu(screen):
    screen.fill(COLORS['background'])
    font = pygame.font.Font(None, 74)
    
    # Título
    title = font.render("HEXAGON MODERNO", True, COLORS['text'])
    title_rect = title.get_rect(center=(WIDTH//2, HEIGHT//4))
    screen.blit(title, title_rect)
    
    # Botones
    button_font = pygame.font.Font(None, 50)
    
    # Botón Jugador vs IA
    pygame.draw.rect(screen, COLORS['player1'], (WIDTH//2 - 150, HEIGHT//2 - 50, 300, 70))
    text_ia = button_font.render("Jugar vs IA", True, COLORS['text'])
    text_ia_rect = text_ia.get_rect(center=(WIDTH//2, HEIGHT//2 - 15))
    screen.blit(text_ia, text_ia_rect)
    
    # Botón Jugador vs Jugador
    pygame.draw.rect(screen, COLORS['player2'], (WIDTH//2 - 150, HEIGHT//2 + 50, 300, 70))
    text_pvp = button_font.render("Jugar vs Jugador", True, COLORS['text'])
    text_pvp_rect = text_pvp.get_rect(center=(WIDTH//2, HEIGHT//2 + 85))
    screen.blit(text_pvp, text_pvp_rect)
    
    pygame.display.flip()