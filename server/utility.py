import time
import msgpack
import config
from server import auth_db


class Utility:
    def __init__(self, lock, sock, player_manager, enemy_manager):
        self.lock = lock
        self.sock = sock
        self.player_manager = player_manager
        self.enemy_manager = enemy_manager
        self.running = True

    def cleanup_inactive(self):
        """Remove players that have timed out and notify others."""
        while self.running:
            time.sleep(config.PRR)
            now = time.time()
            with self.lock:
                inactive = [pid for pid, t in self.player_manager.last_seen.items()
                            if now - t > config.TIMEOUT]
                for pid in inactive:
                    print(f"[TIMEOUT] Removing player {pid}")
                    try:
                        msg = {"type": "player_disconnect", "player_id": pid}
                        packed = msgpack.packb(msg, use_bin_type=True)
                        for p in self.player_manager.clients.values():
                            self.sock.sendto(packed, (p.addr[0], p.addr[1]))
                    except Exception as e:
                        print(f"[ERROR] Failed to broadcast disconnect: {e}")
                    self.player_manager.cleanup_player(pid)

    def autosave_loop(self):
        """Periodically save player data to the DB."""
        while self.running:
            time.sleep(config.SAVE_INTERVAL)
            with self.lock:
                for pid, player in self.player_manager.clients.items():
                    if not getattr(player, "needs_save", False):
                        continue

                    username = self.player_manager.get_username_from_pid(pid)
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
                        self.sock.sendto(msgpack.packb(msg, use_bin_type=True),
                                         (player.addr[0], player.addr[1]))
                        print(f"[AUTOSAVE] Saved player {pid}")
                    except Exception as e:
                        print(f"[ERROR] Failed to notify player {pid}: {e}")

    def refresh_active_tokens_loop(self):
        """Keep token cache fresh."""
        while self.running:
            time.sleep(config.DB_REFRESH_INTERVAL)
            with self.lock:
                self.player_manager.refresh_active_tokens()
