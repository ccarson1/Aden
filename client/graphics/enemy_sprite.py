# client/graphics/enemy_sprite.py
import pygame
import os

class EnemySprite(pygame.sprite.Sprite):
    def __init__(self, x, y,current_map, enemy_type="green-slime"):
        super().__init__()
        self.x = x
        self.y = y

        # Determine the sprite sheet path based on enemy_type
        sprite_path = f"assets/enemies/{enemy_type}.png"
        sprite_sheet = pygame.image.load(sprite_path).convert_alpha()

        # For green-slime, 11 frames of 16x32
        self.frame_width = sprite_sheet.get_width() // 11
        self.frame_height = sprite_sheet.get_height()

        # Slice frames
        self.frames = []
        for i in range(sprite_sheet.get_width() // self.frame_width):
            rect = pygame.Rect(i * self.frame_width, 0, self.frame_width, self.frame_height)
            self.frames.append(sprite_sheet.subsurface(rect))

        self.current_frame = 0
        self.image = self.frames[self.current_frame]
        self.rect = self.image.get_rect(topleft=(x, y))

        self.animation_timer = 0
        self.animation_speed = 0.15
        self.current_map = current_map

    def update(self, dt):
        # Animation
        self.animation_timer += dt
        if self.animation_timer >= self.animation_speed:
            self.animation_timer = 0
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            self.image = self.frames[self.current_frame]

    def apply_server_update(self, data: dict):
        if "x" in data and "y" in data:
            self.x = data["x"]
            self.y = data["y"]
            self.rect.topleft = (self.x, self.y)

        if "frame" in data:
            self.current_frame = data["frame"] % len(self.frames)
            self.image = self.frames[self.current_frame]

    def interpolate(self, dt, smoothing=0.1):
        # Optional: Smooth movement towards target position if needed
        pass
