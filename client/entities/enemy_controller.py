from client.graphics.enemy_sprite import EnemySprite
from client.entities.enemy import Enemy
import pygame

# EnemyController
class EnemyController:
    def __init__(self):
        self.enemies = {}  # id -> Enemy

        #Partial enemy data will be loaded from the client database
        self.loaded_enemies = [
            {"id": 1, "name": "green-slime", "direction_row": {"down": 0}},
            {"id": 2, "name": "red-slime", "direction_row": {"down": 0}},
            {"id": 3, "name": "bull", "direction_row": {"down": 0, "up": 1, "left": 2, "right": 3, "right-idle": 7, "left-idle": 6, "up-idle": 5, "down-idle": 4, "down-attack": 8}, "idle-cols": 4, "move-cols": 6},
            {"id": 4, "name": "bull", "direction_row": {"down": 0, "up": 1, "left": 2, "right": 3, "right-idle": 7, "left-idle": 6, "up-idle": 5, "down-idle": 4, "down-attack": 8}, "idle-cols": 4, "move-cols": 6},
        ]

    def add_enemy(self, enemy_id, enemy_data):
        print(f"Enemy Controller-Enemy Data: {enemy_data}")
        enemy = Enemy(
            eid=enemy_id,
            x=enemy_data.get("x", 0),
            y=enemy_data.get("y", 0),
            rows=enemy_data.get("rows", 1),
            columns=enemy_data.get("columns", 11),
            enemy_type=enemy_data.get("type", "green-slime"),
            current_map=enemy_data.get("current_map", "Test_01"),
            hp=enemy_data.get("hp", 10),
            speed=enemy_data.get("speed", 100.0),
            frame_speed=enemy_data.get("frame_speed", 0.12),
            directions=enemy_data.get("directions", ["down"]),
            z_index=enemy_data.get("z_index", 0),
            c_h_padding=enemy_data.get("c_h_padding", 0),
            c_v_padding=enemy_data.get("c_v_padding", 0),
            direction_row=self.loaded_enemies[enemy_id - 1]["direction_row"]
        )
        self.enemies[enemy_id] = enemy

    def update(self, dt, current_map_name=None):
        for enemy in list(self.enemies.values()):
            enemy.update(dt)


    # def draw(self, surface, cam_rect, current_map_name=None):
    #     for enemy in list(self.enemies.values()):
    #         print(f"Enemy Z Index: {enemy.z_index}")
    #         if current_map_name and enemy.current_map != current_map_name:
    #             continue
    #         draw_x = enemy.x - cam_rect.x
    #         draw_y = enemy.y - cam_rect.y
    #         if enemy.image:
    #             surface.blit(enemy.image, (draw_x, draw_y))
    #         else:
    #             pygame.draw.rect(surface, (255, 0, 0), (draw_x, draw_y, 32, 32))
