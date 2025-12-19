import pygame
import sys
import sqlite3
import os
import config as config
from client.menu.menu_screen import MenuScreen
from client.menu.item import Item
from client.menu.database import Database
import client.menu.gadgets as gadgets
import client.menu.container as cont
import client.menu.container_events as container_events





# ========================
# --- Crafting Screen
# ========================
class CraftingScreen(MenuScreen):
    def __init__(self):
        super().__init__("Crafting")
        self.hover_slot = None
        self.dragging_item = None
        self.dragging_from = None
        self.message = ""
        self.split_popup = None
        self.scroll_y = 0
        self.max_scroll = 0
        self.tabs = ["material", "armor", "weapon", "accessory"]
        self.active_tab = "material"
        self.tab_rects = []
        self.visible_slot_map = []
        self.inventory_area = (config.INV_START_X, config.INV_START_Y, config.CFT_WIDTH, config.CFT_HEIGHT)
        self.database = Database()



    # --- Helper: check if two items can stack ---
    def can_stack(self, item1, item2):
        if not item1 or not item2:
            return False
        # Must be stackable
        if not item1.get("stackable", True) or not item2.get("stackable", True):
            return False
        # Name and type must match
        if item1["name"] != item2["name"] or item1["type"] != item2["type"]:
            return False
        # Only merge spoilable items if spoil matches exactly
        spoil1 = item1.get("spoil")
        spoil2 = item2.get("spoil")
        if spoil1 is not None or spoil2 is not None:
            if spoil1 != spoil2:
                return False
        # Only merge levelable items if level and xp match exactly
        if item1.get("level") != item2.get("level") or item1.get("xp") != item2.get("xp"):
            return False
        return True




    def move_to_inventory(self, source_container, index):
        """Move an item from hotbar or equip back into the first empty inventory slot."""
        src = container_events.get_container(source_container, self.database)
        item = src[index]
        if not item:
            return

        # find first empty slot in inventory
        for i, slot in enumerate(self.database.inventory):
            if slot is None:
                self.database.inventory[i] = item
                src[index] = None
                self.message = f"Moved {item['name']} to inventory."
                return

        # no space
        self.message = "Inventory is full!"



    def handle_scroll(self, dy):
        self.scroll_y += dy
        self.scroll_y = max(0, min(self.scroll_y, self.max_scroll))  # clamp

    def draw(self, surface):

    
        # In draw()
        surface.fill((30, 30, 30), rect=pygame.Rect(0, config.NAV_HEIGHT, config.WIDTH, config.WIDTH - config.NAV_HEIGHT))

        
        # --- Stack All Button ---
        self.stack_all_rect = pygame.Rect(config.INV_START_X, config.INV_START_Y - 35, 100, 32)
        pygame.draw.rect(surface, config.LIGHT_GRAY, self.stack_all_rect, border_radius=6)
        pygame.draw.rect(surface, config.WHITE, self.stack_all_rect, 2, border_radius=6)
        txt = config.font_small.render("Stack All", True, config.BLACK)
        surface.blit(txt, (self.stack_all_rect.centerx - txt.get_width()//2, self.stack_all_rect.centery - txt.get_height()//2))

        # --- Sort by Type Button ---
        self.sort_type_rect = pygame.Rect(config.INV_START_X + 140, config.INV_START_Y - 35, 100, 32)
        pygame.draw.rect(surface, config.LIGHT_GRAY, self.sort_type_rect, border_radius=6)
        pygame.draw.rect(surface, config.WHITE, self.sort_type_rect, 2, border_radius=6)
        txt = config.font_small.render("Sort by Type", True, config.BLACK)
        surface.blit(txt, (self.sort_type_rect.centerx - txt.get_width()//2,
                        self.sort_type_rect.centery - txt.get_height()//2))
        
        # Panels
        
        pygame.draw.rect(surface, config.DARK_GRAY, self.inventory_area, border_radius=10)
        #surface.blit(font_medium.render("Inventory", True, config.WHITE), (INV_START_X + 160, INV_START_Y - 38))

        # pygame.draw.rect(surface, config.DARK_GRAY, (config.EQUIP_START_X - 20, config.EQUIP_START_Y - 20, 160, 360), border_radius=10)
        # surface.blit(config.font_medium.render("Equipment", True, config.WHITE), (config.EQUIP_START_X - 10, config.EQUIP_START_Y - 48))

        #gadgets.draw_stats_panel(self.database, surface)


        #self.draw_inventory_slots(surface)
        surface, self.total_height, self.max_scroll, self.scroll_y, self.visible_slot_map = cont.draw_inventory_slots(self.database, self.inventory_area, self.active_tab, self.dragging_item, self.dragging_from, self.hover_slot, self.scroll_y, config.CFT_COLS, surface)

        #self.draw_inventory_tabs(surface)
        self.tab_rects = gadgets.draw_inventory_tabs(surface, self.tabs, self.active_tab)
        gadgets.draw_material_slots(self.database, self.dragging_item, self.dragging_from, self.hover_slot, surface)
        #gadgets.draw_hotbar_slots(self.database, self.dragging_item, self.dragging_from, self.hover_slot, surface)

        # Drag ghost
        if self.dragging_item:
            mx, my = pygame.mouse.get_pos()
            ghost = pygame.Rect(mx - config.SLOT_SIZE // 2, my - config.SLOT_SIZE // 2, config.SLOT_SIZE, config.SLOT_SIZE)
            cont.draw_item(surface, self.database, self.dragging_item, ghost, config.font_small)

        # Tooltip
        if self.hover_slot and not self.dragging_item:
            container, idx = self.hover_slot
            item = container_events.get_container(container, self.database)[idx]
            if item:
                gadgets.draw_tooltip(surface, item)

        # Split menu
        if self.split_popup:
            gadgets.draw_split_popup(surface, self.split_popup)

        if self.message:
            surface.blit(config.font_small.render(self.message, True, config.RED), (20, config.WIDTH - 28))




    # --- Input Handling ---
    # def get_container(self, name):
    #     return {"inventory": self.database.inventory, "equip": self.database.equipment, "hotbar": self.database.hotbar}[name]

    def handle_mouse_down(self, pos, button):
        container_events.handle_mouse_down(self, pos, button)

   
    def handle_mouse_up(self, pos, button):
        container_events.handle_mouse_up(self, pos, button)

    


    def add_item_to_inventory(self, item):
        for i, it in enumerate(self.database.inventory):
            if it and self.can_stack(item, it):
                it["quantity"] += item["quantity"]
                return True
        # If no stackable match, put in first empty slot
        for i, it in enumerate(self.database.inventory):
            if it is None:
                self.database.inventory[i] = item
                return True
        return False



    def handle_mouse_motion(self, pos):
        self.hover_slot = None
        # Check filtered inventory slots
        for rect, idx in getattr(self, 'visible_slot_map', []):
            if rect.collidepoint(pos):
                self.hover_slot = ("inventory", idx)
                return

        # Equipment
        for i in range(len(config.EQUIP_SLOTS)):
            rect = pygame.Rect(config.EQUIP_START_X, config.EQUIP_START_Y + i*(config.SLOT_SIZE+config.EQUIP_SLOT_GAP), config.SLOT_SIZE, config.SLOT_SIZE)
            if rect.collidepoint(pos):
                self.hover_slot = ("equip", i)
                return
            
        # Crafting
        for i in range(len(config.CFT_SLOTS)):
            rect = pygame.Rect(config.CFT_START_X, config.CFT_START_Y + i*(config.SLOT_SIZE+config.CFT_SLOT_GAP), config.SLOT_SIZE, config.SLOT_SIZE)
            if rect.collidepoint(pos):
                self.hover_slot = ("equip", i)
                return

        # Hotbar
        for i in range(config.HOTBAR_SLOTS):
            rect = pygame.Rect(config.HOTBAR_START_X + i*(config.SLOT_SIZE+config.PADDING), config.HOTBAR_START_Y, config.SLOT_SIZE, config.SLOT_SIZE)
            if rect.collidepoint(pos):
                self.hover_slot = ("hotbar", i)
                return



    def _clear_drag(self):
        self.dragging_item = None
        self.dragging_from = None