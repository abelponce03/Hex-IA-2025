import pygame
from config import COLORS

def restart(screen, exit_font):
    restart_btn_rect = pygame.Rect(1220, 660, 50, 40)
    pygame.draw.rect(screen, COLORS['player2'], restart_btn_rect, border_radius=10)
    restart_text = exit_font.render("R", True, COLORS['text'])
    screen.blit(restart_text, restart_text.get_rect(center=restart_btn_rect.center))
    
    return restart_btn_rect