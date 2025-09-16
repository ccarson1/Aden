# import pygame
# import socket
# import threading
# import msgpack

# # --- Constants ---
# WIDTH, HEIGHT = 800, 600
# PLAYER_SIZE = 50
# MOVE_SPEED = 5
# FONT_SIZE = 32

# # --- Player class ---
# class Player:
#     def __init__(self, player_id, name, x=100, y=100):
#         self.id = player_id
#         self.name = name
#         self.x = x
#         self.y = y

# # --- Networking ---
# local_player = Player(0, "Local")
# local_player_id = None
# players = {}  # other players
# client_socket = None

# # --- Pygame setup ---
# pygame.init()
# screen = pygame.display.set_mode((WIDTH, HEIGHT))
# pygame.display.set_caption("UDP Multiplayer Game - Connect Menu")
# clock = pygame.time.Clock()
# font = pygame.font.SysFont(None, FONT_SIZE)

# # --- Input box ---
# def input_box(prompt, default=""):
#     user_text = default
#     active = True
#     while active:
#         screen.fill((50, 50, 50))
#         text_surface = font.render(f"{prompt}: {user_text}", True, (255, 255, 255))
#         screen.blit(text_surface, (50, HEIGHT//2))
#         pygame.display.flip()

#         for event in pygame.event.get():
#             if event.type == pygame.QUIT:
#                 pygame.quit()
#                 exit()
#             elif event.type == pygame.KEYDOWN:
#                 if event.key == pygame.K_RETURN:
#                     return user_text
#                 elif event.key == pygame.K_BACKSPACE:
#                     user_text = user_text[:-1]
#                 else:
#                     user_text += event.unicode

# # --- Listen for server broadcasts ---
# def listen_server():
#     global players, local_player_id
#     while True:
#         try:
#             data, _ = client_socket.recvfrom(4096)
#             message = msgpack.unpackb(data, raw=False)

#             if message["type"] == "assign_id":
#                 local_player_id = message["player_id"]
#                 local_player.id = local_player_id
#                 print(f"[INFO] Assigned player ID: {local_player_id}")

#             elif message["type"] == "update":
#                 new_players = {}
#                 for p in message["players"]:
#                     if local_player_id is not None and p["id"] == local_player_id:
#                         local_player.x = p["x"]
#                         local_player.y = p["y"]
#                     else:
#                         new_players[p["id"]] = Player(p["id"], p["name"], p["x"], p["y"])
#                 players = new_players
#         except socket.timeout:
#             continue
#         except Exception as e:
#             print("Connection error:", e)
#             break

# # --- --- MAIN MENU --- ---
# server_ip = input_box("Enter server IP", "127.0.0.1")
# server_port_str = input_box("Enter server port", "50880")
# server_port = int(server_port_str)

# # --- Connect to server ---
# client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# client_socket.settimeout(1.0)
# client_socket.sendto(msgpack.packb({"type": "join"}, use_bin_type=True), (server_ip, server_port))

# # Start listener thread
# threading.Thread(target=listen_server, daemon=True).start()

# # --- MAIN GAME LOOP ---
# running = True
# while running:
#     dt = clock.tick(60) / 1000
#     for event in pygame.event.get():
#         if event.type == pygame.QUIT:
#             running = False

#     # Movement
#     keys = pygame.key.get_pressed()
#     if keys[pygame.K_w]: local_player.y -= MOVE_SPEED
#     if keys[pygame.K_s]: local_player.y += MOVE_SPEED
#     if keys[pygame.K_a]: local_player.x -= MOVE_SPEED
#     if keys[pygame.K_d]: local_player.x += MOVE_SPEED

#     # Send position to server
#     if local_player_id is not None:
#         try:
#             msg = msgpack.packb({"type": "move", "x": local_player.x, "y": local_player.y}, use_bin_type=True)
#             client_socket.sendto(msg, (server_ip, server_port))
#         except:
#             pass

#     # --- Drawing ---
#     screen.fill((50,50,50))
#     for p in players.values():
#         pygame.draw.rect(screen, (255,0,0), (p.x, p.y, PLAYER_SIZE, PLAYER_SIZE))
#     pygame.draw.rect(screen, (0,255,0), (local_player.x, local_player.y, PLAYER_SIZE, PLAYER_SIZE))
#     pygame.display.flip()

# pygame.quit()
# client_socket.close()
