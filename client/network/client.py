 #client/network/client.py
import socket, threading, msgpack
import pygame
from ..entities.player import Player
from ..entities import game_map
import config
import time


class Client:
    def __init__(self, player_sprite_path, anim_meta, frame_w=64, frame_h=64):
        self.token = None
        self.client_socket = None
        self.local_player_id = None
        self.local_player = Player(0, "Local", pygame.image.load(player_sprite_path).convert_alpha(), anim_meta=anim_meta)
        # Debug: check attack frames for each direction
        for dir in ["up", "down", "left", "right"]:
            print(f"{dir}-attack frames:", len(self.local_player.frames.get(f"{dir}-attack", [])))
        self.players = {}
        self.player_sprite_path = player_sprite_path
        self.frame_w = frame_w
        self.frame_h = frame_h
        self.scene_manager = None
        self.anim_meta = anim_meta


    def connect(self, server_ip, server_port, token):
        self.token = token

        # Use passed values or fallback to config
        ip = server_ip if server_ip else config.HOST
        port = server_port if server_port else config.PORT

        if self.client_socket is None:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.client_socket.settimeout(1.0)

        try:
            self.client_socket.sendto(
                msgpack.packb({"type": "join", "token": token}, use_bin_type=True),
                (ip, port)
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
                            print(f"[CLIENT] Assigned Player ID: {self.local_player_id} with data: {data}")
                            self.local_player.name = data.get("name", self.local_player.name)
                            self.local_player.x = data.get("x", 100)
                            self.local_player.y = data.get("y", 100)
                            self.local_player.direction = data.get("direction", "down")
                            self.local_player.z_index = data.get("z_index", 0)
                            self.local_player.class_type = data.get("class_type", "mage")
                            print(f"[CLIENT] Character Name: {self.local_player.name}, Class Type: {self.local_player.class_type}")
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
                                        p["x"],
                                        p["y"]
                                    )
                                    player.class_type = p.get("class_type", "mage")
                                    player.render_x = p["x"]
                                    player.render_y = p["y"]
                                    # There is no Default map (I002)
                                    player.current_map = p.get("current_map", "DefaultMap")
                                    self.players[p["id"]] = player


                    elif message["type"] == "update":
                        for p in message["players"]:
                            #print(f"[DEBUG RECV] Player {p['id']} | pos=({p['x']},{p['y']}) moving={p.get('moving')} running={p.get('running')} direction={p.get('direction')} attacking={p.get('attacking')}")

                            if p["id"] == self.local_player_id:
                                # Store server authoritative position
                                self.local_player.server_x = p["x"]
                                self.local_player.server_y = p["y"]
                                self.local_player.direction = p["direction"]
                                self.local_player.moving = p["moving"]
                                self.local_player.current_map = p.get("current_map", self.local_player.current_map)
                                self.local_player.z_index = p.get("z_index", getattr(self.local_player, "z_index", 0))
                                self.scene_manager.scenes["game"].server_time = message["world_time"]
                                
                                
                            else:
                                if p["id"] not in self.players:
                                    player = Player(
                                        p["id"], 
                                        p["name"],
                                        pygame.image.load(self.player_sprite_path).convert_alpha(),
                                        self.anim_meta,
                                        p["x"], 
                                        p["y"]
                                    )
                                    player.render_x = p["x"]
                                    player.render_y = p["y"]
                                    # There is no Default map (I002)
                                    player.current_map = p.get("current_map", "DefaultMap")
                                    player.z_index = p.get("z_index", 0) 
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
                                    player.attack_direction = p["direction"]
                                    player.moving = p["moving"]
                                    player.current_map = p.get("current_map", player.current_map)
                                    player.z_index = p.get("z_index", getattr(player, "z_index", 0))
                                    player.attacking = p.get("attacking", False)
                                    player.running = p.get("running", False)

                                    if p.get('running'):
                                        print(f"[SERVER UPDATE] Player {p['id']}: moving={p.get('moving')} running={p.get('running')}")

                            
                        # --- Sync enemies (if server sent them) ---
                        if "enemies" in message and self.scene_manager and self.scene_manager.current_scene:
                            game_scene = self.scene_manager.scenes.get("game", self.scene_manager.current_scene)
                            ec = getattr(game_scene, "enemy_controller", None)
                            if ec is not None:
                                for e in message["enemies"]:
                                    eid = e.get("id")
                                    if eid is None:
                                        continue
                                    
                                    enemy_data = {
                                        "x": e.get("x", 0),
                                        "y": e.get("y", 0),
                                        "rows": e.get("rows", 1),
                                        "columns": e.get("columns", 11),
                                        "type": e.get("type", "green-slime"),
                                        "current_map": e.get("current_map", "Test_01"),
                                        "hp": e.get("hp", 10),
                                        "speed": e.get("speed", 100.0),
                                        "frame_speed": e.get("frame_speed", 0.12),
                                        "directions": e.get("directions", ["down"]),
                                        "z_index": e.get("z_index", 0),
                                        "c_h_padding": e.get("c_h_padding", 0),
                                        "c_v_padding": e.get("c_v_padding", 0),
                                        "moving": e.get("moving", True),
                                    }

                                    if eid not in ec.enemies:
                                        ec.add_enemy(eid, enemy_data)  # pass a dict now

                                    try:
                                        ec.enemies[eid].apply_server_update(e)
                                    except Exception as exc:
                                        print(f"[CLIENT] Failed to apply server update to enemy {eid}: {exc}")

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


                        # Start fade and provide portal info for spawn
                        self.scene_manager.start_fade("game")
                        print("[CLIENT] start_fade called")

                        # Once fade completes, load the map
                        self.scene_manager.on_map_data_received(message["map"])
                        print("[CLIENT] on_map_data_received called")
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

    def send_move(self, x, y, direction, moving, server_ip, server_port, attacking):
        if not self.token:
            return
        msg = {
            "type": "move",
            "x": x,
            "y": y,
            "direction": direction,
            "moving": moving,
            "current_map": self.local_player.current_map,
            "z_index": self.local_player.z_index,
            "token": self.token,
            "attacking": self.local_player.attacking,
            "running": self.local_player.running
        }
        if self.local_player.running:
            print(f"[DEBUG SEND] x={x:.1f} y={y:.1f} dir={direction} moving={moving} running={self.local_player.running} attacking={self.local_player.attacking}")

        self.client_socket.sendto(msgpack.packb(msg, use_bin_type=True), (server_ip, server_port))

    def set_scene_manager(self, scene_manager):
        self.scene_manager = scene_manager
