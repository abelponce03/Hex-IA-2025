import pygame
import math
import pygame.gfxdraw
from table import HexagonGame
from config import WIDTH, HEIGHT, COLORS
from draw import draw_hexagon


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.SRCALPHA)
    pygame.display.set_caption("Hexagon Moderno")
    clock = pygame.time.Clock()
    game = HexagonGame()
    hover_hex = None

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

        # Dibujar hexágonos
        for hex in game.board.values():
            draw_hexagon(screen, hex, hover_hex == hex)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()