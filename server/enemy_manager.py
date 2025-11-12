# server/enemy_manager.py
from server.enemy import Enemy

class EnemyManager:
    def __init__(self):
        self.enemies = {
            1: Enemy(1, 100, 100, 1, 11, "green-slime", "Test_01", 0.25,40, 1),
            2: Enemy(2, 150, 400, 1, 11, "red-slime", "Test_01", 0.12, 40,1),
            3: Enemy(3, 150, 440, 8, 6, "bull", "Test_01", 0.08, 60, 20),
            4: Enemy(4, 150, 440, 8, 6, "bull", "grasslands_01", 0.08, 60, 20),
        }

    def update_all(self, dt, players):
        """Update all enemies — movement and z-index now handled by Enemy itself."""
        for e in self.enemies.values():
            e.update(dt, players)
