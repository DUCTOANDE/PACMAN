import pygame
from .player import Player
from .game_controller import *
from .assets_manager import *
import pygame

class Ghost:
    def __init__(self,screen,x_coord, y_coord, target, speed, img, direct, dead, box, id, player,assets):
        self.screen = screen
        self.x_pos = x_coord
        self.y_pos = y_coord
        self.center_x = x_coord + 23
        self.center_y = y_coord + 23
        self.target = target
        self.speed = speed
        self.img = img
        self.in_box = box
        self.id = id
        self.direct = direct
        self.dead = dead
        self.player = player  # Lưu thể hiện player
        self.assets = assets
        self.turns, self.in_box = self.check_collisions_ghosts()
        self.rect = self.draw()
        

    
    def draw(self):
        if (not self.player.power and not self.dead) or (self.player.eaten_ghosts[self.id] and self.player.power and not self.dead):
            self.screen.blit(self.img, (self.x_pos, self.y_pos))
        elif self.player.power and not self.dead and self.player.eaten_ghosts[self.id]:
            self.screen.blit(self.img, (self.x_pos, self.y_pos))
        else:
            self.screen.blit(self.assets.spooked_img, (self.x_pos, self.y_pos))
        self.ghost_rect = pygame.rect.Rect((self.center_x - 23, self.center_y - 23, 40, 40))
        return self.ghost_rect

    
    def check_collisions_ghosts(self):
        self.turns = [False, False, False, False]
        self.in_box = True
        return self.turns, self.in_box