import pygame
from PIL import Image, ImageSequence
import os
from .constants import WIDTH, HEIGHT, CELL_SIZE

class AssetManager:
    def __init__(self):
        # Load map tiles
        self.image_maps = {}
        for i in range(1, 5):
            img = pygame.image.load(rf"E:\School\AI\PythonPacman\Image\{i}.png")
            self.image_maps[i] = pygame.transform.scale(img, (CELL_SIZE, CELL_SIZE))

        # Load screens
        self.loading_img = pygame.image.load(r"E:\School\AI\PACMAN\assets\Image\LoadingGame.png")
        self.loading_img = pygame.transform.scale(self.loading_img, (WIDTH, HEIGHT))

        self.menu_img = pygame.image.load(r"E:\School\AI\PACMAN\assets\Image\BackgroundPlay.png")
        self.menu_img = pygame.transform.scale(self.menu_img, (WIDTH, HEIGHT))

        # Load play button
        self.play_button_img = pygame.image.load(r'E:\School\AI\PythonPacman\Image\button_play.png')
        self.play_button_normal = pygame.transform.scale(self.play_button_img, (230, 140))
        self.play_button_hover = pygame.transform.scale(self.play_button_img, (int(230 * 1.1), int(140 * 1.1)))

        # Load and process GIF
        gif = Image.open(r"E:\School\AI\PACMAN\assets\Image\Loading.gif")
        self.gif_frames = []
        
        for frame in ImageSequence.Iterator(gif):
            frame_surface = pygame.image.fromstring(
                frame.convert("RGBA").tobytes(), frame.size, "RGBA"
            )
            frame_surface = pygame.transform.scale(frame_surface, (503.15, 41.6))
            self.gif_frames.append(frame_surface)