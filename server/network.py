import time, config, msgpack
import server.player as player


class Network:
    
    def __init__(self, lock):
        self.running = True
        self.last_broadcast = time.time()
        self.lock = lock

    def broadcast(self, clients, enemies, sock):
        
        
        while self.running:
            now = time.time()
            dt = now - self.last_broadcast
            self.last_broadcast = now

            world_time = time.strftime("%H:%M:%S", time.gmtime())
            state = []
            enemy_state = []

            with self.lock:
                # Interpolate positions first using real dt
                for p in clients.values():
                    player.interpolate_player(p, dt)

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
                        "current_map": getattr(p, "current_map", "Test_01"),
                        "z_index": getattr(p, "z_index", 0),
                        "timestamp": p.last_update_time
                    })

                for e in enemies.values():
                    #print(getattr(e, "columns", 11))
                    enemy_state.append({
                        "id": e.id,
                        "type": e.type,
                        "x": e.x,
                        "y": e.y,
                        "direction": e.direction,
                        "moving": e.moving,
                        "current_map": e.current_map,
                        "rows": getattr(e, "rows", 1),
                        "columns": getattr(e, "columns", 11),
                        "hp": getattr(e, "hp", 10),
                        "speed": getattr(e, "speed", 100.0),
                        "frame_speed": getattr(e, "frame_speed", 0.12),
                        "directions": getattr(e, "directions", ["down"])
                    })

                # Broadcast to all clients
                for p in clients.values():
                    try:
                        sock.sendto(
                            msgpack.packb({
                                "type": "update",
                                "players": state,
                                "enemies": enemy_state,
                                "world_time": world_time,
                                }, use_bin_type=True),
                            (p.addr[0], p.addr[1])
                        )
                    except Exception:
                        continue

            # Sleep until next update
            time.sleep(config.UPDATE_RATE)