import time, config, msgpack
import server.player as player


class Network:
    
    def __init__(self, lock):
        self.running = True
        self.last_broadcast = time.time()
        self.lock = lock

    def broadcast(self, player_manager, enemy_manager, sock):
        self.player_manager = player_manager
        self.enemy_manager = enemy_manager
        self.clients = player_manager.clients
        self.enemies = enemy_manager.enemies
        
        while self.running:
            now = time.time()
            dt = now - self.last_broadcast
            self.last_broadcast = now

            world_time = time.strftime("%H:%M:%S", time.gmtime())
            state = []
            enemy_state = []

            
            

            with self.lock:
                # current_player_scenes = []
                
                # Interpolate positions first using real dt
                for p in self.clients.values():
                    player.interpolate_player(p, dt)

                # Build state packet
                for p in self.clients.values():
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
                        "timestamp": p.last_update_time,
                        "attacking": getattr(p, "attacking", False),
                    })
                    # print(f"Player {p.id} on map {p.current_map}")
                    # current_player_scenes.append(p.current_map)

                enemy_manager.update_all(dt, self.clients)  # Update enemies with dt and player info

                enemy_state = []
                for e in self.enemies.values():
                    # Only send enemies on the same map as a player
                    if not any(p.current_map == e.current_map for p in self.clients.values()):
                        continue
                    #print(current_player_scenes)
                    #if e.current_map in current_player_scenes:
                    # Ensure z_index is always valid
                    z = getattr(e, "z_index", 0)
                    if z is None:
                        z = 0
                        e.z_index = 0  # fallback

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
                        "directions": getattr(e, "directions", ["down"]),
                        "z_index": z,
                        "c_h_padding": getattr(e, "c_h_padding", 0),
                        "c_v_padding": getattr(e, "c_v_padding", 0),
                    })

                # Broadcast to all clients
                for p in self.clients.values():
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