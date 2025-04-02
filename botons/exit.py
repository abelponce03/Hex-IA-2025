import pygame
from config import COLORS

def exit (screen):
    exit_btn_rect = pygame.Rect(1160, 660, 50, 40)
    pygame.draw.rect(screen, (200, 50, 50), exit_btn_rect, border_radius=10)
    exit_font = pygame.font.SysFont('Arial Unicode MS', 40)
    exit_text = exit_font.render("X", True, COLORS['text'])
    text_rect = exit_text.get_rect(center=exit_btn_rect.center)
    screen.blit(exit_text, text_rect)
    
    return exit_btn_rect, exit_font