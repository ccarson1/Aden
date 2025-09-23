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
        self.show_hitbox = True  # Toggle hitbox visualization

        # Default padding (can tweak per sprite)
        self.pad_top = 40
        self.pad_bottom = 20
        self.pad_left = 30
        self.pad_right = 30

        self.frames = {"down": [], "left": [], "right": [], "up": []}

        cols = spritesheet.get_width() // frame_w
        for row, dir_name in enumerate(["down", "left", "right", "up"]):
            for col in range(cols):
                frame = spritesheet.subsurface(
                    pygame.Rect(col*frame_w, row*frame_h, frame_w, frame_h)
                )
                self.frames[dir_name].append(frame)

    def get_hitbox(self, x=None, y=None):
        """Return the player's collision rect with current padding."""
        if x is None: x = self.x
        if y is None: y = self.y

        return pygame.Rect(
            x + self.pad_left,
            y + self.pad_top,
            self.frame_w - (self.pad_left + self.pad_right),
            self.frame_h - (self.pad_top + self.pad_bottom)
        )

    def move(self, dx, dy, dt, colliders):
        if dx == 0 and dy == 0:
            self.anim_frame = 0
            return

        # New proposed position
        new_x = self.x + dx * self.MOVE_SPEED
        new_y = self.y + dy * self.MOVE_SPEED

        # Future hitbox at the new position
        future_rect = self.get_hitbox(new_x, new_y)

        # Collision check
        for rect in colliders:
            if future_rect.colliderect(rect):
                return  # blocked

        # Apply movement
        self.x = new_x
        self.y = new_y

        if dx > 0: self.direction = "right"
        if dx < 0: self.direction = "left"
        if dy > 0: self.direction = "down"
        if dy < 0: self.direction = "up"

        self.anim_timer += dt
        if self.anim_timer >= self.ANIMATION_SPEED:
            self.anim_timer = 0
            self.anim_frame = (self.anim_frame + 1) % len(self.frames[self.direction])

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

        if self.show_hitbox:
            hitbox = self.get_hitbox()
            pygame.draw.rect(surface, (255, 0, 0), hitbox, 1)
