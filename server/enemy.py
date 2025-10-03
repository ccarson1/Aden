class Enemy:
    def __init__(self, eid, x, y, enemy_type="slime"):
        self.id = eid
        self.type = enemy_type
        self.x = x
        self.y = y
        self.prev_x = x
        self.prev_y = y
        self.target_x = x
        self.target_y = y
        self.direction = "down"
        self.moving = False
        self.current_map = "DefaultMap"
        self.last_update_time = 0
        self.speed = 100.0