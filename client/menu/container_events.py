# container_events.py
import pygame
import config as config


def get_container(name, database):
    return {"inventory": database.inventory, "equip": database.equipment, "hotbar": database.hotbar}[name]

# ---------- Helpers ----------
def _get_container_list(inv, name):
    """Return the actual list for container 'inventory', 'equip', or 'hotbar'.
       Uses inv.get_container if present, otherwise uses inv.database."""
    if hasattr(inv, "get_container") and callable(getattr(inv, "get_container")):
        return inv.get_container(name)
    # fallback
    db = getattr(inv, "database", None)
    return {"inventory": db.inventory, "equip": db.equipment, "hotbar": db.hotbar}[name]

def _compute_split_rects(pos):
    """Create three rects for split popup based on the requested pos.
       returns list of pygame.Rect in order: Split 1, Split Half, Split All."""
    x, y = pos
    w, h = 140, 28
    pad = 6
    rects = [
        pygame.Rect(x - w//2, y - h - pad, w, h),   # above cursor
        pygame.Rect(x - w//2, y + pad, w, h),       # below cursor
        pygame.Rect(x - w//2, y + h + pad*2, w, h)  # further below
    ]
    return rects

# ---------- Inventory operations (moved out of class) ----------
def stack_all_items(database):
    merged = {}
    for item in database.inventory:
        if not item:
            continue

        if item.get("stackable", True):
            key_parts = [item["name"], item["type"]]
            if item.get("spoil") is not None:
                key_parts.append(item["spoil"])
            if item.get("level") is not None and item.get("xp") is not None:
                key_parts.append(item["level"])
                key_parts.append(item["xp"])
            key = tuple(key_parts)

            if key not in merged:
                merged[key] = item.copy()
            else:
                merged[key]["quantity"] += item["quantity"]
        else:
            merged[("nonstackable", id(item))] = item

    new_inv = [None] * len(database.inventory)
    for idx, item in enumerate(merged.values()):
        if idx < len(new_inv):
            new_inv[idx] = item
    database.inventory = new_inv

def sort_inventory_by_type(database):
    non_empty = [item for item in database.inventory if item]
    empty_slots = [None] * (len(database.inventory) - len(non_empty))
    non_empty.sort(key=lambda x: x.get("type", ""))
    database.inventory = non_empty + empty_slots

def add_item_to_inventory(inv, item):
    """Try to merge into stacks first, then put in first empty slot.
       Returns True if added, False if inventory full."""
    db = inv.database
    # try stack merge
    for i, it in enumerate(db.inventory):
        if it and inv.can_stack(item, it):
            it["quantity"] += item["quantity"]
            return True
    # first empty
    for i, it in enumerate(db.inventory):
        if it is None:
            db.inventory[i] = item
            return True
    return False

# ---------- Split popup handler ----------
def handle_split_popup_click(inv, pos):
    """Handle clicks on the split popup attached to inv.split_popup.
       Returns True if the popup consumed the click (and was closed/handled), otherwise False."""
    sp = inv.split_popup
    if not sp:
        return False

    # Determine rects: use existing if present, else compute reasonable defaults
    rects = sp.get("rects")
    if not rects:
        rects = _compute_split_rects(sp.get("pos", pos))
        sp["rects"] = rects  # store so draw function can also use them if desired

    db = inv.database
    cont = _get_container_list(inv, sp["container"])
    item = sp["item"]
    idx = sp["index"]

    for i, r in enumerate(rects):
        if r.collidepoint(pos):
            # Split 1
            if i == 0:
                if item["quantity"] > 1:
                    new_item = item.copy()
                    new_item["quantity"] = 1
                    item["quantity"] -= 1
                    inv.dragging_item = new_item
                    inv.dragging_from = None
                    if item["quantity"] == 0:
                        cont[idx] = None
                    inv.message = f"Splitting 1x {new_item['name']}."
                inv.split_popup = None
                return True

            # Split Half
            elif i == 1:
                half = item["quantity"] // 2
                if half > 0:
                    new_item = item.copy()
                    new_item["quantity"] = half
                    item["quantity"] -= half
                    inv.dragging_item = new_item
                    inv.dragging_from = None
                    if item["quantity"] == 0:
                        cont[idx] = None
                    inv.message = f"Splitting {half}x {new_item['name']}."
                inv.split_popup = None
                return True

            # Split All (distribute)
            else:
                qty = item["quantity"]
                start_idx = idx + 1
                cont_len = len(cont)
                remaining = qty

                for j in range(start_idx, cont_len):
                    if cont[j] is None and remaining > 0:
                        new_slot = item.copy()
                        new_slot["quantity"] = 1
                        cont[j] = new_slot
                        remaining -= 1

                for j in range(0, start_idx):
                    if cont[j] is None and remaining > 0:
                        new_slot = item.copy()
                        new_slot["quantity"] = 1
                        cont[j] = new_slot
                        remaining -= 1

                cont[idx] = None
                inv.message = f"Distributed {qty}x {item['name']}."
                inv.split_popup = None
                return True

    # Click outside popup: close it
    inv.split_popup = None
    return True

# ---------- Main event entry point ----------
def handle_mouse_down(inv, pos, button):
    """
    inv: InventorySystem instance
    pos: (x,y)
    button: mouse button (1 left, 3 right, 4 scroll up, 5 scroll down)
    """

    # Scroll wheel
    if button == 4:
        if hasattr(inv, "handle_scroll"):
            inv.handle_scroll(-30)
        return
    elif button == 5:
        if hasattr(inv, "handle_scroll"):
            inv.handle_scroll(30)
        return

    # If split popup exists: let the popup handler consume clicks (close, split, etc.)
    if getattr(inv, "split_popup", None):
        handled = handle_split_popup_click(inv, pos)
        if handled:
            return

    # Tab clicks: if inv has a tab handler in gadgets you may want to call it.
    # We will detect clicks against tab_rects if present.
    if button == 1 and getattr(inv, "tab_rects", None):
        for rect, tab in inv.tab_rects:
            if rect.collidepoint(pos):
                inv.active_tab = tab
                inv.scroll_y = 0
                inv.message = f"{tab.capitalize()} items displayed!"
                return

    # Buttons: Stack All and Sort
    if button == 1 and hasattr(inv, "stack_all_rect") and inv.stack_all_rect.collidepoint(pos):
        stack_all_items(inv.database)
        inv.message = "All stackable items combined!"
        return

    if button == 1 and hasattr(inv, "sort_type_rect") and inv.sort_type_rect.collidepoint(pos):
        sort_inventory_by_type(inv.database)
        inv.message = "Inventory sorted!"
        return

    # Determine hover slot (if not present, we still try to detect from visible slots)
    hover = getattr(inv, "hover_slot", None)
    if not hover:
        # fallback: try to detect from visible_slot_map (uses rectangles from draw)
        for rect, idx in getattr(inv, "visible_slot_map", []):
            if rect.collidepoint(pos):
                hover = ("inventory", idx)
                inv.hover_slot = hover
                break

    if not hover:
        return

    container_name, idx = hover
    cont_list = _get_container_list(inv, container_name)
    item = cont_list[idx]
    if not item:
        return

    # Right-click: open split menu if stackable and quantity > 1
    if button == 3 and item.get("quantity", 1) > 1 and item.get("stackable", True):
        # Create popup info — we do not require 'rects' here, draw routine or handler will compute if needed
        inv.split_popup = {"item": item, "container": container_name, "index": idx, "pos": pos}
        # optionally create rects now so handler/drawer are consistent
        inv.split_popup["rects"] = _compute_split_rects(pos)
        return

    # Left-click: start dragging
    if button == 1:
        inv.dragging_item = item
        inv.dragging_from = (container_name, idx)
        cont_list[idx] = None
        inv.message = ""
        return
    
def handle_mouse_up(inv, pos, button):
    """
    Handles dropping dragged items, merging, swapping, and returning items
    to their original slot when needed.
    """

    # Nothing to drop
    if not inv.dragging_item:
        return

    dragged = inv.dragging_item
    src = inv.dragging_from   # ("inventory", idx) or None

    # Try to determine which slot we are dropping onto
    hover = getattr(inv, "hover_slot", None)

    # If we have a visible slot map (from draw), detect from rectangles
    if not hover:
        for rect, idx in getattr(inv, "visible_slot_map", []):
            if rect.collidepoint(pos):
                hover = ("inventory", idx)
                break

    # No target slot found → return dragged item to original position
    if not hover:
        if src:
            cont_name, cont_idx = src
            cont_list = _get_container_list(inv, cont_name)

            if cont_list[cont_idx] is None:
                cont_list[cont_idx] = dragged
            else:
                # Slot unexpectedly filled → try first empty or stack
                if not add_item_to_inventory(inv, dragged):
                    inv.message = "Inventory full!"
        else:
            # Drag came from a split popup (no source slot)
            add_item_to_inventory(inv, dragged)

        inv.dragging_item = None
        inv.dragging_from = None
        return

    # -------------------------
    # Dropping ONTO a slot
    # -------------------------
    dst_name, dst_idx = hover
    dst_list = _get_container_list(inv, dst_name)
    target_item = dst_list[dst_idx]

    # -------------------------
    # 1) Empty slot → place item
    # -------------------------
    if target_item is None:
        dst_list[dst_idx] = dragged
        inv.message = ""
        inv.dragging_item = None
        inv.dragging_from = None
        return

    # -------------------------
    # 2) Try stack merge
    # -------------------------
    if inv.can_stack(dragged, target_item):
        target_item["quantity"] += dragged["quantity"]
        inv.message = f"Merged {dragged['quantity']}x {dragged['name']}."
        inv.dragging_item = None
        inv.dragging_from = None
        return

    # -------------------------
    # 3) Swap items
    # -------------------------
    dst_list[dst_idx], swapped = dragged, target_item

    # Put swapped item back into source
    if src:
        src_name, src_idx = src
        src_list = _get_container_list(inv, src_name)

        if src_list[src_idx] is None:
            src_list[src_idx] = swapped
        else:
            # If source is unexpectedly full, try placing swapped item elsewhere
            if not add_item_to_inventory(inv, swapped):
                inv.message = "Inventory full! Lost swap destination."
    else:
        # Drag came from split popup → treat swapped item as newly picked up
        add_item_to_inventory(inv, swapped)

    inv.message = f"Swapped {dragged['name']} with {swapped['name']}."
    inv.dragging_item = None
    inv.dragging_from = None

