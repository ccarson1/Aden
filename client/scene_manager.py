from client.scenes.main_menu import MainMenu
from client.scenes.login_scene import LoginScene
from client.scenes.create_scene import CreateScene
from client.scenes.server_scene import ServerScene
from client.scenes.game_scene import GameScene
from client.network.client import Client
import pygame
import config

class SceneManager:
    def __init__(self, font):
        self.font = font
        WIDTH, HEIGHT = config.WIDTH, config.HEIGHT

        # Initialize network client
        self.client = Client("assets/sprites/Swordsman_lvl1_Walk_with_shadow.png")
        self.client.set_scene_manager(self)

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

    def start_fade(self, scene_name):
        """Begin fade-out before switching to another scene."""
        if scene_name in self.scenes:
            self.next_scene = self.scenes[scene_name]
            self.fading_out = True
            self.fading_in = False
            self.fade_alpha = 0
        else:
            print(f"[WARN] Tried to fade to unknown scene '{scene_name}'")

    def switch_scene(self, scene_name):
        if scene_name in self.scenes:
            self.current_scene = self.scenes[scene_name]

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
        # Handle fade-out
        if self.fading_out:
            self.fade_alpha += self.fade_speed * dt
            if self.fade_alpha >= 255:
                self.fade_alpha = 255
                self.fading_out = False

                # Now switch scenes
                self.current_scene = self.next_scene
                self.next_scene = None
                self.fading_in = True

                # If switching to GameScene, connect to server here
                if isinstance(self.current_scene, GameScene) and self.server_info:
                    if self.login_info:
                        server_ip = self.server_info["ip"]
                        server_port = self.server_info["port"]
                        self.current_scene.connect_to_server(server_ip, server_port)
                    else:
                        print("[WARN] Cannot connect to game scene: no login_info")

        # Handle fade-in
        elif self.fading_in:
            self.fade_alpha -= self.fade_speed * dt
            if self.fade_alpha <= 0:
                self.fade_alpha = 0
                self.fading_in = False

        # Update the current scene
        self.current_scene.update(dt)

    def draw(self, surface):
        """Draw current scene with fade overlay if active."""
        self.current_scene.draw(surface)

        if self.fading_out or self.fading_in:
            fade_surf = pygame.Surface(surface.get_size())
            fade_surf.fill((0, 0, 0))
            fade_surf.set_alpha(int(self.fade_alpha))
            surface.blit(fade_surf, (0, 0))
