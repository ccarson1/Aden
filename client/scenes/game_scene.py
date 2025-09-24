#cleint/scenes/game_scene.py
import pygame
import socket
import threading
import msgpack
from ..entities.player import Player
from ..entities import game_map
from assets.maps.map_loader import TileLayer, load_pygame
from pytmx import TiledTileLayer
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
        #self.map = 'Harbor_01'
        self.map = None
        self.current_map = None

        self.clock = pygame.time.Clock()

        # Load first map
        #self.current_map = game_map.GameMap(f"assets/maps/{self.map}.tmx")

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

    def check_portals(self):
        if not self.current_map:
            return

        # Loop through all portal tiles
        for portal in self.current_map.portal_tiles:  # we'll define portal_tiles in GameMap
            rect = portal['rect']
            if rect.colliderect(self.local_player.rect):
                # Collision detected
                target_map = portal.get('target_map')
                spawn_x = portal.get('spawn_x', 100)
                spawn_y = portal.get('spawn_y', 100)
                
                if target_map:
                    print(f"[INFO] Portal triggered: {target_map} at ({spawn_x}, {spawn_y})")
                    self.map = target_map
                    self.load_map(target_map)

                    # Set player spawn position
                    self.local_player.x = spawn_x
                    self.local_player.y = spawn_y
                    break  # only one portal per update


    def update(self, dt):
        # --- Load map only after server tells us ---
        if self.client.local_player and self.client.local_player.current_map:
            if self.map != self.client.local_player.current_map:
                self.map = self.client.local_player.current_map
                print(f"[INFO] Loading map: {self.map}")
                self.load_map(self.map)

        # --- Only update stuff if map is loaded ---
        if self.current_map:
            # Update animated tiles
            self.current_map.update(dt)

            # Local player movement
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

            self.local_player.move(dx, dy, dt, self.current_map.colliders)
            self.local_player.direction = direction

            # --- Check for portal collisions ---
            if self.current_map and self.local_player:
                player_hitbox = self.local_player.get_hitbox()
                portal = self.current_map.get_portal_at(player_hitbox)
                if portal:
                    print(f"[INFO] Player collided with portal to {portal.target_map} at ({portal.spawn_x},{portal.spawn_y})")

                    # Update local player map and position
                    self.map = portal.target_map
                    self.local_player.current_map = portal.target_map  # important
                    self.local_player.x = portal.spawn_x
                    self.local_player.y = portal.spawn_y
                    self.local_player.rect = self.local_player.get_hitbox()  # update rect after teleport

                    # Load the new map
                    self.load_map(self.map)

                    # Send updated state to server immediately to avoid server overwriting
                    if self.client.local_player_id is not None:
                        self.client.send_move(
                        self.local_player.x,
                        self.local_player.y,
                        self.local_player.direction,
                        False,  # moving
                        self.scene_manager.server_info["ip"],
                        self.scene_manager.server_info["port"]
                    )

            # Send local player state
            if self.client.local_player_id is not None:
                self.client.send_move(
                    self.local_player.x,
                    self.local_player.y,
                    self.local_player.direction,
                    moving,
                    self.scene_manager.server_info["ip"],
                    self.scene_manager.server_info["port"]
                )

            # Update remote players
            for p in self.players.values():
                p.update_animation(dt, moving=True)


    def load_map(self, map_name):
        if not map_name:  # None or empty string
            print("[WARN] Tried to load a map but map_name is None")
            return

        path = f"assets/maps/{map_name}.tmx"
        print(f"[INFO] Loading TMX: {path}")

        # Load TMX data and create GameMap instance
        self.current_map = game_map.GameMap(path)

    def draw(self, surface):
        if self.map is None:
            text = self.font.render("Waiting for server...", True, (255, 255, 255))
            surface.blit(text, (50, 50))
        else:
            surface.fill((0, 0, 0))
            if self.current_map:
                self.current_map.draw(surface)

            for p in self.players.values():
                p.draw(surface)

            if self.local_player:
                self.local_player.draw(surface)
