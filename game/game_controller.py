import pygame
import time
from .constants import *
from .board import boards
from .assets_manager import AssetManager
from .player import Player

class GameState:
    def __init__(self, screen, assets):
        self.screen = screen
        self.assets = assets
        self.current_state = LOADING
        self.start_time = time.time()
        self.current_frame = 0
        self.last_frame_time = time.time()
        self.clock = pygame.time.Clock()
        self.button_hover = False
        
        #Biến này dùng để điều khiển nhấp nháy của Power-up
        self.flicker = False
        # Khởi tạo Player
        self.player = Player(self.screen, self.assets.player_images, 300, 500)
        
        # Initialize direction_command
        self.direction_command = self.player.direction
        
    def handle_events(self):
        mouse_pos = pygame.mouse.get_pos()
        
        # Handle button hover
        if self.current_state == MENU:
            self.button_hover = play_button_rect.collidepoint(mouse_pos)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return False
            
            if self.current_state == MENU:
                if play_button_rect.collidepoint(mouse_pos) and event.type == pygame.MOUSEBUTTONDOWN:
                    pygame.time.delay(100)  # Click feel
                    self.current_state = PLAYING
            
            elif self.current_state == PLAYING:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                        self.direction_command = 0
                    elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
                        self.direction_command = 1
                    elif event.key == pygame.K_UP or event.key == pygame.K_w:
                        self.direction_command = 2
                    elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                        self.direction_command = 3             
        return True

    def update(self, current_time):
        if self.current_state == LOADING and current_time - self.start_time > LOADING_DURATION:
            self.current_state = MENU
        elif self.current_state == PLAYING:
              # Cập nhật counter trong Player
            if self.player.counter < 19:
                self.player.counter += 1
                if self.player.counter > 3:
                    self.flicker = False
            else:
                self.player.counter = 0
                self.flicker = True
            self.player.turns_allowed = self.player.check_position()
            # Update direction based on direction_command and turns_allowed
            if self.direction_command == 0 and self.player.turns_allowed[0]:
                self.player.direction = 0
            if self.direction_command == 1 and self.player.turns_allowed[1]:
                self.player.direction = 1
            if self.direction_command == 2 and self.player.turns_allowed[2]:
                self.player.direction = 2
            if self.direction_command == 3 and self.player.turns_allowed[3]:
                self.player.direction = 3
            
            self.player.move_player()
            self.player.check_collision()
    def render(self):
        if self.current_state == LOADING:
            self._render_loading()
        elif self.current_state == MENU:
            self._render_menu()
        elif self.current_state == PLAYING:
            self._render_game()
            
        pygame.display.flip()
        self.clock.tick(60)

    def _render_loading(self):
        current_time = time.time()
        self.screen.blit(self.assets.loading_img, (0, 0))

    def _render_menu(self):
        # Draw background
        self.screen.blit(self.assets.menu_img, (0, 0))
        
        if self.button_hover:
            # Calculate position for larger hover button
            hover_x = play_button_rect.x - (self.assets.play_button_hover.get_width() - play_button_rect.width) // 2
            hover_y = play_button_rect.y - (self.assets.play_button_hover.get_height() - play_button_rect.height) // 2
            self.screen.blit(self.assets.play_button_hover, (hover_x, hover_y))
        else:
            self.screen.blit(self.assets.play_button_normal, play_button_rect)

    def _render_game(self):
        self.screen.fill((0, 0, 0))  # Clear the screen with black
        for i in range(len(boards)):
            for j in range(len(boards[i])):
                
                # Vẽ hình ảnh tương ứng với giá trị trong boards
                image = self.assets.image_maps[boards[i][j]]
                if boards[i][j] == 4 or boards[i][j] == 5:
                    self.screen.blit(image, (j * CELL_SIZE, i * CELL_SIZE))
                if boards[i][j] == 2 and not ((i, j) in [(7, 6), (7, 7), (8, 6), (8, 7)]) :
                    dot_x = j * CELL_SIZE + (CELL_SIZE - 25) // 2
                    dot_y = i * CELL_SIZE + (CELL_SIZE - 25) // 2
                    self.screen.blit(image, (dot_x, dot_y))
                if boards[i][j] == 3 and (not self.flicker):
                    dot_x = j * CELL_SIZE + (CELL_SIZE - 45) // 2
                    dot_y = i * CELL_SIZE + (CELL_SIZE - 45) // 2
                    self.screen.blit(image, (dot_x, dot_y))
                if boards[i][j] == 0 or boards[i][j] == 1:
                    self.screen.blit(image, (j * CELL_SIZE, i * CELL_SIZE))

        self.player.draw_player()
                    