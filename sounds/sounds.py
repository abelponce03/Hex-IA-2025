import pygame

def load_sounds():
        pygame.mixer.init()
        return {
            'place': pygame.mixer.Sound('sounds/place.wav'),
            'hover': pygame.mixer.Sound('sounds/hover.wav'),
            'click': pygame.mixer.Sound('sounds/click.wav'),
            'win': pygame.mixer.Sound('sounds/win.wav')
        }