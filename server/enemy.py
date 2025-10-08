import time

class Enemy:
    def __init__(self, eid, x, y, rows, columns, enemy_type="slime", current_map="Test_01", frame_speed=0.12):
        self.id = eid
        self.type = enemy_type
        self.x = x
        self.y = y
        self.prev_x = x
        self.prev_y = y
        self.target_x = x
        self.target_y = y
        self.rows = rows
        self.columns = columns
        self.direction = "down"
        self.moving = True
        self.current_map = current_map
        self.speed = 100.0  # pixels per second
        self.frame_speed = frame_speed
        self.last_update_time = time.time()

    def update(self, dt):

        """Move towards target position if moving."""
        if not self.moving:
            return

        dx = self.target_x - self.x
        dy = self.target_y - self.y

        distance = (dx**2 + dy**2)**0.5
        if distance == 0:
            self.moving = False
            return

        step = self.speed * dt
        if step >= distance:
            self.x = self.target_x
            self.y = self.target_y
            self.moving = False
        else:
            self.x += dx / distance * step
            self.y += dy / distance * step
