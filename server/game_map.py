# # server/game_map.py
# from pytmx import TiledMap
# import pygame

# class GameMap:
#     def __init__(self, tmx_file):
#         self.tmx_data = TiledMap(tmx_file)
#         self.tile_size = self.tmx_data.tilewidth  # auto-detect (likely 32)


#         self.tiles = []
        

#         # List all attributes (including callables)
#         for attr in dir(self.tmx_data):
#             value = getattr(self.tmx_data, attr)
#             is_callable = callable(value)
#             #print(f"{attr}: {'callable' if is_callable else type(value)}")



#         # Loop through all tiles in the map
#         for gid, tile_props in self.tmx_data.tile_properties.items():
#             #print(f"GID {gid} has properties: {tile_props}")
#             #print(tile_props['id'])
#             # if tile_props['id'] == 5376:
#             #     print(tile_props)
#             #     print(gid)

#             if "z_index" in tile_props:
#                 self.tiles.append((gid, tile_props))

#         print(self.tiles)

#         self.z_index_map = {
#             gid: props["z_index"]
#             for gid, props in self.tiles
#             if "z_index" in props
#         }

#         self.colliders = []
#         for layer in self.tmx_data.layers:
#             if hasattr(layer, "name") and layer.name.lower() == "collision":
#                 for tx, ty, gid in layer.tiles():
#                     if gid != 0:
#                         # Store as pixel rect: (x, y, w, h)
#                         self.colliders.append(
#                             (tx * self.tile_size,
#                              ty * self.tile_size,
#                              self.tile_size,
#                              self.tile_size)
#                         )
#                     tile_props = self.tmx_data.get_tile_properties_by_gid(gid)
#                     #print(f"tx={tx}, ty={ty}, gid={gid}, tile_props={tile_props}")

#         FLIP_MASK = 0x1FFFFFFF

        
#         # --- Elevation colliders using tile properties ---
#         self.elevation_colliders = []

#         for layer in self.tmx_data.layers:
#             if hasattr(layer, "name") and layer.name.lower() == "elevation":
#                 for tx, ty, gid in layer.tiles():
#                     if not gid:
#                         continue

#                     # gid might be a tuple like (image_path, (x, y, w, h), TileFlags)
#                     z_index = 0

#                     # Try matching against tile_properties keys
#                     for known_gid, props in self.tmx_data.tile_properties.items():
#                         if isinstance(known_gid, tuple) and isinstance(gid, tuple):
#                             # Compare by image filename and source rect
#                             if (
#                                 known_gid[0] == gid[0]
#                                 and known_gid[1][:2] == gid[1][:2]  # x, y match
#                             ):
#                                 if "z_index" in props:
#                                     z_index = props["z_index"]
#                                     break

#                     rect = (
#                         tx * self.tile_size,
#                         ty * self.tile_size,
#                         self.tile_size,
#                         self.tile_size
#                     )

#                     self.elevation_colliders.append({
#                         "rect": rect,
#                         "z_index": z_index,
#                         "gid": gid
#                     })

#         # # --- Add any tile with z_index from global tile_properties ---
#         # for gid, tile_props in self.tmx_data.tile_properties.items():
#         #     if "z_index" in tile_props:
#         #         # If it’s not already part of the elevation layer, add it
#         #         # (optional check to avoid duplicates)
#         #         exists = any(c["gid"] == gid for c in self.elevation_colliders)
#         #         if not exists:
#         #             rect = (0, 0, tile_props.get("width", 16), tile_props.get("height", 16))
#         #             self.elevation_colliders.append({
#         #                 "rect": rect,
#         #                 "z_index": tile_props["z_index"],
#         #                 "gid": gid
#         #             })




#         # print("Elevation colliders:")
#         # for c in self.elevation_colliders:
#         #     print(c)



#     def is_collision_tile(self, x, y):
#         """Return True if (x, y) collides with any collision rect."""
#         for (tx, ty, w, h) in self.colliders:
#             if tx <= x < tx + w and ty <= y < ty + h:
#                 return True
#         return False

#     def is_elevation_tile(self, x, y):
#         """Return the z_index of the elevation tile at (x, y), or None if no tile."""
#         for elev in self.elevation_colliders:
#             rect = elev["rect"]
#             z_index = elev["z_index"]
#             tx, ty, w, h = rect
#             if tx <= x < tx + w and ty <= y < ty + h:
#                 return z_index  # return the tile's z_index
#         return None  # no elevation tile here









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
                    self.colliders.append((
                        tx * self.tile_size,
                        ty * self.tile_size,
                        self.tile_size,
                        self.tile_size
                    ))

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
        for tx, ty, w, h in self.colliders:
            if tx <= x < tx + w and ty <= y < ty + h:
                return True
        return False

    def is_elevation_tile(self, x, y):
        for elev in self.elevation_colliders:
            tx, ty, w, h = elev["rect"]
            if tx <= x < tx + w and ty <= y < ty + h:
                return elev["z_index"]
        return None

