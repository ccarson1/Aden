import pygame
import config as config
from client.menu.menu_screen import MenuScreen

class CookingScreen(MenuScreen):
    def __init__(self): super().__init__("Cooking")
    def draw(self, surface):
        surface.fill((50, 50, 30), rect=pygame.Rect(0, config.NAV_HEIGHT, config.WIDTH, config.WIDTH - config.NAV_HEIGHT))
        surface.blit(config.font_large.render("Cooking Station", True, config.WHITE), (100, config.NAV_HEIGHT + 50))