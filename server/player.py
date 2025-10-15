import time

class Player:
    def __init__(self, player_id, name, frame_w, frame_h, x=100, y=100):
        self.id = player_id
        self.name = name
        self.x = x
        self.y = y
        self.frame_w = frame_w
        self.frame_h = frame_h
        self.direction = "down"
        self.moving = False
        self.current_map = None  # default map
        self.needs_save = False
        self.z_index = 0

        # Interpolation state
        self.prev_x = x
        self.prev_y = y
        self.target_x = x
        self.target_y = y
        self.last_update_time = 0.0
        self.prev_map = self.current_map

    # ---------------- Player Updates ----------------
    def update_move(self, msg: dict):
        """Update player movement state from a move message."""
        self.prev_x, self.prev_y = self.x, self.y
        self.last_update_time = time.time()
        self.target_x = msg["x"]
        self.target_y = msg["y"]
        self.direction = msg.get("direction", self.direction)
        self.moving = msg.get("moving", False)
        self.z_index = msg.get("z_index")
        self.needs_save = True

        if "current_map" in msg:
            self.current_map = msg["current_map"]

    def enter_portal(self, msg: dict):
        """Handle portal entry and return response dict."""
        self.current_map = msg["target_map"]
        self.x = msg.get("spawn_x", self.x)
        self.y = msg.get("spawn_y", self.y)

        # Reset movement state
        self.prev_x = self.x
        self.prev_y = self.y
        self.target_x = self.x
        self.target_y = self.y
        self.last_update_time = time.time()

        return {
            "type": "map_switch",
            "map": self.current_map,
            "x": self.x,
            "y": self.y
        }

# ---------------- Interpolation ----------------
def interpolate_player(player, dt):
    """
    Smoothly move a player toward target position at a fixed speed.
    Teleport if the map changes.
    """
    # Make sure target coordinates exist
    if not hasattr(player, "target_x") or not hasattr(player, "target_y"):
        player.target_x = player.x
        player.target_y = player.y

    # Check for map teleport
    if hasattr(player, "prev_map") and player.prev_map != player.current_map:
        player.x = player.target_x
        player.y = player.target_y
        player.prev_x = player.x
        player.prev_y = player.y
        player.prev_map = player.current_map
        return

    # Default speed (units per second)
    speed = getattr(player, "speed", 200.0)

    dx = player.target_x - player.x
    dy = player.target_y - player.y
    dist = (dx**2 + dy**2) ** 0.5

    if dist > 0:
        move_dist = min(dist, speed * dt)
        player.x += dx / dist * move_dist
        player.y += dy / dist * move_dist

    player.prev_map = getattr(player, "current_map", player.prev_map)
