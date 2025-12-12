

# client/entities/game_map.py
import pygame
from assets.maps.map_loader import TileLayer, load_pygame
from pytmx import TiledTileLayer

class Portal:
    def __init__(self, rect, target_map, spawn_x, spawn_y, player_index):
        self.rect = rect
        self.target_map = target_map
        self.spawn_x = spawn_x
        self.spawn_y = spawn_y
        self.player_index = player_index
        

class GameMap:
    def __init__(self, tmx_file):
        self.tmx_data = load_pygame(tmx_file, pixelalpha=True)
        self.opaque_alpha = 180  # default semi-transparent
        self.opaque_tiles = []   # store rects of opaque tiles
        # Store light tiles
        self.light_tiles = []

        # --- Tile layers for drawing & animation ---
        self.layers = [
            TileLayer(self.tmx_data, i)
            for i, layer in enumerate(self.tmx_data.layers)
            if hasattr(layer, "tiles")  # include all layers that have tiles
        ]

        # Track opaque tile rects for collision fading
        # self.opaque_tiles = []
        # for layer in self.layers:
        #     if layer.layer.name.lower() == "foreground_opaque":
        #         for x, y, _ in layer.tiles:
        #             rect = pygame.Rect(
        #                 x * self.tmx_data.tilewidth,
        #                 y * self.tmx_data.tileheight,
        #                 self.tmx_data.tilewidth,
        #                 self.tmx_data.tileheight
        #             )
        #             self.opaque_tiles.append(rect)

        # Track opaque tile rects for collision fading
        self.opaque_tiles = []
        for layer in self.layers:
            if layer.layer.name.lower() == "foreground_opaque":
                # Get the layer's z_index (default 0)
                layer_z = getattr(layer, "z_index", 0)

                for x, y, _ in layer.tiles:
                    rect = pygame.Rect(
                        x * self.tmx_data.tilewidth,
                        y * self.tmx_data.tileheight,
                        self.tmx_data.tilewidth,
                        self.tmx_data.tileheight
                    )
                    # Store both rect and z_index
                    self.opaque_tiles.append({"rect": rect, "z_index": layer_z})

            if hasattr(layer, "tiles"):
                for x, y, tile in layer.tiles:
                    # Get the GID at this position in the original pytmx layer
                    gid = layer.layer.data[y][x]  # TMX layer stores GID in data[y][x]
                    if gid == 0:
                        continue
                    props = self.tmx_data.get_tile_properties_by_gid(gid) or {}
                    radius = props.get("light_radius")
                    if radius:
                        rect = pygame.Rect(
                            x * self.tmx_data.tilewidth,
                            y * self.tmx_data.tileheight,
                            self.tmx_data.tilewidth,
                            self.tmx_data.tileheight
                        )
                        self.light_tiles.append((rect, int(radius)))
                        print(f"Light tile at ({x},{y}) with radius {radius}")  # debug

        #--- Colliders ---
        # self.colliders = []
        # for layer in self.tmx_data.layers:
        #     if layer.name.lower() == "collision":
        #         for x, y, gid in layer:
        #             if gid != 0:
        #                 rect = pygame.Rect(
        #                     x * self.tmx_data.tilewidth,
        #                     y * self.tmx_data.tileheight,
        #                     self.tmx_data.tilewidth,
        #                     self.tmx_data.tileheight
        #                 )
        #                 self.colliders.append(rect)

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
                        
                        # Get z_level from tile properties (default 0)
                        props = self.tmx_data.get_tile_properties_by_gid(gid) or {}
                        z_index = int(props.get("z_index", 0))
                        
                        # Store both rect and z_level
                        self.colliders.append({"rect": rect, "z_index": z_index})

        self.elevation_colliders = []
        for layer in self.tmx_data.layers:
            if layer.name.lower() == "elevation":
                for x, y, gid in layer:
                    if gid != 0:
                        rect = pygame.Rect(
                            x * self.tmx_data.tilewidth,
                            y * self.tmx_data.tileheight,
                            self.tmx_data.tilewidth,
                            self.tmx_data.tileheight
                        )

                        # Get z_index from tile properties (default 0)
                        props = self.tmx_data.get_tile_properties_by_gid(gid) or {}
                        z_index = int(props.get("z_index", 0))

                        # Store both rect and z_index
                        self.elevation_colliders.append({"rect": rect, "z_index": z_index})
                        # print(f"Evelation Colliders")
                        # print(self.elevation_colliders)

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
                        player_index = props.get("player_index", 0)
                        rect = pygame.Rect(
                            x * self.tmx_data.tilewidth,
                            y * self.tmx_data.tileheight,
                            self.tmx_data.tilewidth,
                            self.tmx_data.tileheight
                        )
                        print(f"Tile ({x},{y}) gid={gid}, target_map={target_map}, player_index={player_index}, sx={spawn_x}, sy={spawn_y}")  # debug
                        if target_map:
                            self.portals.append(Portal(rect, target_map, int(float(spawn_x)), int(float(spawn_y)), player_index))

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

    



    def draw(self, surface, offset=(0,0), alpha=None, draw_only=None):
        ox, oy = offset

        draw_only = draw_only or []  # list of layer types to draw, empty = draw all

        # Separate layers
        background_layers = []
        decoration_layers = []
        foreground_layers = []
        foreground_opaque_layers = []

        for layer in self.layers:
            name = layer.layer.name.lower()
            if name in ["background", "ground"]:
                background_layers.append(layer)
            elif name in ["decoration", "objects"]:
                decoration_layers.append(layer)
            elif name in ["foreground", "above"]:
                foreground_layers.append(layer)
            elif name == "foreground_opaque":
                foreground_opaque_layers.append(layer)
            else:
                decoration_layers.append(layer)

        # Draw only requested layers
        if not draw_only or "background" in draw_only or "ground" in draw_only:
            for layer in background_layers:
                layer.draw(surface, offset, alpha)

        if not draw_only or "decoration" in draw_only or "objects" in draw_only:
            for layer in decoration_layers:
                layer.draw(surface, offset, alpha)

        if not draw_only or "foreground" in draw_only or "above" in draw_only:
            for layer in foreground_layers:
                layer.draw(surface, offset, alpha)

        if not draw_only or "foreground_opaque" in draw_only:
            for layer in foreground_opaque_layers:
                layer.draw(surface, offset, alpha)



    def get_portal_at(self, player_rect):
        """
        Returns the portal that the player is colliding with, or None.
        """
        for portal in self.portals:
            if portal.rect.colliderect(player_rect):
                return portal
        return None
