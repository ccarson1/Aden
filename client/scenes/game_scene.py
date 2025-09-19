#cleint/scenes/game_scene.py
import pygame
import socket
import threading
import msgpack
from ..entities.player import Player
from assets.maps.map_loader import MapLoader
from ..network.client import Client
import time


class GameScene:
    def __init__(self, scene_manager, font):
        self.scene_manager = scene_manager
        self.font = font
        spritesheet_path = "assets/sprites/Swordsman_lvl1_Walk_with_shadow.png"
        self.client = Client(spritesheet_path)
        self.local_player = self.client.local_player
        self.players = self.client.players
        self.SAVE_INTERVAL = 30  
        self.map = 'Test_01'

        # Load first map
        self.current_map = MapLoader(f"assets/maps/{self.map}.tmx")

    def connect_to_server(self, ip, port):
            token = self.scene_manager.login_info["token"]  # get the token
            self.client.connect(ip, port, token)  # now pass token!
            self.start_auto_save(self.client, ip, port, token)

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

    def start_auto_save(self, client, server_ip, server_port, token):
        def save_loop():
            while True:
                time.sleep(self.SAVE_INTERVAL)
                player = self.local_player  # always get the latest reference
                if player is None:
                    continue
                msg = {
                    "type": "save",
                    "token": token,
                    "x": player.x,
                    "y": player.y,
                    "direction": player.direction,
                    "current_map": self.map
                }
                client.client_socket.sendto(msgpack.packb(msg, use_bin_type=True), (server_ip, server_port))

        threading.Thread(target=save_loop, daemon=True).start()

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
