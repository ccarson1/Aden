import pygame
from client.scenes.main_menu import MainMenu
from client.scenes.login_scene import LoginScene
from client.scenes.create_scene import CreateScene
from client.scenes.server_scene import ServerScene
from client.scenes.game_scene import GameScene  # Later integrate your game_scene

pygame.init()


# Create a font instance to pass to UI elements
FONT_SIZE = 32
MAIN_FONT = pygame.font.SysFont(None, FONT_SIZE)

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("UDP Multiplayer Game")

class SceneManager:
    def __init__(self, font):
        self.font = font  # store it if needed by scenes
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

scene_manager = SceneManager(MAIN_FONT)
clock = pygame.time.Clock()

running = True
while running:
    dt = clock.tick(60) / 1000
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        scene_manager.current_scene.handle_event(event)

    scene_manager.current_scene.update(dt)
    scene_manager.current_scene.draw(screen)
    pygame.display.flip()

pygame.quit()
