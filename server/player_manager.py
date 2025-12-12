# server/player_manager.py
import time
from server import auth_db
import config
from server import player

class PlayerManager:
    def __init__(self):
        self.clients = {}          # pid -> Player object
        self.last_seen = {}        # pid -> last active timestamp
        self.tokens = {}           # token -> pid
        self.player_counter = 1
        self.available_ids = []
        self.token_cache = config.token_cache
        self.TOKEN_CACHE_TTL = config.TOKEN_CACHE_TTL
        self.player = None

    # ---------------- Player Lifecycle ----------------
    def get_username_from_pid(self, pid):
        for token, id in self.tokens.items():
            if id == pid:
                return auth_db.get_username_from_token(token)
        return None

    def get_new_pid(self):
        if self.available_ids:
            return self.available_ids.pop(0)
        else:
            pid = self.player_counter
            self.player_counter += 1
            return pid

    def cleanup_player(self, pid):
        if pid in self.clients: del self.clients[pid]
        if pid in self.last_seen: del self.last_seen[pid]
        for tok, id in list(self.tokens.items()):
            if id == pid:
                del self.tokens[tok]
        self.available_ids.append(pid)
        print(f"[TIMEOUT] Removed player {pid}, ID available again")

    # ---------------- Token Handling ----------------
    def verify_token(self, token):
        now = time.time()
        if token in self.token_cache:
            username, expires_at = self.token_cache[token]
            if now < expires_at:
                self.token_cache[token] = (username, now + self.TOKEN_CACHE_TTL)
                return True
            else:
                del self.token_cache[token]

        valid, username = auth_db.verify_token(token)
        if valid:
            self.token_cache[token] = (username, now + self.TOKEN_CACHE_TTL)
            return True

        return False

    def refresh_active_tokens(self):
        now = time.time()
        for token, (username, expires_at) in list(self.token_cache.items()):
            if expires_at > now:
                auth_db.refresh_token(token)  # extend DB TTL

    # ---------------- Player Creation ----------------
    def create_or_get_player(self, token, addr):
        if token not in self.tokens:
            pid = self.get_new_pid()
            self.tokens[token] = pid
            username = auth_db.get_username_from_token(token)
            saved_data = auth_db.load_player_state(username)

            # 🔹 Get character name from DB
            char_name = auth_db.get_char_name(username)
            if not char_name:
                char_name = f"Player{pid}"  # fallback

            # Create the Player instance
            new_player = player.Player(
                pid,
                char_name,  # 🔹 use char_name instead of Player{pid}
                x=saved_data.get("x", 100),
                y=saved_data.get("y", 100)
            )
            new_player.addr = addr
            new_player.direction = saved_data.get("direction", "down")
            new_player.current_map = saved_data.get("current_map", "DefaultMap")
            new_player.z_index = saved_data.get("z_index", 0)
            new_player.username = username

            self.clients[pid] = new_player
            self.last_seen[pid] = time.time()
            print(f"[INFO] Assigned player ID {pid} to {username} ({char_name})")

            return pid, new_player, saved_data
        else:
            pid = self.tokens[token]
            existing_player = self.clients[pid]
            self.last_seen[pid] = time.time()
            existing_player.addr = addr
            return pid, existing_player, None


