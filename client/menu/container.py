import pygame
import os
import config as config

def draw_item(surface, database, item, slot_rect, font_small, show_quantity=True):
        if not item:
            return

        # Draw image or color block
        img_surf = None
        image_path = item.get("image_path")
        if image_path:
            key = os.path.normpath(image_path)
            raw = config.IMAGE_CACHE.get(key)
            if raw is None:
                raw = database.load_image(image_path)
                config.IMAGE_CACHE[key] = raw
            if raw:
                inner_size = (slot_rect.width - 14, slot_rect.height - 14)
                img_surf = database.load_image(image_path, size=inner_size)

        if img_surf:
            img_rect = img_surf.get_rect(center=slot_rect.center)
            surface.blit(img_surf, img_rect)
        else:
            pygame.draw.rect(surface, item.get("color", (100, 100, 100)),
                            slot_rect.inflate(-14, -14), border_radius=6)

        # Draw quantity
        if show_quantity and item.get("quantity", 1) > 1:
            qty = font_small.render(str(item["quantity"]), True, config.WHITE)
            surface.blit(qty, (slot_rect.x + slot_rect.width - 18,
                                slot_rect.y + slot_rect.height - 20))

        # --- Draw XP bar for levelable items ---
        if all(hasattr(item, attr) for attr in ("level", "xp", "max_xp")) and item.max_xp > 0:
            bar_w = slot_rect.width - 8
            bar_h = 6
            bar_x = slot_rect.x + 4
            bar_y = slot_rect.bottom - bar_h - 4
            pct = max(0, min(1, item.xp / item.max_xp))

            pygame.draw.rect(surface, config.DARK_GRAY, (bar_x, bar_y, bar_w, bar_h), border_radius=3)
            pygame.draw.rect(surface, config.BLUE, (bar_x, bar_y, int(bar_w * pct), bar_h), border_radius=3)

            lvl_text = font_small.render(f"Lv{item.level}", True, config.WHITE)
            surface.blit(lvl_text, (slot_rect.x + 4, slot_rect.y + 4))

        # --- Draw spoil bar for potions ---
        if hasattr(item, "type") and item.type == "potion" and hasattr(item, "spoil"):
            bar_w = slot_rect.width - 8
            bar_h = 4
            bar_x = slot_rect.x + 4
            bar_y = slot_rect.bottom - bar_h - 2
            pct = max(0, min(1, item["spoil"] / 100))
            pygame.draw.rect(surface, config.DARK_GRAY, (bar_x, bar_y, bar_w, bar_h), border_radius=2)
            pygame.draw.rect(surface, config.RED, (bar_x, bar_y, int(bar_w * pct), bar_h), border_radius=2)


def draw_inventory_slots(database, inventory_area, active_tab, dragging_item, dragging_from, hover_slot, scroll_y, INV_COLS, surface):
    panel_rect = pygame.Rect(inventory_area)
    surface.set_clip(panel_rect)

    start_x = config.INV_START_X
    start_y = config.INV_START_Y + config.INV_PANEL_TOP_PADDING - scroll_y

    visible_slot_map = []  # reset mapping

    # Build a list of (inventory_index, item) that match the active tab
    filtered_items = []
    for idx, item in enumerate(database.inventory):
        if item is None:
            filtered_items.append((idx, None))
            # if active_tab == "All":
            #     filtered_items.append((idx, None))
            # pass
        elif active_tab == "All" or item["type"] == active_tab:
            filtered_items.append((idx, item))

    #print(inventory)
    for display_idx, (inv_idx, item) in enumerate(filtered_items):
        
        row = display_idx // INV_COLS
        col = display_idx % INV_COLS
        x = start_x + col * (config.SLOT_SIZE + config.PADDING)
        y = start_y + row * (config.SLOT_SIZE + config.PADDING)
        slot_rect = pygame.Rect(x, y, config.SLOT_SIZE, config.SLOT_SIZE)


        # Skip slots completely outside panel
        if slot_rect.bottom < panel_rect.top or slot_rect.top > panel_rect.bottom:
            continue

        visible_slot_map.append((slot_rect, inv_idx))  # map visible slot to inventory index

        # Draw slot background
        pygame.draw.rect(surface, config.GRAY, slot_rect, border_radius=8)

        if item and not (dragging_item and dragging_from == ("inventory", inv_idx)):
            draw_item(surface, database, item, slot_rect, config.font_small)

        # Hover highlight
        if hover_slot == ("inventory", inv_idx):
            pygame.draw.rect(surface, config.YELLOW, slot_rect, 3, border_radius=8)

    surface.set_clip(None)

    # Update max scroll
    total_height = ((len(filtered_items) + INV_COLS - 1) // INV_COLS) * (config.SLOT_SIZE + config.PADDING) + config.INV_PANEL_TOP_PADDING + config.INV_PANEL_BOTTOM_PADDING
    max_scroll = max(0, total_height - panel_rect.height)
    scroll_y = max(0, min(scroll_y, max_scroll))

    return surface, total_height, max_scroll, scroll_y, visible_slot_map
