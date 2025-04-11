import pygame
import time
from .constants import *
from .board import boards

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
                    
        return True

    def update(self, current_time):
        if self.current_state == LOADING and current_time - self.start_time > LOADING_DURATION:
            self.current_state = MENU

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
        self.screen.fill((255, 204, 0))  # Màu nền
        for i in range(len(boards)):
            for j in range(len(boards[i])):
                # Vẽ hình ảnh tương ứng với giá trị trong boards
                image = self.assets.image_maps[boards[i][j]]
                self.screen.blit(image, (j * CELL_SIZE, i * CELL_SIZE))
                
                # Nếu là vị trí power-up, vẽ dot lớn hơn
                if (i, j) in [(4, 1), (4, 12), (9, 1), (9, 12)]:
                    dot_x = j * CELL_SIZE + (CELL_SIZE - self.assets.large_dot.get_width()) // 2
                    dot_y = i * CELL_SIZE + (CELL_SIZE - self.assets.large_dot.get_height()) // 2
                    self.screen.blit(self.assets.large_dot, (dot_x, dot_y))
                
                # Nếu giá trị là 2 và không nằm trong các vị trí loại trừ, vẽ dot thường
                elif boards[i][j] == 2 and not ((i, j) in [(7, 6), (7, 7), (8, 6), (8, 7)]):
                    dot_x = j * CELL_SIZE + (CELL_SIZE - self.assets.loading_dot.get_width()) // 2
                    dot_y = i * CELL_SIZE + (CELL_SIZE - self.assets.loading_dot.get_height()) // 2
                    self.screen.blit(self.assets.loading_dot, (dot_x, dot_y))
                    