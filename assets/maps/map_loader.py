# assets/maps/map_loader.py
import pygame
import pytmx

class MapLoader:
    def __init__(self, filename, scale=1):
        self.tmx_data = pytmx.load_pygame(filename, pixelalpha=True)
        self.scale = scale

        self.width = self.tmx_data.width * self.tmx_data.tilewidth
        self.height = self.tmx_data.height * self.tmx_data.tileheight

        # --- Store collision rects from "Collision" layer ---
        self.colliders = []
        for layer in self.tmx_data.layers:
            if layer.name == "Collision":
                for x, y, gid in layer:
                    if gid != 0:  # skip empty tiles
                        rect = pygame.Rect(
                            x * self.tmx_data.tilewidth,
                            y * self.tmx_data.tileheight,
                            self.tmx_data.tilewidth,
                            self.tmx_data.tileheight
                        )
                        self.colliders.append(rect)

    def draw(self, surface):
        """Draw ALL visible layers, including Collision."""
        for layer in self.tmx_data.visible_layers:
            if isinstance(layer, pytmx.TiledTileLayer):
                for x, y, gid in layer:
                    tile = self.tmx_data.get_tile_image_by_gid(gid)
                    if tile:
                        surface.blit(
                            tile,
                            (x * self.tmx_data.tilewidth, y * self.tmx_data.tileheight)
                        )
