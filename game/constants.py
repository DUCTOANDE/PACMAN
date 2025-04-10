import pygame

# Window settings
WIDTH = 700
HEIGHT =750
CELL_SIZE = 50

# Game states
LOADING = 0
MENU = 1
PLAYING = 2

# UI Elements
play_button_rect = pygame.Rect((WIDTH - 100) // 2, HEIGHT - 270, 100, 60) 

# Animation settings
LOADING_DURATION = 3  # seconds
HOVER_SCALE = 1.1  # Button hover scale factor