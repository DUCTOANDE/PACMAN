import pygame
import time
import json
from .constants import *
from .board import boards_level1, boards_level2
from .assets_manager import AssetManager
from .player import Player
from .ghosts import Ghost
import os
from .analyze_ghost_logs import load_ghost_log, analyze_ghost_logs, compare_algorithms, evaluate_algorithms, save_comparison_to_file, visualize_evaluation
import glob
import sys

LOADING = 0
MENU = 1
PLAYING = 2
WIN_SCREEN = 3
GAME_OVER_SCREEN = 4

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
        self.button_hover = {'play': False, 'continue': False, 'menu': False, 'exit': False}
        self.startup_counter = 0
        self.moving = False
        self.game_over = False
        self.game_won = False
        self.background_music_playing = False
        self.level = 1  # Bắt đầu từ màn 1
        self.boards = {1: boards_level1, 2: boards_level2}  # Ánh xạ màn chơi với bảng
        self.current_board = self.copy_board(self.boards[self.level])  # Trạng thái bảng hiện tại
        self.player = Player(self.screen, self.assets.player_images, 300, 500)
        self.player.game_state = self
        self.target = [[self.player.center_x, self.player.center_y]] * 4
        self.flicker = False
        self.blinky = Ghost(
            screen=self.screen, x_coord=300, y_coord=350, target=self.target[0],
            img=self.assets.binky_img, direct=2, dead=False, box=True, id=0,
            player=self.player, assets=self.assets, game_state=self
        )
        self.inky = Ghost(
            screen=self.screen, x_coord=350, y_coord=350, target=self.target[1],
            img=self.assets.inky_img, direct=2, dead=False, box=True, id=1,
            player=self.player, assets=self.assets, game_state=self
        )
        self.pinky = Ghost(
            screen=self.screen, x_coord=300, y_coord=400, target=self.target[2],
            img=self.assets.pinky_img, direct=2, dead=False, box=True, id=2,
            player=self.player, assets=self.assets, game_state=self
        )
        self.clyde = Ghost(
            screen=self.screen, x_coord=350, y_coord=400, target=self.target[3],
            img=self.assets.clyde_img, direct=2, dead=False, box=True, id=3,
            player=self.player, assets=self.assets, game_state=self
        )
        self.ghosts = [self.blinky, self.inky, self.pinky, self.clyde]
        self.ghost_release_timer = [0, 60, 120, 180]
        self.direction_command = self.player.direction
        pygame.font.init()
        self.font = pygame.font.Font(None, 36)
        self.game_over_font = pygame.font.Font(None, 72)
        self.victory_sound_played = False
        self.defeat_sound_played = False
        # Định nghĩa các hình chữ nhật cho nút trong màn thắng và thua
        self.continue_button_rect = pygame.Rect((WIDTH - 100) // 2 - 150, HEIGHT - 270, 100, 60)
        self.menu_button_rect = pygame.Rect((WIDTH - 100) // 2, HEIGHT - 270, 100, 60)
        self.exit_button_rect = pygame.Rect((WIDTH - 100) // 2 + 150, HEIGHT - 270, 100, 60)
        # Đọc điểm cao nhất từ file
        self.high_score = self.load_high_score()

    def copy_board(self, board):
        """Tạo bản sao sâu của bảng để tránh sửa đổi dữ liệu gốc."""
        return [row[:] for row in board]

    def reset_game(self, new_level=None):
        """Đặt lại trạng thái trò chơi cho màn mới hoặc trò chơi mới."""
        # Lưu điểm cao nhất trước khi đặt lại
        if self.player.score > self.high_score:
            self.high_score = self.player.score
            self.save_high_score()
        if new_level:
            self.level = new_level
            self.current_board = self.copy_board(self.boards.get(self.level, boards_level1))
        else:
            self.current_board = self.copy_board(self.boards[self.level])
        self.player = Player(self.screen, self.assets.player_images, 300, 500)
        self.player.game_state = self
        self.target = [[self.player.center_x, self.player.center_y]] * 4
        self.blinky = Ghost(
            screen=self.screen, x_coord=300, y_coord=350, target=self.target[0],
            img=self.assets.binky_img, direct=2, dead=False, box=True, id=0,
            player=self.player, assets=self.assets, game_state=self
        )
        self.inky = Ghost(
            screen=self.screen, x_coord=350, y_coord=350, target=self.target[1],
            img=self.assets.inky_img, direct=2, dead=False, box=True, id=1,
            player=self.player, assets=self.assets, game_state=self
        )
        self.pinky = Ghost(
            screen=self.screen, x_coord=300, y_coord=400, target=self.target[2],
            img=self.assets.pinky_img, direct=2, dead=False, box=True, id=2,
            player=self.player, assets=self.assets, game_state=self
        )
        self.clyde = Ghost(
            screen=self.screen, x_coord=350, y_coord=400, target=self.target[3],
            img=self.assets.clyde_img, direct=2, dead=False, box=True, id=3,
            player=self.player, assets=self.assets, game_state=self
        )
        self.ghosts = [self.blinky, self.inky, self.pinky, self.clyde]
        self.ghost_release_timer = [0, 60, 120, 180]
        self.game_over = False
        self.game_won = False
        self.startup_counter = 0
        self.moving = False
        self.flicker = False
        self.player.counter = 0
        self.direction_command = self.player.direction
        self.victory_sound_played = False
        self.defeat_sound_played = False

    def load_high_score(self):
        """Đọc điểm cao nhất từ file high_score.json."""
        try:
            with open("high_score.json", "r") as f:
                data = json.load(f)
                return data.get("high_score", 0)
        except (FileNotFoundError, json.JSONDecodeError):
            return 0

    def save_high_score(self):
        """Lưu điểm cao nhất vào file high_score.json."""
        try:
            with open("high_score.json", "w") as f:
                json.dump({"high_score": self.high_score}, f, indent=4)
            print(f"Đã lưu điểm cao nhất: {self.high_score}")
        except Exception as e:
            print(f"Lỗi khi lưu điểm cao nhất: {e}")

    def analyze_ghost_logs(self, log_filepath, from_game=True):
        """Phân tích file nhật ký di chuyển của ma và lưu kết quả."""
        try:
            pygame.display.quit()  # Đóng cửa sổ Pygame trước khi phân tích
            data = load_ghost_log(log_filepath)
            if data:
                metrics = analyze_ghost_logs(data)
                comparison = compare_algorithms(metrics)
                scores = evaluate_algorithms(comparison)
                save_comparison_to_file(comparison)
                visualize_evaluation(scores, from_game=from_game)
        except Exception as e:
            print(f"Lỗi khi phân tích nhật ký: {e}")
        if not from_game:
            pygame.quit()
            sys.exit()
        else:
            pygame.init()
            self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
            return True

    def handle_events(self):
        mouse_pos = pygame.mouse.get_pos()
        if self.current_state == MENU:
            self.button_hover['play'] = play_button_rect.collidepoint(mouse_pos)
        elif self.current_state == WIN_SCREEN:
            self.button_hover['continue'] = self.continue_button_rect.collidepoint(mouse_pos)
            self.button_hover['menu'] = self.menu_button_rect.collidepoint(mouse_pos)
            self.button_hover['exit'] = self.exit_button_rect.collidepoint(mouse_pos)
        elif self.current_state == GAME_OVER_SCREEN:
            self.button_hover['menu'] = self.menu_button_rect.collidepoint(mouse_pos)
            self.button_hover['exit'] = self.exit_button_rect.collidepoint(mouse_pos)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                # Lưu điểm cao nhất trước khi thoát
                if self.player.score > self.high_score:
                    self.high_score = self.player.score
                    self.save_high_score()
                self.save_ghost_logs()
                log_dir = "log"
                log_files = glob.glob(os.path.join(log_dir, "ghost_movement_log_*.json"))
                if log_files:
                    latest_file = max(log_files, key=os.path.getmtime)
                    self.analyze_ghost_logs(latest_file, from_game=False)
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                # Lưu điểm cao nhất trước khi thoát
                if self.player.score > self.high_score:
                    self.high_score = self.player.score
                    self.save_high_score()
                self.save_ghost_logs()
                log_dir = "log"
                log_files = glob.glob(os.path.join(log_dir, "ghost_movement_log_*.json"))
                if log_files:
                    latest_file = max(log_files, key=os.path.getmtime)
                    self.analyze_ghost_logs(latest_file, from_game=False)
                pygame.quit()
                sys.exit()
            if self.current_state == MENU:
                if play_button_rect.collidepoint(mouse_pos) and event.type == pygame.MOUSEBUTTONDOWN:
                    pygame.time.delay(100)
                    self.current_state = PLAYING
                    self.reset_game(self.level)
                    if self.background_music_playing:
                        self.assets.background_music_path.set_volume(0.2)
                    self.assets.pellet_sound.set_volume(1.0)
                    self.assets.beginning_sound.play()
            elif self.current_state == WIN_SCREEN:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.continue_button_rect.collidepoint(mouse_pos):
                        # Lưu điểm cao nhất
                        if self.player.score > self.high_score:
                            self.high_score = self.player.score
                            self.save_high_score()
                        self.save_ghost_logs()
                        next_level = self.level + 1 if self.level + 1 in self.boards else 1
                        self.reset_game(next_level)
                        self.current_state = PLAYING
                        self.assets.beginning_sound.play()
                    elif self.menu_button_rect.collidepoint(mouse_pos):
                        # Lưu điểm cao nhất
                        if self.player.score > self.high_score:
                            self.high_score = self.player.score
                            self.save_high_score()
                        self.save_ghost_logs()
                        self.reset_game(1)
                        self.current_state = MENU
                        if self.background_music_playing:
                            self.assets.background_music_path.set_volume(1.0)
                    elif self.exit_button_rect.collidepoint(mouse_pos):
                        # Lưu điểm cao nhất
                        if self.player.score > self.high_score:
                            self.high_score = self.player.score
                            self.save_high_score()
                        self.save_ghost_logs()
                        log_dir = "log"
                        log_files = glob.glob(os.path.join(log_dir, "ghost_movement_log_*.json"))
                        if log_files:
                            latest_file = max(log_files, key=os.path.getmtime)
                            self.analyze_ghost_logs(latest_file, from_game=False)
                        pygame.quit()
                        sys.exit()
            elif self.current_state == GAME_OVER_SCREEN:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.menu_button_rect.collidepoint(mouse_pos):
                        # Lưu điểm cao nhất
                        if self.player.score > self.high_score:
                            self.high_score = self.player.score
                            self.save_high_score()
                        self.save_ghost_logs()
                        self.reset_game(1)
                        self.current_state = MENU
                        if self.background_music_playing:
                            self.assets.background_music_path.set_volume(1.0)
                    elif self.exit_button_rect.collidepoint(mouse_pos):
                        # Lưu điểm cao nhất
                        if self.player.score > self.high_score:
                            self.high_score = self.player.score
                            self.save_high_score()
                        self.save_ghost_logs()
                        log_dir = "log"
                        log_files = glob.glob(os.path.join(log_dir, "ghost_movement_log_*.json"))
                        if log_files:
                            latest_file = max(log_files, key=os.path.getmtime)
                            self.analyze_ghost_logs(latest_file, from_game=False)
                        pygame.quit()
                        sys.exit()
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
            if self.startup_counter < STARTUP_DELAY:
                self.moving = False
                self.startup_counter += 1
            else:
                self.moving = True
            if self.player.power and self.player.power_count < POWERUP_DURATION:
                self.player.power_count += 1
            elif self.player.power and self.player.power_count >= POWERUP_DURATION:
                self.player.power_count = 0
                self.player.power = False
                self.player.eaten_ghosts = [False, False, False, False]
            if self.player.counter < 19:
                self.player.counter += 1
                if self.player.counter > 3:
                    self.flicker = False
            else:
                self.player.counter = 0
                self.flicker = True
            if self.moving:
                self.player.turns_allowed = self.player.check_position()
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
                for i in range(len(self.ghosts)):
                    self.target[i] = [self.player.center_x, self.player.center_y]
                for i, ghost in enumerate(self.ghosts):
                    if self.startup_counter >= self.ghost_release_timer[i]:
                        ghost.move_ghost()

    def render(self):
        if self.current_state == LOADING:
            self._render_loading()
        elif self.current_state == MENU:
            self._render_menu()
        elif self.current_state == PLAYING:
            self._render_game()
        elif self.current_state == WIN_SCREEN:
            self._render_win_screen()
        elif self.current_state == GAME_OVER_SCREEN:
            self._render_game_over_screen()
        pygame.display.flip()
        self.clock.tick(60)

    def _render_loading(self):
        if not self.background_music_playing:
            self.assets.background_music_path.play(-1)
            self.assets.background_music_path.set_volume(1.0)
            self.background_music_playing = True
        self.screen.blit(self.assets.loading_img, (0, 0))

    def _render_menu(self):
        self.screen.blit(self.assets.menu_img, (0, 0))
        if self.button_hover['play']:
            hover_x = play_button_rect.x - (self.assets.play_button_hover.get_width() - play_button_rect.width) // 2
            hover_y = play_button_rect.y - (self.assets.play_button_hover.get_height() - play_button_rect.height) // 2
            self.screen.blit(self.assets.play_button_hover, (hover_x, hover_y))
        else:
            self.screen.blit(self.assets.play_button_normal, play_button_rect)
        # Hiển thị điểm cao nhất
        high_score_text = self.font.render(f"High Score: {self.high_score}", True, (255, 255, 255))
        self.screen.blit(high_score_text, (WIDTH // 2 - high_score_text.get_width() // 2, HEIGHT - 150))

    def _render_game(self):
        if self.game_over:
            self.current_state = GAME_OVER_SCREEN
            if self.background_music_playing:
                self.assets.background_music_path.stop()
                self.background_music_playing = False
            if not self.defeat_sound_played:
                pygame.mixer.stop()
                self.assets.defeat_sound.play()
                self.defeat_sound_played = True
        elif self.game_won:
            self.current_state = WIN_SCREEN
            if self.background_music_playing:
                self.assets.background_music_path.stop()
                self.background_music_playing = False
            if not self.victory_sound_played:
                pygame.mixer.stop()
                self.assets.victory_sound.play()
                self.victory_sound_played = True
        else:
            self.victory_sound_played = False
            self.defeat_sound_played = False
            self.screen.fill((0, 0, 0))
            for i in range(len(self.current_board)):
                for j in range(len(self.current_board[i])):
                    tile_value = self.current_board[i][j]
                    if tile_value in self.assets.image_maps:
                        image = self.assets.image_maps[tile_value]
                        if tile_value == 4 or tile_value == 5:
                            self.screen.blit(image, (j * CELL_SIZE, i * CELL_SIZE))
                        elif tile_value == 2:
                            if not (7 <= i <= 8 and 6 <= j <= 7):
                                self.screen.blit(image, (j * CELL_SIZE, i * CELL_SIZE))
                        elif tile_value == 3 and not self.flicker:
                            self.screen.blit(image, (j * CELL_SIZE, i * CELL_SIZE))
                        elif tile_value == 0 or tile_value == 1:
                            self.screen.blit(image, (j * CELL_SIZE, i * CELL_SIZE))
            self.player.draw_player()
            for ghost in self.ghosts:
                ghost.draw()
            for ghost in self.ghosts:
                if ghost.check_player_collision():
                    self.game_over = True
                    break
            self.draw_misc()
            if not self.moving and self.current_state == PLAYING and not self.game_over and not self.game_won:
                if (self.startup_counter % 40) < 20:
                    self.screen.blit(self.assets.ready_img, (300, 400))

    def _render_win_screen(self):
        self.screen.fill((0, 0, 0))
        win_text = self.game_over_font.render("Victory!", True, (0, 255, 0))
        score_text = self.font.render(f"Score: {self.player.score}", True, (255, 255, 255))
        level_text = self.font.render(f"Complete level {self.level}", True, (255, 255, 255))
        self.screen.blit(win_text, (WIDTH // 2 - win_text.get_width() // 2, HEIGHT // 2 - 150))
        self.screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, HEIGHT // 2))
        self.screen.blit(level_text, (WIDTH // 2 - level_text.get_width() // 2, HEIGHT // 2 - 150))

        # Vẽ các nút theo hàng dọc: Exit, Menu, Continue
        button_width = self.assets.exit_button_normal.get_width()
        button_height = self.assets.exit_button_normal.get_height()
        hover_width = self.assets.exit_button_hover.get_width()
        hover_height = self.assets.exit_button_hover.get_height()
        base_y = HEIGHT // 2 + 100
        spacing = 20

        # Nút Exit
        exit_x = WIDTH // 2 - button_width // 2
        exit_y = base_y
        if self.button_hover['exit']:
            hover_x = WIDTH // 2 - hover_width // 2
            hover_y = base_y - (hover_height - button_height) // 2
            self.screen.blit(self.assets.exit_button_hover, (hover_x, hover_y))
        else:
            self.screen.blit(self.assets.exit_button_normal, (exit_x, exit_y))
        self.exit_button_rect = pygame.Rect(exit_x, exit_y, button_width, button_height)

        # Nút Menu
        menu_x = WIDTH // 2 - button_width // 2
        menu_y = base_y + button_height + spacing
        if self.button_hover['menu']:
            hover_x = WIDTH // 2 - hover_width // 2
            hover_y = menu_y - (hover_height - button_height) // 2
            self.screen.blit(self.assets.menu_button_hover, (hover_x, hover_y))
        else:
            self.screen.blit(self.assets.menu_button_normal, (menu_x, menu_y))
        self.menu_button_rect = pygame.Rect(menu_x, menu_y, button_width, button_height)

        # Nút Continue
        continue_x = WIDTH // 2 - button_width // 2
        continue_y = base_y + 2 * (button_height + spacing)
        if self.button_hover['continue']:
            hover_x = WIDTH // 2 - hover_width // 2
            hover_y = continue_y - (hover_height - button_height) // 2
            self.screen.blit(self.assets.continue_button_hover, (hover_x, hover_y))
        else:
            self.screen.blit(self.assets.continue_button_normal, (continue_x, continue_y))
        self.continue_button_rect = pygame.Rect(continue_x, continue_y, button_width, button_height)

    def _render_game_over_screen(self):
        self.screen.fill((0, 0, 0))
        game_over_text = self.game_over_font.render("Game Over", True, (255, 0, 0))
        score_text = self.font.render(f"Score: {self.player.score}", True, (255, 255, 255))
        self.screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2 - 100))
        self.screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, HEIGHT // 2 + 10))

        # Vẽ các nút theo hàng dọc: Exit, Menu
        button_width = self.assets.exit_button_normal.get_width()
        button_height = self.assets.exit_button_normal.get_height()
        hover_width = self.assets.exit_button_hover.get_width()
        hover_height = self.assets.exit_button_hover.get_height()
        base_y = HEIGHT // 2 + 50
        spacing = 10

        # Nút Exit
        exit_x = WIDTH // 2 - button_width // 2
        exit_y = base_y
        if self.button_hover['exit']:
            hover_x = WIDTH // 2 - hover_width // 2
            hover_y = base_y - (hover_height - button_height) // 2
            self.screen.blit(self.assets.exit_button_hover, (hover_x, hover_y))
        else:
            self.screen.blit(self.assets.exit_button_normal, (exit_x, exit_y))
        self.exit_button_rect = pygame.Rect(exit_x, exit_y, button_width, button_height)

        # Nút Menu
        menu_x = WIDTH // 2 - button_width // 2
        menu_y = base_y + button_height + spacing
        if self.button_hover['menu']:
            hover_x = WIDTH // 2 - hover_width // 2
            hover_y = menu_y - (hover_height - button_height) // 2
            self.screen.blit(self.assets.menu_button_hover, (hover_x, hover_y))
        else:
            self.screen.blit(self.assets.menu_button_normal, (menu_x, menu_y))
        self.menu_button_rect = pygame.Rect(menu_x, menu_y, button_width, button_height)

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
        # Hiển thị level hiện tại
        level_text = self.font.render(f"Level: {self.level}", True, (255, 255, 255))
        self.screen.blit(level_text, (WIDTH // 2 - level_text.get_width() // 2, HEIGHT - CELL_SIZE + 5))

    def save_ghost_logs(self):
        ghost_names = ['Blinky', 'Inky', 'Pinky', 'Clyde']
        logs = {}
        for i, ghost in enumerate(self.ghosts):
            logs[ghost_names[i]] = {
                'id': ghost.id,
                'movements': ghost.movement_log
            }
        log_dir = "log"
        try:
            os.makedirs(log_dir, exist_ok=True)
        except OSError as e:
            print(f"Lỗi khi tạo thư mục log '{log_dir}': {e}")
            return
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"ghost_movement_log_{timestamp}.json"
        filepath = os.path.join(log_dir, filename)
        try:
            with open(filepath, 'w') as f:
                json.dump(logs, f, indent=4)
            print(f"Nhật ký di chuyển của ma đã được lưu vào: {filepath}")
        except Exception as e:
            print(f"Lỗi khi lưu nhật ký di chuyển của ma vào {filepath}: {e}")