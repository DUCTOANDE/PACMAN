import pygame

# Cài đặt cửa sổ
WIDTH = 700
HEIGHT = 750
CELL_SIZE = 50

# Trạng thái trò chơi
LOADING = 0
MENU = 1
PLAYING = 2
WIN_SCREEN = 3
GAME_OVER_SCREEN = 4

# Phần tử giao diện
play_button_rect = pygame.Rect((WIDTH - 100) // 2, HEIGHT - 270, 100, 60)

# Cài đặt hoạt hình
LOADING_DURATION = 3  # giây
HOVER_SCALE = 1.1  # Hệ số phóng to khi di chuột qua nút