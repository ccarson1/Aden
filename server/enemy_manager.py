from server.enemy import Enemy

class EnemyManager:
    def __init__(self):
        self.enemies = {
            1: Enemy(1, 100, 100, 1, 11, "green-slime", "Test_01", 0.25),
            2: Enemy(2, 150, 400, 1, 11, "red-slime", "Test_01", 0.12),
            3: Enemy(3, 150, 440, 8, 6, "bull", "Test_01", 0.25),
        }

    def update_all(self, dt):
        for e in self.enemies.values():
            e.update(dt)
