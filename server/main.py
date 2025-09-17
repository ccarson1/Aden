

import socket
import threading, time, signal
import config
from server import network, game_state

clients = {}      # {addr: Player}
last_seen = {}    # {addr: timestamp}
player_id_counter = 1
running = True
lock = threading.Lock()

# Cleanup inactive clients
def cleanup_inactive():
    while running:
        time.sleep(config.PRR)
        now = time.time()
        inactive = [addr for addr, t in last_seen.items() if now - t > config.TIMEOUT]
        for addr in inactive:
            print(f"[TIMEOUT] Removing {addr}")
            del clients[addr]
            del last_seen[addr]

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
                    "moving": getattr(p, "moving", False)
                })
            for addr in clients.keys():
                try:
                    network.send_msg(sock, addr, {"type":"update","players":state})
                except:
                    continue


# Main loop
sock = network.create_udp_socket()
threading.Thread(target=broadcast, daemon=True).start()
threading.Thread(target=cleanup_inactive, daemon=True).start()

def signal_handler(sig, frame):
    global running
    running = False
    sock.close()

signal.signal(signal.SIGINT, signal_handler)

while running:
    try:
        msg, addr = network.recv_msg(sock, config.BUFFER_SIZE)
        now = time.time()
        if addr not in clients:
            clients[addr] = game_state.Player(player_id_counter, f"Player{player_id_counter}", frame_w=64, frame_h=64) 
            last_seen[addr] = now
            network.send_msg(sock, addr, {"type":"assign_id","player_id":clients[addr].id})
            player_id_counter += 1
        player = clients[addr]
        last_seen[addr] = now
        if msg["type"] == "move":
            player.x = msg["x"]
            player.y = msg["y"]
            player.direction = msg.get("direction", player.direction)
            player.moving = msg.get("moving", False)
    except socket.timeout:
        continue

