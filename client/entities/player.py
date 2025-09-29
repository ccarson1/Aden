# import pygame

# class Player:
#     def __init__(self, player_id, name, spritesheet, frame_w, frame_h, x=100, y=100):
#         self.id = player_id
#         self.name = name
#         self.x = x
#         self.y = y
#         self.direction = "down"
#         self.anim_timer = 0
#         self.anim_frame = 0
#         self.frame_w = frame_w
#         self.frame_h = frame_h
#         self.current_map = None

#         self.MOVE_SPEED = 1
#         self.ANIMATION_SPEED = 0.15  # seconds per frame
#         self.show_hitbox = True  # Toggle hitbox visualization

#         # Default padding (can tweak per sprite)
#         self.pad_top = 40
#         self.pad_bottom = 20
#         self.pad_left = 30
#         self.pad_right = 30

#         self.rect = pygame.Rect(self.x, self.y, self.frame_w, self.frame_h)

#         self.frames = {"down": [], "left": [], "right": [], "up": []}

#         cols = spritesheet.get_width() // frame_w
#         for row, dir_name in enumerate(["down", "left", "right", "up"]):
#             for col in range(cols):
#                 frame = spritesheet.subsurface(
#                     pygame.Rect(col*frame_w, row*frame_h, frame_w, frame_h)
#                 )
#                 self.frames[dir_name].append(frame)

#     def get_hitbox(self, x=None, y=None):
#         """Return the player's collision rect with current padding."""
#         if x is None: x = self.x
#         if y is None: y = self.y

#         return pygame.Rect(
#             x + self.pad_left,
#             y + self.pad_top,
#             self.frame_w - (self.pad_left + self.pad_right),
#             self.frame_h - (self.pad_top + self.pad_bottom)
#         )

#     def move(self, dx, dy, dt, colliders):
#         if dx == 0 and dy == 0:
#             self.anim_frame = 0
#             return

#         # New proposed position
#         new_x = self.x + dx * self.MOVE_SPEED
#         new_y = self.y + dy * self.MOVE_SPEED

#         # Future hitbox at the new position
#         future_rect = self.get_hitbox(new_x, new_y)

#         # Collision check
#         for rect in colliders:
#             if future_rect.colliderect(rect):
#                 return  # blocked

#         # Apply movement
#         self.x = new_x
#         self.y = new_y

#         if dx > 0: self.direction = "right"
#         if dx < 0: self.direction = "left"
#         if dy > 0: self.direction = "down"
#         if dy < 0: self.direction = "up"

#         self.anim_timer += dt
#         if self.anim_timer >= self.ANIMATION_SPEED:
#             self.anim_timer = 0
#             self.anim_frame = (self.anim_frame + 1) % len(self.frames[self.direction])

#     def update_animation(self, dt, moving=True):
#         if not moving:
#             self.anim_frame = 0
#             return
#         self.anim_timer += dt
#         if self.anim_timer >= self.ANIMATION_SPEED:
#             self.anim_timer = 0
#             self.anim_frame = (self.anim_frame + 1) % len(self.frames[self.direction])

#     def draw(self, surface):
#         frame = self.frames[self.direction][self.anim_frame]
#         surface.blit(frame, (self.x, self.y))

#         if self.show_hitbox:
#             hitbox = self.get_hitbox()
#             pygame.draw.rect(surface, (255, 0, 0), hitbox, 1)


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
        self.current_map = None
        self.speed = 100
        self.MOVE_SPEED = 100  # pixels per second
        self.ANIMATION_SPEED = 0.15  # seconds per frame
        self.show_hitbox = True

        # Interpolation state
        self.prev_x = x
        self.prev_y = y
        self.target_x = x
        self.target_y = y
        self.render_x = x
        self.render_y = y
        self.last_update_time = 0.0

        # Default padding for collision
        self.pad_top = 40
        self.pad_bottom = 20
        self.pad_left = 30
        self.pad_right = 30
        self.moving = False  # Is the player currently moving?

        # Rect used for portal/collider detection (sync with hitbox)
        self.rect = self.get_hitbox()

        # Load animation frames
        self.frames = {"down": [], "left": [], "right": [], "up": []}
        cols = spritesheet.get_width() // frame_w
        for row, dir_name in enumerate(["down", "left", "right", "up"]):
            for col in range(cols):
                frame = spritesheet.subsurface(
                    pygame.Rect(col * frame_w, row * frame_h, frame_w, frame_h)
                )
                self.frames[dir_name].append(frame)

    def get_hitbox(self, x=None, y=None):
        """Return a collision rect with current padding."""
        if x is None: x = self.x
        if y is None: y = self.y
        return pygame.Rect(
            x + self.pad_left,
            y + self.pad_top,
            self.frame_w - (self.pad_left + self.pad_right),
            self.frame_h - (self.pad_top + self.pad_bottom)
        )

    def move(self, dx, dy, dt, colliders):
        """Move player, handle collisions, update direction & animation."""
        if dx == 0 and dy == 0:
            self.anim_frame = 0
            return

        # Calculate movement based on delta time
        move_x = dx * self.MOVE_SPEED * dt
        move_y = dy * self.MOVE_SPEED * dt

        new_x = self.x + move_x
        new_y = self.y + move_y
        future_rect = self.get_hitbox(new_x, new_y)

        # Check collisions
        for collider in colliders:
            if future_rect.colliderect(collider):
                # Block movement along the axis that collides
                if dx != 0:
                    move_x = 0
                if dy != 0:
                    move_y = 0
                future_rect = self.get_hitbox(self.x + move_x, self.y + move_y)

        # Apply movement
        self.x += move_x
        self.y += move_y
        self.rect = future_rect  # update main rect for portal/collision checks

        # Update direction
        if dx > 0: self.direction = "right"
        if dx < 0: self.direction = "left"
        if dy > 0: self.direction = "down"
        if dy < 0: self.direction = "up"

        # Update animation
        self.anim_timer += dt
        if self.anim_timer >= self.ANIMATION_SPEED:
            self.anim_timer = 0
            self.anim_frame = (self.anim_frame + 1) % len(self.frames[self.direction])

    def update_animation(self, dt, moving=True):
        """Update animation independently (e.g., for other players)."""
        if not moving:
            self.anim_frame = 0
            return
        self.anim_timer += dt
        if self.anim_timer >= self.ANIMATION_SPEED:
            self.anim_timer = 0
            self.anim_frame = (self.anim_frame + 1) % len(self.frames[self.direction])

    def draw(self, surface):
        """Draw player and optional hitbox."""
        frame = self.frames[self.direction][self.anim_frame]
        surface.blit(frame, (self.x, self.y))

        if self.show_hitbox:
            pygame.draw.rect(surface, (255, 0, 0), self.get_hitbox(), 1)

