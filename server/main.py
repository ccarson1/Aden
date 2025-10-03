import socket
import threading
import time
import msgpack
import config
from server import auth_db
from server.network import Network
from server.player_manager import PlayerManager
from server.enemy_manager import EnemyManager
from server.message_handler import MessageHandler
from server.utility import Utility

running = True
lock = threading.Lock()
sock = None

# Auth server connection settings
AUTH_HOST = config.HOST
AUTH_PORT = config.AUTH_PORT



neti = Network(lock)
player_manager = PlayerManager()
enemy_manager = EnemyManager()

utils = None


# ---------------- Main Server Loop ----------------

def start_server():
    global sock, running, utils
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((config.HOST, config.PORT))
    sock.settimeout(1.0)
    
    print(f"[SERVER] Server started on {config.HOST}:{config.PORT}")
    handler = MessageHandler(sock, player_manager, lock)
    utils = Utility(lock, sock, player_manager, enemy_manager)

    # Background threads
    threading.Thread(target=utils.cleanup_inactive, daemon=True).start()
    threading.Thread(target=neti.broadcast,
                     args=(player_manager.clients, enemy_manager.enemies, sock),
                     daemon=True).start()
    threading.Thread(target=utils.refresh_active_tokens_loop, daemon=True).start()
    threading.Thread(target=utils.autosave_loop, daemon=True).start()


    while running:
        try:
            data, addr = sock.recvfrom(config.BUFFER_SIZE)
            msg = msgpack.unpackb(data, raw=False)
            handler.handle_message( msg, addr)

        except socket.timeout:
            continue
        except OSError as e:
            if e.errno == 10054:  # Connection reset
                continue
            print(f"[ERROR] {e}")

    # Main receive loop
    # while running:
    #     try:
    #         data, addr = sock.recvfrom(config.BUFFER_SIZE)
    #         msg = msgpack.unpackb(data, raw=False)

    #         token = msg.get("token")
    #         if not token:
    #             continue

    #         # Verify token
    #         if not player_manager.verify_token(token):
    #             print(f"[WARN] Invalid token from {addr}, ignoring")
    #             continue

    #         with lock:
    #             pid, player, saved_data = player_manager.create_or_get_player(token, addr)

    #             if saved_data:  # new player
    #                 sock.sendto(
    #                     msgpack.packb({
    #                         "type": "assign_id",
    #                         "player_id": pid,
    #                         "player_data": saved_data
    #                     }, use_bin_type=True),
    #                     addr
    #                 )
    #             else:  # existing player actions
    #                 if msg["type"] == "move":
    #                     player.prev_x, player.prev_y = player.x, player.y
    #                     player.last_update_time = time.time()
    #                     player.target_x = msg["x"]
    #                     player.target_y = msg["y"]
    #                     player.direction = msg.get("direction", player.direction)
    #                     player.moving = msg.get("moving", False)
    #                     player.needs_save = True
    #                     if "current_map" in msg:
    #                         player.current_map = msg["current_map"]

    #                 if msg["type"] == "save":
    #                     username = player_manager.get_username_from_pid(pid)
    #                     auth_db.save_player_state(
    #                         pid, username, msg["x"], msg["y"], msg["direction"], msg["current_map"]
    #                     )

    #                 if msg["type"] == "portal_enter":
    #                     player.current_map = msg["target_map"]
    #                     player.x = msg.get("spawn_x", player.x)
    #                     player.y = msg.get("spawn_y", player.y)

    #                     player.prev_x = player.x
    #                     player.prev_y = player.y
    #                     player.target_x = player.x
    #                     player.target_y = player.y
    #                     player.last_update_time = time.time()

    #                     sock.sendto(
    #                         msgpack.packb({
    #                             "type": "map_switch",
    #                             "map": player.current_map,
    #                             "x": player.x,
    #                             "y": player.y
    #                         }, use_bin_type=True),
    #                         addr
    #                     )

    #     except socket.timeout:
    #         continue
    #     except OSError as e:
    #         if e.errno == 10054:  # Connection reset
    #             continue
    #         print(f"[ERROR] {e}")


# ---------------- Run ----------------

if __name__ == "__main__":
    start_server()
