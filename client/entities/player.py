

import pygame

class Player:
    def __init__(self, player_id, name, spritesheet, anim_meta=None, x=100, y=100):
        self.id = player_id
        self.name = name
        self.x = x
        self.y = y
        self.direction = "down"
        self.attack_direction = self.direction
        self.anim_timer = 0
        self.anim_frame = 0
        self.current_map = None
        self.speed = 50
        self.MOVE_SPEED = 100
        self.show_hitbox = True
        self.z_index = 0
        self.class_type = "mage"

        # Interpolation
        self.prev_x = x
        self.prev_y = y
        self.target_x = x
        self.target_y = y
        self.render_x = x
        self.render_y = y
        self.last_update_time = 0.0

        # Padding
        self.pad_top = 40
        self.pad_bottom = 20
        self.pad_left = 30
        self.pad_right = 30

        self.moving = False
        self.attacking = False
        self.attack_anim_timer = 0
        self.attack_anim_frame = 0
        self.last_attack_anim = None
        self.long_attacking = False
        self.running = False

        if anim_meta is None:
            raise ValueError("Player requires anim_meta for dynamic animations")

        self.anim_meta = anim_meta
        self.spritesheet = spritesheet
        self.frames = {}

        # Load all frames
        self.load_frames()

        # Default frame size
        self.frame_w = anim_meta.get("move-width", 64)
        self.frame_h = anim_meta.get("move-height", 64)
        self.image = next(iter(self.frames.values()))[0]
        self.rect = self.get_hitbox()

    def load_frames(self):
        meta = self.anim_meta
        sheet_w, sheet_h = self.spritesheet.get_size()
        skip_frames = meta.get("skip_frames", {})

        print("\n========== LOADING PLAYER FRAMES ==========")

        for anim_name, row_idx in meta.get("direction_row", {}).items():

            if "-attack" in anim_name:
                frame_w = meta.get("attack-width", meta.get("move-width", 64))
                frame_h = meta.get("attack-height", meta.get("move-height", 64))
                cols = meta.get("attack-cols", 6)
            elif "-longAttack" in anim_name:
                frame_w = meta.get("attack-width", 64)
                frame_h = meta.get("attack-height", 64)
                cols = meta.get("longAttack-cols", 13)
            elif "-idle" in anim_name:
                frame_w = meta.get("idle-width", 64)
                frame_h = meta.get("idle-height", 64)
                cols = meta.get("idle-cols", 1)
            elif "-running" in anim_name:
                frame_w = meta.get("move-width", 64)
                frame_h = meta.get("move-height", 64)
                cols = meta.get("running-cols", 8)
            else:
                frame_w = meta.get("move-width", 64)
                frame_h = meta.get("move-height", 64)
                cols = meta.get("move-cols", 1)

            skip = skip_frames.get(anim_name, 0)
            frames = []

            print(f"\n[LOAD] Animation '{anim_name}'")
            print(f"       Row: {row_idx}")
            print(f"       Frame size: {frame_w}x{frame_h}")
            print(f"       Columns: {cols}, Skip first: {skip}")

            for i in range(skip, cols):
                rect_x = i * frame_w
                rect_y = row_idx * frame_h

                # Bounds check instead of clamping
                if rect_x + frame_w > sheet_w or rect_y + frame_h > sheet_h:
                    print(f"       [SKIP] Frame {i}: OUT OF BOUNDS ({rect_x},{rect_y})")
                    continue

                try:
                    frame = self.spritesheet.subsurface(
                        pygame.Rect(rect_x, rect_y, frame_w, frame_h)
                    ).copy()
                    frames.append(frame)
                    print(f"       [OK]   Frame {i}: ({rect_x},{rect_y})")

                except Exception as e:
                    print(f"       [ERR]  Frame {i}: ({rect_x},{rect_y}) - {e}")

            self.frames[anim_name] = frames

            print(f"       => Loaded {len(frames)} frames for '{anim_name}'")

            if len(frames) == 0:
                print(f"       !!! ERROR: NO FRAMES LOADED for '{anim_name}' !!!")

            if len(frames) < cols - skip:
                print(f"       !!! WARNING: Missing frames for '{anim_name}' !!!")

        print("========== DONE LOADING FRAMES ==========\n")



    def get_hitbox(self, x=None, y=None):
        if x is None: x = self.x
        if y is None: y = self.y
        return pygame.Rect(
            x + self.pad_left,
            y + self.pad_top,
            self.frame_w - (self.pad_left + self.pad_right),
            self.frame_h - (self.pad_top + self.pad_bottom)
        )

    def move(self, dx, dy, dt, colliders, elevations):
        moving = dx != 0 or dy != 0

        if not moving:
            anim_name = f"{self.direction}-idle"
            anim_speed = self.get_anim_speed(anim_name)

            self.anim_timer += dt
            if self.anim_timer >= anim_speed:
                self.anim_timer = 0
                self.anim_frame = (self.anim_frame + 1) % len(self.frames[anim_name])

            return

        # --- Movement code remains unchanged ---
        move_x = dx * self.MOVE_SPEED * dt
        move_y = dy * self.MOVE_SPEED * dt

        new_x = self.x + move_x
        new_y = self.y + move_y
        future_rect = self.get_hitbox(new_x, new_y)

        for collider in colliders:
            if self.z_index == collider["z_index"] and future_rect.colliderect(collider["rect"]):
                if dx != 0: move_x = 0
                if dy != 0: move_y = 0
                future_rect = self.get_hitbox(self.x + move_x, self.y + move_y)

        self.x += move_x
        self.y += move_y
        self.rect = future_rect

        for elevation in elevations:
            if "z_index" in elevation and self.rect.colliderect(elevation["rect"]):
                self.z_index = elevation["z_index"]
                break

        # Update direction
        if dx > 0: self.direction = "right"
        if dx < 0: self.direction = "left"
        if dy > 0: self.direction = "down"
        if dy < 0: self.direction = "up"

        # Update movement animation
        anim_name = self.direction

        # Get speed from anim_meta
        anim_speed = self.get_anim_speed(anim_name)



        self.anim_timer += dt
        if self.anim_timer >= anim_speed:
            self.anim_timer = 0
            self.anim_frame = (self.anim_frame + 1) % len(self.frames[anim_name])

    def get_anim_speed(self, anim_name):
        speeds = self.anim_meta.get("anim_speeds", {})
        if anim_name.endswith("-idle"):
            return speeds.get("-idle", speeds.get("default", 0.35))
        elif anim_name.endswith("-running"):
            return speeds.get("-running", speeds.get("running", 0.1))
        elif anim_name.endswith("-attack"):
            return speeds.get("-attack", speeds.get("default", 0.1))
        elif anim_name.endswith("-longAttack"):
            return speeds.get("-longAttack", speeds.get("default", 0.1))
        else:
            return speeds.get("default", .02)

    def update_animation(self, dt, moving=True, running=False):
        # Determine animation key
        if moving:
            if running:
                anim_name = f"{self.direction}-running"
            else:
                anim_name = self.direction
        else:
            anim_name = f"{self.direction}-idle"

        if anim_name not in self.frames:
            anim_name = f"{self.direction}-idle"  # fallback

        # 🔑 MINIMAL FIX: reset frame if animation changed
        if getattr(self, "current_anim", None) != anim_name:
            self.current_anim = anim_name
            self.anim_frame = 0
            self.anim_timer = 0

        anim_speed = self.get_anim_speed(anim_name)
        self.anim_timer += dt
        if self.anim_timer >= anim_speed:
            self.anim_timer = 0
            self.anim_frame = (self.anim_frame + 1) % len(self.frames[anim_name])

    def update_attack_animation(self, dt, remote=False):
        if not self.attacking:
            return

        anim_key = f"{self.attack_direction}-attack"
        if self.long_attacking:
            anim_key = f"{self.attack_direction}-longAttack"

        frames = self.frames.get(anim_key, [])
        if not frames:
            return

        # Only reset frame if animation changed (local or remote)
        if getattr(self, "last_attack_anim", None) != anim_key:
            self.attack_anim_frame = 0
            self.attack_anim_timer = 0
        self.last_attack_anim = anim_key

        speed = self.get_anim_speed(anim_key)
        self.attack_anim_timer += dt

        while self.attack_anim_timer >= speed:
            self.attack_anim_timer -= speed
            self.attack_anim_frame += 1

            if self.attack_anim_frame >= len(frames):
                if not remote:
                    # Local player stops automatically
                    self.attacking = False
                    self.attack_anim_frame = 0
                    self.last_attack_anim = None
                else:
                    # Remote player: loop the animation instead of freezing
                    self.attack_anim_frame = 0  # loop remote attack animation



    def draw(self, surface, cam_rect, render_x=None, render_y=None):
        if render_x is None: render_x = self.x
        if render_y is None: render_y = self.y

        if self.attacking:
            if self.long_attacking:
                anim_key = f"{self.attack_direction}-longAttack"
            else:
                anim_key = f"{self.attack_direction}-attack"
            print(f"[DRAW] Attacking, anim_key={anim_key}, frame={self.attack_anim_frame}")
            print(self.anim_meta.keys())
            #print(self.anim_meta[f"{anim_key}"])
            print(f"{self.frames[anim_key][self.attack_anim_frame]}")
            frame = self.frames[anim_key][self.attack_anim_frame]
            print(f"Frames: {self.frames}")
        else:
            if not self.moving:
                anim_key = f"{self.direction}-idle"
            elif self.running:
                anim_key = f"{self.direction}-running"
            else:
                anim_key = self.direction
            #print(f"[DRAW] Moving/Idle, anim_key={anim_key}, frame={self.anim_frame}")
            #print(f"[DRAW] Attack Animation Frame: {self.attack_anim_frame} / {len(self.frames.get(anim_key, []))}")
            if anim_key != getattr(self, "last_anim", None):
                self.anim_frame = 0
                self.anim_timer = 0
            self.last_anim = anim_key
            self.anim_frame %= len(self.frames[anim_key])
            frame = self.frames[anim_key][self.anim_frame]

        # Apply offset from anim_meta if exists
        offsets = self.anim_meta.get("anim_offsets", {})
        x_off, y_off = offsets.get(anim_key, (0, 0))
        screen_x = render_x - cam_rect.x + x_off
        screen_y = render_y - cam_rect.y + y_off

        surface.blit(frame, (screen_x, screen_y))

        if self.show_hitbox:
            hitbox = self.get_hitbox(render_x, render_y)
            hitbox_screen = hitbox.move(-cam_rect.x, -cam_rect.y)
            pygame.draw.rect(surface, (255, 0, 0), hitbox_screen, 1)
