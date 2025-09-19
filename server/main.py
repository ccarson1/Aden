import socket
import threading
import time
import msgpack
import config
from server import game_state
from server import auth_db

clients = {}          # player_id -> Player
last_seen = {}        # player_id -> timestamp
tokens = {}           # token -> player_id
player_counter = 1
available_ids = []
running = True
lock = threading.Lock()
token_cache = {}
TOKEN_CACHE_TTL = 30  # seconds
DB_REFRESH_INTERVAL = 60 

sock = None

# Auth server connection settings
AUTH_HOST = config.HOST
AUTH_PORT = config.AUTH_PORT

TOKEN_TIMEOUT = 5  # seconds to wait for auth server response


# ---------------- Helper Functions ----------------

def get_new_pid():
    global player_counter
    if available_ids:
        return available_ids.pop(0)  # reuse an old ID
    else:
        pid = player_counter
        player_counter += 1
        return pid


def cleanup_player(pid):
    if pid in clients: del clients[pid]
    if pid in last_seen: del last_seen[pid]
    for tok, id in list(tokens.items()):
        if id == pid:
            del tokens[tok]
    available_ids.append(pid)  # make ID reusable
    print(f"[TIMEOUT] Removed player {pid}, ID available again")


    
def verify_token(token):
    now = time.time()
    if token in token_cache:
        username, expires_at = token_cache[token]
        if now < expires_at:
            # Extend cache expiration for sliding TTL
            token_cache[token] = (username, now + TOKEN_CACHE_TTL)
            return True
        else:
            # Token expired in cache, remove it
            del token_cache[token]

    # Token not in cache, check DB once
    valid, username = auth_db.verify_token(token)
    if valid:
        token_cache[token] = (username, now + TOKEN_CACHE_TTL)
        return True

    return False

def refresh_active_tokens():
    while running:
        time.sleep(DB_REFRESH_INTERVAL)
        now = time.time()
        with lock:
            for token, (username, expires_at) in token_cache.items():
                if expires_at > now:
                    auth_db.refresh_token(token)  # update DB TTL



# ---------------- Cleanup & Broadcast ----------------

def cleanup_inactive():
    global running
    while running:
        time.sleep(config.PRR)
        now = time.time()
        with lock:
            inactive = [pid for pid, t in last_seen.items() if now - t > config.TIMEOUT]
            for pid in inactive:
                print(f"[TIMEOUT] Removing player {pid}")
                # Notify others
                try:
                    msg = {"type": "player_disconnect", "player_id": pid}
                    packed = msgpack.packb(msg, use_bin_type=True)
                    for p in clients.values():
                        sock.sendto(packed, (p.addr[0], p.addr[1]))
                except Exception as e:
                    print(f"[ERROR] Failed to broadcast disconnect: {e}")
                # Remove player cleanly
                cleanup_player(pid)


def broadcast():
    global running
    while running:
        time.sleep(config.UPDATE_RATE)
        state = []
        with lock:
            for p in clients.values():
                state.append({
                    "id": p.id,
                    "name": p.name,
                    "x": p.x,
                    "y": p.y,
                    "direction": getattr(p, "direction", "down"),
                    "moving": getattr(p, "moving", False),
                    "frame_w": getattr(p, "frame_w", 64),
                    "frame_h": getattr(p, "frame_h", 64)
                })
            for p in clients.values():
                try:
                    sock.sendto(
                        msgpack.packb({"type": "update", "players": state}, use_bin_type=True),
                        (p.addr[0], p.addr[1])
                    )
                except Exception:
                    continue


# ---------------- Main Server Loop ----------------

def start_server():
    global sock, running
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((config.HOST, config.PORT))
    sock.settimeout(1.0)

    print(f"[SERVER] Server started on {config.HOST}:{config.PORT}")

    # Start background threads
    threading.Thread(target=cleanup_inactive, daemon=True).start()
    threading.Thread(target=broadcast, daemon=True).start()
    threading.Thread(target=refresh_active_tokens, daemon=True).start()

    while running:
        try:
            data, addr = sock.recvfrom(config.BUFFER_SIZE)
            msg = msgpack.unpackb(data, raw=False)

            token = msg.get("token")
            if not token:
                continue  # ignore messages without token

            # Verify token with auth server
            if not verify_token(token):
                print(f"[WARN] Invalid token from {addr}, ignoring")
                continue

            with lock:
                if token not in tokens:
                    pid = get_new_pid()
                    tokens[token] = pid

                    # Load saved data from DB
                    username = auth_db.get_username_from_token(token)
                    saved_data = auth_db.load_player_state(username)  # implement this

                    # Create player with saved position/direction
                    clients[pid] = game_state.Player(
                        pid, f"Player{pid}", 
                        frame_w=64, frame_h=64,
                        x=saved_data.get("x", 100),
                        y=saved_data.get("y", 100)
                    )
                    clients[pid].direction = saved_data.get("direction", "down")
                    clients[pid].addr = addr
                    last_seen[pid] = time.time()

                    # Send assigned ID + initial state to client
                    sock.sendto(
                        msgpack.packb({
                            "type": "assign_id",
                            "player_id": pid,
                            "player_data": saved_data
                        }, use_bin_type=True),
                        addr
                    )
                    print(f"[INFO] Assigned player ID: {pid}")
                else:
                    pid = tokens[token]
                    player = clients[pid]
                    last_seen[pid] = time.time()
                    player.addr = addr  # update address if changed

                    if msg["type"] == "move":
                        player.x = msg["x"]
                        player.y = msg["y"]
                        player.direction = msg.get("direction", player.direction)
                        player.moving = msg.get("moving", False)

                    if msg["type"] == "save":
                        # Example save payload: {"token": ..., "type": "save", "x":..., "y":..., "direction":...}
                        username = auth_db.get_username_from_token(token)
                        auth_db.save_player_state(pid, username, msg["x"], msg["y"], msg["direction"], msg['current_map'])

        except socket.timeout:
            continue
        except OSError as e:
            if e.errno == 10054:  # Connection reset
                continue
            print(f"[ERROR] {e}")


# ---------------- Run ----------------

if __name__ == "__main__":
    start_server()
