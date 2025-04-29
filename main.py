import pygame
import time
from game.constants import WIDTH, HEIGHT, CELL_SIZE
from game.assets_manager import AssetManager
from game.game_controller import GameState
from game.analyze_ghost_logs import *
def main():
    pygame.init()
    
    screen = pygame.display.set_mode([WIDTH, HEIGHT])
    pygame.display.set_caption("PACMAN GAME")
    
    assets = AssetManager()
    game = GameState(screen, assets)
    
    running = True
    while running:
        running = game.handle_events()
        game.update(time.time())
        game.render()
         
    pygame.quit()

if __name__ == "__main__":
    main()
