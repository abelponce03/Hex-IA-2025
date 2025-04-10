import pygame
import pygame.gfxdraw
from game import HexagonGame
from config import WIDTH, HEIGHT, COLORS
from draw import draw_hexagon, draw_win_message, draw_edges, draw_glass_button_1, draw_ai_thinking
from game import ai_turn
from menu import menu
import queue


def main():
    
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.SRCALPHA)
    pygame.display.set_caption("Hex")
    clock = pygame.time.Clock()

    
    while True:
        
        # Mostrar menú inicial
        in_menu = True
        vs_ai = False 
        board_size = 11
        running = True
        
        running = True
    
        while in_menu:
        
            in_menu, board_size, vs_ai, running = menu(in_menu, screen, board_size, vs_ai, running)        
            if not running:
                pygame.quit()            
            
            
        game = HexagonGame(vs_ai=vs_ai, board_size=board_size)
        hover_hex = None
        prev_hover_hex = None  # Para detectar cambios en el hover

        game_running = True
        while game_running:
        
            # Capturar fondo antes del desenfoque
            background = screen.copy()
            screen.fill(COLORS['background'])
            mouse_pos = pygame.mouse.get_pos()
            hover_hex = game.get_hex_at_position(mouse_pos)

            # Sonido al pasar sobre hexágono
            if hover_hex != prev_hover_hex and hover_hex is not None:
                game.sounds['hover'].play()
            prev_hover_hex = hover_hex
        
            # Dibujar hexágonos
            for hex in game.board.values():
                draw_hexagon(screen, hex, hover_hex == hex, game.board)
            
            #Dibujar extremos a conectar
            #draw_edges(screen, game.board_size, game.board)
        
            button_size = 80  # Tamaño cuadrado
            button_margin = 10
            button_font = pygame.font.SysFont('Arial', 20, bold=True)
            mouse_pos = pygame.mouse.get_pos()

            # Posiciones iniciales
            start_x = 40
            start_y = 40

            # Botón Menú (icono o texto compacto)
            menu_btn_rect = draw_glass_button_1(
                "≡",  # Símbolo hamburguesa
                start_y,
                COLORS['player1'],
                mouse_pos,
                screen,
                button_font,
                pos_x=start_x,
                width=button_size,
                height=button_size
            )

            # Botón Reiniciar (icono de flecha circular)
            restart_btn_rect = draw_glass_button_1(
                "R",
                start_y + button_size + button_margin,
                COLORS['player2'],
                mouse_pos,
                screen,
                button_font,
                pos_x=start_x,
                width=button_size,
                height=button_size
            )

            # Botón Salir (X)
            exit_btn_rect = draw_glass_button_1(
                "×",
                start_y + 2*(button_size + button_margin),
                COLORS['red'],
                mouse_pos,
                screen,
                button_font,
                pos_x=start_x,
                width=button_size,
                height=button_size
            )
        
            # Turno de la IA (solo en modo vs IA)
            # Verificar si la IA ha terminado de pensar
            if game.vs_ai and not game.game_over and game.current_player == 2:
                ai_turn(game)
                try:
                    # Esperar un tiempo razonable pero no bloquear indefinidamente
                    ai_move = game.ai_queue.get(block=False)
                    if ai_move:
                        print(f"IA juega en: {ai_move}")  # Depuración
                        game.play_move(*ai_move)
                except queue.Empty:
                    # Mostrar indicador de carga mientras la IA piensa
                    draw_ai_thinking(screen)
        
            # Procesar eventos
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    # Reiniciar partida
                    if restart_btn_rect.collidepoint(event.pos):
                        game = HexagonGame(vs_ai=vs_ai, board_size=board_size)
                    # Volver al menú
                    elif menu_btn_rect.collidepoint(event.pos):
                        game_running = False  # Sale del bucle del juego
                    # Salir del juego
                    elif exit_btn_rect.collidepoint(event.pos):
                        pygame.quit()
                        return
                    # Jugada del usuario
                    else:
                        game.handle_click(mouse_pos)
        
        
            
            # Mensaje de victoria
            if game.game_over:
                restart_rect, exit_rect, menu_rect = draw_win_message(screen, game, background)
                for event in pygame.event.get():
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if restart_rect.collidepoint(event.pos):
                            game = HexagonGame(vs_ai=vs_ai, board_size=board_size)
                        elif exit_rect.collidepoint(event.pos):
                            pygame.quit()
                            return
                        elif menu_rect.collidepoint(event.pos):
                            game_running = False

            pygame.display.flip()
            clock.tick(60)


if __name__ == "__main__":
    main()