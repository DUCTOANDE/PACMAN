import pygame
from .constants import *
from .board import boards

class Player:
    def __init__(self, screen, player_image, player_x, player_y):
        self.screen = screen
        self.player_image = player_image
        self.player_x = player_x
        self.player_y = player_y
        self.direction = 0  # 0 = right, 1 = left, 2 = up, 3 = down
        self.counter = 0
        self.image_width = self.player_image[0].get_width()
        self.image_height = self.player_image[0].get_height()
        self.center_x = self.player_x + self.image_width // 2
        self.center_y = self.player_y + self.image_height // 2
        self.turns_allowed = [False, False, False, False]  # R, L, U, D
        self.COLLISION_FUDGE_FACTOR = CELL_SIZE // 2
        self.GRID_WIDTH = WIDTH // CELL_SIZE
        self.GRID_HEIGHT = (HEIGHT - CELL_SIZE) // CELL_SIZE
        self.speed = 2
        self.score = 0
        self.power = False
        self.power_count = 0
        self.eaten_ghosts = [False, False, False, False]
        self.lives = 3
        

    def draw_player(self):
        frame = self.player_image[self.counter // 5]
        if self.direction == 0:
            self.screen.blit(frame, (self.player_x, self.player_y))
        elif self.direction == 1:
            flipped_frame = pygame.transform.flip(frame, True, False)
            self.screen.blit(flipped_frame, (self.player_x, self.player_y))
        elif self.direction == 2:
            rotated_frame = pygame.transform.rotate(frame, 90)
            self.screen.blit(rotated_frame, (self.player_x, self.player_y))
        elif self.direction == 3:
            rotated_frame = pygame.transform.rotate(frame, 270)
            self.screen.blit(rotated_frame, (self.player_x, self.player_y))

    def check_position(self):
        turns = [False, False, False, False]
        num1 = self.GRID_HEIGHT
        num2 = self.GRID_WIDTH
        num3 = self.COLLISION_FUDGE_FACTOR
        centerx = self.center_x
        centery = self.center_y

        if centerx // CELL_SIZE < self.GRID_WIDTH -1:
            if self.direction == 0:
                if boards[centery // CELL_SIZE][(centerx - num3) // CELL_SIZE] not in [0,1]:
                    turns[1] = True
            elif self.direction == 1:
                if boards[centery // CELL_SIZE][(centerx + num3) // CELL_SIZE] not in [0,1]:
                    turns[0] = True
            elif self.direction == 2:
                if boards[(centery + num3) // CELL_SIZE][centerx // CELL_SIZE] not in [0,1]:
                    turns[3] = True
            elif self.direction == 3:
                if boards[(centery - num3) // CELL_SIZE][centerx // CELL_SIZE] not in [0,1]:
                    turns[2] = True

            if self.direction == 2 or self.direction == 3:
                if self.COLLISION_FUDGE_FACTOR -3 <= centerx % CELL_SIZE <= self.COLLISION_FUDGE_FACTOR + 3:
                    if boards[(centery + num3) // CELL_SIZE][centerx // CELL_SIZE] not in [0,1]:
                        turns[3] = True
                    if boards[(centery - num3) // CELL_SIZE][centerx // CELL_SIZE] not in [0,1]:
                        turns[2] = True
                if self.COLLISION_FUDGE_FACTOR -3 <= centery % CELL_SIZE <= self.COLLISION_FUDGE_FACTOR + 3:
                    if boards[centery // CELL_SIZE][(centerx - CELL_SIZE) // CELL_SIZE] not in [0,1]:
                        turns[1] = True
                    if boards[centery // CELL_SIZE][(centerx + CELL_SIZE) // CELL_SIZE] not in [0,1]:
                        turns[0] = True
            elif self.direction == 0 or self.direction == 1:
                if self.COLLISION_FUDGE_FACTOR -3 <= centerx % CELL_SIZE <= self.COLLISION_FUDGE_FACTOR + 3:
                    if boards[(centery + CELL_SIZE) // CELL_SIZE][centerx // CELL_SIZE] not in [0,1]:
                        turns[3] = True
                    if boards[(centery - CELL_SIZE) // CELL_SIZE][centerx // CELL_SIZE] not in [0,1]:
                        turns[2] = True
                if self.COLLISION_FUDGE_FACTOR - 3 <= centery % CELL_SIZE <= self.COLLISION_FUDGE_FACTOR + 3:
                    if boards[centery // CELL_SIZE][(centerx - num3) // CELL_SIZE] not in [0,1]:
                        turns[1] = True
                    if boards[centery // CELL_SIZE][(centerx + num3) // CELL_SIZE] not in [0,1]:
                        turns[0] = True
        else:
            turns[0] = True
            turns[1] = True

        return turns
    
    def move_player(self):
        if self.direction == 0 and self.turns_allowed[0]:
            self.player_x += self.speed
        elif self.direction == 1 and self.turns_allowed[1]:
            self.player_x -= self.speed
        elif self.direction == 2 and self.turns_allowed[2]:
            self.player_y -= self.speed
        elif self.direction == 3 and self.turns_allowed[3]:
            self.player_y += self.speed

        # Screen wrapping logic
        if self.player_x > WIDTH:
            self.player_x = -self.image_width
        elif self.player_x < -self.image_width:
            self.player_x = WIDTH - 3
        
        if self.player_y > HEIGHT:
            self.player_y = -self.image_height
        elif self.player_y < -self.image_height:
            self.player_y = HEIGHT - 3
        
        self.center_x = self.player_x + self.image_width // 2
        self.center_y = self.player_y + self.image_height // 2
    
    def check_collision(self):
        # Xác định ô lưới dựa trên tâm của người chơi
        center_col = self.center_x // CELL_SIZE
        center_row = self.center_y // CELL_SIZE
        if 0 <= center_row < len(boards) and 0 <= center_col < len(boards[0]):
            if boards[center_row][center_col] == 2:
                boards[center_row][center_col] = 6  
                self.score += 10
            elif boards[center_row][center_col] == 3:
                boards[center_row][center_col] = 6 
                
                self.score += 50
                self.power = True
                self.power_count = 0
                self.eaten_ghosts = [False, False, False, False]

