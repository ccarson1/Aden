from server.enemy import Enemy

class EnemyManager:
    def __init__(self):
        self.enemies = {
            1: Enemy(1, 100, 100, 1, 11, "green-slime", "Test_01", 0.25),
            2: Enemy(2, 150, 400, 1, 11, "red-slime", "Test_01", 0.12),
            3: Enemy(3, 150, 440, 8, 6, "bull", "Test_01", 0.25),
            4: Enemy(4, 150, 440, 8, 6, "bull", "grasslands_01", 0.25),
        }

    def update_all(self, dt, players, game_map):
        """Update all enemies on the same map as any player."""
        for e in self.enemies.values():
            # Skip enemies not on the same map as any player
            if not any(p.current_map == e.current_map for p in players.values()):
                continue

            # --- Follow nearest player on the same map ---
            closest_player = None
            closest_distance = float('inf')
            for p in players.values():
                if p.current_map != e.current_map:
                    continue  # ignore players on other maps
                dx = p.x - e.x
                dy = p.y - e.y
                distance = (dx**2 + dy**2)**0.5
                if distance < closest_distance:
                    closest_distance = distance
                    closest_player = p

            if closest_player:
                e.target_x = closest_player.x
                e.target_y = closest_player.y
                e.moving = True

            # --- Update movement and z_index ---
            e.update(dt, game_map)
