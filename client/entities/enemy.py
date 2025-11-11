
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
        """Interpolate smoothly toward target position."""
        dx = self.target_x - self.x
        dy = self.target_y - self.y
        distance = (dx**2 + dy**2)**0.5
        if distance == 0:
            self.moving = False
            return

        # move step based on speed and dt
        step = self.speed * dt
        if step >= distance:
            self.x = self.target_x
            self.y = self.target_y
            self.moving = False
        else:
            self.x += dx / distance * step
            self.y += dy / distance * step
            self.moving = True

    def update(self, dt):
        """Call each frame."""
        self.update_movement(dt)
        self.update_animation(dt)

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
        draw_x = self.x - cam_rect.x
        draw_y = self.y - cam_rect.y
        surface.blit(frame, (draw_x, draw_y))

        

        # Draw the rectangle around the enemy
        if config.SHOW_ENEMY_RECT:
            rect_width, rect_height = frame.get_size()
            rect = pygame.Rect(draw_x, draw_y, rect_width, rect_height)
            pygame.draw.rect(surface, (0, 255, 0), rect, 2)  # green outline, thickness 2
