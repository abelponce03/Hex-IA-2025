import math
import pygame
from config import COLORS, WIDTH, HEIGHT
from hexagon import Hexagon
from botons.restart import restart
from botons.home import home
from botons.exit import exit


def draw_hexagon(screen, hex, hover=False, board=None):
    center = hex.get_pixel_position(board)
    corners = []
    for i in range(6):
        angle = math.radians(60 * i + 30)  # +30 para alinear vértices
        x = center[0] + hex.HEX_SIZE * math.cos(angle)
        y = center[1] + hex.HEX_SIZE * math.sin(angle)
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
    
    if hover:
        color = tuple(min(c + 60, 255) for c in color)
        # Agregar brillo interno
        highlight = pygame.Surface((hex.HEX_SIZE*2, hex.HEX_SIZE*2), pygame.SRCALPHA)
        pygame.gfxdraw.filled_circle(highlight, hex.HEX_SIZE, hex.HEX_SIZE, int(hex.HEX_SIZE*0.7), (*color, 50))
        screen.blit(highlight, (center[0]-hex.HEX_SIZE, center[1]-hex.HEX_SIZE))

    
    
def draw_rounded_rect(surface, rect, color, radius=15):
    """Dibuja un rectángulo con esquinas redondeadas"""
    rect = pygame.Rect(rect)
    
    # Dibujar rectángulos principales
    pygame.draw.rect(surface, color, (rect.x + radius, rect.y, rect.width - 2*radius, rect.height))
    pygame.draw.rect(surface, color, (rect.x, rect.y + radius, rect.width, rect.height - 2*radius))
    
    # Dibujar círculos para las esquinas
    pygame.draw.circle(surface, color, (rect.x + radius, rect.y + radius), radius)
    pygame.draw.circle(surface, color, (rect.x + rect.width - radius, rect.y + radius), radius)
    pygame.draw.circle(surface, color, (rect.x + radius, rect.y + rect.height - radius), radius)
    pygame.draw.circle(surface, color, (rect.x + rect.width - radius, rect.y + rect.height - radius), radius)

def blur_surface(surface, amount):
    """Efecto de desenfoque usando escalado"""
    scale = 1.0 / amount
    small = pygame.transform.smoothscale(surface, (int(WIDTH*scale), int(HEIGHT*scale)))
    return pygame.transform.smoothscale(small, (WIDTH, HEIGHT))

