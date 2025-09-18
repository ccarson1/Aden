import socket
import threading
import time
import msgpack
import config
from server import game_state

clients = {}      # player_id -> Player
last_seen = {}    # player_id -> timestamp
tokens = {}       # token -> player_id
global player_counter
player_counter = 1
running = True
lock = threading.Lock()

# UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((config.HOST, config.PORT))
sock.settimeout(1.0)

# Cleanup inactive players
def cleanup_inactive():
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

                # Remove from state
                del clients[pid]
                del last_seen[pid]
                token_to_remove = [tok for tok, id in tokens.items() if id == pid]
                for tok in token_to_remove:
                    del tokens[tok]

# Broadcast game state
def broadcast():
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
                    sock.sendto(msgpack.packb({"type":"update","players":state}, use_bin_type=True),
                                (p.addr[0], p.addr[1]))
                except Exception:
                    continue

# Start threads
threading.Thread(target=cleanup_inactive, daemon=True).start()
threading.Thread(target=broadcast, daemon=True).start()

# Main loop
while running:
    try:
        data, addr = sock.recvfrom(config.BUFFER_SIZE)
        msg = msgpack.unpackb(data, raw=False)

        token = msg.get("token")
        if not token:
            continue  # ignore messages without token

        with lock:
            if token not in tokens:
                # Assign new player_id
                
                pid = player_counter
                player_counter += 1
                tokens[token] = pid
                clients[pid] = game_state.Player(pid, f"Player{pid}", frame_w=64, frame_h=64)
                clients[pid].addr = addr
                last_seen[pid] = time.time()
                sock.sendto(msgpack.packb({"type":"assign_id","player_id":pid}, use_bin_type=True), addr)
                print(f"[INFO] Assigned player ID: {pid}")
            else:
                pid = tokens[token]
                player = clients[pid]
                last_seen[pid] = time.time()
                player.addr = addr  # update address in case it changed

                if msg["type"] == "move":
                    player.x = msg["x"]
                    player.y = msg["y"]
                    player.direction = msg.get("direction", player.direction)
                    player.moving = msg.get("moving", False)

    except socket.timeout:
        continue
    except Exception as e:
        print(f"[ERROR] {e}")
        continue
