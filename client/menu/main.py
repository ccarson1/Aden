import pygame
import sys
import sqlite3
import os
import config as config
from client.menu.menu_screen import MenuScreen
from client.menu.menu_manager import MenuManager
from client.menu.inventory import InventorySystem
from client.menu.alchemy_screen import AlchemyScreen
from client.menu.crafting_screen import CraftingScreen
from client.menu.item import Item

#pygame.init()

inventory = InventorySystem()


# Sample items
sample_items = [
    Item("Health Potion", 5, "potion", config.ITEM_COLORS["potion"], {}, True, "potions/Transperent/Icon1.png", spoil=20),
    Item("Health Potion", 2, "potion", config.ITEM_COLORS["potion"], {}, True, "potions/Transperent/Icon1.png", spoil=50),
    Item("Mana Potion", 3, "potion", config.ITEM_COLORS["potion"], {}, True, "potions/Transperent/Icon3.png", spoil=80),

    Item("Jasmine", 6, "ingredient", config.ITEM_COLORS["ingredient"], {}, True, "items/item381.png"),

    Item("Iron Sword", 1, "weapon", config.ITEM_COLORS["weapon"], {"attack": 5},
         False, "items/item1.png", level=1, xp=60, max_xp=100),

    Item("Leather Armor", 1, "armor", config.ITEM_COLORS["armor"], {"defense": 3},
         False, "items/item123.png"),

    Item("Iron Helmet", 1, "armor", config.ITEM_COLORS["armor"], {"defense": 2},
         False, "items/item117.png"),

    Item("Lucky Charm", 1, "accessory", config.ITEM_COLORS["accessory"], {"luck": 5},
         False, "items/item102.png"),

    Item("Monster Crystal", 1, "material", config.ITEM_COLORS["material"], {},
         True, "items/item256.png", level=1, xp=13, max_xp=50),
    Item("Monster Crystal", 1, "material", config.ITEM_COLORS["material"], {},
         True, "items/item256.png", level=1, xp=13, max_xp=50),
    Item("Monster Crystal", 1, "material", config.ITEM_COLORS["material"], {},
         True, "items/item256.png", level=1, xp=30, max_xp=50),

    Item("Potion Crystal", 1, "material", config.ITEM_COLORS["material"], {},
         False, "items/item270.png"),
]


