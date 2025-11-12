
import pygame
import os
import time
import config

# Map directions to row index (used only if you have multi-row sheets)
DIRECTION_ROW = {
    "down": 0,
    "left": 1,
    "right": 2,
    "up": 3
}

class Enemy:
    def __init__(self, eid, **kwargs):
        self.id = eid
        self.x = kwargs.get("x", 0)
        self.y = kwargs.get("y", 0)
        self.rows = kwargs.get("rows", 1)
        self.columns = kwargs.get("columns", 11)
        self.type = kwargs.get("enemy_type", "green-slime")
        self.current_map = kwargs.get("current_map", "Test_01")
        self.hp = kwargs.get("hp", 10)
        self.speed = kwargs.get("speed", 100.0)
        self.frame_speed = kwargs.get("frame_speed", 0.12)
        self.directions = kwargs.get("directions", ["down"])
        self.z_index = kwargs.get("z_index", 0)
        self.collision_padding = kwargs.get("collision_padding", 0)

        self.last_update_time = time.time() 

        

        # Movement
        self.prev_x = self.x
        self.prev_y = self.y
        self.target_x = self.x
        self.target_y = self.y
        self.moving = True

        # Animation state
        self.direction = self.directions[0] if self.directions else "down"
        self.frame_index = 0
        self.frame_timer = 0
        self.image = None

        # Load sprite sheet
        sprite_path = f"assets/enemies/{self.type}.png"
        if not os.path.exists(sprite_path):
            raise FileNotFoundError(f"Enemy sprite not found: {sprite_path}")

        sheet = pygame.image.load(sprite_path).convert_alpha()
        sheet_width, sheet_height = sheet.get_size()
        frame_width = sheet_width // self.columns
        frame_height = sheet_height // self.rows

        print(f"Rows: {self.rows}")
        print(f"columns: {self.columns}")

        # Crop frames
        self.animations = {}
        for row_idx in range(self.rows):
            # If there is only one direction, just use "down"
            direction_name = self.directions[row_idx] if row_idx < len(self.directions) else f"row{row_idx}"
            frames = []
            for col_idx in range(self.columns):
                rect = pygame.Rect(
                    col_idx * frame_width,
                    row_idx * frame_height,
                    frame_width,
                    frame_height
                )
                frames.append(sheet.subsurface(rect).copy())
            self.animations[direction_name] = frames

        # Default image
        self.image = list(self.animations.values())[0][0]

    def update_animation(self, dt):
        """Animate the sprite based on movement and direction."""
        frames = self.animations.get(self.direction)
        if not frames:
            # fallback to first row if direction missing
            frames = list(self.animations.values())[0]

        if len(frames) <= 1:
            self.image = frames[0]
            return


        self.frame_timer += dt
        if self.frame_timer >= self.frame_speed:
            self.frame_timer -= self.frame_speed
            self.frame_index = (self.frame_index + 1) % len(frames)

        self.image = frames[self.frame_index]

    def update_movement(self, dt):
        """Smoothly interpolate toward the last known server position."""
        interp_speed = 10.0  # adjust for smoothness
        self.x += (self.target_x - self.x) * interp_speed * dt
        self.y += (self.target_y - self.y) * interp_speed * dt

    def update(self, dt):
        # Smooth position interpolation
        self.update_movement(dt)

        # Determine if moving (based on small threshold)
        # moving_now = abs(self.target_x - self.x) > 0.1 or abs(self.target_y - self.y) > 0.1
        # self.moving = moving_now

        # Animate only if moving or always animate for certain enemies
        if self.moving:
            self.update_animation(dt)
        else:
            self.frame_index = 0 

        # Always sync rect and position together
        if not hasattr(self, "rect"):
            rect_w, rect_h = self.image.get_size()
            self.rect = pygame.Rect(
                self.x + self.collision_padding,
                self.y + self.collision_padding,
                rect_w - 2 * self.collision_padding,
                rect_h - 2 * self.collision_padding
            )
        else:
            self.rect.topleft = (round(self.x), round(self.y))

        self.x, self.y = self.rect.topleft



    def apply_server_update(self, data):
        self.target_x = data.get("x", self.target_x)
        self.target_y = data.get("y", self.target_y)
        self.direction = data.get("direction", self.direction)
        self.current_map = data.get("current_map", self.current_map)
        self.moving = data.get("moving", self.moving)
        self.z_index = data.get("z_index", getattr(self, "z_index", 0))
        self.last_update_time = time.time()

    def draw(self, surface, cam_rect):
        """
        Draw the enemy's current frame relative to the camera.
        """
        frame = self.animations[self.direction][self.frame_index]
        draw_x = self.x - cam_rect.x - self.collision_padding
        draw_y = self.y - cam_rect.y - self.collision_padding
        surface.blit(frame, (draw_x, draw_y))

        

        # Draw the rectangle around the enemy
        if config.SHOW_ENEMY_RECT:
            rect_width, rect_height = frame.get_size()
            rect = pygame.Rect(
                draw_x + self.collision_padding,
                draw_y + self.collision_padding,
                rect_width - 2 * self.collision_padding,
                rect_height - 2 * self.collision_padding
            )
            pygame.draw.rect(surface, (0, 255, 0), rect, 2)
