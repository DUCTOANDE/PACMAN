import pygame
import time
import json
from .constants import *
from .board import boards_level1, boards_level2
from .assets_manager import AssetManager
from .player import Player
from .ghosts import Ghost
import os
from .analyze_ghost_logs import *
import glob
import sys

# Game states
MENU = 0
READY = 1
PLAYING = 2
WIN_SCREEN = 3
GAME_OVER_SCREEN = 4

STARTUP_DELAY = 180  # 3 seconds (60 fps * 3)
POWERUP_DURATION = 600

# Global play button rectangle, positioned at the top
play_button_rect = pygame.Rect(WIDTH // 2 - 50, 50, 100, 90)

class GameState:
    def __init__(self, screen, assets):
        self.screen = screen
        self.assets = assets
        self.current_state = MENU
        self.start_time = time.time()
        self.current_frame = 0
        self.last_frame_time = time.time()
        self.clock = pygame.time.Clock()
        self.button_hover = {'play': False, 'continue': False, 'menu': False, 'exit': False, 'select_algo': False}
        self.startup_counter = 0
        self.moving = False
        self.game_over = False
        self.game_won = False
        self.background_music_playing = False
        self.level = 1
        self.boards = {1: boards_level1, 2: boards_level2}
        self.current_board = self.copy_board(self.boards[self.level])
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
        self.font = pygame.font.Font(None, 28)
        self.bold_font = pygame.font.Font(None, 32)
        self.game_over_font = pygame.font.Font(None, 72)
        self.victory_sound_played = False
        self.defeat_sound_played = False
        self.continue_button_rect = pygame.Rect((WIDTH - 100) // 2 - 150, HEIGHT - 270, 100, 80)
        self.menu_button_rect = pygame.Rect((WIDTH - 100) // 2, HEIGHT - 270, 100, 80)
        self.exit_button_rect = pygame.Rect((WIDTH - 100) // 2 + 150, HEIGHT - 270, 100, 80)
        self.high_score = self.load_high_score()
        self.total_score = 0
        self.has_saved_logs = False
        # Algorithm selection
        self.ghost_algorithms = {
            'Blinky': 'A*',
            'Inky': 'BFS',
            'Pinky': 'Dijkstra',
            'Clyde': 'Random'
        }
        self.ghost_names = ['Blinky', 'Inky', 'Pinky', 'Clyde']
        self.algo_buttons = {}
        self.algo_button_rects = {}
        self.ghost_display_rects = {}
        self._init_algo_buttons()
        self.current_ghost_index = 0
        self.show_algo_bar = False
        self.algo_bar_y = 360
        self.target_algo_bar_y = 360
        self.algo_bar_speed = 10
        self.select_algo_rect = pygame.Rect(WIDTH // 2 - 100, 380, 200, 50)
        self.selected_algorithm = 'A*'

    def _init_algo_buttons(self):
        algorithms = ['A*', 'BFS', 'Dijkstra', 'Random', 'DFS', 'Greedy']
        button_width, button_height = 150, 40
        start_x = WIDTH // 2 - button_width // 2
        start_y = 440
        for i, algo in enumerate(algorithms):
            self.algo_buttons[algo] = False
            self.algo_button_rects[algo] = pygame.Rect(start_x, start_y + i * (button_height + 5), button_width, button_height)
        
        ghost_start_y = 180
        for i, ghost in enumerate(self.ghost_names):
            self.ghost_display_rects[ghost] = pygame.Rect(WIDTH // 2 - 150, ghost_start_y + i * 40, 300, 30)

    def copy_board(self, board):
        return [row[:] for row in board]

    def reset_game(self, new_level=None):
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
        for i, ghost in enumerate(self.ghosts):
            ghost.algorithm = self.ghost_algorithms[self.ghost_names[i]]
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
        try:
            with open("high_score.json", "r") as f:
                data = json.load(f)
                return data.get("high_score", 0)
        except (FileNotFoundError, json.JSONDecodeError):
            return 0

    def save_high_score(self):
        try:
            with open("high_score.json", "w") as f:
                json.dump({"high_score": self.high_score}, f, indent=4)
            print(f"Đã lưu điểm cao nhất: {self.high_score}")
        except Exception as e:
            print(f"Lỗi khi lưu điểm cao nhất: {e}")

    def analyze_ghost_logs(self, log_filepath, from_game=True):
        try:
            pygame.display.quit()
            data = load_ghost_log(log_filepath)
            if data:
                metrics = analyze_ghost_logs(data)
                comparison = compare_algorithms(metrics)
                scores = evaluate_algorithms(comparison)
                save_comparison_to_file(comparison)
                visualize_evaluation(scores, metrics, from_game=from_game)
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
        # Update button hover states
        if self.current_state == MENU:
            self.button_hover['play'] = play_button_rect.collidepoint(mouse_pos)
            self.button_hover['select_algo'] = self.select_algo_rect.collidepoint(mouse_pos)
            if self.show_algo_bar:
                for algo in self.algo_buttons:
                    self.algo_buttons[algo] = self.algo_button_rects[algo].move(0, self.algo_bar_y - 440).collidepoint(mouse_pos)
        elif self.current_state in [WIN_SCREEN, GAME_OVER_SCREEN]:
            self.button_hover['continue'] = self.continue_button_rect.collidepoint(mouse_pos)
            self.button_hover['menu'] = self.menu_button_rect.collidepoint(mouse_pos)
            self.button_hover['exit'] = self.exit_button_rect.collidepoint(mouse_pos)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                current_total = self.total_score + self.player.score
                if current_total > self.high_score:
                    self.high_score = current_total
                    self.save_high_score()
                if not self.has_saved_logs:
                    self.save_ghost_logs()
                log_dir = "log"
                log_files = glob.glob(os.path.join(log_dir, "ghost_movement_log_*.json"))
                if log_files:
                    latest_file = max(log_files, key=os.path.getmtime)
                    self.analyze_ghost_logs(latest_file, from_game=False)
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                current_total = self.total_score + self.player.score
                if current_total > self.high_score:
                    self.high_score = current_total
                    self.save_high_score()
                if not self.has_saved_logs:
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
                    self.current_state = READY
                    self.startup_counter = 0
                    self.total_score = 0
                    self.has_saved_logs = False
                    if self.background_music_playing:
                        self.assets.background_music_path.set_volume(0.2)
                    self.assets.pellet_sound.set_volume(1.0)
                    self.assets.beginning_sound.play()
                elif self.select_algo_rect.collidepoint(mouse_pos) and event.type == pygame.MOUSEBUTTONDOWN:
                    if self.show_algo_bar:
                        self.show_algo_bar = False
                        self.target_algo_bar_y = 360
                    else:
                        self.current_ghost_index = 0
                        self.show_algo_bar = True
                        self.algo_bar_y = 360
                        self.target_algo_bar_y = 440
                elif self.show_algo_bar and event.type == pygame.MOUSEBUTTONDOWN:
                    for algo, rect in self.algo_button_rects.items():
                        if rect.move(0, self.algo_bar_y - 440).collidepoint(mouse_pos):
                            self.ghost_algorithms[self.ghost_names[self.current_ghost_index]] = algo
                            self.current_ghost_index += 1
                            if self.current_ghost_index >= len(self.ghost_names):
                                self.show_algo_bar = False
                                self.target_algo_bar_y = 360
            elif self.current_state == WIN_SCREEN:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.level < 2 and self.continue_button_rect.collidepoint(mouse_pos):
                        self.total_score += self.player.score
                        self.level += 1
                        self.reset_game(self.level)
                        self.current_state = READY
                        self.startup_counter = 0
                        self.game_won = False
                        self.victory_sound_played = False
                        self.assets.beginning_sound.play()
                    elif self.menu_button_rect.collidepoint(mouse_pos):
                        current_total = self.total_score + self.player.score
                        if current_total > self.high_score:
                            self.high_score = current_total
                            self.save_high_score()
                        if not self.has_saved_logs:
                            self.save_ghost_logs()
                            self.has_saved_logs = True
                        self.reset_game(1)
                        self.total_score = 0
                        self.current_state = MENU
                        if self.background_music_playing:
                            self.assets.background_music_path.set_volume(1.0)
                    elif self.exit_button_rect.collidepoint(mouse_pos):
                        current_total = self.total_score + self.player.score
                        if current_total > self.high_score:
                            self.high_score = current_total
                            self.save_high_score()
                        if not self.has_saved_logs:
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
                        current_total = self.total_score + self.player.score
                        if current_total > self.high_score:
                            self.high_score = current_total
                            self.save_high_score()
                        if not self.has_saved_logs:
                            self.save_ghost_logs()
                            self.has_saved_logs = True
                        self.reset_game(1)
                        self.total_score = 0
                        self.current_state = MENU
                        if self.background_music_playing:
                            self.assets.background_music_path.set_volume(1.0)
                    elif self.exit_button_rect.collidepoint(mouse_pos):
                        current_total = self.total_score + self.player.score
                        if current_total > self.high_score:
                            self.high_score = current_total
                            self.save_high_score()
                        if not self.has_saved_logs:
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
        if self.current_state == READY:
            if self.startup_counter < STARTUP_DELAY:
                self.startup_counter += 1
            else:
                self.current_state = PLAYING
                self.startup_counter = 0
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
        if self.algo_bar_y != self.target_algo_bar_y:
            distance = self.target_algo_bar_y - self.algo_bar_y
            if abs(distance) > 1:
                self.algo_bar_y += self.algo_bar_speed * (distance / abs(distance))
                self.algo_bar_y = max(360, min(self.algo_bar_y, 710))
            else:
                self.algo_bar_y = self.target_algo_bar_y

    def render(self):
        if self.current_state == MENU:
            self._render_menu()
        elif self.current_state == READY:
            self._render_ready()
        elif self.current_state == PLAYING:
            self._render_game()
        elif self.current_state == WIN_SCREEN:
            self._render_win_screen()
        elif self.current_state == GAME_OVER_SCREEN:
            self._render_game_over_screen()
        pygame.display.flip()
        self.clock.tick(60)

    def _render_menu(self):
        if not self.background_music_playing:
            self.assets.background_music_path.play(-1)
            self.assets.background_music_path.set_volume(1.0)
            self.background_music_playing = True
        self.screen.blit(self.assets.menu_img, (0, 0))
        
        if self.button_hover['play']:
            hover_x = play_button_rect.x - (self.assets.play_button_hover.get_width() - play_button_rect.width) // 2
            hover_y = play_button_rect.y - (self.assets.play_button_hover.get_height() - play_button_rect.height) // 2
            self.screen.blit(self.assets.play_button_hover, (hover_x, hover_y))
        else:
            self.screen.blit(self.assets.play_button_normal, play_button_rect)
        
        high_score_text = self.font.render(f"High Score: {self.high_score}", True, (255, 255, 255))
        self.screen.blit(high_score_text, (WIDTH // 2 - high_score_text.get_width() // 2, 130))
        
        colors = [(255, 0, 0), (0, 255, 255), (255, 105, 180), (255, 165, 0)]
        start_y = 180
        for i, ghost in enumerate(self.ghost_names):
            font = self.bold_font if self.show_algo_bar and i == self.current_ghost_index else self.font
            ghost_text = font.render(f"{ghost}: {self.ghost_algorithms[ghost]}", True, colors[i])
            text_y = start_y + i * 40 + (0 if font == self.font else -4)
            self.screen.blit(ghost_text, (WIDTH // 2 - ghost_text.get_width() // 2, text_y))
        
        pygame.draw.rect(self.screen, (0, 255, 0) if self.button_hover['select_algo'] else (150, 150, 150), self.select_algo_rect)
        pygame.draw.rect(self.screen, (255, 255, 255), self.select_algo_rect, 1)
        select_text = self.font.render("Select Algorithm", True, (255, 255, 255))
        self.screen.blit(select_text, (self.select_algo_rect.x + 20, self.select_algo_rect.y + 15))
        
        if self.show_algo_bar:
            for algo, rect in self.algo_button_rects.items():
                new_rect = rect.move(0, self.algo_bar_y - 440)
                is_selected = algo == self.ghost_algorithms.get(self.ghost_names[self.current_ghost_index], '')
                color = (255, 255, 153) if is_selected else (0, 255, 0) if self.algo_buttons.get(algo, False) else (150, 150, 150)
                pygame.draw.rect(self.screen, color, new_rect, 0)
                pygame.draw.rect(self.screen, (255, 255, 255), new_rect, 1)
                algo_text = self.font.render(algo, True, (255, 255, 255))
                self.screen.blit(algo_text, (new_rect.x + 10, new_rect.y + 10))

    def _render_ready(self):
        self.screen.fill((0, 0, 0))
        x = (WIDTH - self.assets.ready_screen_img.get_width()) // 2
        y = (HEIGHT - self.assets.ready_screen_img.get_height()) // 2
        self.screen.blit(self.assets.ready_screen_img, (0,0))
        if (self.startup_counter // 30) % 2 == 0:
            ready_text = self.game_over_font.render("Ready!", True, (255, 255, 0))
            self.screen.blit(ready_text, (WIDTH // 2 - ready_text.get_width() // 2, HEIGHT // 2 + 50))

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

    def _render_win_screen(self):
        self.screen.fill((0, 0, 0))
        if self.level == 2:
            win_text = self.game_over_font.render("Congratulations!", True, (0, 255, 0))
            sub_text = self.font.render("You have won all levels!", True, (255, 255, 0))
            self.screen.blit(win_text, (WIDTH // 2 - win_text.get_width() // 2, HEIGHT // 2 - 150))
            self.screen.blit(sub_text, (WIDTH // 2 - sub_text.get_width() // 2, HEIGHT // 2 - 80))
        else:
            win_text = self.game_over_font.render("Victory!", True, (0, 255, 0))
            level_text = self.font.render(f"Completed level {self.level}", True, (255, 255, 0))
            self.screen.blit(win_text, (WIDTH // 2 - win_text.get_width() // 2, HEIGHT // 2 - 150))
            self.screen.blit(level_text, (WIDTH // 2 - level_text.get_width() // 2, HEIGHT // 2 - 80))
        
        score_text = self.font.render(f"Score: {self.player.score}", True, (255, 255, 0))
        self.screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, HEIGHT // 2))
        
        button_width = self.assets.exit_button_normal.get_width()
        button_height = self.assets.exit_button_normal.get_height()
        hover_width = self.assets.exit_button_hover.get_width()
        hover_height = self.assets.exit_button_hover.get_height()
        base_x = WIDTH // 2 - button_width // 2
        base_y = HEIGHT // 2 + 100
        spacing = 20
        
        if self.level == 2:
            # Position for Exit button
            exit_y = base_y
            if self.button_hover['exit']:
                hover_x = base_x
                hover_y = exit_y - (hover_height - button_height) // 2
                self.screen.blit(self.assets.exit_button_hover, (hover_x, hover_y))
            else:
                self.screen.blit(self.assets.exit_button_normal, (base_x, exit_y))
            self.exit_button_rect = pygame.Rect(base_x, exit_y, button_width, button_height)
            
            # Position for Menu button
            menu_y = exit_y + button_height + spacing
            if self.button_hover['menu']:
                hover_x = base_x
                hover_y = menu_y - (hover_height - button_height) // 2
                self.screen.blit(self.assets.menu_button_hover, (hover_x, hover_y))
            else:
                self.screen.blit(self.assets.menu_button_normal, (base_x, menu_y))
            self.menu_button_rect = pygame.Rect(base_x, menu_y, button_width, button_height)
        else:
            # Position for Continue button
            continue_y = base_y
            if self.button_hover['continue']:
                hover_x = base_x
                hover_y = continue_y - (hover_height - button_height) // 2
                self.screen.blit(self.assets.continue_button_hover, (hover_x, hover_y))
            else:
                self.screen.blit(self.assets.continue_button_normal, (base_x, continue_y))
            self.continue_button_rect = pygame.Rect(base_x, continue_y, button_width, button_height)
            
            # Position for Menu button
            menu_y = continue_y + button_height + spacing
            if self.button_hover['menu']:
                hover_x = base_x
                hover_y = menu_y - (hover_height - button_height) // 2
                self.screen.blit(self.assets.menu_button_hover, (hover_x, hover_y))
            else:
                self.screen.blit(self.assets.menu_button_normal, (base_x, menu_y))
            self.menu_button_rect = pygame.Rect(base_x, menu_y, button_width, button_height)
            
            # Position for Exit button
            exit_y = menu_y + button_height + spacing
            if self.button_hover['exit']:
                hover_x = base_x
                hover_y = exit_y - (hover_height - button_height) // 2
                self.screen.blit(self.assets.exit_button_hover, (hover_x, hover_y))
            else:
                self.screen.blit(self.assets.exit_button_normal, (base_x, exit_y))
            self.exit_button_rect = pygame.Rect(base_x, exit_y, button_width, button_height)

    def _render_game_over_screen(self):
        self.screen.fill((0, 0, 0))
        game_over_text = self.game_over_font.render("Game Over", True, (255, 0, 0))
        score_text = self.font.render(f"Score: {self.player.score}", True, (255, 255, 0))
        self.screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2 - 100))
        self.screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, HEIGHT // 2 + 10))
        
        button_width = self.assets.exit_button_normal.get_width()
        button_height = self.assets.exit_button_normal.get_height()
        hover_width = self.assets.exit_button_hover.get_width()
        hover_height = self.assets.exit_button_hover.get_height()
        base_x = WIDTH // 2 - button_width // 2
        base_y = HEIGHT // 2 + 50
        spacing = 10
        
        menu_x = base_x
        menu_y = base_y
        if self.button_hover['menu']:
            hover_x = base_x
            hover_y = base_y - (hover_height - button_height) // 2
            self.screen.blit(self.assets.menu_button_hover, (hover_x, hover_y))
        else:
            self.screen.blit(self.assets.menu_button_normal, (menu_x, menu_y))
        self.menu_button_rect = pygame.Rect(menu_x, menu_y, button_width, button_height)
        
        exit_x = base_x
        exit_y = base_y + button_height + spacing
        if self.button_hover['exit']:
            hover_x = base_x
            hover_y = exit_y - (hover_height - button_height) // 2
            self.screen.blit(self.assets.exit_button_hover, (hover_x, hover_y))
        else:
            self.screen.blit(self.assets.exit_button_normal, (exit_x, exit_y))
        self.exit_button_rect = pygame.Rect(exit_x, exit_y, button_width, button_height)

    def draw_misc(self):
        score_icon_x = 60
        score_icon_y = HEIGHT - CELL_SIZE + 5
        self.screen.blit(self.assets.score_img, (score_icon_x, score_icon_y))
        score_value_text = self.font.render(f"Score: {self.player.score}", True, (255, 255, 0))
        score_text_x = score_icon_x + self.assets.score_img.get_width() + 2
        score_text_y = score_icon_y + (self.assets.score_img.get_height() - score_value_text.get_height()) // 2
        self.screen.blit(score_value_text, (score_text_x, score_text_y))
        for i in range(self.player.lives):
            self.screen.blit(pygame.transform.scale(self.assets.lives_img, (CELL_SIZE - 10, CELL_SIZE - 10)), (520 + i*40, 705))
        level_text = self.font.render(f"Level: {self.level}", True, (255, 255, 0))
        self.screen.blit(level_text, (WIDTH // 2 - level_text.get_width() // 2, HEIGHT - CELL_SIZE + 5))

    def save_ghost_logs(self):
        ghost_names = ['Blinky', 'Inky', 'Pinky', 'Clyde']
        logs = {}
        for i, ghost in enumerate(self.ghosts):
            logs[ghost_names[i]] = {
                'id': ghost.id,
                'algorithm': self.ghost_algorithms[ghost_names[i]],
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