# ========================
# --- Game Menu Screen
# ========================
class GameMenuScreen(MenuScreen):
    def __init__(self):
        super().__init__("Menu")
        self.buttons = []
        self.create_buttons()

    def create_buttons(self):
        # x, y, width, height
        start_x = config.WIDTH // 2 - 80
        start_y = config.WIDTH // 2 - 60
        btn_w, btn_h = 160, 40
        gap = 20

        self.buttons = [
            {"label": "Save", "rect": pygame.Rect(start_x, start_y, btn_w, btn_h)},
            {"label": "Load", "rect": pygame.Rect(start_x, start_y + (btn_h + gap), btn_w, btn_h)},
            {"label": "Exit", "rect": pygame.Rect(start_x, start_y + 2*(btn_h + gap), btn_w, btn_h)},
        ]

    def draw(self, surface):
        width, height = surface.get_size()  # Use actual surface size

        # Dim background
        overlay = pygame.Surface((width, height), pygame.SRCALPHA)
        overlay.fill((0,0,0,180))  # 180 alpha
        surface.blit(overlay, (0, 0))

        # Center buttons dynamically
        btn_w, btn_h = 160, 40
        gap = 20
        start_x = width // 2 - btn_w // 2
        start_y = height // 2 - (btn_h*3 + gap*2)//2  # vertically center 3 buttons

        for i, btn in enumerate(self.buttons):
            rect = pygame.Rect(start_x, start_y + i*(btn_h + gap), btn_w, btn_h)
            pygame.draw.rect(surface, config.GRAY, rect, border_radius=6)
            pygame.draw.rect(surface, config.WHITE, rect, 2, border_radius=6)
            txt = config.font_medium.render(btn["label"], True, config.WHITE)
            surface.blit(txt, (rect.centerx - txt.get_width()//2,
                            rect.centery - txt.get_height()//2))


    def handle_mouse_down(self, pos, button):
        if button != 1:  # only left click
            return
        for btn in self.buttons:
            if btn["rect"].collidepoint(pos):
                if btn["label"] == "Save":
                    inventory.save_to_db()
                elif btn["label"] == "Load":
                    inventory.load_from_db()
                elif btn["label"] == "Exit":
                    pygame.quit()
                    sys.exit()




# ========================
# --- Other Screens
# ========================

# class AlchemyScreen(MenuScreen):
#     def __init__(self): super().__init__("Alchemy")
#     def draw(self, surface):
#         surface.fill((50, 30, 50), rect=pygame.Rect(0, config.NAV_HEIGHT, config.WIDTH, config.WIDTH - config.NAV_HEIGHT))
#         surface.blit(config.font_large.render("Alchemy Lab", True, config.WHITE), (100, config.NAV_HEIGHT + 50))

# class CraftingScreen(MenuScreen):
#     def __init__(self): super().__init__("Crafting")
#     def draw(self, surface):
#         surface.fill((30, 50, 30), rect=pygame.Rect(0, config.NAV_HEIGHT, config.WIDTH, config.WIDTH - config.NAV_HEIGHT))
#         surface.blit(config.font_large.render("Crafting Bench", True, config.WHITE), (100, config.NAV_HEIGHT + 50))

class CookingScreen(MenuScreen):
    def __init__(self): super().__init__("Cooking")
    def draw(self, surface):
        surface.fill((50, 50, 30), rect=pygame.Rect(0, config.NAV_HEIGHT, config.WIDTH, config.WIDTH - config.NAV_HEIGHT))
        surface.blit(config.font_large.render("Cooking Station", True, config.WHITE), (100, config.NAV_HEIGHT + 50))

class SkillsScreen(MenuScreen):
    def __init__(self): super().__init__("Skills")
    def draw(self, surface):
        surface.fill((30, 30, 50), rect=pygame.Rect(0, config.NAV_HEIGHT, config.WIDTH, config.WIDTH - config.NAV_HEIGHT))
        surface.blit(config.font_large.render("Skills", True, config.WHITE), (100, config.NAV_HEIGHT + 50))

class EnchantingScreen(MenuScreen):
    def __init__(self): super().__init__("Enchanting")
    def draw(self, surface):
        surface.fill((50, 30, 50), rect=pygame.Rect(0, config.NAV_HEIGHT, config.WIDTH, config.WIDTH - config.NAV_HEIGHT))
        surface.blit(config.font_large.render("Enchanting Table", True, config.WHITE), (100, config.NAV_HEIGHT + 50))

class GuildScreen(MenuScreen):
    def __init__(self): super().__init__("Guild")
    def draw(self, surface):
        surface.fill((30, 50, 50), rect=pygame.Rect(0, config.NAV_HEIGHT, config.WIDTH, config.WIDTH - config.NAV_HEIGHT))
        surface.blit(config.font_large.render("Guild Hall", True, config.WHITE), (100, config.NAV_HEIGHT + 50))

class QuestsScreen(MenuScreen):
    def __init__(self): super().__init__("Quests")
    def draw(self, surface):
        surface.fill((50, 50, 50), rect=pygame.Rect(0, config.NAV_HEIGHT, config.WIDTH, config.WIDTH - config.NAV_HEIGHT))
        surface.blit(config.font_large.render("Quest Log", True, config.WHITE), (100, config.NAV_HEIGHT + 50))

class SettingsScreen(MenuScreen):
    def __init__(self): super().__init__("Settings")
    def draw(self, surface):
        surface.fill((40, 40, 40), rect=pygame.Rect(0, config.NAV_HEIGHT, config.WIDTH, config.WIDTH - config.NAV_HEIGHT))
        surface.blit(config.font_large.render("Settings", True, config.WHITE), (100, config.NAV_HEIGHT + 50))

# ========================
# --- Main Loop
# ========================
def main():
    
    inventory.database.init_db()
    inventory.database.load_from_db()

    # preload sample items if inventory empty
    if all(i is None for i in inventory.database.inventory):
        for idx,item in enumerate(sample_items):
            inventory.database.inventory[idx] = item

    clock = pygame.time.Clock()
    manager = MenuManager()

    # Add screens
    manager.add_screen(GameMenuScreen())
    manager.add_screen(InventorySystem())
    manager.add_screen(AlchemyScreen())
    manager.add_screen(CraftingScreen())
    manager.add_screen(CookingScreen())
    manager.add_screen(SkillsScreen())
    manager.add_screen(EnchantingScreen())
    manager.add_screen(GuildScreen())
    manager.add_screen(QuestsScreen())
    manager.add_screen(SettingsScreen())

    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); sys.exit()
            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_m: manager.switch_screen("Menu")
                elif e.key == pygame.K_i: manager.switch_screen("Inventory")
                elif e.key == pygame.K_a: manager.switch_screen("Alchemy")
                elif e.key == pygame.K_c: manager.switch_screen("Crafting")
                elif e.key == pygame.K_k: manager.switch_screen("Cooking")
                elif e.key == pygame.K_l: manager.switch_screen("Skills")
                elif e.key == pygame.K_e: manager.switch_screen("Enchanting")
                elif e.key == pygame.K_g: manager.switch_screen("Guild")
                elif e.key == pygame.K_q: manager.switch_screen("Quests")
                elif e.key == pygame.K_s: manager.switch_screen("Settings")
                manager.handle_key_down(e.key)
            elif e.type == pygame.MOUSEMOTION: manager.handle_mouse_motion(e.pos)
            elif e.type == pygame.MOUSEBUTTONDOWN:
                manager.handle_nav_click(e.pos)
                manager.handle_mouse_down(e.pos, e.button)
            elif e.type == pygame.MOUSEBUTTONUP: manager.handle_mouse_up(e.pos, e.button)

        #config.screen.fill(config.BLACK)
        manager.draw(config.screen)
        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()
