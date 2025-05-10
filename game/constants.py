import pygame

# Cài đặt cửa sổ
WIDTH = 700
HEIGHT = 750
CELL_SIZE = 50

# Trạng thái trò chơi
MENU = 0
ALGORITHM_SELECTION = 1
READY = 2
PLAYING = 3
WIN_SCREEN = 4
GAME_OVER_SCREEN = 5

# Phần tử giao diện
play_button_rect = pygame.Rect((WIDTH - 100) // 2, HEIGHT - 270, 100, 60)

# Cài đặt hoạt hình
LOADING_DURATION = 3  # giây
HOVER_SCALE = 1.1  # Hệ số phóng to khi di chuột qua nút