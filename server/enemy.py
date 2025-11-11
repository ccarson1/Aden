import time
import pygame

class Enemy:
    def __init__(self, eid, x, y, rows, columns, enemy_type="slime", current_map="Test_01", frame_speed=0.12):
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
        self.speed = 100.0  # pixels per second
        self.frame_speed = frame_speed
        self.last_update_time = time.time()
        self.rect = pygame.Rect(x, y, 16, 16)
        self.z_index = 0  # start at ground level

    

    def update(self, dt, game_map):
        """Move enemy towards target and update z_index based on elevation."""
        if not self.moving:
            return

        # Calculate movement towards target
        dx = self.target_x - self.x
        dy = self.target_y - self.y
        distance = (dx**2 + dy**2)**0.5

        if distance == 0:
            self.moving = False
        else:
            step = self.speed * dt
            if step >= distance:
                self.x = self.target_x
                self.y = self.target_y
                self.moving = False
            else:
                self.x += dx / distance * step
                self.y += dy / distance * step

        # Update rect position
        self.rect.topleft = (self.x, self.y)

        # --- Update z_index based on elevation tile under feet ---
        sample_x = self.x + self.rect.width // 2
        sample_y = self.y + self.rect.height  # sample feet instead of top-left
        new_z = game_map.is_elevation_tile(sample_x, sample_y)
        
        if new_z is not None:
            self.z_index = new_z
            print(f"Enemy {self.id} at ({sample_x},{sample_y}) -> z_index: {new_z}")
