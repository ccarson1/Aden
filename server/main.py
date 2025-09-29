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
SAVE_INTERVAL = 30 

sock = None

# Auth server connection settings
AUTH_HOST = config.HOST
AUTH_PORT = config.AUTH_PORT

TOKEN_TIMEOUT = 5  # seconds to wait for auth server response


# ---------------- Helper Functions ----------------

def get_username_from_pid(pid):
    """
    Given a player ID, return the username associated with that player.
    """
    for token, id in tokens.items():
        if id == pid:
            return auth_db.get_username_from_token(token)
    return None

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
    last_broadcast = time.time()
    
    while running:
        now = time.time()
        dt = now - last_broadcast
        last_broadcast = now

        world_time = time.strftime("%H:%M:%S", time.gmtime())
        state = []

        with lock:
            # Interpolate positions first using real dt
            for p in clients.values():
                interpolate_player(p, dt)

            # Build state packet
            for p in clients.values():
                state.append({
                    "id": p.id,
                    "name": p.name,
                    "x": p.x,
                    "y": p.y,
                    "prev_x": p.prev_x,
                    "prev_y": p.prev_y,
                    "target_x": p.target_x,
                    "target_y": p.target_y,
                    "direction": getattr(p, "direction", "down"),
                    "moving": getattr(p, "moving", False),
                    "frame_w": getattr(p, "frame_w", 64),
                    "frame_h": getattr(p, "frame_h", 64),
                    "current_map": getattr(p, "current_map", "DefaultMap"),
                    "timestamp": p.last_update_time
                })

            # Broadcast to all clients
            for p in clients.values():
                try:
                    sock.sendto(
                        msgpack.packb({"type": "update", "players": state, "world_time": world_time}, use_bin_type=True),
                        (p.addr[0], p.addr[1])
                    )
                except Exception:
                    continue

        # Sleep until next update
        time.sleep(config.UPDATE_RATE)

def interpolate_player(player, dt):
    """
    Smoothly move a player from their current position (x, y)
    toward their target position (target_x, target_y) at a fixed speed.
    Instantly teleport if the target map changed.
    
    Args:
        player: Player object with x, y, prev_x, prev_y, target_x, target_y, current_map
        dt: Time delta in seconds since last update
    """

    # Make sure target coordinates exist
    if not hasattr(player, "target_x") or not hasattr(player, "target_y"):
        player.target_x = player.x
        player.target_y = player.y

    # Check for map teleport (target != current)
    if hasattr(player, "prev_map") and player.prev_map != player.current_map:
        # Instant jump on map switch
        player.x = player.target_x
        player.y = player.target_y
        player.prev_x = player.x
        player.prev_y = player.y
        player.prev_map = player.current_map
        return

    # Default speed (units per second)
    speed = getattr(player, "speed", 200.0)

    # Compute distance
    dx = player.target_x - player.x
    dy = player.target_y - player.y
    dist = (dx**2 + dy**2) ** 0.5

    if dist > 0:
        move_dist = min(dist, speed * dt)
        player.x += dx / dist * move_dist
        player.y += dy / dist * move_dist

    # Update previous map for next tick
    player.prev_map = getattr(player, "current_map", player.prev_map)




def autosave_loop():
    global running
    while running:
        time.sleep(SAVE_INTERVAL)
        with lock:
            for pid, player in clients.items():
                if not getattr(player, "needs_save", False):
                    continue

                username = get_username_from_pid(pid)

                # Only save fields that actually exist
                x = getattr(player, "x", None)
                y = getattr(player, "y", None)
                direction = getattr(player, "direction", None)
                current_map = getattr(player, "current_map", None)

                # Skip save if essential fields are missing
                if x is None or y is None or direction is None or current_map is None:
                    print(f"[AUTOSAVE] Skipping player {pid} because some fields are missing")
                    continue

                auth_db.save_player_state(
                    pid,
                    username,
                    x,
                    y,
                    direction,
                    current_map
                )
                
                # Reset flag
                player.needs_save = False  

                # Notify client
                try:
                    msg = {"type": "save_confirm", "message": "Your game has been saved."}
                    sock.sendto(msgpack.packb(msg, use_bin_type=True), (player.addr[0], player.addr[1]))
                    print(f"[AUTOSAVE] Checked {len(clients)} players")
                except Exception as e:
                    print(f"[ERROR] Failed to notify player {pid}: {e}")

            


            




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
    threading.Thread(target=autosave_loop, daemon=True).start() 

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
                    clients[pid].current_map = saved_data.get("current_map", "DefaultMap")

                    

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

                    # if msg["type"] == "move":
                    #     player.x = msg["x"]
                    #     player.y = msg["y"]
                    #     player.direction = msg.get("direction", player.direction)
                    #     player.moving = msg.get("moving", False)
                    #     player.needs_save = True 
                        
                    #     # Update current_map from client
                    #     if "current_map" in msg:
                    #         player.current_map = msg["current_map"]

                    if msg["type"] == "move":
                        # Save previous position for interpolation
                        player.prev_x = player.x
                        player.prev_y = player.y
                        player.last_update_time = time.time()

                        # Set target position from client
                        player.target_x = msg["x"]
                        player.target_y = msg["y"]
                        player.direction = msg.get("direction", player.direction)
                        player.moving = msg.get("moving", False)
                        player.needs_save = True

                        # Update current_map if included
                        if "current_map" in msg:
                            player.current_map = msg["current_map"]

                    if msg["type"] == "save":
                        # Example save payload: {"token": ..., "type": "save", "x":..., "y":..., "direction":...}
                        username = auth_db.get_username_from_token(token)
                        auth_db.save_player_state(pid, username, msg["x"], msg["y"], msg["direction"], msg['current_map'])

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
