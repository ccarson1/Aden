import pygame


class Map:
    def __init__(self, map_id, tmx_data):
        self.map_id = map_id
        self.tmx_data = tmx_data
        self.width = tmx_data.width * tmx_data.tilewidth
        self.height = tmx_data.height * tmx_data.tileheight