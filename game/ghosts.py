import pygame
import heapq
import random
from queue import Queue
from collections import deque
from .player import Player
from .game_controller import *
from .assets_manager import *
from .constants import CELL_SIZE, WIDTH, HEIGHT

class Ghost:
    def __init__(self, screen, x_coord, y_coord, target, img, direct, dead, box, id, player, assets, game_state):
        self.screen = screen
        self.center_x = x_coord + CELL_SIZE // 2
        self.center_y = y_coord + CELL_SIZE // 2
        self.initial_center_x = self.center_x
        self.initial_center_y = self.center_y
        self.initial_grid_pos = (self.center_y // CELL_SIZE, self.center_x // CELL_SIZE)
        self.x_pos = self.center_x - CELL_SIZE // 2
        self.y_pos = self.center_y - CELL_SIZE // 2
        self.target = target
        self.move_counter = 0
        self.move_delay = 40
        self.eyes_move_delay = 10
        self.img = img
        self.in_box = box
        self.id = id
        self.direction = direct
        self.dead = dead
        self.player = player
        self.assets = assets
        self.game_state = game_state
        self.eyes_mode = False
        self.respawn_timer = 0
        self.RESPAWN_DELAY = 30
        self.COLLISION_FUDGE_FACTOR = CELL_SIZE // 2
        self.GRID_WIDTH = WIDTH // CELL_SIZE
        self.GRID_HEIGHT = (HEIGHT - CELL_SIZE) // CELL_SIZE
        self.turns, self.in_box = self.check_collisions()
        self.ghost_rect = None
        self.movement_log = []
        self.movement_log.append({
            'position': [self.x_pos, self.y_pos],
            'direction': self.direction,
            'algorithm': 'Initial',
            'time': pygame.time.get_ticks()
        })
        self.algorithm = 'A*'

    def draw(self):
        if self.eyes_mode:
            img = self.assets.dead_img
        elif self.player.power and not self.dead and not self.player.eaten_ghosts[self.id]:
            img = self.assets.spooked_img
        else:
            img = self.img
        self.screen.blit(img, (self.x_pos, self.y_pos))
        self.ghost_rect = pygame.Rect(self.x_pos, self.y_pos, CELL_SIZE, CELL_SIZE)
        return self.ghost_rect

    def check_collisions(self):
        turns = [False, False, False, False]
        row = int(self.center_y // CELL_SIZE)
        col = int(self.center_x // CELL_SIZE)
        if not (0 <= row < len(self.game_state.current_board) and 0 <= col < len(self.game_state.current_board[0])):
            print(f"Invalid collision check position: ({row}, {col})")
            return turns, True
        if col + 1 < len(self.game_state.current_board[0]) and self.game_state.current_board[row][col + 1] not in [0, 1]:
            turns[0] = True
        if col - 1 >= 0 and self.game_state.current_board[row][col - 1] not in [0, 1]:
            turns[1] = True
        if row - 1 >= 0 and self.game_state.current_board[row - 1][col] not in [0, 1]:
            turns[2] = True
        if row + 1 < len(self.game_state.current_board) and self.game_state.current_board[row + 1][col] not in [0, 1]:
            turns[3] = True
        if self.center_x // CELL_SIZE >= self.GRID_WIDTH - 1 or self.center_x < 0:
            turns[0] = turns[1] = True
        in_box = (7 <= row <= 8 and 6 <= col <= 7)
        return turns, in_box

    def get_grid_pos(self):
        row = self.center_y // CELL_SIZE
        col = self.center_x // CELL_SIZE
        if not (0 <= row < len(self.game_state.current_board) and 0 <= col < len(self.game_state.current_board[0])):
            print(f"Invalid ghost position: ({row}, {col}), resetting to initial")
            self.center_x = self.initial_center_x
            self.center_y = self.initial_center_y
            row = self.center_y // CELL_SIZE
            col = self.center_x // CELL_SIZE
        return (row, col)

    def get_neighbors(self, pos):
        row, col = pos
        neighbors = []
        for dr, dc in [(0, 1), (0, -1), (-1, 0), (1, 0)]:
            new_row, new_col = row + dr, col + dc
            if (0 <= new_row < len(self.game_state.current_board) and 
                0 <= new_col < len(self.game_state.current_board[0])):
                if self.game_state.current_board[new_row][new_col] not in [0, 1]:
                    occupied = any((new_row, new_col) == g.get_grid_pos() for g in self.game_state.ghosts if g != self)
                    if not occupied:
                        neighbors.append((new_row, new_col))
            else:
                print(f"Invalid neighbor position: ({new_row}, {new_col}) from ({row}, {col})")
        return neighbors

    def heuristic(self, pos, target):
        return abs(pos[0] - target[0]) + abs(pos[1] - target[1])

    def a_star(self, start, goal):
        open_set = [(0, start)]
        came_from = {}
        g_score = {start: 0}
        f_score = {start: self.heuristic(start, goal)}
        while open_set:
            _, current = heapq.heappop(open_set)
            if current == goal:
                path = []
                while current in came_from:
                    path.append(current)
                    current = came_from[current]
                return path[::-1]
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
            _, current = heapq.heappop(open_set)
            if current == goal:
                path = []
                while current in came_from:
                    path.append(current)
                    current = came_from[current]
                return path[::-1]
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
                return path[::-1][1:] if len(path) > 1 else path
            for neighbor in self.get_neighbors(current):
                if neighbor not in visited:
                    visited.add(neighbor)
                    came_from[neighbor] = current
                    queue.put(neighbor)
        return []

    def dfs(self, start, goal):
        stack = [(start, [start])]
        visited = {start}
        while stack:
            current, path = stack.pop()
            if current == goal:
                return path[1:] if len(path) > 1 else path
            for neighbor in self.get_neighbors(current):
                if neighbor not in visited:
                    visited.add(neighbor)
                    stack.append((neighbor, path + [neighbor]))
        return []

    def greedy_best_first(self, start, goal):
        open_set = [(self.heuristic(start, goal), start)]
        came_from = {}
        visited = {start}
        while open_set:
            _, current = heapq.heappop(open_set)
            if current == goal:
                path = []
                while current in came_from:
                    path.append(current)
                    current = came_from[current]
                path.append(start)
                return path[::-1]
            for neighbor in self.get_neighbors(current):
                if neighbor not in visited:
                    visited.add(neighbor)
                    came_from[neighbor] = current
                    heapq.heappush(open_set, (self.heuristic(neighbor, goal), neighbor))
        return []

    def random_walk(self):
        possible_dirs = [i for i, allowed in enumerate(self.turns) if allowed]
        return random.choice(possible_dirs) if possible_dirs else self.direction

    def move_ghost(self):
        self.move_counter += 1
        current_delay = self.eyes_move_delay if self.eyes_mode else self.move_delay
        if self.move_counter < current_delay:
            return
        self.move_counter = 0
        self.turns, self.in_box = self.check_collisions()
        player_grid = (self.player.center_y // CELL_SIZE, self.player.center_x // CELL_SIZE)
        ghost_grid = self.get_grid_pos()
        algorithm_used = 'None'
        if self.eyes_mode:
            if self.respawn_timer > 0:
                self.respawn_timer -= 1
                if self.respawn_timer <= 0 and self.in_box:
                    self.reset_ghost()
                return
            target = self.initial_grid_pos
            path = self.a_star(ghost_grid, target)
            algorithm_used = 'A* (Eyes)'
            if path:
                self.set_direction(ghost_grid, path[0])
            else:
                self.direction = self.random_walk()
                algorithm_used = 'Random Walk (Eyes)'
            if self.in_box:
                self.respawn_timer = self.RESPAWN_DELAY
        else:
            if self.in_box:
                target = (6, 6)
                if self.algorithm == 'A*':
                    path = self.a_star(ghost_grid, target)
                    algorithm_used = 'A*'
                elif self.algorithm == 'BFS':
                    path = self.bfs(ghost_grid, target)
                    algorithm_used = 'BFS'
                elif self.algorithm == 'Dijkstra':
                    path = self.dijkstra(ghost_grid, target)
                    algorithm_used = 'Dijkstra'
                elif self.algorithm == 'DFS':
                    path = self.dfs(ghost_grid, target)
                    algorithm_used = 'DFS'
                elif self.algorithm == 'Greedy':
                    path = self.greedy_best_first(ghost_grid, target)
                    algorithm_used = 'Greedy'
                else:
                    path = []
                    algorithm_used = 'Random Walk'
            else:
                target = self.get_flee_target(player_grid) if self.player.power and not self.dead else player_grid
                if self.algorithm == 'A*':
                    path = self.a_star(ghost_grid, target)
                    algorithm_used = 'A*'
                elif self.algorithm == 'BFS':
                    path = self.bfs(ghost_grid, target)
                    algorithm_used = 'BFS'
                elif self.algorithm == 'Dijkstra':
                    path = self.dijkstra(ghost_grid, target)
                    algorithm_used = 'Dijkstra'
                elif self.algorithm == 'DFS':
                    path = self.dfs(ghost_grid, target)
                    algorithm_used = 'DFS'
                elif self.algorithm == 'Greedy':
                    path = self.greedy_best_first(ghost_grid, target)
                    algorithm_used = 'Greedy'
                else:
                    path = []
                    algorithm_used = 'Random Walk'
            if path:
                self.set_direction(ghost_grid, path[0])
            else:
                self.direction = self.random_walk()
                algorithm_used = 'Random Walk'
        if abs(self.center_x % CELL_SIZE - CELL_SIZE // 2) <= 2 and abs(self.center_y % CELL_SIZE - CELL_SIZE // 2) <= 2:
            next_row, next_col = ghost_grid
            if self.direction == 0 and self.turns[0]:
                next_col += 1
            elif self.direction == 1 and self.turns[1]:
                next_col -= 1
            elif self.direction == 2 and self.turns[2]:
                next_row -= 1
            elif self.direction == 3 and self.turns[3]:
                next_row += 1
            self.center_x = next_col * CELL_SIZE + CELL_SIZE // 2
            self.center_y = next_row * CELL_SIZE + CELL_SIZE // 2
            self.x_pos = self.center_x - CELL_SIZE // 2
            self.y_pos = self.center_y - CELL_SIZE // 2
        if self.center_x >= WIDTH:
            self.center_x = 0
        elif self.center_x < 0:
            self.center_x = WIDTH - CELL_SIZE
        if self.center_y >= HEIGHT:
            self.center_y = 0
        elif self.center_y < 0:
            self.center_y = HEIGHT - CELL_SIZE
        self.x_pos = self.center_x - CELL_SIZE // 2
        self.y_pos = self.center_y - CELL_SIZE // 2
        self.movement_log.append({
            'position': [self.x_pos, self.y_pos],
            'direction': self.direction,
            'algorithm': algorithm_used,
            'time': pygame.time.get_ticks()
        })

    def reset_ghost(self):
        self.dead = False
        self.eyes_mode = False
        self.player.eaten_ghosts[self.id] = False
        self.center_x = self.initial_center_x
        self.center_y = self.initial_center_y
        self.x_pos = self.center_x - CELL_SIZE // 2
        self.y_pos = self.center_y - CELL_SIZE // 2
        self.in_box = True
        self.direction = 2
        self.respawn_timer = 0
        self.movement_log.append({
            'position': [self.x_pos, self.y_pos],
            'direction': self.direction,
            'algorithm': 'Reset',
            'time': pygame.time.get_ticks()
        })

    def set_direction(self, current, next_pos):
        curr_row, curr_col = current
        next_row, next_col = next_pos
        if next_col > curr_col:
            self.direction = 0
        elif next_col < curr_col:
            self.direction = 1
        elif next_row < curr_row:
            self.direction = 2
        elif next_row > curr_row:
            self.direction = 3

    def get_flee_target(self, player_pos):
        max_dist = -1
        flee_pos = self.get_grid_pos()
        for row in range(len(self.game_state.current_board)):
            for col in range(len(self.game_state.current_board[0])):
                if self.game_state.current_board[row][col] not in [0, 1]:
                    dist = abs(row - player_pos[0]) + abs(col - player_pos[1])
                    if dist > max_dist:
                        max_dist = dist
                        flee_pos = (row, col)
        return flee_pos

    def check_player_collision(self):
        player_rect = pygame.Rect(self.player.player_x, self.player.player_y, CELL_SIZE, CELL_SIZE)
        if self.ghost_rect and self.ghost_rect.colliderect(player_rect):
            if self.player.power and not self.dead and not self.eyes_mode:
                if not self.player.eaten_ghosts[self.id]:
                    self.player.score += 200 * (2 ** sum(self.player.eaten_ghosts))
                    self.player.eaten_ghosts[self.id] = True
                    self.eyes_mode = True
                    self.dead = False
                    self.respawn_timer = 0
                    self.assets.eatghost_sound.play()
            elif not self.player.power and not self.dead and not self.eyes_mode:
                self.player.lives -= 1
                self.player.center_x = 300 + self.player.image_width // 2
                self.player.center_y = 500 + self.player.image_height // 2
                self.player.x_pos = self.player.center_x - self.player.image_width // 2
                self.player.y_pos = self.player.center_y - self.player.image_height // 2
                self.player.direction = 0
                self.reset_ghost()
                self.assets.death_sound.play()
                if self.player.lives <= 0:
                    return True
        return False