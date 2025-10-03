import socket
import threading
import time
import msgpack
import config
from server import auth_db
from server.game_state import Enemy
from server.network import Network
from server.player_manager import PlayerManager

running = True
lock = threading.Lock()
sock = None

# Auth server connection settings
AUTH_HOST = config.HOST
AUTH_PORT = config.AUTH_PORT

# Game state
enemies = {
    1: Enemy(1, 100, 100, "green-slime"),
    2: Enemy(2, 150, 400, "green-slime"),
}

neti = Network(lock)
player_manager = PlayerManager()


# ---------------- Cleanup & Broadcast ----------------

def cleanup_inactive():
    global running
    while running:
        time.sleep(config.PRR)
        now = time.time()
        with lock:
            inactive = [pid for pid, t in player_manager.last_seen.items()
                        if now - t > config.TIMEOUT]
            for pid in inactive:
                print(f"[TIMEOUT] Removing player {pid}")
                try:
                    msg = {"type": "player_disconnect", "player_id": pid}
                    packed = msgpack.packb(msg, use_bin_type=True)
                    for p in player_manager.clients.values():
                        sock.sendto(packed, (p.addr[0], p.addr[1]))
                except Exception as e:
                    print(f"[ERROR] Failed to broadcast disconnect: {e}")
                player_manager.cleanup_player(pid)


def autosave_loop():
    global running
    while running:
        time.sleep(config.SAVE_INTERVAL)
        with lock:
            for pid, player in player_manager.clients.items():
                if not getattr(player, "needs_save", False):
                    continue

                username = player_manager.get_username_from_pid(pid)

                x = getattr(player, "x", None)
                y = getattr(player, "y", None)
                direction = getattr(player, "direction", None)
                current_map = getattr(player, "current_map", None)

                if None in (x, y, direction, current_map):
                    print(f"[AUTOSAVE] Skipping player {pid} (incomplete data)")
                    continue

                auth_db.save_player_state(pid, username, x, y, direction, current_map)
                player.needs_save = False

                try:
                    msg = {"type": "save_confirm", "message": "Your game has been saved."}
                    sock.sendto(msgpack.packb(msg, use_bin_type=True),
                                (player.addr[0], player.addr[1]))
                    print(f"[AUTOSAVE] Saved player {pid}")
                except Exception as e:
                    print(f"[ERROR] Failed to notify player {pid}: {e}")


def refresh_active_tokens_loop():
    global running
    while running:
        time.sleep(config.DB_REFRESH_INTERVAL)
        with lock:
            player_manager.refresh_active_tokens()


# ---------------- Main Server Loop ----------------

def start_server():
    global sock, running
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((config.HOST, config.PORT))
    sock.settimeout(1.0)

    print(f"[SERVER] Server started on {config.HOST}:{config.PORT}")

    # Background threads
    threading.Thread(target=cleanup_inactive, daemon=True).start()
    threading.Thread(target=neti.broadcast, args=(player_manager.clients, enemies, sock), daemon=True).start()
    threading.Thread(target=refresh_active_tokens_loop, daemon=True).start()
    threading.Thread(target=autosave_loop, daemon=True).start()

    # Main receive loop
    while running:
        try:
            data, addr = sock.recvfrom(config.BUFFER_SIZE)
            msg = msgpack.unpackb(data, raw=False)

            token = msg.get("token")
            if not token:
                continue

            # Verify token
            if not player_manager.verify_token(token):
                print(f"[WARN] Invalid token from {addr}, ignoring")
                continue

            with lock:
                pid, player, saved_data = player_manager.create_or_get_player(token, addr)

                if saved_data:  # new player
                    sock.sendto(
                        msgpack.packb({
                            "type": "assign_id",
                            "player_id": pid,
                            "player_data": saved_data
                        }, use_bin_type=True),
                        addr
                    )
                else:  # existing player actions
                    if msg["type"] == "move":
                        player.prev_x, player.prev_y = player.x, player.y
                        player.last_update_time = time.time()
                        player.target_x = msg["x"]
                        player.target_y = msg["y"]
                        player.direction = msg.get("direction", player.direction)
                        player.moving = msg.get("moving", False)
                        player.needs_save = True
                        if "current_map" in msg:
                            player.current_map = msg["current_map"]

                    if msg["type"] == "save":
                        username = player_manager.get_username_from_pid(pid)
                        auth_db.save_player_state(
                            pid, username, msg["x"], msg["y"], msg["direction"], msg["current_map"]
                        )

                    if msg["type"] == "portal_enter":
                        player.current_map = msg["target_map"]
                        player.x = msg.get("spawn_x", player.x)
                        player.y = msg.get("spawn_y", player.y)

                        player.prev_x = player.x
                        player.prev_y = player.y
                        player.target_x = player.x
                        player.target_y = player.y
                        player.last_update_time = time.time()

                        sock.sendto(
                            msgpack.packb({
                                "type": "map_switch",
                                "map": player.current_map,
                                "x": player.x,
                                "y": player.y
                            }, use_bin_type=True),
                            addr
                        )

        except socket.timeout:
            continue
        except OSError as e:
            if e.errno == 10054:  # Connection reset
                continue
            print(f"[ERROR] {e}")


# ---------------- Run ----------------

if __name__ == "__main__":
    start_server()
