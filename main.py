import pygame
import pygame.gfxdraw
from game import HexagonGame
from config import WIDTH, HEIGHT, COLORS
from draw import draw_hexagon, draw_win_message, draw_edges, draw_menu


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.SRCALPHA)
    pygame.display.set_caption("Hexagon Moderno")
    clock = pygame.time.Clock()

    # Mostrar menú inicial
    in_menu = True
    vs_ai = False 
    
    while in_menu:
        draw_menu(screen)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()
                # Botón "Jugar vs IA"
                if WIDTH//2 - 150 <= x <= WIDTH//2 + 150 and HEIGHT//2 - 50 <= y <= HEIGHT//2 + 20:
                    vs_ai = True
                    in_menu = False
                # Botón "Jugar vs Jugador"
                elif WIDTH//2 - 150 <= x <= WIDTH//2 + 150 and HEIGHT//2 + 50 <= y <= HEIGHT//2 + 120:
                    vs_ai = False
                    in_menu = False
                    
    game = HexagonGame(vs_ai=vs_ai)
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
        
        # Turno de la IA (solo en modo vs IA)
        if vs_ai and not game.game_over and game.current_player == 2:
            game.ai_turn()
            
        # Mensaje de victoria
        if game.game_over:
            draw_win_message(screen, game.current_player)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()