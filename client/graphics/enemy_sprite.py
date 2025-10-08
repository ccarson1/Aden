import pygame
import os

# Map directions to row index if needed
DIRECTION_ROW = {
    "down": 0,
    "left": 1,
    "right": 2,
    "up": 3
}

class EnemySprite(pygame.sprite.Sprite):
    def __init__(self, enemy: "Enemy", sprite_path, frame_speed=0.15):
        super().__init__()
        self.id = enemy.id
        self.type = enemy.type
        self.x = enemy.x
        self.y = enemy.y
        self.prev_x = enemy.prev_x
        self.prev_y = enemy.prev_y
        self.target_x = enemy.target_x
        self.target_y = enemy.target_y
        self.rows = enemy.rows
        self.cols = enemy.columns
        self.direction = enemy.direction
        self.moving = enemy.moving
        self.frame_speed = frame_speed
        self.animation_timer = 0
        self.current_frame = 0
        self.current_map = enemy.current_map

        # Load the full spritesheet
        if sprite_path and os.path.exists(sprite_path):
            sheet = pygame.image.load(sprite_path).convert_alpha()
            self.frame_width = sheet.get_width() // self.cols
            self.frame_height = sheet.get_height() // self.rows
            self.frames = []

            for r in range(self.rows):
                row_frames = []
                for c in range(self.cols):
                    rect = pygame.Rect(c * self.frame_width, r * self.frame_height, self.frame_width, self.frame_height)
                    row_frames.append(sheet.subsurface(rect))
                self.frames.append(row_frames)
        else:
            print(f"[WARN] Sprite file missing: {sprite_path}, using placeholder")
            self.frames = [[pygame.Surface((32,32)) for _ in range(self.cols)] for _ in range(self.rows)]
            for row in self.frames:
                for frame in row:
                    frame.fill((255,0,0))

        self.image = self.frames[0][0]
        self.rect = self.image.get_rect(topleft=(self.x, self.y))

    def apply_server_update(self, data):
        self.prev_x = self.x
        self.prev_y = self.y
        self.x = data.get("x", self.x)
        self.y = data.get("y", self.y)
        self.target_x = self.x
        self.target_y = self.y
        self.direction = data.get("direction", self.direction)
        self.moving = data.get("moving", self.moving)
        self.current_map = data.get("current_map", self.current_map)

    def update_animation(self, dt):
        if not self.frames:
            return

        row_index = DIRECTION_ROW.get(self.direction, 0)
        row_frames = self.frames[row_index]

        if len(row_frames) <= 1:
            self.image = row_frames[0]
            return

        if self.moving:
            self.animation_timer += dt
            if self.animation_timer >= self.frame_speed:
                self.animation_timer = 0
                self.current_frame = (self.current_frame + 1) % len(row_frames)

        self.image = row_frames[self.current_frame]
        self.rect.topleft = (self.x, self.y)
