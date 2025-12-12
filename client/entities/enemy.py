import pygame
import os
import time
import config

class Enemy:
    def __init__(self, eid, **kwargs):
        self.id = eid
        self.x = kwargs.get("x", 0)
        self.y = kwargs.get("y", 0)
        self.rows = kwargs.get("rows", 1)
        self.columns = kwargs.get("columns", 1)  # full width columns for the sheet
        self.type = kwargs.get("enemy_type", "green-slime")
        self.current_map = kwargs.get("current_map", "Test_01")
        self.hp = kwargs.get("hp", 10)
        self.speed = kwargs.get("speed", 100.0)
        self.frame_speed = kwargs.get("frame_speed", 0.12)
        self.z_index = kwargs.get("z_index", 0)
        self.c_h_padding = kwargs.get("c_h_padding", 0)
        self.c_v_padding = kwargs.get("c_v_padding", 0)

        # Movement & state
        self.target_x = self.x
        self.target_y = self.y
        self.moving = True
        self.attacking = False

        # Animation state
        self.direction = kwargs.get("directions", ["down"])[0]
        self.frame_index = 0
        self.frame_timer = 0
        self.image = None

        # Columns per animation type
        self.move_cols = kwargs.get("move-cols", self.columns)
        self.idle_cols = kwargs.get("idle-cols", self.columns)
        self.attack_cols = kwargs.get("attack-cols", self.columns)
        self.max_cols = max(self.move_cols, self.idle_cols, self.attack_cols)

        # Must provide mapping of direction -> row index
        if "direction_row" not in kwargs:
            raise ValueError("Enemy must be initialized with direction_row from EnemyController")
        self.direction_row = kwargs["direction_row"]

        # Load sprite sheet
        sprite_path = f"assets/enemies/{self.type}.png"
        if not os.path.exists(sprite_path):
            raise FileNotFoundError(f"Enemy sprite not found: {sprite_path}")

        sheet = pygame.image.load(sprite_path).convert_alpha()
        sheet_width, sheet_height = sheet.get_size()
        frame_height = sheet_height // self.rows
        full_frame_width = sheet_width // self.max_cols  # real width of a frame in sheet

        # Build animations dynamically
        self.animations = {}
        for name, row_idx in self.direction_row.items():
            if "-idle" in name:
                frames_count = self.idle_cols
            elif "-attack" in name:
                frames_count = self.attack_cols
            else:
                frames_count = self.move_cols

            frames = []
            for i in range(frames_count):
                rect_x = i * full_frame_width
                rect_y = row_idx * frame_height

                # Clamp rect inside sheet
                rect_x = min(rect_x, sheet_width - full_frame_width)
                rect_y = min(rect_y, sheet_height - frame_height)

                rect = pygame.Rect(rect_x, rect_y, full_frame_width, frame_height)
                frames.append(sheet.subsurface(rect).copy())

            self.animations[name] = frames
            

        # Fallback image
        self.image = next(iter(self.animations.values()))[0]


        # print(self.animations.keys())
        # for anim in self.animations.keys():
        #     print(f" {anim} animation {self.animations[anim]} with {len(self.animations[anim])} frames.")

    def update_movement(self, dt):
        interp_speed = 10.0
        self.x += (self.target_x - self.x) * interp_speed * dt
        self.y += (self.target_y - self.y) * interp_speed * dt
        threshold = 0.5
        self.moving = abs(self.target_x - self.x) > threshold or abs(self.target_y - self.y) > threshold

    def update_animation(self, dt):
        dx = self.target_x - self.x
        dy = self.target_y - self.y

        # Determine base direction
        if abs(dx) > abs(dy):
            base_dir = "right" if dx > 0 else "left"
        else:
            base_dir = "down" if dy > 0 else "up"

        # Determine animation type
        if self.attacking:
            desired_dir = f"{base_dir}-attack"
        elif not self.moving:
            desired_dir = f"{base_dir}-idle"
        else:
            desired_dir = base_dir

        # Fallback if animation missing
        if desired_dir not in self.animations:
            desired_dir = base_dir
        if desired_dir not in self.animations:
            desired_dir = next(iter(self.animations.keys()))

        # Change direction resets frame
        if self.direction != desired_dir:
            self.direction = desired_dir
            self.frame_index = 0
            self.frame_timer = 0

        # Animate frame
        frames = self.animations[self.direction]
        self.frame_timer += dt
        if self.frame_timer >= self.frame_speed:
            self.frame_timer -= self.frame_speed
            self.frame_index += 1

            # **Skip last two frames for idle animations**
            if "-idle" in self.direction:
                if self.frame_index >= len(frames) - 2:
                    self.frame_index = 0  # loop back to start
            else:
                self.frame_index %= len(frames)

        self.image = frames[self.frame_index]


    def update(self, dt):
        self.update_movement(dt)
        self.update_animation(dt)
        if not hasattr(self, "rect"):
            w, h = self.image.get_size()
            self.rect = pygame.Rect(self.x + self.c_h_padding, self.y + self.c_v_padding,
                                    w - 2*self.c_h_padding, h - 2*self.c_v_padding)
        else:
            self.rect.topleft = (round(self.x), round(self.y))

    def apply_server_update(self, data):
        self.target_x = data.get("x", self.target_x)
        self.target_y = data.get("y", self.target_y)
        self.current_map = data.get("current_map", self.current_map)
        self.moving = data.get("moving", self.moving)
        self.z_index = data.get("z_index", self.z_index)
        self.attacking = data.get("attacking", self.attacking)

    def draw(self, surface, cam_rect, current_map_name=None, render_x=None, render_y=None):
        if current_map_name and self.current_map != current_map_name:
            return

        if render_x is None:
            render_x = self.x
        if render_y is None:
            render_y = self.y

        frames = self.animations[self.direction]

        if "-idle" in self.direction:
            max_index = max(0, len(frames) - (self.max_cols - self.idle_cols))
            frame_index = min(self.frame_index, max_index)
        else:
            frame_index = self.frame_index

        frame = frames[frame_index]

        draw_x = render_x - cam_rect.x - self.c_h_padding
        draw_y = render_y - cam_rect.y - self.c_v_padding
        surface.blit(frame, (draw_x, draw_y))

        if config.SHOW_ENEMY_RECT:
            w, h = frame.get_size()
            rect = pygame.Rect(draw_x + self.c_h_padding, draw_y + self.c_v_padding,
                            w - 2*self.c_h_padding, h - 2*self.c_v_padding)
            pygame.draw.rect(surface, (0, 255, 0), rect, 2)

