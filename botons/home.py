import pygame
from config import COLORS

def home (screen, exit_font):
    
    menu_btn_rect = pygame.Rect(1280, 660, 50, 40)
    pygame.draw.rect(screen, COLORS['player1'], menu_btn_rect, border_radius=10)
    menu_text = exit_font.render("M", True, COLORS['text'])
    screen.blit(menu_text, menu_text.get_rect(center=menu_btn_rect.center))
    
    return menu_btn_rect