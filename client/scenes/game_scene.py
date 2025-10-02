

# client/scenes/game_scene.py
import pygame
import time
from ..entities.player import Player
from ..entities import game_map
from client.entities.camera import Camera
from client.entities.world_time import WorldTime
import config
import random
from client.graphics.weather import Rain
from ..ui import toast_manager
from ..tools import tool_utilities
from client.entities.player_controller import PlayerController


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

        # self.frozen = False

        # Time interval for autosaving player state (currently unused)
        self.SAVE_INTERVAL = 30

        # Map references
        self.map = None          # Deprecated, use current_map
        self.current_map = None  # Current active GameMap

        self.toast_manager = toast_manager.ToastManager(None, font)
        

        self.camera = Camera(config.WIDTH, config.HEIGHT, zoom=1.0)
        self.server_time = "00:00:00"
        self.world_time = WorldTime(self.font)
        self.rain = Rain(config.WIDTH, config.HEIGHT, density=350, fall_speed=7, wind=1, drop_length=7, thickness=1, overlay_color=(50, 50, 60), overlay_alpha=120)
        self.tool_utilities = tool_utilities.ToolUtilities()
        self.player_controller = PlayerController(self.local_player)

    


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



    def update(self, dt):
        
        if self.current_map:
            self.current_map.update(dt)
        

        #self.check_portals()

        self.player_controller.update(dt, self.current_map, self.players, self.client, self.scene_manager, self.camera)

        self.toast_manager.update()
        self.world_time.update(self.server_time)


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
        print("[GAME] map loaded, unfreezing player_controller")
        self.player_controller.frozen = False

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



        # --- Step 4: Draw local player and remmote players---
        self.player_controller.draw(temp_surface, cam_rect, self.players)


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
        self.world_time.draw(surface, self.current_map, self.camera)


        # Update + draw rain
        # self.rain.update()
        # self.rain.draw(surface)

        # draw toasts in top-right
        self.toast_manager.draw(surface)





