# # server/entities/game_map.py or client/maps/game_map.py
# import pygame
# from assets.maps.map_loader import TileLayer, load_pygame
# from pytmx import TiledTileLayer

# class Portal:
#     def __init__(self, rect, target_map, spawn_x, spawn_y):
#         self.rect = rect
#         self.target_map = target_map
#         self.spawn_x = spawn_x
#         self.spawn_y = spawn_y

# class GameMap:
#     def __init__(self, tmx_file):
#         self.tmx_data = load_pygame(tmx_file, pixelalpha=True)

#         # --- Tile layers for drawing & animation ---
#         self.layers = [
#             TileLayer(self.tmx_data, i)
#             for i, layer in enumerate(self.tmx_data.layers)
#             if isinstance(layer, TiledTileLayer)
#         ]

#         # --- Colliders ---
#         self.colliders = []
#         for layer in self.tmx_data.layers:
#             if layer.name.lower() == "collision":
#                 for x, y, gid in layer:
#                     if gid != 0:
#                         rect = pygame.Rect(
#                             x * self.tmx_data.tilewidth,
#                             y * self.tmx_data.tileheight,
#                             self.tmx_data.tilewidth,
#                             self.tmx_data.tileheight
#                         )
#                         self.colliders.append(rect)

#         # --- Portals ---
#         self.portals = []
#         for layer in self.tmx_data.layers:
#             if layer.name.lower() == "portal":
#                 for x, y, gid in layer:
#                     if gid != 0:
#                         props = self.tmx_data.get_tile_properties_by_gid(gid) or {}
#                         target_map = props.get("target_map")
#                         spawn_x = props.get("spawn_x", 0)
#                         spawn_y = props.get("spawn_y", 0)
#                         rect = pygame.Rect(
#                             x * self.tmx_data.tilewidth,
#                             y * self.tmx_data.tileheight,
#                             self.tmx_data.tilewidth,
#                             self.tmx_data.tileheight
#                         )
#                         if target_map:
#                             self.portals.append(Portal(rect, target_map, spawn_x, spawn_y))

#         # Optional default player start
#         self.player_start = (0, 0)
#         for layer in self.tmx_data.layers:
#             if layer.name.lower() == "player_start":
#                 for obj in layer:
#                     self.player_start = (obj.x, obj.y)
#                     break

#     def update(self, dt):
#         for layer in self.layers:
#             layer.update(dt)

#     def draw(self, surface):
#         for layer in self.layers:
#             layer.draw(surface)

# client/entities/game_map.py
import pygame
from assets.maps.map_loader import TileLayer, load_pygame
from pytmx import TiledTileLayer

class Portal:
    def __init__(self, rect, target_map, spawn_x, spawn_y):
        self.rect = rect
        self.target_map = target_map
        self.spawn_x = spawn_x
        self.spawn_y = spawn_y

class GameMap:
    def __init__(self, tmx_file):
        self.tmx_data = load_pygame(tmx_file, pixelalpha=True)

        # --- Tile layers for drawing & animation ---
        self.layers = [
            TileLayer(self.tmx_data, i)
            for i, layer in enumerate(self.tmx_data.layers)
            if isinstance(layer, TiledTileLayer)
        ]

        # --- Colliders ---
        self.colliders = []
        for layer in self.tmx_data.layers:
            if layer.name.lower() == "collision":
                for x, y, gid in layer:
                    if gid != 0:
                        rect = pygame.Rect(
                            x * self.tmx_data.tilewidth,
                            y * self.tmx_data.tileheight,
                            self.tmx_data.tilewidth,
                            self.tmx_data.tileheight
                        )
                        self.colliders.append(rect)

        # --- Portals ---
        self.portals = []
        for layer in self.tmx_data.layers:
            if layer.name.lower() == "portal":
                for x, y, gid in layer:
                    if gid != 0:
                        props = self.tmx_data.get_tile_properties_by_gid(gid) or {}
                        target_map = props.get("target_map")
                        spawn_x = props.get("spawn_x", 0)
                        spawn_y = props.get("spawn_y", 0)
                        rect = pygame.Rect(
                            x * self.tmx_data.tilewidth,
                            y * self.tmx_data.tileheight,
                            self.tmx_data.tilewidth,
                            self.tmx_data.tileheight
                        )
                        print(f"Tile ({x},{y}) gid={gid}, target_map={target_map}")  # debug
                        if target_map:
                            self.portals.append(Portal(rect, target_map, int(float(spawn_x)), int(float(spawn_y))))

        print(f"Total portals loaded: {len(self.portals)}")

        # --- Optional default player start ---
        self.player_start = (0, 0)
        for layer in self.tmx_data.layers:
            if layer.name.lower() == "player_start":
                for obj in layer:
                    self.player_start = (obj.x, obj.y)
                    break

    def update(self, dt):
        for layer in self.layers:
            layer.update(dt)

    def draw(self, surface):
        for layer in self.layers:
            layer.draw(surface)

    def get_portal_at(self, player_rect):
        """
        Returns the portal that the player is colliding with, or None.
        """
        for portal in self.portals:
            if portal.rect.colliderect(player_rect):
                return portal
        return None
