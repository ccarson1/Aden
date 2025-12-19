import pygame
import pygame
import sys
import sqlite3
import os
import config as config
from client.menu.menu_screen import MenuScreen

# ========================
# --- Menu Manager System
# ========================

class MenuManager:
    def __init__(self):
        self.screens = {}
        self.active_screen = None
        # Nav bar
        self.nav_buttons = []

    def draw_nav_bar(self, surface):
        if not self.active_screen:
            return
        # Background
        pygame.draw.rect(surface, config.DARK_GRAY, (0, 0, config.WIDTH, config.NAV_HEIGHT))
        gap = 5
        btn_x = gap
        btn_y = 8
        btn_w = config.WIDTH // 10 - gap
        btn_h = 34
        self.nav_buttons = []

        for name in self.screens.keys():
            rect = pygame.Rect(btn_x, btn_y, btn_w, btn_h)
            color = config.LIGHT_GRAY if name == self.active_screen else config.GRAY
            pygame.draw.rect(surface, color, rect, border_radius=6)
            pygame.draw.rect(surface, config.WHITE, rect, 2, border_radius=6)

            txt = config.font_small.render(name, True, config.WHITE)
            surface.blit(txt, (rect.centerx - txt.get_width()//2, rect.centery - txt.get_height()//2))

            self.nav_buttons.append((rect, name))
            btn_x += btn_w + gap

    def handle_nav_click(self, pos):
        for rect, name in self.nav_buttons:
            if rect.collidepoint(pos):
                self.switch_screen(name)
                return
    def add_screen(self, screen: MenuScreen):
        self.screens[screen.name] = screen
        if self.active_screen is None:
            self.active_screen = screen.name
    def switch_screen(self, screen_name):
        if self.active_screen == screen_name:
            # Hide the screen if it's already active
            self.active_screen = None
        else:
            self.active_screen = screen_name
    def draw(self, surface):
        # Draw nav bar on top
        self.draw_nav_bar(surface)
        if self.active_screen:
            self.screens[self.active_screen].draw(surface)
    def handle_mouse_down(self, pos, button):
        if self.active_screen: self.screens[self.active_screen].handle_mouse_down(pos, button)
    def handle_mouse_up(self, pos, button):
        if self.active_screen: self.screens[self.active_screen].handle_mouse_up(pos, button)
    def handle_mouse_motion(self, pos):
        if self.active_screen: self.screens[self.active_screen].handle_mouse_motion(pos)
    def handle_key_down(self, key):
        if self.active_screen: self.screens[self.active_screen].handle_key_down(key)
