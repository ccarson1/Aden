import pygame
import config as config
import client.menu.container as container

# --- Total stats ---
def calc_total_stats(database):
    total = database.base_stats.copy()
    for item in database.equipment:
        if not item: continue
        for k,v in item.bonus.items():
            total[k] = total.get(k,0)+v
    return total


# 🟩 Draw updated stats and bars
def draw_stats_panel(database, surface):
    stats = calc_total_stats(database)
    panel_rect = pygame.Rect(config.STATS_PANEL_X, config.STATS_PANEL_Y, 200, 380)
    pygame.draw.rect(surface, config.DARK_GRAY, panel_rect, border_radius=10)
    surface.blit(config.font_medium.render("Character Stats", True, config.WHITE), (config.STATS_PANEL_X + 20, config.STATS_PANEL_Y + 10))

    y = config.STATS_PANEL_Y + 50
    for k, v in stats.items():
        txt = config.font_small.render(f"{k.capitalize()}: {v}", True, config.LIGHT_GRAY)
        surface.blit(txt, (config.STATS_PANEL_X + 20, y))
        y += 20

    # --- Status Bars ---
    y += 20
    draw_bar(surface, "Health", database.current_status["hp"], database.base_stats["hp"], config.RED, config.STATS_PANEL_X + 20, y)
    y += 40
    draw_bar(surface, "Stamina", database.current_status["stamina"], 100, config.GREEN, config.STATS_PANEL_X + 20, y)
    y += 40
    draw_bar(surface, "Mana", database.current_status["mana"], database.base_stats["mana"], config.BLUE, config.STATS_PANEL_X + 20, y)

def draw_bar(surface, label, value, max_val, color, x, y):
    bar_w, bar_h = 140, 16
    pct = max(0, min(1, value / max_val))
    pygame.draw.rect(surface, config.GRAY, (x, y, bar_w, bar_h), border_radius=4)
    pygame.draw.rect(surface, color, (x, y, int(bar_w * pct), bar_h), border_radius=4)
    txt = config.font_small.render(f"{label}: {value}/{max_val}", True, config.WHITE)
    surface.blit(txt, (x, y - 18))


