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
from server.game_map import GameMap
import os

running = True
lock = threading.Lock()
sock = None

# Auth server connection settings
AUTH_HOST = config.HOST
AUTH_PORT = config.AUTH_PORT



neti = Network(lock)
player_manager = PlayerManager()
enemy_manager = EnemyManager()
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
map_path = os.path.join(BASE_DIR, "../assets/maps/grasslands_01.tmx")

game_map = GameMap(os.path.normpath(map_path))

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
    threading.Thread(target=neti.broadcast, args=(player_manager, enemy_manager, sock, game_map), daemon=True).start()
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


# ---------------- Run ----------------

if __name__ == "__main__":
    start_server()
