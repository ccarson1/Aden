# client/entities/enemy_controller.py

from client.graphics.enemy_sprite import EnemySprite
import pygame

class EnemyController:
    def __init__(self):
        self.enemies = {}  # id -> EnemySprite
        self.map_name = "Test_01"

    def add_enemy(self, enemy_id, x, y, enemy_type="green-slime", current_map="Test_01"):
        # Fallback if type is None
        if not enemy_type:
            enemy_type = "green-slime"
        self.enemies[enemy_id] = EnemySprite(x, y, current_map, enemy_type)

    def sync_from_server(self, enemy_list):
        for e in enemy_list:
            eid = e.get("id")
            if eid is None:
                continue
            ex = e.get("x", 0)
            ey = e.get("y", 0)
            etype = e.get("type") or "green-slime"
            

            if eid not in self.enemies:
                self.add_enemy(eid, ex, ey, etype, current_map=self.map_name)
            self.enemies[eid].apply_server_update(e)

    def update(self, dt, current_map):
        for enemy in self.enemies.values():
            enemy.update(dt)         # animation
            enemy.interpolate(dt)    # smoothing if implemented
            self.map_name = current_map

    # def draw(self, surface, cam_rect, current_map_name):
    #     for enemy in self.enemies.values():
    #         if enemy.current_map != current_map_name:
    #             continue
    #         # Draw enemy with camera offset
    #         draw_x = enemy.x - cam_rect.x
    #         draw_y = enemy.y - cam_rect.y
    #         surface.blit(enemy.image, (draw_x, draw_y))

    def draw(self, surface, cam_rect, current_map_name):
        for enemy in self.enemies.values():
            #print(f"[DEBUG] Enemy map: {enemy.current_map}, Current map: {current_map_name}")
            if enemy.current_map != current_map_name:
                continue

            draw_x = enemy.x - cam_rect.x
            draw_y = enemy.y - cam_rect.y

            # Draw debug rectangle
            #pygame.draw.rect(surface, (255, 0, 0), (draw_x, draw_y, enemy.frame_width, enemy.frame_height))

            # Draw sprite
            if hasattr(enemy, "image") and enemy.image:
                surface.blit(enemy.image, (draw_x, draw_y))
