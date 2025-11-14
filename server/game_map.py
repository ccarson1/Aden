# # server/game_map.py






import os
os.environ["SDL_VIDEODRIVER"] = "dummy"  # headless mode

import pygame
from pytmx import load_pygame

pygame.init()
pygame.display.set_mode((1, 1))

class GameMap:
    def __init__(self, tmx_file):
        self.tmx_data = load_pygame(tmx_file)
        self.tile_size = self.tmx_data.tilewidth
        self.map_width = self.tmx_data.width
        self.map_height = self.tmx_data.height

        self.colliders = []
        self.elevation_colliders = []
        self.teleport_tiles = []

        print(f"Loading map: {tmx_file}")
        print("Layers:", [layer.name for layer in self.tmx_data.layers if hasattr(layer, "name")])

        # --- COLLISION LAYER ---
        for layer in self.tmx_data.layers:
            if hasattr(layer, "name") and layer.name.lower() == "collision":
                for tx, ty, surf in layer.tiles():

                    # Calculate the rect for this tile
                    rect = pygame.Rect(
                        tx * self.tile_size,
                        ty * self.tile_size,
                        self.tile_size,
                        self.tile_size
                    )

                    # Get the GID from the TMX layer (tiles() does NOT include gid)
                    gid = layer.data[ty][tx]

                    # Read tile properties
                    props = self.tmx_data.get_tile_properties_by_gid(gid) or {}
                    z_index = int(props.get("z_index", 0))

                    # Store rect + z_index
                    self.colliders.append({
                        "rect": rect,
                        "z_index": z_index
                    })

        # --- ELEVATION LAYER ---
        for layer_index, layer in enumerate(self.tmx_data.layers):
            if hasattr(layer, "name") and layer.name.lower() == "elevation":
                for tx, ty, surf in layer.tiles():
                    gid = self.tmx_data.get_tile_gid(tx, ty, layer_index)
                    props = self.tmx_data.get_tile_properties_by_gid(gid)
                    z_index = props.get("z_index") if props else None

                    rect = (
                        tx * self.tile_size,
                        ty * self.tile_size,
                        self.tile_size,
                        self.tile_size
                    )
                    self.elevation_colliders.append({
                        "rect": rect,
                        "z_index": z_index
                    })
                    
        print(f"Elevation colliders: {len(self.elevation_colliders)}")
        for c in self.elevation_colliders[:20]:
            print(c)

        print(f"Elevation tiles: {len(self.elevation_colliders)}")

        # --- TILESET PROPERTIES (teleports, spawns, etc.) ---
        for gid, props in self.tmx_data.tile_properties.items():
            if not props:
                continue
            if "target_map" in props:
                self.teleport_tiles.append({
                    "gid": gid,
                    "target_map": props["target_map"],
                    "spawn_x": props.get("spawn_x", 0),
                    "spawn_y": props.get("spawn_y", 0),
                    "player_index": props.get("player_index")
                })

        print(f"Collision tiles: {len(self.colliders)}")
        print(f"Elevation tiles: {len(self.elevation_colliders)}")
        print(f"Teleport tiles: {len(self.teleport_tiles)}")

    def get_tile_properties(self, gid):
        return self.tmx_data.tile_properties.get(gid, {})

    def is_collision_tile(self, x, y):
        for col in self.colliders:

            if isinstance(col, dict):
                rect = col["rect"]
                tx, ty, w, h = rect.x, rect.y, rect.width, rect.height
            else:
                tx, ty, w, h = col

            if x >= tx and x < tx + w and y >= ty and y < ty + h:
                return True

    def is_elevation_tile(self, x, y):
        for elev in self.elevation_colliders:
            tx, ty, w, h = elev["rect"]
            if tx <= x < tx + w and ty <= y < ty + h:
                return elev["z_index"]
        return None

