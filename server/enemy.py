# server/enemy.py
import time
import pygame
import os
from server.game_map import GameMap

class Enemy:
    def __init__(self, eid, x, y, rows, columns, enemy_type="slime",
                 current_map="Test_01", frame_speed=0.12, speed=60, cpadding=0):
        self.id = eid
        self.type = enemy_type
        self.x = x
        self.y = y
        self.prev_x = x
        self.prev_y = y
        self.target_x = x
        self.target_y = y
        self.rows = rows
        self.columns = columns
        self.direction = "down"
        self.moving = True
        self.current_map = current_map
        self.speed = speed  # pixels per second
        self.frame_speed = frame_speed
        self.last_update_time = time.time()
        
        self.z_index = 0  # start at ground level

        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        map_path = os.path.join(BASE_DIR, f"../assets/maps/{current_map}.tmx")

        self.game_map = GameMap(os.path.normpath(map_path))


        # Load sprite sheet
        sprite_path = f"assets/enemies/{self.type}.png"
        if not os.path.exists(sprite_path):
            raise FileNotFoundError(f"Enemy sprite not found: {sprite_path}")

        sheet = pygame.image.load(sprite_path).convert_alpha()
        sheet_width, sheet_height = sheet.get_size()
        frame_width = sheet_width // self.columns
        frame_height = sheet_height // self.rows

        self.collision_padding = cpadding

        self.rect = pygame.Rect(x  , y , frame_width - 2 * self.collision_padding, frame_height - 2 * self.collision_padding)

    def distance_to(self, x, y):
        dx = x - self.x
        dy = y - self.y
        return (dx**2 + dy**2)**0.5

    def find_closest_player(self, players):
        """Return the closest player on the same map, or None if none exist."""
        same_map_players = [p for p in players.values() if p.current_map == self.current_map]
        if not same_map_players:
            return None
        closest_player = min(same_map_players, key=lambda p: self.distance_to(p.x, p.y))
        return closest_player

    def move_towards_target(self, dt, game_map):
        if not self.moving:
            return

        dx = self.target_x - self.x
        dy = self.target_y - self.y
        distance = (dx**2 + dy**2)**0.5
        if distance == 0:
            self.moving = False
            return

        # Calculate step
        step = self.speed * dt
        step_ratio = min(step / distance, 1)  # avoid overshoot
        new_x = self.x + dx * step_ratio
        new_y = self.y + dy * step_ratio

        # --- Collision check ---
        # Check corners of enemy rect at the new position
        rect_width, rect_height = self.rect.width, self.rect.height
        corners = [
            (new_x, new_y),  # top-left
            (new_x + rect_width, new_y),  # top-right
            (new_x, new_y + rect_height),  # bottom-left
            (new_x + rect_width, new_y + rect_height)  # bottom-right
        ]
        if any(game_map.is_collision_tile(cx, cy) for cx, cy in corners):
            # Stop movement if collision detected
            self.moving = False
            return

        # Apply movement
        self.x = new_x
        self.y = new_y
        self.rect.topleft = (self.x, self.y)

    def update(self, dt, players):
        """Update movement towards closest player and z_index."""
        closest_player = self.find_closest_player(players)
        if closest_player:
            self.target_x = closest_player.x
            self.target_y = closest_player.y
            self.moving = True

        self.move_towards_target(dt, self.game_map)

        # --- Update z_index based on elevation tile under feet ---

        sample_x = self.x + self.rect.width // 2
        sample_y = self.y + self.rect.height
        new_z = self.game_map.is_elevation_tile(sample_x , sample_y)
        if new_z is not None:
            self.z_index = new_z
            # Optional debug:
            # print(f"Enemy {self.id} at ({sample_x},{sample_y}) -> z_index: {new_z}")
