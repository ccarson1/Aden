from server.enemy import Enemy

class EnemyManager:
    def __init__(self):
        self.enemies = {
            1: Enemy(1, 100, 100, 1, 11, "green-slime", "Test_01", 0.25),
            2: Enemy(2, 150, 400, 1, 11, "red-slime", "Test_01", 0.12),
            3: Enemy(3, 150, 440, 8, 6, "bull", "Test_01", 0.25),
        }

    # def update_all(self, dt):
    #     for e in self.enemies.values():
    #         e.update(dt)

    def update_all(self, dt, players):
        """Update all enemies and make them follow the closest player."""
        for e in self.enemies.values():
            # Skip if no players
            if not players:
                continue

            # Find the nearest player
            closest_player = None
            closest_distance = float('inf')
            for p in players.values():
                dx = p.x - e.x
                dy = p.y - e.y
                distance = (dx**2 + dy**2)**0.5
                if distance < closest_distance:
                    closest_distance = distance
                    closest_player = p

            if closest_player:
                # Make enemy target the player's current position
                e.target_x = closest_player.x
                e.target_y = closest_player.y
                e.moving = True

            # Update movement toward target
            e.update(dt)
