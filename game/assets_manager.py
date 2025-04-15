import pygame
from PIL import Image, ImageSequence
import os
from .constants import WIDTH, HEIGHT, CELL_SIZE

class AssetManager:
    def __init__(self):  
        # Load map tiles
        self.image_maps = {}
        for i in range(0, 3):
            img = pygame.image.load(rf"E:\School\AI\PACMAN\assets\Image\{i}.png")
            self.image_maps[i] = pygame.transform.scale(img, (CELL_SIZE, CELL_SIZE))
        for i in range(5, 7):
            img = pygame.image.load(rf"assets/other_images/{i}.png")
            self.image_maps[i] = pygame.transform.scale(img, (CELL_SIZE, CELL_SIZE))
        # Load screens
        self.loading_img = pygame.image.load(r"E:\School\AI\PACMAN\assets\Image\LoadingGame.png")
        self.loading_img = pygame.transform.scale(self.loading_img, (WIDTH, HEIGHT))

        self.menu_img = pygame.image.load(r"E:\School\AI\PACMAN\assets\Image\BackgroundPlay.png")
        self.menu_img = pygame.transform.scale(self.menu_img, (WIDTH, HEIGHT))

        # Load play button
        self.play_button_img = pygame.image.load(r'E:\School\AI\PACMAN\assets\Image\button_play.png')
        self.play_button_normal = pygame.transform.scale(self.play_button_img, (100, 60))
        self.play_button_hover = pygame.transform.scale(self.play_button_img, (int(100 * 1.1), int(60 * 1.1)))
        
        # Load Dot
        self.loading_dot = pygame.image.load(r"E:\School\AI\PACMAN\assets\Image\Dot.png")
        self.loading_dot = pygame.transform.scale(self.loading_dot, (25, 25))
        
        # Load Power-up
        self.large_dot = pygame.image.load(r"E:\School\AI\PACMAN\assets\Image\Dot.png")
        self.large_dot = pygame.transform.scale(self.loading_dot, (45, 45))
        
        # Khởi tạo self.player_images là một danh sách
        self.player_images = []
        for i in range(1, 5):
            img = pygame.image.load(rf"E:\School\AI\PACMAN\assets\player_images\{i}.png")
            scaled_img = pygame.transform.scale(img, (47, 47))
            self.player_images.append(scaled_img)
        
        # Load other images
        self.other_images1 = pygame.image.load(r"E:\School\AI\PACMAN\assets\other_images\5.png")
        self.other_images1 = pygame.transform.scale(self.other_images1, (CELL_SIZE, CELL_SIZE))
        self.other_images2 = pygame.image.load(r"E:\School\AI\PACMAN\assets\other_images\6.png")
        self.other_images2 = pygame.transform.scale(self.other_images2, (CELL_SIZE, CELL_SIZE))