import pygame
from draw import draw_menu, draw_text_input

def menu(in_menu, screen, board_size, vs_ai, running):
    btn_ia, btn_pvp, btn_exit = draw_menu(screen)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            in_menu = False
        if event.type == pygame.MOUSEBUTTONDOWN:
               
            if btn_ia.collidepoint(event.pos) or btn_pvp.collidepoint(event.pos) or btn_pvp.collidepoint(event.pos):
                vs_ai = btn_ia.collidepoint(event.pos)
                input_text = ""
                error = ""
                board_size = None
                    
                # Bucle de entrada de texto
                while True:
                    draw_text_input(screen, input_text, 
                        "Ingrese tamaño del tablero (5-N):", error)
                        
                    for size_event in pygame.event.get():
                        if size_event.type == pygame.QUIT:
                            pygame.quit()
                            return
                            
                        if size_event.type == pygame.KEYDOWN:
                            if size_event.key == pygame.K_RETURN:
                                try:
                                    board_size = int(input_text)
                                    if 5 <= board_size:
                                        in_menu = False
                                        break
                                    else:
                                        error = "El tamaño debe estar entre 5 y N"
                                except ValueError:
                                    error = "Ingrese un número válido"
                            elif size_event.key == pygame.K_BACKSPACE:
                                input_text = input_text[:-1]
                            elif size_event.unicode.isdigit():
                                input_text += size_event.unicode
                        
                    if not in_menu:
                        break
                            
                if board_size is None:
                    continue
                                        
            # Botón "Jugar vs IA"
            elif btn_ia.collidepoint(event.pos):
                vs_ai = True
                in_menu = False
            # Botón "Jugar vs Jugador"
            elif btn_pvp.collidepoint(event.pos):
                vs_ai = False
                in_menu = False
                
            elif btn_exit.collidepoint(event.pos):
                vs_ai = False
                in_menu = False
                running = False
                
                
    return in_menu, board_size, vs_ai, running