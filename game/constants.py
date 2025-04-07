import pygame

# Window settings
WIDTH = 600
HEIGHT = 650
CELL_SIZE = 20

# Game states
LOADING = 0
MENU = 1
PLAYING = 2

# UI Elements
play_button_rect = pygame.Rect(168, 493, 230, 140)

# Animation settings
GIF_DELAY = 100  # milliseconds
LOADING_DURATION = 3  # seconds
HOVER_SCALE = 1.1  # Button hover scale factor