def draw_equipment_slots(database, dragging_item,dragging_from, hover_slot, surface):
    for i, slot in enumerate(config.EQUIP_SLOTS):
        x = config.EQUIP_START_X
        y = config.EQUIP_START_Y + i * (config.SLOT_SIZE + config.EQUIP_SLOT_GAP)
        rect = pygame.Rect(x, y, config.SLOT_SIZE, config.SLOT_SIZE)

        # draw the slot background
        pygame.draw.rect(surface, config.GRAY, rect, border_radius=8)
        surface.blit(config.font_small.render(slot, True, config.LIGHT_GRAY), (x + config.SLOT_SIZE + 8, y + config.SLOT_SIZE // 2 - 8))

        # draw the item (use image if available)
        item = database.equipment[i]
        if item and not (dragging_item and dragging_from == ("equip", i)):
            container.draw_item(surface, database, item, rect, config.font_small)

        # draw hover highlight
        if hover_slot == ("equip", i):
            pygame.draw.rect(surface, config.YELLOW, rect, 3, border_radius=8)

def draw_material_slots(database, dragging_item,dragging_from, hover_slot, surface):
    for i, slot in enumerate(config.CFT_SLOTS):
        x = config.CFT_START_X
        y = config.CFT_START_Y + i * (config.SLOT_SIZE + config.CFT_SLOT_GAP)
        rect = pygame.Rect(x, y, config.SLOT_SIZE, config.SLOT_SIZE)

        # draw the slot background
        pygame.draw.rect(surface, config.GRAY, rect, border_radius=8)
        surface.blit(config.font_small.render(slot, True, config.LIGHT_GRAY), (x + config.SLOT_SIZE + 8, y + config.SLOT_SIZE // 2 - 8))

        # draw the item (use image if available)
        item = database.crafting[i]
        if item and not (dragging_item and dragging_from == ("equip", i)):
            container.draw_item(surface, database, item, rect, config.font_small)

        # draw hover highlight
        if hover_slot == ("equip", i):
            pygame.draw.rect(surface, config.YELLOW, rect, 3, border_radius=8)

    # draw the slot for the resutl of the crafted item
    result = pygame.Rect(x + 250, y - 125, config.SLOT_SIZE, config.SLOT_SIZE)
    pygame.draw.rect(surface, config.GRAY, result, border_radius=8)
    surface.blit(config.font_small.render(slot, True, config.LIGHT_GRAY), ((x + config.SLOT_SIZE + 8)*2, y + config.SLOT_SIZE - 8))


def draw_hotbar_slots(database, dragging_item, dragging_from, hover_slot, surface):
    for i in range(config.HOTBAR_SLOTS):
        x = config.HOTBAR_START_X + i * (config.SLOT_SIZE + config.PADDING)
        y = config.HOTBAR_START_Y
        rect = pygame.Rect(x, y, config.SLOT_SIZE, config.SLOT_SIZE)
        pygame.draw.rect(surface, config.GRAY, rect, border_radius=8)
        item = database.hotbar[i]
        if item and not (dragging_item and dragging_from == ("hotbar", i)):
            container.draw_item(surface, database, item, rect, config.font_small)
        idx_txt = config.font_small.render(str(i + 1), True, config.LIGHT_GRAY)
        surface.blit(idx_txt, (x + 6, y + 6))
        if hover_slot == ("hotbar", i):
            pygame.draw.rect(surface, config.YELLOW, rect, 3, border_radius=8)

# Tooltip
def draw_tooltip(surface, item):
    mx, my = pygame.mouse.get_pos()
    w, h = 180, 80
    rect = pygame.Rect(mx + 12, my + 12, w, h)
    pygame.draw.rect(surface, config.BLACK, rect, border_radius=6)
    pygame.draw.rect(surface, config.LIGHT_GRAY, rect, 2, border_radius=6)
    surface.blit(config.font_small.render(item["name"], True, config.WHITE), (rect.x + 8, rect.y + 6))
    surface.blit(config.font_small.render(f"x{item['quantity']} ({item['type']})", True, config.LIGHT_GRAY), (rect.x + 8, rect.y + 26))
    if hasattr(item, "bonus") and item.bonus:
        by = rect.y + 46
        for stat, val in item["bonus"].items():
            surface.blit(config.font_small.render(f"+{val} {stat}", True, config.YELLOW), (rect.x + 8, by))
            by += 16


# Right-click split menu
def draw_split_popup(surface, split_popup):
    menu_w, menu_h = 120, 90
    x, y = split_popup["pos"]
    rect = pygame.Rect(x, y, menu_w, menu_h)
    pygame.draw.rect(surface, config.DARK_GRAY, rect, border_radius=6)
    pygame.draw.rect(surface, config.WHITE, rect, 2, border_radius=6)

    options = ["Split 1", "Split Half", "Split All"]
    split_popup["rects"] = []
    for i, opt in enumerate(options):
        option_rect = pygame.Rect(x + 5, y + 5 + i*28, menu_w - 10, 24)
        pygame.draw.rect(surface, config.LIGHT_GRAY, option_rect)
        surface.blit(config.font_small.render(opt, True, config.BLACK), (option_rect.x + 5, option_rect.y + 3))
        split_popup["rects"].append(option_rect)


def draw_inventory_tabs(surface, tabs, active_tab):
    tab_rects = []
    start_x = config.INV_START_X
    start_y = config.INV_START_Y - 50
    tab_w, tab_h = 72, 28
    gap = 6

    for i, tab in enumerate(tabs):
        rect = pygame.Rect(start_x + i*(tab_w + gap), start_y-20, tab_w, tab_h)
        color = config.LIGHT_GRAY if tab == active_tab else config.DARK_GRAY
        pygame.draw.rect(surface, color, rect, border_radius=6)
        pygame.draw.rect(surface, config.WHITE, rect, 2, border_radius=6)
        txt = config.font_small.render(tab.capitalize(), True, config.WHITE)
        surface.blit(txt, (rect.centerx - txt.get_width()//2, rect.centery - txt.get_height()//2))
        tab_rects.append((rect, tab))

    return tab_rects
