# class Player:
#     def __init__(self, player_id, name, frame_w, frame_h, x=100, y=100):
#         self.id = player_id
#         self.name = name
#         self.x = x
#         self.y = y
#         self.frame_w = frame_w
#         self.frame_h = frame_h
#         self.direction = "down"
#         self.moving = False
#         self.current_map = None  # default map
#         self.needs_save = False

#         # Interpolation state
#         self.prev_x = x
#         self.prev_y = y
#         self.target_x = x
#         self.target_y = y
#         self.last_update_time = 0.0
#         self.prev_map = self.current_map 



class NPC:
    pass  # Future expansion

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

class GameMap:
    pass  # Load maps, Tiled integration
