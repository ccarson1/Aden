#client/network/client.py
import socket, threading, msgpack
import pygame
from ..entities.player import Player

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

                        # Load initial position from server
                        if "player_data" in message:
                            data = message["player_data"]
                            self.local_player.x = data.get("x", 100)
                            self.local_player.y = data.get("y", 100)
                            self.local_player.direction = data.get("direction", "down")

                            # NEW: load map
                            if "current_map" in data:
                                print(f"[INFO] Loading map: {data['current_map']}")
                                self.local_player.current_map = data["current_map"]

                                # Instead of trying to use scene_manager here,
                                # just store it locally in the client.
                                self.current_map = data["current_map"]

                        print(f"[INFO] Assigned player ID: {self.local_player_id} at ({self.local_player.x}, {self.local_player.y})")

                    elif message["type"] == "update":
                        for p in message["players"]:
                            if p["id"] == self.local_player_id:
                                self.local_player.x = p["x"]
                                self.local_player.y = p["y"]
                                self.local_player.direction = p["direction"]
                                self.local_player.moving = p["moving"]
                            else:
                                if p["id"] not in self.players:
                                    self.players[p["id"]] = Player(
                                        p["id"], p["name"],
                                        pygame.image.load(self.player_sprite_path).convert_alpha(),
                                        p.get("frame_w", self.frame_w),
                                        p.get("frame_h", self.frame_h),
                                        p["x"], p["y"]
                                    )
                                else:
                                    player = self.players[p["id"]]
                                    player.x = p["x"]
                                    player.y = p["y"]
                                    player.direction = p["direction"]
                                    player.moving = p["moving"]

                    elif message["type"] == "player_disconnect":
                        pid = message["player_id"]
                        if pid in self.players:
                            print(f"[CLIENT] Removing disconnected player {pid}")
                            del self.players[pid]

                except socket.timeout:
                    continue
                except Exception as e:
                    print("Connection error:", e)
                    break

        threading.Thread(target=listen_server, daemon=True).start()

    def send_move(self, x, y, direction, moving, server_ip, server_port):
        if not self.token:
            return
        msg = {
            "type": "move",
            "x": x,
            "y": y,
            "direction": direction,
            "moving": moving,
            "token": self.token
        }
        self.client_socket.sendto(msgpack.packb(msg, use_bin_type=True), (server_ip, server_port))