def draw_win_message(screen, game, background):
    
    # Aplicar desenfoque al fondo
    blurred_bg = blur_surface(background, 8)
    screen.blit(blurred_bg, (0, 0))
    
    # Capa oscura semi-transparente
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))  # 70% de opacidad
    screen.blit(overlay, (0, 0))

    # Panel para el texto con un efecto de brillo adicional
    text_panel = pygame.Surface((900, 280), pygame.SRCALPHA)
    pygame.draw.rect(text_panel, (0, 0, 0, 150), text_panel.get_rect(), border_radius=25)
    
    # Añadir un halo alrededor del panel para hacerlo destacar
    glow_panel = pygame.Surface((920, 270), pygame.SRCALPHA)
    color_player = COLORS[f'player{game.current_player}']
    

    # Mensaje de victoria con sombra y borde luminoso
    font = pygame.font.SysFont('Arial', 120, bold=True)
    
    # Múltiples capas de sombra para efecto 3D
    for offset in range(3, 6):
        shadow = font.render(f"¡JUGADOR {game.current_player} GANA!", True, (0, 0, 0, 100))
        shadow_rect = shadow.get_rect(center=(WIDTH//2 + offset, HEIGHT//2 - 180 + offset))
        screen.blit(shadow, shadow_rect)
    
    # Borde blanco alrededor del texto para hacerlo destacar
    glow = font.render(f"¡JUGADOR {game.current_player} GANA!", True, (255, 255, 255))
    for dx, dy in [(-2,0), (2,0), (0,-2), (0,2)]:
        glow_rect = glow.get_rect(center=(WIDTH//2 + dx, HEIGHT//2 - 180 + dy))
        screen.blit(glow, glow_rect)
    
    # Texto principal con el color del jugador ganador
    text = font.render(f"¡JUGADOR {game.current_player} GANA!", True, color_player)
    text_rect = text.get_rect(center=(WIDTH//2, HEIGHT//2 - 180))
    screen.blit(text, text_rect)
    
     # Botones debajo del mensaje
    button_font = pygame.font.SysFont('Arial', 50, bold=True)
    center_x = WIDTH//2
    center_y = HEIGHT//2
    mouse_pos = pygame.mouse.get_pos()

    # Ajustar posiciones Y
    restart_rect = draw_glass_button(
        "REINICIAR", 
        center_y - 70, 
        COLORS['player2'], 
        mouse_pos, 
        screen, 
        button_font
    )
    
    menu_rect = draw_glass_button(
        "MENU", 
        center_y + 100, 
        COLORS['player1'], 
        mouse_pos, 
        screen, 
        button_font
    )
    
    exit_rect = draw_glass_button(
        "SALIR", 
        center_y + 270, 
        COLORS['red'], 
        mouse_pos, 
        screen, 
        button_font
    ) 

    return restart_rect, exit_rect, menu_rect

def draw_edges(screen, size, board):
    offset = size // 2
    corners = [
        (0, -offset),
        (size - 1, -offset),
        (-2 * offset + (size % 2), offset - (size % 2)),
        (0, offset - (size % 2))
    ]
    
    # Dibujar solo las 4 esquinas
    for q, r in corners:
        pos = Hexagon(q, r).get_pixel_position(board)
        pygame.draw.circle(screen, (255, 255, 255), pos, 8)

    # Bordes de jugadores (precalculados)
    for player in [1, 2]:
        color = COLORS[f'player{player}']
        edge_hexes = [
            Hexagon(q, r) 
            for q, r in board.keys() 
            if (player == 1 and (q == -offset - r or q == offset - r)) or 
               (player == 2 and (r == -offset or r == offset))
        ]
        
        # Dibujar solo los bordes extremos
        for hex in edge_hexes[:size]:  # Limitar a cantidad necesaria
            pos = hex.get_pixel_position(board)
            pygame.draw.circle(screen, color, pos, 8)
            pygame.draw.circle(screen, (255, 255, 255), pos, 8, 2)
    

def draw_text_input(screen, text, prompt, error=""):
    screen.fill(COLORS['background'])
    font = pygame.font.SysFont('Arial', 60)
    input_font = pygame.font.SysFont('Arial', 80, bold=True)
    
    # Dibujar prompt
    prompt_surf = font.render(prompt, True, COLORS['text'])
    prompt_rect = prompt_surf.get_rect(center=(WIDTH//2, HEIGHT//3))
    screen.blit(prompt_surf, prompt_rect)
    
    # Dibujar caja de texto
    input_rect = pygame.Rect(WIDTH//2 - 200, HEIGHT//2 - 40, 400, 80)
    pygame.draw.rect(screen, COLORS['button_hover'], input_rect, border_radius=10)
    pygame.draw.rect(screen, COLORS['hex_border'], input_rect, 3, border_radius=10)
    
    # Texto ingresado
    input_surf = input_font.render(text, True, COLORS['text'])
    screen.blit(input_surf, (input_rect.x + 20, input_rect.y - 10))
    
    # Mensaje de error
    if error:
        error_surf = font.render(error, True, (255, 50, 50))
        error_rect = error_surf.get_rect(center=(WIDTH//2, HEIGHT//2 + 100))
        screen.blit(error_surf, error_rect)
    
    pygame.display.flip()
    return input_rect

def draw_glass_button_1(text_str, y_pos, base_color, mouse_pos, screen, button_font, pos_x=None, width=150, height=40):
    # Posición X personalizada
    x = pos_x if pos_x is not None else WIDTH//2 - width//2
    btn_rect = pygame.Rect(x, y_pos, width, height)
    hover = btn_rect.collidepoint(mouse_pos)
    
    # Superficie transparente
    button_surface = pygame.Surface((width, height), pygame.SRCALPHA)
    
    # Base del botón
    base_alpha = 200 if hover else 150
    pygame.draw.rect(button_surface, (*base_color, base_alpha), (0, 0, width, height), border_radius=8)
    
    # Efecto de vidrio
    if hover:
        overlay = pygame.Surface((width, height), pygame.SRCALPHA)
        pygame.draw.rect(overlay, (255, 255, 255, 50), (0, 0, width, height//2), border_radius=8)
        button_surface.blit(overlay, (0, 0))
    
    # Borde luminoso
    border_color = (255, 255, 255, 100) if hover else (*base_color, 100)
    pygame.draw.rect(button_surface, border_color, (0, 0, width, height), 2, border_radius=8)
    
    screen.blit(button_surface, (x, y_pos))
    
    # Texto centrado
    text = button_font.render(text_str, True, COLORS['text'])
    text_rect = text.get_rect(center=(x + width//2, y_pos + height//2))
    screen.blit(text, text_rect)
    
    return btn_rect

def draw_glass_button(text_str, y_pos, base_color, mouse_pos, screen, button_font):
        btn_rect = pygame.Rect(WIDTH//2 - 300, y_pos, 600, 150)  # Botones más grandes
        hover = btn_rect.collidepoint(mouse_pos)
        
        # Superficie transparente para efectos
        button_surface = pygame.Surface((600, 150), pygame.SRCALPHA)
        
        # Base del botón
        base_alpha = 200 if hover else 150
        pygame.draw.rect(button_surface, (*base_color, base_alpha), (0, 0, 600, 150), border_radius=30)
        
        # Efecto de vidrio
        if hover:
            overlay = pygame.Surface((600, 150), pygame.SRCALPHA)
            pygame.draw.rect(overlay, (255, 255, 255, 50), (0, 0, 600, 75), border_radius=30)
            button_surface.blit(overlay, (0, 0))
        
        # Borde luminoso
        border_color = (255, 255, 255, 100) if hover else (*base_color, 100)
        pygame.draw.rect(button_surface, border_color, (0, 0, 600, 150), 5, border_radius=30)
        
        screen.blit(button_surface, (WIDTH//2 - 300, y_pos))
        
        # Texto con efecto de elevación
        text = button_font.render(text_str, True, (0, 0, 0, 100))
        text_rect = text.get_rect(center=(WIDTH//2 + 3, y_pos + 80))
        screen.blit(text, text_rect)
        
        text = button_font.render(text_str, True, COLORS['text'])
        text_rect = text.get_rect(center=(WIDTH//2, y_pos + 75))
        screen.blit(text, text_rect)
        
        return btn_rect



def draw_menu(screen):
    screen.fill(COLORS['background'])
    font = pygame.font.SysFont('Arial', 120, bold=True)  # Fuente mejorada
    button_font = pygame.font.SysFont('Arial', 80, bold=True)  # Fuente más grande
    
    # Título con sombra
    title = font.render("HEX", True, COLORS['text'])
    title_rect = title.get_rect(center=(WIDTH//2, HEIGHT//4 - 30))
    # Sombra del título
    shadow = font.render("HEX", True, (100, 50, 74))
    screen.blit(shadow, (title_rect.x + 5, title_rect.y + 5))
    screen.blit(title, title_rect)
    
    mouse_pos = pygame.mouse.get_pos()

    # Botones principales
    btn_ia = draw_glass_button("VS IA", HEIGHT//2 - 180, COLORS['player1'], mouse_pos, screen, button_font)
    btn_pvp = draw_glass_button("VS PLAYER", HEIGHT//2 + 0, COLORS['player2'], mouse_pos, screen, button_font)
    btn_exit = draw_glass_button("EXIT", HEIGHT//2 + 180, COLORS['red'], mouse_pos, screen, button_font)

    pygame.display.flip()
    return btn_ia, btn_pvp, btn_exit