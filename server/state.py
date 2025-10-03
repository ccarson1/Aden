import threading
from server.game_state import Enemy

# ----------------- Global Game State -----------------
clients = {}          # player_id -> Player
last_seen = {}        # player_id -> timestamp
tokens = {}           # token -> player_id
player_counter = 1
available_ids = []
lock = threading.Lock()

token_cache = {}
TOKEN_CACHE_TTL = 30  # seconds

enemies = {
    1: Enemy(1, 100, 100, "green-slime"),
    2: Enemy(2, 150, 400, "green-slime")
}

running = True
