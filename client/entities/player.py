#client/entities/player.py
import pygame

class Player:
    def __init__(self, player_id, name, spritesheet, frame_w, frame_h, x=100, y=100):
        self.id = player_id
        self.name = name
        self.x = x
        self.y = y
        self.direction = "down"
        self.anim_timer = 0
        self.anim_frame = 0
        self.frame_w = frame_w
        self.frame_h = frame_h

        self.MOVE_SPEED = 1
        self.ANIMATION_SPEED = 0.15  # seconds per frame

        self.frames = {"down": [], "left": [], "right": [], "up": []}

        cols = spritesheet.get_width() // frame_w
        for row, dir_name in enumerate(["down", "left", "right", "up"]):
            for col in range(cols):
                frame = spritesheet.subsurface(
                    pygame.Rect(col*frame_w, row*frame_h, frame_w, frame_h)
                )
                self.frames[dir_name].append(frame)

    def move(self, dx, dy, dt):
        if dx == 0 and dy == 0:
            self.anim_frame = 0
            return
        self.x += dx * self.MOVE_SPEED
        self.y += dy * self.MOVE_SPEED
        if dx > 0: self.direction = "right"
        if dx < 0: self.direction = "left"
        if dy > 0: self.direction = "down"
        if dy < 0: self.direction = "up"

        self.anim_timer += dt
        if self.anim_timer >= self.ANIMATION_SPEED:
            self.anim_timer = 0
            self.anim_frame = (self.anim_frame + 1) % len(self.frames[self.direction])

    # NEW method to animate remote players
    def update_animation(self, dt, moving=True):
        if not moving:
            self.anim_frame = 0
            return
        self.anim_timer += dt
        if self.anim_timer >= self.ANIMATION_SPEED:
            self.anim_timer = 0
            self.anim_frame = (self.anim_frame + 1) % len(self.frames[self.direction])

    def draw(self, surface):
        frame = self.frames[self.direction][self.anim_frame]
        surface.blit(frame, (self.x, self.y))

