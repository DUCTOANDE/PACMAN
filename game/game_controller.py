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

        # Biến để theo dõi trạng thái nhạc nền
        self.background_music_playing = False # Correctly initialized

        # Khởi tạo Player
        self.player = Player(self.screen, self.assets.player_images, 300, 500)
        self.player.game_state = self

        # Ma
        self.target = [[self.player.center_x, self.player.center_y]]*4
        self.flicker = False

        # Khởi tạo Ma (Ghost initialization remains the same)
        self.blinky = Ghost(
            screen=self.screen,
            x_coord=300,
            y_coord=350,
            target=self.target[0],
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
            img=self.assets.clyde_img,
            direct=2,
            dead=False,
            box=True,
            id=3,
            player=self.player,
            assets=self.assets,
            game_state=self
        )

        self.ghosts = [self.blinky, self.inky, self.pinky, self.clyde]
        self.ghost_release_timer = [0, 60, 120, 180]

        self.direction_command = self.player.direction
        pygame.font.init()
        self.font = pygame.font.Font(None, 36)
        self.game_over_font = pygame.font.Font(None, 72)

        self.victory_sound_played = False
        self.defeat_sound_played = False

    def handle_events(self):
        mouse_pos = pygame.mouse.get_pos()

        if self.current_state == MENU:
            self.button_hover = play_button_rect.collidepoint(mouse_pos)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return False

            if self.current_state == MENU:
                if play_button_rect.collidepoint(mouse_pos) and event.type == pygame.MOUSEBUTTONDOWN:
                    pygame.time.delay(100)
                    self.current_state = PLAYING
                    self.startup_counter = 0
                    self.moving = False

                    # --- CORRECTION HERE ---
                    # Adjust volume of the background music Sound object
                    if self.background_music_playing:
                        # Use self.assets directly, not self.game_state.assets
                        self.assets.background_music_path.set_volume(0.2) # Reduce volume to 20%

                    # Set pellet sound volume (already correct)
                    self.assets.pellet_sound.set_volume(1.0)
                    # Play beginning sound (already correct)
                    self.assets.beginning_sound.play()
                    # --- END CORRECTION ---

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
        # --- Update logic remains the same ---
        if self.current_state == LOADING and current_time - self.start_time > LOADING_DURATION:
            self.current_state = MENU
        elif self.current_state == PLAYING and not self.game_over and not self.game_won:
            # Startup counter
            if self.startup_counter < STARTUP_DELAY:
                self.moving = False
                self.startup_counter += 1
            else:
                self.moving = True

            # Power pellet timer
            if self.player.power and self.player.power_count < POWERUP_DURATION:
                self.player.power_count += 1
            elif self.player.power and self.player.power_count >= POWERUP_DURATION:
                self.player.power_count = 0
                self.player.power = False
                self.player.eaten_ghosts = [False, False, False, False]

            # Player animation counter
            if self.player.counter < 19:
                self.player.counter += 1
                if self.player.counter > 3:
                    self.flicker = False
            else:
                self.player.counter = 0
                self.flicker = True

            # Player movement and collision
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
                self.player.check_collision() # This handles game_won flag

                # Ghost target update
                for i in range(len(self.ghosts)):
                    self.target[i] = [self.player.center_x, self.player.center_y]

                # Ghost movement
                for i, ghost in enumerate(self.ghosts):
                    if self.startup_counter >= self.ghost_release_timer[i]:
                        # ghost.in_box = False # This should likely be handled within ghost.move_ghost()
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
        if not self.background_music_playing:
            self.assets.background_music_path.play(-1) 
            self.assets.background_music_path.set_volume(1.0) 
            self.background_music_playing = True
        self.screen.blit(self.assets.loading_img, (0, 0))

    def _render_menu(self):
        self.screen.blit(self.assets.menu_img, (0, 0))

        # Button hover effect (already correct)
        if self.button_hover:
            hover_x = play_button_rect.x - (self.assets.play_button_hover.get_width() - play_button_rect.width) // 2
            hover_y = play_button_rect.y - (self.assets.play_button_hover.get_height() - play_button_rect.height) // 2
            self.screen.blit(self.assets.play_button_hover, (hover_x, hover_y))
        else:
            self.screen.blit(self.assets.play_button_normal, play_button_rect)

    def _render_game(self):
        if self.game_over:
            # --- CORRECTION HERE ---
            # Stop background music and play defeat sound only once
            if self.background_music_playing:
                self.assets.background_music_path.stop() # Stop the specific Sound object
                self.background_music_playing = False
            if not self.defeat_sound_played:
                pygame.mixer.stop() # Stop other sounds
                self.assets.defeat_sound.play()
                self.defeat_sound_played = True
            # --- END CORRECTION ---

            self.screen.fill((0, 0, 0))
            game_over_text = self.game_over_font.render("Game Over", True, (255, 0, 0))
            score_text = self.font.render(f"Final Score: {self.player.score}", True, (255, 255, 255))
            self.screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2 - 50))
            self.screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, HEIGHT // 2 + 50))

        elif self.game_won:
            # --- CORRECTION HERE ---
            # Stop background music (use the correct object) and play victory sound only once
            if self.background_music_playing:
                # Stop the specific Sound object, not the music stream
                self.assets.background_music_path.stop()
                self.background_music_playing = False
            # --- END CORRECTION ---

            if not self.victory_sound_played:
                pygame.mixer.stop() # Stop other sounds
                self.assets.victory_sound.play()
                self.victory_sound_played = True

            self.screen.fill((0, 0, 0))
            win_text = self.game_over_font.render("You Win!", True, (0, 255, 0))
            score_text = self.font.render(f"Final Score: {self.player.score}", True, (255, 255, 255))
            self.screen.blit(win_text, (WIDTH // 2 - win_text.get_width() // 2, HEIGHT // 2 - 50))
            self.screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, HEIGHT // 2 + 50))

        else: # Normal game rendering
            # Reset sound played flags if returning to game (e.g., after pause - though pause isn't implemented here)
            self.victory_sound_played = False
            self.defeat_sound_played = False

            self.screen.fill((0, 0, 0))
            # Draw board (logic seems okay)
            for i in range(len(boards)):
                for j in range(len(boards[i])):
                    # Check if the tile index is valid for image_maps
                    tile_value = boards[i][j]
                    if tile_value in self.assets.image_maps:
                        image = self.assets.image_maps[tile_value]
                        # Specific rendering conditions for different tiles
                        if tile_value == 4 or tile_value == 5: # Bottom border
                            self.screen.blit(image, (j * CELL_SIZE, i * CELL_SIZE))
                        elif tile_value == 2: # Pellet
                             # Don't draw pellets inside the ghost box
                            if not (7 <= i <= 8 and 6 <= j <= 7):
                                self.screen.blit(image, (j * CELL_SIZE, i * CELL_SIZE))
                        elif tile_value == 3 and not self.flicker: # Power pellet
                            self.screen.blit(image, (j * CELL_SIZE, i * CELL_SIZE))
                        elif tile_value == 0 or tile_value == 1: # Walls
                            self.screen.blit(image, (j * CELL_SIZE, i * CELL_SIZE))
                        # Tile 6 (empty space after eating pellet/powerup) doesn't need explicit drawing if background is black

            self.player.draw_player()

            # Draw ghosts
            for ghost in self.ghosts:
                ghost.draw() # Draw returns the rect, but it's not used here

            # Check for collisions *after* drawing everything for the frame
            for ghost in self.ghosts:
                # check_player_collision now returns True if game over, False otherwise
                if ghost.check_player_collision():
                    self.game_over = True
                    # Break immediately if game over condition met
                    break

            self.draw_misc()

            # Draw "Ready?" text
            if not self.moving and self.current_state == PLAYING and not self.game_over and not self.game_won:
                if (self.startup_counter % 40) < 20: # Flicker effect
                    self.screen.blit(self.assets.ready_img, (300, 400)) # Consider centering this text

    def draw_misc(self):
        # --- Drawing score and lives remains the same ---
        score_icon_x = 60
        score_icon_y = HEIGHT - CELL_SIZE + 5
        self.screen.blit(self.assets.score_img, (score_icon_x, score_icon_y))
        score_value_text = self.font.render(f"Score: {self.player.score}", True, (255, 255, 255))
        score_text_x = score_icon_x + self.assets.score_img.get_width() + 2
        score_text_y = score_icon_y + (self.assets.score_img.get_height() - score_value_text.get_height()) // 2
        self.screen.blit(score_value_text, (score_text_x, score_text_y))

        for i in range(self.player.lives):
            self.screen.blit(pygame.transform.scale(self.assets.lives_img, (CELL_SIZE - 10, CELL_SIZE - 10)), (520 + i*40, 705))

