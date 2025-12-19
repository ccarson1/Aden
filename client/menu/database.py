import pygame
import sys
import sqlite3
import os
import config as config
from client.menu.menu_screen import MenuScreen
from client.menu.item import Item


class Database:
    # --- Inventory & Containers ---

    inventory = [None] * config.TOTAL_INV_SLOTS
    equipment = [None] * len(config.EQUIP_SLOTS)
    crafting = [None] * len(config.CFT_SLOTS)
    hotbar = [None] * config.HOTBAR_SLOTS

    # --- Stats ---
    base_stats = {"attack": 10, "defense": 5, "hp": 100, "mana": 40, "luck": 0}
    current_status = {"hp": 85, "mana": 32, "stamina": 60}

    # Dynamic inventory size
    inventory = [None] * config.TOTAL_INV_SLOTS


    def init_db(self):
        conn = sqlite3.connect(config.DB_FILE)
        c = conn.cursor()
        c.execute("""CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            container TEXT,
            slot INTEGER,
            name TEXT,
            type TEXT,
            quantity INTEGER,
            color_r INTEGER,
            color_g INTEGER,
            color_b INTEGER,
            bonus TEXT,
            stackable INTEGER,
            image_path TEXT,
            level INTEGER,
            xp INTEGER,
            max_xp INTEGER,
            spoil INTEGER
        )""")
        conn.commit()
        conn.close()


    def save_to_db(self):
        conn = sqlite3.connect(config.DB_FILE)
        c = conn.cursor()
        c.execute("DELETE FROM items")
        def store(container_name, container):
            for idx, item in enumerate(container):
                if item:
                    bonus = str(item.bonus)
                    stackable = int(item.stackable)
                    r,g,b = item.color
                    c.execute("""INSERT INTO items
                        (container, slot, name, type, quantity, color_r, color_g, color_b,
                        bonus, stackable, image_path, level, xp, max_xp, spoil)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                        (container_name, idx, item.name, item.type, item.quantity,
                        r,g,b,bonus,stackable,item.image_path,item.level,item.xp,item.max_xp,item.spoil))
        store("inventory", inventory)
        store("equip", equipment)
        store("hotbar", hotbar)
        conn.commit()
        conn.close()
        print("Saved to DB")

    def load_from_db(self):
        global inventory, equipment, hotbar
        conn = sqlite3.connect(config.DB_FILE)
        c = conn.cursor()
        c.execute("SELECT container, slot, name, type, quantity, color_r, color_g, color_b, bonus, stackable, image_path, level, xp, max_xp, spoil FROM items")
        rows = c.fetchall()
        inventory = [None] * config.TOTAL_INV_SLOTS
        equipment = [None] * len(config.EQUIP_SLOTS)
        hotbar = [None] * config.HOTBAR_SLOTS
        for row in rows:
            container, slot, name, type_, quantity, r, g, b, bonus_str, stackable, image_path, level, xp, max_xp, spoil = row
            item = Item(name, quantity, type_, (r,g,b), eval(bonus_str), bool(stackable), image_path, level, xp, max_xp, spoil)
            if container=="inventory": inventory[slot] = item
            elif container=="equip": equipment[slot] = item
            elif container=="hotbar": hotbar[slot] = item
        conn.close()
        print("Loaded from DB")

    def load_image(self, path, size=None):
        if not path: return None
        path = os.path.normpath(path)
        if path in config.IMAGE_CACHE:
            surf = config.IMAGE_CACHE[path]
        else:
            try:
                surf = pygame.image.load(path).convert_alpha()
                config.IMAGE_CACHE[path] = surf
            except:
                config.IMAGE_CACHE[path] = None
                return None
        if size and surf:
            iw, ih = surf.get_size()
            tw, th = size
            scale = min(tw/iw, th/ih)
            surf = pygame.transform.smoothscale(surf, (max(1,int(iw*scale)), max(1,int(ih*scale))))
        return surf