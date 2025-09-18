import pygame
import socket
import threading
import msgpack
from ..entities.player import Player
from assets.maps.map_loader import MapLoader
from ..network.client import Client


class GameScene:
    def __init__(self, scene_manager, font):
        self.scene_manager = scene_manager
        self.font = font
        spritesheet_path = "assets/sprites/Swordsman_lvl1_Walk_with_shadow.png"
        self.client = Client(spritesheet_path)
        self.local_player = self.client.local_player
        self.players = self.client.players

        # Load first map
        self.current_map = MapLoader("assets/maps/Test_01.tmx")

    def connect_to_server(self, ip, port):
            token = self.scene_manager.login_info["token"]  # get the token
            self.client.connect(ip, port, token)  # now pass token!

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

    def update(self, dt):

        # --- Local player movement ---
        keys = pygame.key.get_pressed()
        dx = dy = 0
        moving = False
        direction = self.local_player.direction

        if keys[pygame.K_w]:
            dy = -1; direction = "up"; moving = True
        if keys[pygame.K_s]:
            dy = 1; direction = "down"; moving = True
        if keys[pygame.K_a]:
            dx = -1; direction = "left"; moving = True
        if keys[pygame.K_d]:
            dx = 1; direction = "right"; moving = True

        self.local_player.move(dx, dy, dt)
        self.local_player.direction = direction

        # Send local player state to server
        if self.client.local_player_id is not None:
            self.client.send_move(
                self.local_player.x,
                self.local_player.y,
                self.local_player.direction,
                moving,
                self.scene_manager.server_info["ip"],
                self.scene_manager.server_info["port"]
            )

        # --- Remote players ---
        for p in self.players.values():
            # Update animation only (position is synced from server)
            p.update_animation(dt, moving=True)

    def load_map(self, map_name):
        self.current_map = MapLoader(f"assets/maps/{map_name}.tmx")

    def draw(self, surface):
        surface.fill((0, 0, 0))
        self.current_map.draw(surface)
        for p in self.players.values():
            
            p.draw(surface)
        self.local_player.draw(surface)
