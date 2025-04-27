import pygame
import time
from .constants import *
from .board import boards
from .assets_manager import AssetManager
from .player import Player
from .ghosts import Ghost

STARTUP_DELAY = 240
POWERUP_DURATION = 600

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
        
        self.startup_counter = 0
        self.moving = False
        self.game_over = False 
        self.game_won = False 
        
        # Khởi tạo Player
        self.player = Player(self.screen, self.assets.player_images, 300, 500)
        self.player.game_state = self  # Thêm tham chiếu game_state vào player
        
        # Ghosts
        self.target = [[self.player.center_x, self.player.center_y]]*4
        # self.ghost_speeds = [1, 1, 1, 1]
        self.flicker = False
        
        # Khởi tạo Ghosts
        self.blinky = Ghost(
            screen=self.screen, 
            x_coord=300,
            y_coord=350,
            target=self.target[0],
            # speed=self.ghost_speeds[0], 
            img=self.assets.binky_img, 
            direct=2,
            dead=False, 
            box=True, 
            id=0, 
            player=self.player, 
            assets=self.assets, 
            game_state=self
        )
        self.inky = Ghost(
            screen=self.screen, 
            x_coord=350,
            y_coord=350,
            target=self.target[1],
            # speed=self.ghost_speeds[1], 
            img=self.assets.inky_img, 
            direct=2,
            dead=False, 
            box=True, 
            id=1, 
            player=self.player, 
            assets=self.assets, 
            game_state=self
        )
        self.pinky = Ghost(
            screen=self.screen, 
            x_coord=300,
            y_coord=400,
            target=self.target[2],
            # speed=self.ghost_speeds[2], 
            img=self.assets.pinky_img, 
            direct=2,
            dead=False, 
            box=True, 
            id=2, 
            player=self.player, 
            assets=self.assets, 
            game_state=self
        )
        self.clyde = Ghost(
            screen=self.screen, 
            x_coord=350,
            y_coord=400,
            target=self.target[3],
            # speed=self.ghost_speeds[3], 
            img=self.assets.clyde_img, 
            direct=2,
            dead=False, 
            box=True, 
            id=3, 
            player=self.player, 
            assets=self.assets, 
            game_state=self
        )
        
        # Khởi tạo danh sách ghosts
        self.ghosts = [self.blinky, self.inky, self.pinky, self.clyde]
        self.ghost_release_timer = [0, 60, 120, 180]  # Thời gian thả ghost (frame)
        
        self.direction_command = self.player.direction
        pygame.font.init()
        self.font = pygame.font.Font(None, 36)
        self.game_over_font = pygame.font.Font(None, 72)
        
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
                    self.startup_counter = 0
                    self.moving = False
                    
            elif self.current_state == PLAYING and self.moving and not self.game_over and not self.game_won:
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
        elif self.current_state == PLAYING and not self.game_over and not self.game_won:
            # Logic Startup Delay
            if self.startup_counter < STARTUP_DELAY:
                self.moving = False
                self.startup_counter += 1
            else:
                self.moving = True
                
            # Logic Power-up timer
            if self.player.power and self.player.power_count < POWERUP_DURATION:
                self.player.power_count += 1
            elif self.player.power and self.player.power_count >= POWERUP_DURATION:
                self.player.power_count = 0
                self.player.power = False
                self.player.eaten_ghosts = [False, False, False, False]
                
            # Cập nhật counter trong Player
            if self.player.counter < 19:
                self.player.counter += 1
                if self.player.counter > 3:
                    self.flicker = False
            else:
                self.player.counter = 0
                self.flicker = True
                
            if self.moving:
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
                
                # Cập nhật target của ghost
                for i in range(len(self.ghosts)):
                    self.target[i] = [self.player.center_x, self.player.center_y]
                
                # Di chuyển các ghost dựa trên thời gian thả
                for i, ghost in enumerate(self.ghosts):
                    if self.startup_counter >= self.ghost_release_timer[i]:
                        ghost.in_box = False
                        ghost.move_ghost()

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
        self.screen.blit(self.assets.menu_img, (0, 0))
        
        if self.button_hover:
            hover_x = play_button_rect.x - (self.assets.play_button_hover.get_width() - play_button_rect.width) // 2
            hover_y = play_button_rect.y - (self.assets.play_button_hover.get_height() - play_button_rect.height) // 2
            self.screen.blit(self.assets.play_button_hover, (hover_x, hover_y))
        else:
            self.screen.blit(self.assets.play_button_normal, play_button_rect)

    def _render_game(self):
        if self.game_over:
            self.screen.fill((0, 0, 0))
            game_over_text = self.game_over_font.render("Game Over", True, (255, 0, 0))
            score_text = self.font.render(f"Final Score: {self.player.score}", True, (255, 255, 255))
            self.screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2 - 50))
            self.screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, HEIGHT // 2 + 50))
        elif self.game_won:
            self.screen.fill((0, 0, 0))
            win_text = self.game_over_font.render("You Win!", True, (0, 255, 0))
            score_text = self.font.render(f"Final Score: {self.player.score}", True, (255, 255, 255))
            self.screen.blit(win_text, (WIDTH // 2 - win_text.get_width() // 2, HEIGHT // 2 - 50))
            self.screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, HEIGHT // 2 + 50))
        else:
            self.screen.fill((0, 0, 0))
            for i in range(len(boards)):
                for j in range(len(boards[i])):
                    image = self.assets.image_maps[boards[i][j]]
                    if boards[i][j] == 4 or boards[i][j] == 5:
                        self.screen.blit(image, (j * CELL_SIZE, i * CELL_SIZE))
                    if boards[i][j] == 2 and not ((i, j) in [(7, 6), (7, 7), (8, 6), (8, 7)]):
                        dot_x = j * CELL_SIZE
                        dot_y = i * CELL_SIZE
                        self.screen.blit(image, (dot_x, dot_y))
                    if boards[i][j] == 3 and (not self.flicker):
                        dot_x = j * CELL_SIZE
                        dot_y = i * CELL_SIZE
                        self.screen.blit(image, (dot_x, dot_y))
                    if boards[i][j] == 0 or boards[i][j] == 1:
                        self.screen.blit(image, (j * CELL_SIZE, i * CELL_SIZE))

            self.player.draw_player()
            
            for ghost in self.ghosts:
                ghost.draw()
            
            for ghost in self.ghosts:
                if ghost.check_player_collision():
                    self.game_over = True
            
            self.draw_misc()
            
            if not self.moving and self.current_state == PLAYING and not self.game_over and not self.game_won:
                if (self.startup_counter % 40) < 20:
                    self.screen.blit(self.assets.ready_img, (300, 400))
             
    def draw_misc(self):
        score_icon_x = 60
        score_icon_y = HEIGHT - CELL_SIZE + 5
        self.screen.blit(self.assets.score_img, (score_icon_x, score_icon_y))
        score_value_text = self.font.render(f"Score: {self.player.score}", True, (255, 255, 255))
        score_text_x = score_icon_x + self.assets.score_img.get_width() + 2
        score_text_y = score_icon_y + (self.assets.score_img.get_height() - score_value_text.get_height()) // 2
        self.screen.blit(score_value_text, (score_text_x, score_text_y))
        
        for i in range(self.player.lives):
            self.screen.blit(pygame.transform.scale(self.assets.lives_img, (CELL_SIZE - 10, CELL_SIZE - 10)), (520 + i*40, 705))