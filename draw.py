import math
import pygame
from config import HEX_SIZE, COLORS


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