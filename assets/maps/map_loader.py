# assets/maps/map_loader.py
import pygame
import pytmx
from pytmx.util_pygame import load_pygame
from pytmx import TiledTileLayer

class AnimatedTile:
    def __init__(self, frames, tmx_data):
        self.frames = [tmx_data.get_tile_image_by_gid(frame.gid) for frame in frames]
        self.durations = [frame.duration for frame in frames]
        self.index = 0
        self.timer = 0
        self.image = self.frames[0]

    def update(self, dt):
        self.timer += dt
        if self.timer >= self.durations[self.index] / 1000:  # convert ms -> s
            self.timer = 0
            self.index = (self.index + 1) % len(self.frames)
            self.image = self.frames[self.index]

class TileLayer:
    def __init__(self, tmx_data, layer_index):
        self.layer = tmx_data.layers[layer_index]
        self.tmx_data = tmx_data
        self.tiles = []

        for x, y, gid in self.layer:
            if gid == 0:
                continue
            props = tmx_data.get_tile_properties_by_gid(gid) or {}
            anim = props.get("frames")
            if anim:
                self.tiles.append((x, y, AnimatedTile(anim, tmx_data)))
            else:
                self.tiles.append((x, y, tmx_data.get_tile_image_by_gid(gid)))

    def update(self, dt):
        for _, _, tile in self.tiles:
            if isinstance(tile, AnimatedTile):
                tile.update(dt)

    def draw(self, surface, offset=(0, 0), alpha=None):
        ox, oy = offset
        for x, y, tile in self.tiles:
            draw_x = x * self.tmx_data.tilewidth + ox
            draw_y = y * self.tmx_data.tileheight + oy
            if isinstance(tile, AnimatedTile):
                img = tile.image
            else:
                img = tile

            if img:
                img_copy = img.copy()
                if alpha is not None:
                    img_copy.set_alpha(alpha)
                surface.blit(img_copy, (draw_x, draw_y))
