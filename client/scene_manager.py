from client.scenes.main_menu import MainMenu
from client.scenes.login_scene import LoginScene
from client.scenes.create_scene import CreateScene
from client.scenes.server_scene import ServerScene
from client.scenes.game_scene import GameScene
from client.network.client import Client
from client.network.network import NetworkClient
from client.ui.game_cursor import GameCursor
import pygame
import config

class SceneManager:
    def __init__(self, font, screen):
        self.font = font
        self.screen = screen
        WIDTH, HEIGHT = config.WIDTH, config.HEIGHT
        self.game_cursor = GameCursor()

        anim_meta = {
            "direction_row": {
                "down": 10,
                "up": 8,
                "left": 9,
                "right": 11,
                "down-running": 40,
                "up-running": 38,
                "left-running": 39,
                "right-running": 41,
                "down-idle": 24,
                "up-idle": 22,
                "left-idle": 23,
                "right-idle": 25,
                "down-attack": 37,
                "up-attack": 35,
                "left-attack": 36,
                "right-attack": 38,
                "down-longAttack": 33,
                "up-longAttack": 31,
                "left-longAttack": 32,
                "right-longAttack": 34,
                "down-jumping": 28,
                "up-jumping": 26,
                "left-jumping": 27,
                "right-jumping": 29

            },
            "idle-cols": 2,
            "move-cols": 9,
            "attack-cols": 6,
            "longAttack-cols": 13,
            "running-cols": 8,
            "jumping-cols": 5,
            "idle-width": 48,
            "idle-height": 48,
            "move-width": 48,
            "move-height": 48,
            "attack-width": 96,
            "attack-height": 96,
            "skip_frames": {
                "down": 1,
                "left": 1,
                "right": 1,
                "up": 1
            },
            "anim_speeds": {
                "default": 0.2,
                "-idle": 0.35,
                "-attack": 0.06,
                "-longAttack": 0.03,
                "-running": 0.1,
                "-jumping": 2.45,
            },
            "anim_offsets": {
                "down-attack": (-19, -28),
                "up-attack": (-19, -28),
                "left-attack": (-19, -28),
                "right-attack": (-19, -28),
                "down-longAttack": (-19, -28),
                "up-longAttack": (-19, -28),
                "left-longAttack": (-19, -28),
                "right-longAttack": (-19, -28),
                "down": (0, 0),
                "up": (0, 0),
                "left": (0, 0),
                "right": (0, 0),
                "down-idle": (0, 0),
                "up-idle": (0, 0),
                "left-idle": (0, 0),
                "right-idle": (0, 0),
            }
        }

        # Initialize network client
        self.client = Client("assets/sprites/character-spritesheet-2.png", anim_meta)
        self.client.set_scene_manager(self)

        # Initialize the network client once
        self.network = NetworkClient()
        self.current_scene = None

        # Server info
        self.server_info = {"ip": config.HOST, "port": config.PORT}

        # Login/create info
        self.login_info = None
        self.create_info = None

        # Scenes
        self.scenes = {
            "main_menu": MainMenu(self, font, WIDTH, HEIGHT),
            "login": LoginScene(self, font, WIDTH, HEIGHT),
            "create": CreateScene(self, font, WIDTH, HEIGHT),
            "server": ServerScene(self, font, WIDTH, HEIGHT),
            "game": GameScene(self, font, self.client)
        }

        self.current_scene = self.scenes["main_menu"]
        self.next_scene = None

        # Fade variables
        self.fading_out = False
        self.fading_in = False
        self.fade_alpha = 0
        self.fade_speed = 400  # alpha per second


    def start_fade(self, scene_name, portal=None):
        if scene_name in self.scenes:
            self.next_scene = self.scenes[scene_name]
            self.pending_portal = portal  # store for later
            self.fading_out = True
            self.fading_in = False
            self.fade_alpha = 0
        else:
            print(f"[WARN] Tried to fade to unknown scene '{scene_name}'")

    def switch_scene(self, scene_name):
        if scene_name in self.scenes:
            self.current_scene = self.scenes[scene_name]

            # Update InputBox text when activating the scene
            if hasattr(self.current_scene, "on_activate"):
                self.current_scene.on_activate()

            # If switching to GameScene, connect to server
            if isinstance(self.current_scene, GameScene) and self.server_info:
                if self.login_info:  # <-- use self.login_info
                    server_ip = self.server_info["ip"]
                    server_port = self.server_info["port"]
                    self.current_scene.connect_to_server(server_ip, server_port)
                else:
                    print("[WARN] Cannot connect to game scene: no login_info")

        else:
            print(f"[WARN] Tried to switch to unknown scene '{scene_name}'")

    def update(self, dt):
        # Fade out
        if self.fading_out:
            self.fade_alpha += self.fade_speed * dt
            if self.fade_alpha >= 255:
                self.fade_alpha = 255
                self.fading_out = False

                # Switch to the next scene
                self.current_scene = self.next_scene
                self.next_scene = None

                # If GameScene, freeze until map loads
                if isinstance(self.current_scene, GameScene):
                    self.current_scene.frozen = True
                    if self.pending_portal:
                        portal = self.pending_portal
                        self.current_scene.client.send_portal_enter(
                            portal.target_map,
                            portal.spawn_x,
                            portal.spawn_y,
                            self.server_info["ip"],
                            self.server_info["port"]
                        )
                        self.current_scene.local_player.z_index = portal.player_index
                        self.pending_portal = None

                # Start fade-in immediately
                self.fading_in = True
                self.fade_alpha = 255

        # Fade in
        elif self.fading_in:
            self.fade_alpha -= self.fade_speed * dt
            if self.fade_alpha <= 0:
                self.fade_alpha = 0
                self.fading_in = False

        # Update scene only when not completely black (or always, depends on design)
        self.current_scene.update(dt)


    def on_map_data_received(self, map_name):
        """Called by the network client when the server sends map data."""
        if isinstance(self.current_scene, GameScene):
            self.current_scene.load_map(map_name)   # load TMX file
            self.current_scene.frozen = False       # let the player move again

            #Initialize the camera position immediately after map load
            player = self.current_scene.local_player
            print(f"player x {player.x} : y {player.y}")
            cam = self.current_scene.camera
            map_width = self.current_scene.current_map.tmx_data.width * self.current_scene.current_map.tmx_data.tilewidth
            map_height = self.current_scene.current_map.tmx_data.height * self.current_scene.current_map.tmx_data.tileheight
            cam.rect.center = player.rect.center
            cam.rect.clamp_ip(pygame.Rect(0, 0, map_width, map_height))
            cam.initialized = False

        self.blackout = False
        self.fading_in = True
        self.fade_alpha = 255

    def draw(self, surface):
        # Draw the current scene always
        self.current_scene.draw(surface)

        # Overlay fade
        fade_surf = pygame.Surface(surface.get_size())
        fade_surf.fill((0, 0, 0))
        fade_surf.set_alpha(int(self.fade_alpha))
        surface.blit(fade_surf, (0, 0))
