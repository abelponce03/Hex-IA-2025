import pygame
import pygame.gfxdraw
from game import HexagonGame
from config import WIDTH, HEIGHT, COLORS
from draw import draw_hexagon, draw_win_message, draw_edges


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.SRCALPHA)
    pygame.display.set_caption("Hexagon Moderno")
    clock = pygame.time.Clock()
    game = HexagonGame()
    hover_hex = None
    prev_hover_hex = None  # Para detectar cambios en el hover

    running = True
    while running:
        screen.fill(COLORS['background'])
        mouse_pos = pygame.mouse.get_pos()
        hover_hex = game.get_hex_at_position(mouse_pos)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                game.handle_click(mouse_pos)

        # Sonido al pasar sobre hexágono
        if hover_hex != prev_hover_hex and hover_hex is not None:
            game.sounds['hover'].play()
        prev_hover_hex = hover_hex
        
        # Dibujar hexágonos
        for hex in game.board.values():
            draw_hexagon(screen, hex, hover_hex == hex)
            
        #Dibujar extremos a conectar
        draw_edges(screen)
            
        # Mensaje de victoria
        if game.game_over:
            draw_win_message(screen, game.current_player)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()