import pygame
import socket
import threading
import msgpack
from ..entities.player import Player

WIDTH, HEIGHT = 800, 600
MOVE_SPEED = 1
ANIMATION_SPEED = 0.15  # seconds per frame

# class Player:
#     def __init__(self, player_id, name, spritesheet, frame_w, frame_h, x=100, y=100):
#         self.id = player_id
#         self.name = name
#         self.x = x
#         self.y = y
#         self.direction = "down"  # default facing direction
#         self.anim_timer = 0
#         self.anim_frame = 0

#         # Cut spritesheet into frames
#         self.frames = {
#             "down": [],
#             "left": [],
#             "right": [],
#             "up": []
#         }

#         # Assuming sheet has 4 rows (down, left, right, up) and N columns
#         sheet = spritesheet
#         cols = sheet.get_width() // frame_w
#         for row, dir_name in enumerate(["down", "left", "right", "up"]):
#             for col in range(cols):
#                 frame = sheet.subsurface(pygame.Rect(col*frame_w, row*frame_h, frame_w, frame_h))
#                 self.frames[dir_name].append(frame)

#     def move(self, dx, dy, dt):
#         if dx == 0 and dy == 0:
#             self.anim_frame = 0  # reset to standing frame
#             return

#         self.x += dx * MOVE_SPEED
#         self.y += dy * MOVE_SPEED

#         # Set direction
#         if dx > 0: self.direction = "right"
#         if dx < 0: self.direction = "left"
#         if dy > 0: self.direction = "down"
#         if dy < 0: self.direction = "up"

#         # Animate
#         self.anim_timer += dt
#         if self.anim_timer >= ANIMATION_SPEED:
#             self.anim_timer = 0
#             self.anim_frame = (self.anim_frame + 1) % len(self.frames[self.direction])

#     def draw(self, surface):
#         frame = self.frames[self.direction][self.anim_frame]
#         surface.blit(frame, (self.x, self.y))


class GameScene:
    def __init__(self, scene_manager, font):
        self.scene_manager = scene_manager
        self.font = font
        # Load your spritesheet (replace with your file!)
        spritesheet = pygame.image.load("assets/sprites/Swordsman_lvl1_Walk_with_shadow.png").convert_alpha()
        frame_w, frame_h = 64, 64  # change to your sheet frame size
        self.local_player = Player(0, "Local", spritesheet, frame_w, frame_h)
        self.local_player_id = None
        self.players = {}
        self.client_socket = None
        self.connected = False

    def connect_to_server(self, server_ip, server_port):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.client_socket.settimeout(1.0)
        try:
            self.client_socket.sendto(msgpack.packb({"type": "join"}, use_bin_type=True), (server_ip, server_port))
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
                        print(f"[INFO] Assigned player ID: {self.local_player_id}")

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
                                        pygame.image.load("assets/sprites/Swordsman_lvl1_Walk_with_shadow.png").convert_alpha(),
                                        p.get("frame_w", 64),
                                        p.get("frame_h", 64),
                                        p["x"],
                                        p["y"]
                                    )
                                else:
                                    player = self.players[p["id"]]
                                    player.x = p["x"]
                                    player.y = p["y"]
                                    player.direction = p["direction"]
                                    player.moving = p["moving"]
                except socket.timeout:
                    continue
                except Exception as e:
                    print("Connection error:", e)
                    break

        threading.Thread(target=listen_server, daemon=True).start()
        self.connected = True

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

    def update(self, dt):
        if not self.connected:
            return

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
        if self.local_player_id is not None:
            try:
                msg = msgpack.packb({
                    "type": "move",
                    "x": self.local_player.x,
                    "y": self.local_player.y,
                    "direction": self.local_player.direction,
                    "moving": moving
                }, use_bin_type=True)
                self.client_socket.sendto(msg, (self.scene_manager.server_info["ip"],
                                                self.scene_manager.server_info["port"]))
            except:
                pass

        # --- Remote players ---
        for p in self.players.values():
            # Update animation only (position is synced from server)
            p.update_animation(dt, moving=True)

    def draw(self, surface):
        surface.fill((50, 50, 50))
        for p in self.players.values():
            
            p.draw(surface)
        self.local_player.draw(surface)
