import pygame
from game import Game

def main():
    pygame.init()
    pygame.mixer.init()
    game = Game()
    game.show_menu()

if __name__ == "__main__":
    main()