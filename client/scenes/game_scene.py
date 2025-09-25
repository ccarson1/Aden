

# client/scenes/game_scene.py
import pygame
import time
from ..entities.player import Player
from ..entities import game_map
from client.entities.camera import Camera
import config

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

        # Input history for client-side prediction and reconciliation
        self.input_history = []
        self.camera = Camera(config.WIDTH, config.HEIGHT, zoom=1.0)

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
            
        # if portal:
        #     print(f"[INFO] Portal triggered: {portal.target_map} at ({portal.spawn_x},{portal.spawn_y})")
        #     self.client.send_portal_enter(
        #         portal.target_map,
        #         portal.spawn_x,
        #         portal.spawn_y,
        #         self.scene_manager.server_info["ip"],
        #         self.scene_manager.server_info["port"]
        #     )

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

        # --- Step 2: Draw map with camera offset ---
        self.current_map.draw(temp_surface, offset=(-cam_rect.x, -cam_rect.y))

        # --- Step 3: Draw remote players with offset ---
        for p in self.players.values():
            if p.current_map == self.local_player.current_map:
                frame = p.frames[p.direction][p.anim_frame]
                temp_surface.blit(frame, (p.x - cam_rect.x, p.y - cam_rect.y))

        # --- Step 4: Draw local player ---
        frame = self.local_player.frames[self.local_player.direction][self.local_player.anim_frame]
        temp_surface.blit(frame, (self.local_player.x - cam_rect.x, self.local_player.y - cam_rect.y))

        # --- Step 5: Zoom ---
        if self.camera.zoom != 1.0:
            scaled = pygame.transform.scale(
                temp_surface,
                (int(cam_rect.width * self.camera.zoom), int(cam_rect.height * self.camera.zoom))
            )
            surface.blit(scaled, (0, 0))
        else:
            surface.blit(temp_surface, (0, 0))




