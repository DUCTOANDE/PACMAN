import pygame
from PIL import Image, ImageSequence
import os
from .constants import WIDTH, HEIGHT, CELL_SIZE

class AssetManager:
    def __init__(self):  
        # Load map tiles
        self.image_maps = {}
        for i in range(0, 3):
            img = pygame.image.load(rf"C:\PACMAN\assets\Image\{i}.png")
            self.image_maps[i] = pygame.transform.scale(img, (CELL_SIZE, CELL_SIZE))

        # Load screens
        self.loading_img = pygame.image.load(r"C:\PACMAN\assets\Image\LoadingGame.png")
        self.loading_img = pygame.transform.scale(self.loading_img, (WIDTH, HEIGHT))

        self.menu_img = pygame.image.load(r"C:\PACMAN\assets\Image\BackgroundPlay.png")
        self.menu_img = pygame.transform.scale(self.menu_img, (WIDTH, HEIGHT))

        # Load play button
        self.play_button_img = pygame.image.load(r'C:\PACMAN\assets\Image\button_play.png')
        self.play_button_normal = pygame.transform.scale(self.play_button_img, (100, 60))
        self.play_button_hover = pygame.transform.scale(self.play_button_img, (int(100 * 1.1), int(60 * 1.1)))
