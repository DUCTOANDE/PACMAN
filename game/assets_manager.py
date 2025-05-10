import pygame
from PIL import Image, ImageSequence
import os
from .constants import WIDTH, HEIGHT, CELL_SIZE

class AssetManager:
    def __init__(self):
        # Khởi tạo pygame mixer để xử lý âm thanh
        pygame.mixer.init()
        # Tải các ô bản đồ
        self.image_maps = {}
        for i in range(0, 7):
            img = pygame.image.load(rf".\assets\Image\{i}.png")
            if i == 2:
                self.image_maps[i] = pygame.transform.scale(img, (CELL_SIZE, CELL_SIZE))
            elif i == 3:
                self.image_maps[i] = pygame.transform.scale(img, (CELL_SIZE, CELL_SIZE))
            else:
                self.image_maps[i] = pygame.transform.scale(img, (CELL_SIZE, CELL_SIZE))

        self.menu_img = pygame.image.load(r".\assets\Image\BackgroundPlay.jpg")
        self.menu_img = pygame.transform.scale(self.menu_img, (WIDTH, HEIGHT))

        # Tải nút chơi
        self.play_button_img = pygame.image.load(r'.\assets\Image\button_play.png')
        self.play_button_normal = pygame.transform.scale(self.play_button_img, (100, 80))
        self.play_button_hover = pygame.transform.scale(self.play_button_img, (int(100 * 1.1), int(60 * 1.1)))

        # Tải các nút menu, continue, exit
        # ---->> Menu <<----
        self.menu_button_img = pygame.image.load(r'.\assets\Image\menu.png')
        self.menu_button_normal = pygame.transform.scale(self.menu_button_img, (100, 60))
        self.menu_button_hover = pygame.transform.scale(self.menu_button_img, (int(100 * 1.1), int(60 * 1.1)))

        # ---->> Continue <<----
        self.continue_button_img = pygame.image.load(r'.\assets\Image\continue.png')
        self.continue_button_normal = pygame.transform.scale(self.continue_button_img, (100, 60))
        self.continue_button_hover = pygame.transform.scale(self.continue_button_img, (int(100 * 1.1), int(60 * 1.1)))

        # ---->> Exit <<----
        self.exit_button_img = pygame.image.load(r'.\assets\Image\exit.png')
        self.exit_button_normal = pygame.transform.scale(self.exit_button_img, (100, 60))
        self.exit_button_hover = pygame.transform.scale(self.exit_button_img, (int(100 * 1.1), int(60 * 1.1)))

        # Khởi tạo danh sách hình ảnh người chơi
        self.player_images = []
        for i in range(1, 5):
            img = pygame.image.load(rf".\assets\player_images\{i}.png")
            scaled_img = pygame.transform.scale(img, (CELL_SIZE, CELL_SIZE))
            self.player_images.append(scaled_img)

        # Tải điểm
        self.score_img = pygame.image.load(r".\assets\Image\Score.png")
        self.score_img = pygame.transform.scale(self.score_img, (40, 40))

        # Tải hình ảnh sẵn sàng
        self.ready_img = pygame.image.load(r".\assets\Image\ready.png")
        self.ready_img = pygame.transform.scale(self.ready_img, (90, 150))

        # Tải hình ảnh ready
        self.ready_screen_img = pygame.image.load(r".\assets\Image\ready_background.png")
        self.ready_screen_img = pygame.transform.scale(self.ready_screen_img, (WIDTH, HEIGHT))
        # Tải mạng
        self.lives_img = pygame.image.load(r".\assets\Image\lives.png")
        self.lives_img = pygame.transform.scale(self.lives_img, (40, 40))

        # Tải hình ảnh ma
        self.binky_img = pygame.image.load(r".\assets\ghost_images\red.png")
        self.binky_img = pygame.transform.scale(self.binky_img, (CELL_SIZE, CELL_SIZE))

        self.pinky_img = pygame.image.load(r".\assets\ghost_images\pink.png")
        self.pinky_img = pygame.transform.scale(self.pinky_img, (CELL_SIZE, CELL_SIZE))

        self.inky_img = pygame.image.load(r".\assets\ghost_images\blue.png")
        self.inky_img = pygame.transform.scale(self.inky_img, (CELL_SIZE, CELL_SIZE))

        self.clyde_img = pygame.image.load(r".\assets\ghost_images\orange.png")
        self.clyde_img = pygame.transform.scale(self.clyde_img, (CELL_SIZE, CELL_SIZE))

        self.spooked_img = pygame.image.load(r".\assets\ghost_images\powerup.png")
        self.spooked_img = pygame.transform.scale(self.spooked_img, (CELL_SIZE, CELL_SIZE))

        self.dead_img = pygame.image.load(r".\assets\ghost_images\dead.png")
        self.dead_img = pygame.transform.scale(self.dead_img, (CELL_SIZE, CELL_SIZE))

        # Tải hiệu ứng âm thanh
        self.beginning_sound = pygame.mixer.Sound(r".\assets\sound\pacman_beginning.wav")
        self.death_sound = pygame.mixer.Sound(r".\assets\sound\pacman_death.wav")
        self.eatghost_sound = pygame.mixer.Sound(r".\assets\sound\pacman_eatghost.wav")
        self.pellet_sound = pygame.mixer.Sound(r".\assets\sound\pacman_pellet_low.wav")
        self.power_pellet_sound = pygame.mixer.Sound(r".\assets\sound\pacman_power_pellet.wav")

        # Đường dẫn đến tệp nhạc nền
        self.background_music_path = pygame.mixer.Sound(r".\assets\sound\background.mp3")

        # Tải âm thanh chiến thắng và thua cuộc
        self.victory_sound = pygame.mixer.Sound(r".\assets\sound\victory.mp3")
        self.defeat_sound = pygame.mixer.Sound(r".\assets\sound\gameover.mp3")
        
        # Tải ảnh High Score
        self.high_score_img = pygame.image.load(r".\assets\Image\HighScore.png")