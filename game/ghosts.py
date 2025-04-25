import pygame
import heapq
import random
import math
from queue import Queue
from .player import Player
from .game_controller import *
from .assets_manager import *
from .board import boards
from .constants import CELL_SIZE, WIDTH, HEIGHT

class Ghost:
    def __init__(self, screen, x_coord, y_coord, target, speed, img, direct, dead, box, id, player, assets, game_state):
        self.screen = screen
        self.x_pos = x_coord
        self.y_pos = y_coord
        self.initial_x_pos = x_coord
        self.initial_y_pos = y_coord
        self.initial_grid_pos = (y_coord // CELL_SIZE, x_coord // CELL_SIZE)
        self.image_width = img.get_width()
        self.image_height = img.get_height()
        self.center_x = self.x_pos + self.image_width // 2
        self.center_y = self.y_pos + self.image_height // 2
        self.target = target
        self.speed = speed
        self.img = img
        self.in_box = box
        self.id = id
        self.direct = direct
        self.dead = dead
        self.player = player
        self.assets = assets
        self.game_state = game_state
        self.eyes_mode = False
        self.respawn_timer = 0
        self.RESPAWN_DELAY = 120
        self.COLLISION_FUDGE_FACTOR = CELL_SIZE // 2
        self.GRID_WIDTH = WIDTH // CELL_SIZE
        self.GRID_HEIGHT = (HEIGHT - CELL_SIZE) // CELL_SIZE
        self.turns, self.in_box = self.check_collisions_ghosts()
        self.rect = self.draw()

    def draw(self):
        if self.eyes_mode:
            self.screen.blit(self.assets.dead_img, (self.x_pos, self.y_pos))
        elif (not self.player.power and not self.dead) or (self.player.eaten_ghosts[self.id] and self.player.power and not self.dead):
            self.screen.blit(self.img, (self.x_pos, self.y_pos))
        elif self.player.power and not self.dead and not self.player.eaten_ghosts[self.id]:
            self.screen.blit(self.assets.spooked_img, (self.x_pos, self.y_pos))
        else:
            self.screen.blit(self.assets.dead_img, (self.x_pos, self.y_pos))
        self.ghost_rect = pygame.rect.Rect(
            self.center_x - self.image_width // 2,
            self.center_y - self.image_height // 2,
            self.image_width,
            self.image_height
        )
        return self.ghost_rect

    def check_collisions_ghosts(self):
        turns = [False, False, False, False]  # Phải, Trái, Lên, Xuống
        fudge = self.COLLISION_FUDGE_FACTOR
        centerx = self.center_x
        centery = self.center_y
        row = centery // CELL_SIZE
        col = centerx // CELL_SIZE

        # Kiểm tra các hướng khả thi
        if 0 <= row < len(boards) and 0 <= col < len(boards[0]):
            # Phải
            if col + 1 < len(boards[0]) and boards[row][col + 1] not in [0, 1]:
                turns[0] = True
            # Trái
            if col - 1 >= 0 and boards[row][col - 1] not in [0, 1]:
                turns[1] = True
            # Lên
            if row - 1 >= 0 and boards[row - 1][col] not in [0, 1]:
                turns[2] = True
            # Xuống
            if row + 1 < len(boards) and boards[row + 1][col] not in [0, 1]:
                turns[3] = True

            # Căn chỉnh với lưới khi gần giao điểm
            if self.direct in [2, 3]:  # Lên hoặc Xuống
                if fudge - 3 <= centerx % CELL_SIZE <= fudge + 3:
                    if row + 1 < len(boards) and boards[row + 1][col] not in [0, 1]:
                        turns[3] = True
                    if row - 1 >= 0 and boards[row - 1][col] not in [0, 1]:
                        turns[2] = True
                if fudge - 3 <= centery % CELL_SIZE <= fudge + 3:
                    if col - 1 >= 0 and boards[row][col - 1] not in [0, 1]:
                        turns[1] = True
                    if col + 1 < len(boards[0]) and boards[row][col + 1] not in [0, 1]:
                        turns[0] = True
            elif self.direct in [0, 1]:  # Phải hoặc Trái
                if fudge - 3 <= centerx % CELL_SIZE <= fudge + 3:
                    if row + 1 < len(boards) and boards[row + 1][col] not in [0, 1]:
                        turns[3] = True
                    if row - 1 >= 0 and boards[row - 1][col] not in [0, 1]:
                        turns[2] = True
                if fudge - 3 <= centery % CELL_SIZE <= fudge + 3:
                    if col - 1 >= 0 and boards[row][col - 1] not in [0, 1]:
                        turns[1] = True
                    if col + 1 < len(boards[0]) and boards[row][col + 1] not in [0, 1]:
                        turns[0] = True

        # Cho phép vòng quanh màn hình
        if centerx // CELL_SIZE >= self.GRID_WIDTH - 1 or centerx < 0:
            turns[0] = True
            turns[1] = True

        # Nếu không có hướng nào khả thi, thử giữ hướng hiện tại
        if not any(turns) and 0 <= row < len(boards) and 0 <= col < len(boards[0]):
            if self.direct == 0 and col + 1 < len(boards[0]) and boards[row][col + 1] not in [0, 1]:
                turns[0] = True
            elif self.direct == 1 and col - 1 >= 0 and boards[row][col - 1] not in [0, 1]:
                turns[1] = True
            elif self.direct == 2 and row - 1 >= 0 and boards[row - 1][col] not in [0, 1]:
                turns[2] = True
            elif self.direct == 3 and row + 1 < len(boards) and boards[row + 1][col] not in [0, 1]:
                turns[3] = True

        in_box = (7 <= row <= 8 and 6 <= col <= 7)
        return turns, in_box

    def get_grid_pos(self):
        return (self.center_y // CELL_SIZE, self.center_x // CELL_SIZE)

    def get_neighbors(self, pos):
        row, col = pos
        neighbors = []
        directions = [(0, 1), (0, -1), (-1, 0), (1, 0)]  # Phải, Trái, Lên, Xuống
        for dr, dc in directions:
            new_row, new_col = row + dr, col + dc
            if (0 <= new_row < len(boards) and 0 <= new_col < len(boards[0]) and
                boards[new_row][new_col] not in [0, 1]):
                occupied = False
                for other_ghost in [g for g in self.game_state.ghosts if g != self]:
                    other_pos = other_ghost.get_grid_pos()
                    if (new_row, new_col) == other_pos:
                        occupied = True
                        break
                if not occupied:
                    neighbors.append((new_row, new_col))
        return neighbors

    def heuristic(self, pos, target):
        return abs(pos[0] - target[0]) + abs(pos[1] - target[1])

    def a_star(self, start, goal):
        open_set = [(0, start)]
        came_from = {}
        g_score = {start: 0}
        f_score = {start: self.heuristic(start, goal)}

        while open_set:
            current_f, current = heapq.heappop(open_set)

            if current == goal:
                path = []
                while current in came_from:
                    path.append(current)
                    current = came_from[current]
                path.reverse()
                return path

            for neighbor in self.get_neighbors(current):
                tentative_g = g_score[current] + 1
                if neighbor not in g_score or tentative_g < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g
                    f_score[neighbor] = tentative_g + self.heuristic(neighbor, goal)
                    heapq.heappush(open_set, (f_score[neighbor], neighbor))
        return []

    def dijkstra(self, start, goal):
        open_set = [(0, start)]
        came_from = {}
        cost_so_far = {start: 0}

        while open_set:
            current_cost, current = heapq.heappop(open_set)

            if current == goal:
                path = []
                while current in came_from:
                    path.append(current)
                    current = came_from[current]
                path.reverse()
                return path

            for neighbor in self.get_neighbors(current):
                new_cost = cost_so_far[current] + 1
                if neighbor not in cost_so_far or new_cost < cost_so_far[neighbor]:
                    cost_so_far[neighbor] = new_cost
                    heapq.heappush(open_set, (new_cost, neighbor))
                    came_from[neighbor] = current
        return []

    def bfs(self, start, goal):
        queue = Queue()
        queue.put(start)
        came_from = {start: None}
        visited = {start}

        while not queue.empty():
            current = queue.get()

            if current == goal:
                path = []
                while current is not None:
                    path.append(current)
                    current = came_from[current]
                path.reverse()
                return path[1:] if len(path) > 1 else path

            for neighbor in self.get_neighbors(current):
                if neighbor not in visited:
                    visited.add(neighbor)
                    came_from[neighbor] = current
                    queue.put(neighbor)
        return []

    def random_move(self):
        possible_dirs = [i for i, allowed in enumerate(self.turns) if allowed]
        if possible_dirs:
            return random.choice(possible_dirs)
        return self.direct

    def move_ghost(self):
        self.turns, self.in_box = self.check_collisions_ghosts()
        player_grid = (self.player.center_y // CELL_SIZE, self.player.center_x // CELL_SIZE)
        ghost_grid = self.get_grid_pos()

        if self.dead and self.respawn_timer > 0:
            self.respawn_timer -= 1
            if self.respawn_timer <= 0:
                self.dead = False
                self.eyes_mode = False
                self.player.eaten_ghosts[self.id] = False
                self.x_pos = self.initial_x_pos
                self.y_pos = self.initial_y_pos
                self.center_x = self.x_pos + self.image_width // 2
                self.center_y = self.y_pos + self.image_height // 2
                self.in_box = True
            return

        if self.eyes_mode:
            target = self.initial_grid_pos
            path = self.a_star(ghost_grid, target)
            if path:
                next_pos = path[0]
                self.set_direction(ghost_grid, next_pos)
            else:
                self.direct = self.random_move()

            if ghost_grid == target:
                self.eyes_mode = False
                self.dead = True
                self.in_box = True
                self.respawn_timer = self.RESPAWN_DELAY
                self.x_pos = self.initial_x_pos
                self.y_pos = self.initial_y_pos
                self.center_x = self.x_pos + self.image_width // 2
                self.center_y = self.y_pos + self.image_height // 2
        else:
            if self.in_box:
                target = (6, 6)
                if self.id == 0:
                    path = self.a_star(ghost_grid, target)
                else:
                    path = self.dijkstra(ghost_grid, target)
                if path:
                    next_pos = path[0]
                    self.set_direction(ghost_grid, next_pos)
                else:
                    self.direct = self.random_move()
            else:
                if self.player.power and not self.dead:
                    target = self.get_flee_target(player_grid)
                else:
                    target = player_grid

                if self.id == 0:
                    path = self.a_star(ghost_grid, target)
                    if path:
                        next_pos = path[0]
                        self.set_direction(ghost_grid, next_pos)
                    else:
                        self.direct = self.random_move()
                elif self.id == 1:
                    path = self.dijkstra(ghost_grid, target)
                    if path:
                        next_pos = path[0]
                        self.set_direction(ghost_grid, next_pos)
                    else:
                        self.direct = self.random_move()
                elif self.id == 2:
                    if random.random() < 0.7:
                        path = self.a_star(ghost_grid, target)
                        if path:
                            next_pos = path[0]
                            self.set_direction(ghost_grid, next_pos)
                        else:
                            self.direct = self.random_move()
                    else:
                        self.direct = self.random_move()
                else:
                    path = self.bfs(ghost_grid, target)
                    if path:
                        next_pos = path[0]
                        self.set_direction(ghost_grid, next_pos)
                    else:
                        self.direct = self.random_move()

        if self.direct == 0 and self.turns[0]:
            self.center_x += self.speed
        elif self.direct == 1 and self.turns[1]:
            self.center_x -= self.speed
        elif self.direct == 2 and self.turns[2]:
            self.center_y -= self.speed
        elif self.direct == 3 and self.turns[3]:
            self.center_y += self.speed
        
        
        self.x_pos = self.center_x - self.image_width // 2
        self.y_pos = self.center_y - self.image_height // 2
        
        if self.center_x > WIDTH:
            self.center_x = -self.image_width // 2
        elif self.center_x < -self.image_width // 2:
            self.center_x = WIDTH - self.image_width // 2
        if self.center_y > HEIGHT:
            self.center_y = -self.image_height // 2
        elif self.center_y < -self.image_height // 2:
            self.center_y = HEIGHT - self.image_height // 2


    def set_direction(self, current, next_pos):
        curr_row, curr_col = current
        next_row, next_col = next_pos
        if next_col > curr_col:
            self.direct = 0
        elif next_col < curr_col:
            self.direct = 1
        elif next_row < curr_row:
            self.direct = 2
        elif next_row > curr_row:
            self.direct = 3

    def get_flee_target(self, player_pos):
        max_dist = -1
        flee_pos = self.get_grid_pos()
        for row in range(len(boards)):
            for col in range(len(boards[0])):
                if boards[row][col] not in [0, 1]:
                    dist = abs(row - player_pos[0]) + abs(col - player_pos[1])
                    if dist > max_dist:
                        max_dist = dist
                        flee_pos = (row, col)
        return flee_pos

    def check_player_collision(self):
        player_rect = pygame.rect.Rect(
            self.player.center_x - self.player.image_width // 2,
            self.player.center_y - self.player.image_height // 2,
            self.player.image_width,
            self.player.image_height
        )
        if self.ghost_rect.colliderect(player_rect):
            if self.player.power and not self.dead and not self.eyes_mode:
                if not self.player.eaten_ghosts[self.id]:
                    self.player.score += 200 * (2 ** sum(self.player.eaten_ghosts))
                    self.player.eaten_ghosts[self.id] = True
                    self.eyes_mode = True
                    self.dead = False
            elif not self.player.power and not self.dead and not self.eyes_mode:
                self.player.lives -= 1
                self.player.player_x = 300
                self.player.player_y = 500
                self.player.center_x = self.player.player_x + self.player.image_width // 2
                self.player.center_y = self.player.player_y + self.image_height // 2
                self.player.direction = 0
                self.x_pos = self.initial_x_pos
                self.y_pos = self.initial_y_pos
                self.center_x = self.x_pos + self.image_width // 2
                self.center_y = self.y_pos + self.image_height // 2
                self.in_box = True
                if self.player.lives <= 0:
                    return True
        return False