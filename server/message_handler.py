# server/message_handler.py
import msgpack, time
from server import auth_db

class MessageHandler:
    def __init__(self, sock, player_manager, lock):
        self.sock = sock
        self.player_manager = player_manager
        self.lock = lock

    def handle_message(self, msg, addr):
        token = msg.get("token")
        if not token:
            return

        # Verify token
        if not self.player_manager.verify_token(token):
            print(f"[WARN] Invalid token from {addr}, ignoring")
            return

        with self.lock:
            pid, player, saved_data = self.player_manager.create_or_get_player(token, addr)

            if saved_data:  # new player
                self._send_assign_id(pid, saved_data, addr)
            else:
                handler = getattr(self, f"on_{msg['type']}", None)
                if handler:
                    handler(pid, player, msg, addr)
                else:
                    print(f"[WARN] Unknown message type: {msg['type']}")

    # ---------------- Handlers ----------------
    def on_move(self, pid, player, msg, addr):
        player.update_move(msg)  # use Player method

    def on_save(self, pid, player, msg, addr):
        username = self.player_manager.get_username_from_pid(pid)
        auth_db.save_player_state(
            pid, username, msg["x"], msg["y"], msg["direction"], msg["current_map"]
        )

    def on_portal_enter(self, pid, player, msg, addr):
        resp = player.enter_portal(msg)  # use Player method
        self.sock.sendto(msgpack.packb(resp, use_bin_type=True), addr)

    # ---------------- Utilities ----------------
    def _send_assign_id(self, pid, saved_data, addr):
        self.sock.sendto(
            msgpack.packb({
                "type": "assign_id",
                "player_id": pid,
                "player_data": saved_data
            }, use_bin_type=True),
            addr
        )
