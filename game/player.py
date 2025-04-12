import pygame


class Player:
    def __init__(self, screen, player_image, player_x, player_y):
        self.screen = screen
        self.player_image = player_image  # Danh sách các khung hình
        self.player_x = player_x    
        self.player_y = player_y
        self.direction = 0
        self.counter = 0
    
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

         

    
 