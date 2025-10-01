

# client/scenes/game_scene.py
import pygame
import time
from ..entities.player import Player
from ..entities import game_map
from client.entities.camera import Camera
import config
import random
from client.graphics.weather import Rain
from ..ui import toast_manager
from ..tools import tool_utilities

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

        self.toast_manager = toast_manager.ToastManager(None, font)
        

        # Input history for client-side prediction and reconciliation
        self.input_history = []
        self.camera = Camera(config.WIDTH, config.HEIGHT, zoom=1.0)
        self.server_time = "00:00:00"
        self.world_time = "00:00"
        self.rain = Rain(config.WIDTH, config.HEIGHT, density=350, fall_speed=7, wind=1, drop_length=7, thickness=1, overlay_color=(50, 50, 60), overlay_alpha=120)
        self.tool_utilities = tool_utilities.ToolUtilities()

    def load(self, map_name=None):
        """
        Load heavy assets or maps AFTER fade-out finishes.
        """
        if map_name:
            path = f"assets/maps/{map_name}.tmx"
            print(f"[INFO] Loading TMX AFTER FADE: {path}")
            self.current_map = game_map.GameMap(path)
            self.map_name = map_name


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
            #self.print_click_position(event.pos)
            self.tool_utilities.print_click_position(event.pos, self.camera.rect)

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
        
    def update_render_position(self, player, server_rate=20):
        """Interpolate remote players between last known positions."""
        now = time.time()
        elapsed = now - player.last_update_time
        interval = 1.0 / server_rate
        t = min(1.0, elapsed / interval)
        player.render_x = player.prev_x + (player.target_x - player.prev_x) * t
        player.render_y = player.prev_y + (player.target_y - player.prev_y) * t

    def update_remote_players(self, dt):
        """
        Smoothly interpolate all remote players toward their server-reported target positions.
        """
        for player in self.client.players.values():
            # Initialize render positions if they don't exist
            if not hasattr(player, "render_x"):
                player.render_x = player.x
                player.render_y = player.y

            # Initialize target positions if missing
            if not hasattr(player, "target_x"):
                player.target_x = player.x
            if not hasattr(player, "target_y"):
                player.target_y = player.y

            # Interpolation speed (units per second)
            speed = getattr(player, "speed", 200.0)

            # Compute distance to target
            dx = player.target_x - player.render_x
            dy = player.target_y - player.render_y
            dist = (dx**2 + dy**2)**0.5

            if dist > 0:
                move_dist = min(dist, speed * dt)
                player.render_x += dx / dist * move_dist
                player.render_y += dy / dist * move_dist



    def update(self, dt):
        if self.frozen:
            if self.current_map:
                self.current_map.update(dt)
            return

        input_state = self.capture_input()
        moving = self.apply_input(input_state, dt)

        if self.current_map:
            self.current_map.update(dt)

        self.check_portals()

        # --- Interpolate local player towards server ---
        if hasattr(self.local_player, "server_x"):
            dx = self.local_player.server_x - self.local_player.x
            dy = self.local_player.server_y - self.local_player.y
            dist = (dx**2 + dy**2)**0.5

            # Snap only if extremely out of sync
            max_snap = 64
            if dist > max_snap:
                self.local_player.x = self.local_player.server_x
                self.local_player.y = self.local_player.server_y
            else:
                # Smoothly nudge towards server position
                correction_factor = 0.1  # tweak 0.1~0.3 for snappiness
                self.local_player.x += dx * correction_factor
                self.local_player.y += dy * correction_factor

        # --- Remote players ---
        self.update_remote_players(dt)  # interpolate all remote players
        for p in self.players.values():
            if p.current_map == self.local_player.current_map and p.moving:
                p.update_animation(dt, moving=True)

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


        self.toast_manager.update()
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
            if p.current_map != self.local_player.current_map:
                continue  # skip players in other maps

            # Interpolate remote players


            frame = p.frames[p.direction][p.anim_frame]

            draw_x = getattr(p, "render_x", p.x)
            draw_y = getattr(p, "render_y", p.y)

            temp_surface.blit(frame, (draw_x - cam_rect.x, draw_y - cam_rect.y))

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

        # Update + draw rain
        # self.rain.update()
        # self.rain.draw(surface)

        # draw toasts in top-right
        self.toast_manager.draw(surface)


        # Draw world clock (HH:MM only)
        
        time_text = self.font.render(self.world_time, True, (255, 255, 255))
        surface.blit(time_text, (surface.get_width() - time_text.get_width() - 10, 10))




