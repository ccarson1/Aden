from client.scenes.main_menu import MainMenu
from client.scenes.login_scene import LoginScene
from client.scenes.create_scene import CreateScene
from client.scenes.server_scene import ServerScene
from client.scenes.game_scene import GameScene  # Later integrate your game_scene
import config

class SceneManager:
    def __init__(self, font):
        self.font = font  # store it if needed by scenes
        WIDTH, HEIGHT = config.WIDTH, config.HEIGHT
        self.scenes = {
            "main_menu": MainMenu(self, font, WIDTH, HEIGHT),
            "login": LoginScene(self, font, WIDTH, HEIGHT),
            "create": CreateScene(self, font, WIDTH, HEIGHT),
            "server": ServerScene(self, font, WIDTH, HEIGHT),
            "game": GameScene(self, font)
        }
        self.current_scene = self.scenes["main_menu"]
        self.login_info = None
        self.create_info = None
        self.server_info = None

    def switch_scene(self, name):
        self.current_scene = self.scenes[name]

        if name == "game":
            # Make sure you call connect_to_server once
            server_ip = self.server_info["ip"]
            server_port = self.server_info["port"]
            self.current_scene.connect_to_server(server_ip, server_port)