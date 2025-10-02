#client/network/client.py
import socket, threading, msgpack
import pygame
from ..entities.player import Player
from ..entities import game_map
import config
import time


class Client:
    def __init__(self, player_sprite_path, frame_w=64, frame_h=64):
        self.token = None
        self.client_socket = None
        self.local_player_id = None
        self.local_player = Player(0, "Local", pygame.image.load(player_sprite_path).convert_alpha(), frame_w, frame_h)
        self.players = {}
        self.player_sprite_path = player_sprite_path
        self.frame_w = frame_w
        self.frame_h = frame_h
        self.scene_manager = None
        


    def connect(self, server_ip, server_port, token):
        self.token = token 
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.client_socket.settimeout(1.0)
        try:
            # Include token in join request
            self.client_socket.sendto(
                msgpack.packb({"type": "join", "token": token}, use_bin_type=True),
                (server_ip, server_port)
            )
        except Exception as e:
            print("Failed to send join:", e)
            return

        def listen_server():
            while True:
                try:
                    data, _ = self.client_socket.recvfrom(4096)
                    message = msgpack.unpackb(data, raw=False)

                    if message["type"] == "assign_id":
                        self.local_player_id = message["player_id"]
                        self.local_player.id = self.local_player_id
                        if "player_data" in message:
                            data = message["player_data"]
                            self.local_player.x = data.get("x", 100)
                            self.local_player.y = data.get("y", 100)
                            self.local_player.direction = data.get("direction", "down")
                            if "current_map" in data:
                                self.local_player.current_map = data["current_map"]
                                # Tell GameScene to load it
                                if hasattr(self.scene_manager.scenes["game"], "load_map"):
                                    self.scene_manager.scenes["game"].load_map(data["current_map"])

                        if "players" in message:
                            for p in message["players"]:
                                if p["id"] != self.local_player_id and p["id"] not in self.players:
                                    player = Player(
                                        p["id"],
                                        p["name"],
                                        pygame.image.load(self.player_sprite_path).convert_alpha(),
                                        p.get("frame_w", self.frame_w),
                                        p.get("frame_h", self.frame_h),
                                        p["x"],
                                        p["y"]
                                    )
                                    player.render_x = p["x"]
                                    player.render_y = p["y"]
                                    player.current_map = p.get("current_map", "DefaultMap")
                                    self.players[p["id"]] = player


                    elif message["type"] == "update":
                        for p in message["players"]:
                            if p["id"] == self.local_player_id:
                                # Store server authoritative position
                                self.local_player.server_x = p["x"]
                                self.local_player.server_y = p["y"]
                                self.local_player.direction = p["direction"]
                                self.local_player.moving = p["moving"]
                                self.local_player.current_map = p.get("current_map", self.local_player.current_map)
                                self.scene_manager.scenes["game"].server_time = message["world_time"]
                            else:
                                if p["id"] not in self.players:
                                    player = Player(
                                        p["id"], 
                                        p["name"],
                                        pygame.image.load(self.player_sprite_path).convert_alpha(),
                                        p.get("frame_w", self.frame_w),
                                        p.get("frame_h", self.frame_h),
                                        p["x"], 
                                        p["y"]
                                    )
                                    player.render_x = p["x"]
                                    player.render_y = p["y"]
                                    player.current_map = p.get("current_map", "DefaultMap")
                                    self.players[p["id"]] = player
                                else:
                                    player = self.players[p["id"]]

                                    # **If map changed, snap immediately**
                                    if player.current_map != p.get("current_map", player.current_map):
                                        player.render_x = p["x"]
                                        player.render_y = p["y"]
                                        player.prev_x = p["x"]
                                        player.prev_y = p["y"]
                                    else:
                                        # Normal interpolation
                                        player.prev_x = player.render_x
                                        player.prev_y = player.render_y

                                    # Update interpolation targets
                                    player.prev_x = player.render_x
                                    player.prev_y = player.render_y
                                    player.target_x = p["x"]
                                    player.target_y = p["y"]
                                    player.last_update_time = time.time()
                                    player.direction = p["direction"]
                                    player.moving = p["moving"]
                                    player.current_map = p.get("current_map", player.current_map)

                    elif message["type"] == "player_disconnect":
                        pid = message["player_id"]
                        if pid in self.players:
                            print(f"[CLIENT] Removing disconnected player {pid}")
                            del self.players[pid]

                    elif message["type"] == "map_switch":
                        self.local_player.current_map = message["map"]
                        self.local_player.x = message["x"]
                        self.local_player.y = message["y"]

                        # Reset interpolation to avoid sliding
                        self.local_player.prev_x = self.local_player.x
                        self.local_player.prev_y = self.local_player.y
                        self.local_player.target_x = self.local_player.x
                        self.local_player.target_y = self.local_player.y
                        self.local_player.last_update_time = time.time()

                        # Freeze the player during fade
                        print("[CLIENT] Received map_switch:", message)
                        self.scene_manager.current_scene.player_controller.frozen = True
                        
                        print("[CLIENT] Set frozen True on current_scene")

                        self.scene_manager.start_fade("game")
                        print("[CLIENT] start_fade called")

                        self.scene_manager.on_map_data_received(message["map"])
                        print("[CLIENT] on_map_data_received called")

                        # Start fade and provide portal info for spawn
                        self.scene_manager.start_fade("game")

                        # Once fade completes, load the map
                        self.scene_manager.on_map_data_received(message["map"])
                        #self.scene_manager.scenes["game"].player_controller.frozen = False


                        print(f"[INFO] Map switch requested: {message['map']} at ({message['x']}, {message['y']})")

                    elif message["type"] == "save_confirm":
                        print(f"[SERVER] {message['message']}")
                        if self.scene_manager and "game" in self.scene_manager.scenes:
                            game_scene = self.scene_manager.scenes["game"]
                            
                            game_scene.toast_manager.add_toast(message["message"])

                except socket.timeout:
                    continue
                except Exception as e:
                    print("Connection error:", e)
                    break

        threading.Thread(target=listen_server, daemon=True).start()

    def send_portal_enter(self, target_map, spawn_x, spawn_y, server_ip, server_port):
        msg = {
            "type": "portal_enter",
            "target_map": target_map,
            "spawn_x": spawn_x,
            "spawn_y": spawn_y,
            "token": self.token
        }
        self.client_socket.sendto(msgpack.packb(msg, use_bin_type=True), (server_ip, server_port))

    def send_move(self, x, y, direction, moving, server_ip, server_port):
        if not self.token:
            return
        msg = {
            "type": "move",
            "x": x,
            "y": y,
            "direction": direction,
            "moving": moving,
            "current_map": self.local_player.current_map,
            "token": self.token
        }
        self.client_socket.sendto(msgpack.packb(msg, use_bin_type=True), (server_ip, server_port))

    def set_scene_manager(self, scene_manager):
        self.scene_manager = scene_manager
