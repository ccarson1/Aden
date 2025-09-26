

# client/scenes/game_scene.py
import pygame
import time
from ..entities.player import Player
from ..entities import game_map
from client.entities.camera import Camera
import config
import random

class GameScene:
    """
    Represents the main gameplay scene where the local player, remote players,
    and the game map (including portals and collisions) are updated and drawn.
    Handles input, server communication, and map transitions.
    """

    def __init__(self, scene_manager, font, client):
        """
        Initialize the GameScene.
        
        Args:
            scene_manager: Reference to the SceneManager for switching scenes.
            font: pygame Font object for rendering text/UI.
            client: Network client instance for communicating with the server.
        """
        
        self.scene_manager = scene_manager
        self.font = font
        self.client = client

        # Local player instance (controlled by this client)
        self.local_player = self.client.local_player

        # Dictionary of other players received from the server
        self.players = self.client.players

        self.frozen = False

        # Time interval for autosaving player state (currently unused)
        self.SAVE_INTERVAL = 30

        # Map references
        self.map = None          # Deprecated, use current_map
        self.current_map = None  # Current active GameMap

        self.clock = pygame.time.Clock()

        self.toasts = [] 

        # Input history for client-side prediction and reconciliation
        self.input_history = []
        self.camera = Camera(config.WIDTH, config.HEIGHT, zoom=1.0)
        self.server_time = "00:00:00"
        self.world_time = "00:00"

    def add_toast(self, text, duration=2.0):
        self.toasts.append({
            "text": text,
            "time": pygame.time.get_ticks(),
            "duration": duration * 1000  # convert to ms
        })

    def load(self, map_name=None):
        """
        Load heavy assets or maps AFTER fade-out finishes.
        """
        if map_name:
            path = f"assets/maps/{map_name}.tmx"
            print(f"[INFO] Loading TMX AFTER FADE: {path}")
            self.current_map = game_map.GameMap(path)
            self.map_name = map_name

    def print_click_position(self, mouse_pos):
        """
        Prints the world coordinates of the mouse click.
        
        Args:
            mouse_pos (tuple): (x, y) position from pygame.mouse.get_pos()
        """
        cam_rect = self.camera.rect
        world_x = mouse_pos[0] + cam_rect.x
        world_y = mouse_pos[1] + cam_rect.y
        print(f"Clicked at world coordinates: ({world_x}, {world_y})")

    def connect_to_server(self, server_ip, server_port):
        """
        Connect to the game server using the token stored in login_info.
        Acts as a wrapper for client.connect().
        """
        token = self.scene_manager.login_info["token"]
        self.client.connect(server_ip, server_port, token)

    def handle_event(self, event):
        """
        Handle Pygame events for the scene.
        Currently only handles quitting the game.
        """
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left click
            self.print_click_position(event.pos)

    def capture_input(self):
        """
        Capture the current keyboard state for movement controls.

        Returns:
            dict: Dictionary representing directional input state.
                  Keys: "w", "s", "a", "d"; values: True if pressed.
        """
        keys = pygame.key.get_pressed()
        input_state = {
            "w": keys[pygame.K_w],
            "s": keys[pygame.K_s],
            "a": keys[pygame.K_a],
            "d": keys[pygame.K_d],
        }
        return input_state

    def apply_input(self, input_state, dt):
        """
        Apply movement input locally for client-side prediction.
        
        Args:
            input_state (dict): Current directional inputs.
            dt (float): Time delta since last frame (seconds).

        Returns:
            bool: True if the player moved this frame, False otherwise.
        """
        dx = input_state["d"] - input_state["a"]
        dy = input_state["s"] - input_state["w"]
        moving = dx != 0 or dy != 0

        # Move the player with collision detection
        if self.current_map:
            self.local_player.move(dx, dy, dt, self.current_map.colliders)

        # Record input with timestamp for server reconciliation
        timestamp = time.time()
        self.input_history.append((timestamp, input_state))

        return moving

    def reconcile(self, authoritative_state):
        """
        Reconcile the local player's position with the server's authoritative state.
        Applies server position and replays any local inputs not yet acknowledged.

        Args:
            authoritative_state (dict): Server-provided player state containing
                                        x, y, direction, and optionally current_map.
        """
        # Apply authoritative position
        self.local_player.x = authoritative_state["x"]
        self.local_player.y = authoritative_state["y"]
        self.local_player.direction = authoritative_state["direction"]
        self.local_player.current_map = authoritative_state.get("current_map", self.local_player.current_map)

        # Replay unsent input events after the reconciliation timestamp
        now = time.time()
        new_history = []
        for ts, input_state in self.input_history:
            if ts > now:
                dx = input_state["d"] - input_state["a"]
                dy = input_state["s"] - input_state["w"]
                if self.current_map:
                    self.local_player.move(dx, dy, 1/60, self.current_map.colliders)
                new_history.append((ts, input_state))
        self.input_history = new_history

    def check_portals(self):
        """
        Check if the local player is colliding with any portals on the current map.
        If so, send a portal enter request to the server.
        """
        if not self.current_map or self.frozen:
            return

        portal = self.current_map.get_portal_at(self.local_player.rect)
        if portal:
            print(f"[INFO] Portal triggered: {portal.target_map}")
            self.frozen = True  # freeze player immediately
            self.scene_manager.start_fade("game", portal)  #

    def update_world_time(self, server_time_str):
        """
        Convert server-provided UTC time to accelerated game time.
        1 real second = 1 in-game minute.
        Display HH:MM only.
        """
        try:
            h, m, s = map(int, server_time_str.split(":"))

            # Total real seconds since midnight
            total_seconds = h * 3600 + m * 60 + s

            # Accelerated time: 1 real second = 1 in-game minute
            total_game_minutes = total_seconds

            # Convert back to HH:MM
            game_hours = (total_game_minutes // 60) % 24
            game_minutes = total_game_minutes % 60

            self.world_time = f"{game_hours:02d}:{game_minutes:02d}"

        except Exception:
            self.world_time = "00:00"

            
    def get_light_alpha(self):
        """
        Convert accelerated world_time (HH:MM) to overlay alpha.
        0 = day, 180 = night.
        """
        try:
            h, m = map(int, self.world_time.split(":"))
            total_minutes = h * 60 + m  # in-game total minutes

            # Define thresholds in minutes
            dawn_start = 5 * 60   # 05:00
            day_start  = 6 * 60   # 06:00
            dusk_start = 18 * 60  # 18:00
            night_start= 19 * 60  # 19:00

            if day_start <= total_minutes < dusk_start:
                return 0  # Day

            elif dusk_start <= total_minutes < night_start:
                # Fade into night
                progress = (total_minutes - dusk_start) / 60
                return int(progress * 180)

            elif dawn_start <= total_minutes < day_start:
                # Fade into day
                progress = (total_minutes - dawn_start) / 60
                return int((1 - progress) * 180)

            else:
                return 180  # Night

        except Exception:
            return 0


    def update(self, dt):
        """
        Main update loop for GameScene.
        Handles input, movement, portal detection, map updates, and server communication.
        
        Args:
            dt (float): Time delta since last frame (seconds)
        """
        if self.frozen:  # freeze player + stop anims during fade
            if self.current_map:
                self.current_map.update(dt)  # still update animated tiles
            return
        
        input_state = self.capture_input()
        moving = self.apply_input(input_state, dt)

        # Update map (animated tiles)
        if self.current_map:
            self.current_map.update(dt)

        # Check for portal collisions
        self.check_portals()

        # Update remote players animations
        for p in self.players.values():
            if p.current_map == self.local_player.current_map:
                if p.moving:
                    p.update_animation(dt, moving=True)
                    #p.update(dt)  # <-- make sure Player.update(dt) advances animation

        # Send updated position and movement state to server
        self.client.send_move(
            self.local_player.x,
            self.local_player.y,
            self.local_player.direction,
            moving,
            self.scene_manager.server_info["ip"],
            self.scene_manager.server_info["port"]
        )

        if self.current_map:
            map_width = self.current_map.tmx_data.width * self.current_map.tmx_data.tilewidth
            map_height = self.current_map.tmx_data.height * self.current_map.tmx_data.tileheight
            self.camera.update(self.local_player, map_width, map_height)

        if self.current_map and hasattr(self.current_map, "opaque_tiles"):
            colliding = any(self.local_player.rect.colliderect(r) for r in self.current_map.opaque_tiles)

            # Target alpha: 0 when colliding, 180 when not colliding
            target_alpha = 150 if colliding else 255
            fade_speed = 300 * dt  # alpha per second

            if self.current_map.opaque_alpha < target_alpha:
                self.current_map.opaque_alpha = min(target_alpha, self.current_map.opaque_alpha + fade_speed)
            elif self.current_map.opaque_alpha > target_alpha:
                self.current_map.opaque_alpha = max(target_alpha, self.current_map.opaque_alpha - fade_speed)


        self.toasts = [
            t for t in self.toasts if pygame.time.get_ticks() - t["time"] < t["duration"]
        ]

        self.update_world_time(self.server_time)

    def load_map(self, map_name):
        """
        Load a Tiled map from the assets directory.
        
        Args:
            map_name (str): Name of the TMX map file (without .tmx extension)
        """
        if not map_name:
            print("[WARN] Tried to load a map but map_name is None")
            return

        path = f"assets/maps/{map_name}.tmx"
        print(f"[INFO] Loading TMX: {path}")
        self.current_map = game_map.GameMap(path)
        self.map_name = map_name

    def draw(self, surface):
        # Clear screen
        surface.fill((0, 0, 0))

        if not self.current_map:
            text = self.font.render("Waiting for server...", True, (255, 255, 255))
            surface.blit(text, (50, 50))
            return

        # --- Step 1: Make a temp surface the size of the camera viewport ---
        cam_rect = self.camera.rect
        temp_surface = pygame.Surface((cam_rect.width, cam_rect.height), pygame.SRCALPHA)
        ox, oy = cam_rect.x, cam_rect.y 

        # --- Step 2: Draw map with camera offset ---
        self.current_map.draw(temp_surface, offset=(-cam_rect.x, -cam_rect.y),
                      draw_only=["background", "decoration"])

        # --- Step 3: Draw remote players with offset ---
        for p in self.players.values():
            if p.current_map == self.local_player.current_map:
                frame = p.frames[p.direction][p.anim_frame]
                temp_surface.blit(frame, (p.x - cam_rect.x, p.y - cam_rect.y))

        # --- Step 4: Draw local player ---
        frame = self.local_player.frames[self.local_player.direction][self.local_player.anim_frame]
        temp_surface.blit(frame, (self.local_player.x - cam_rect.x, self.local_player.y - cam_rect.y))

        self.current_map.draw(temp_surface, offset=(-cam_rect.x, -cam_rect.y),
                      draw_only=["foreground"])

        # --- Step 6: Draw foreground_opaque with dynamic alpha ---
        self.current_map.draw(temp_surface, offset=(-cam_rect.x, -cam_rect.y),
                            draw_only=["foreground_opaque"],
                            alpha=self.current_map.opaque_alpha)

        
        

        # --- Step 5: Zoom ---
        if self.camera.zoom != 1.0:
            scaled = pygame.transform.scale(
                temp_surface,
                (int(cam_rect.width * self.camera.zoom), int(cam_rect.height * self.camera.zoom))
            )
            surface.blit(scaled, (0, 0))
        else:
            surface.blit(temp_surface, (0, 0))

        


        # --- Step: Apply lighting overlay ---
        alpha = self.get_light_alpha()
        if alpha > 0:
            # Base night overlay
            overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
            overlay.fill((0, 0, 50, alpha))  # night blue

            # Light tiles reduce darkness
            for rect, radius in getattr(self.current_map, "light_tiles", []):
                light_surf = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)

                # Radial gradient: center = brightest, edges = dim
                for r in range(radius, 0, -1):
                    t = r / radius  # 1 at edge, 0 at center
                    fade = int(alpha * ((1 - t) ** 2))  # quadratic: center stronger
                    pygame.draw.circle(
                        light_surf,
                        (0, 0, 0, fade),
                        (radius, radius),
                        r
                    )

                # Subtract from overlay to clear darkness
                overlay.blit(
                    light_surf,
                    (rect.centerx - radius - self.camera.rect.x,
                    rect.centery - radius - self.camera.rect.y),
                    special_flags=pygame.BLEND_RGBA_SUB
                )

            # Apply overlay
            surface.blit(overlay, (0, 0))


        # # Draw light radii
        # for rect, radius in getattr(self.current_map, "light_tiles", []):
        #     light_surf = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)

        #     # Radial gradient for fire-like light
        #     for r in range(radius, 0, -1):
        #         # Quadratic falloff for smooth transparency
        #         alpha = int((r / radius) ** 2 * 80)  # much lower than before (max 80 instead of 180)
        #         color = (255, 140 + int(115*(r/radius)), 0, alpha)  # warm orange-yellow gradient
        #         pygame.draw.circle(light_surf, color, (radius, radius), r)

        #     # Draw with additive blending
        #     surface.blit(
        #         light_surf,
        #         (rect.centerx - radius - ox, rect.centery - radius - oy),
        #         special_flags=pygame.BLEND_ADD
        #         )
        


        # draw toasts in top-right
        y = 10
        for toast in self.toasts:
            surf = self.font.render(toast["text"], True, (255, 255, 255))
            rect = surf.get_rect(topright=(surface.get_width() - 10, y))
            surface.blit(surf, rect)
            y += rect.height + 5

        # Draw world clock (HH:MM only)
        
        time_text = self.font.render(self.world_time, True, (255, 255, 255))
        surface.blit(time_text, (surface.get_width() - time_text.get_width() - 10, 10))




