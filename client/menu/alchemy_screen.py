


from client.menu.inventory import InventorySystem
from client.menu.menu_screen import MenuScreen
import config as config
import pygame


class AlchemyScreen(MenuScreen):
    """
    AlchemyScreen reuses InventorySystem functionality but:
      - defaults to showing only ingredients (self.active_tab = "ingredient")
      - provides a 3-slot combine bench where ingredients can be dropped
      - a Combine button which consumes one of each ingredient in the bench
        and creates a new potion item that is added to the player's inventory
    """
    def __init__(self):
        super().__init__("Alchemy")   # THIS is enough
        self.title = "Alchemy"
        self.active_tab = "ingredient"
        # Combine bench configuration
        self.combine_slots = [None, None, None]    # each slot stores an item dict or None
        # layout: place combine bench to the right of inventory panel
        bench_x = config.INV_START_X + 540
        bench_y = config.INV_START_Y + 20
        self.combine_area_rect = pygame.Rect(bench_x - 12, bench_y - 12, 240, 220)
        self.combine_slot_rects = []
        slot_gap = 16
        slot_x = bench_x + 16
        slot_y = bench_y + 20
        for i in range(3):
            r = pygame.Rect(slot_x + (i * (config.SLOT_SIZE + slot_gap)), slot_y, config.SLOT_SIZE, config.SLOT_SIZE)
            self.combine_slot_rects.append(r)

        self.combine_btn_rect = pygame.Rect(bench_x + 20, slot_y + config.SLOT_SIZE + 22, 200, 36)
        self.message = ""
        # when dragging from combine bench we need to remember origin
        # we'll represent it as ("combine", index)
        # dragging_from already used by parent; that's fine.

    # override draw to add the bench UI on top of the inventory UI
    def draw(self, surface):
        # call parent's draw to render inventory/equipment/hotbar etc.
        super().draw(surface)

        # Draw combine bench background
        pygame.draw.rect(surface, config.DARK_GRAY, self.combine_area_rect, border_radius=10)
        surface.blit(config.font_medium.render("Alchemy Lab", True, config.WHITE),
                     (self.combine_area_rect.x + 12, self.combine_area_rect.y + 6))

        # Draw combine slots
        for i, r in enumerate(self.combine_slot_rects):
            pygame.draw.rect(surface, config.GRAY, r, border_radius=8)
            item = self.combine_slots[i]
            # If dragging item is from this combine slot, don't render it here
            if item and not (self.dragging_item and self.dragging_from == ("combine", i)):
                self.draw_item(surface, item, r, config.font_small)
            # highlight hover
            if self.hover_slot == ("combine", i):
                pygame.draw.rect(surface, config.YELLOW, r, 3, border_radius=8)

        # Draw Combine button
        pygame.draw.rect(surface, config.LIGHT_GRAY, self.combine_btn_rect, border_radius=8)
        pygame.draw.rect(surface, config.WHITE, self.combine_btn_rect, 2, border_radius=8)
        txt = config.font_small.render("Combine", True, config.BLACK)
        surface.blit(txt, (self.combine_btn_rect.centerx - txt.get_width()//2,
                           self.combine_btn_rect.centery - txt.get_height()//2))

        # Drag ghost (if dragging from combine bench or elsewhere)
        if self.dragging_item:
            mx, my = pygame.mouse.get_pos()
            ghost = pygame.Rect(mx - config.SLOT_SIZE // 2, my - config.SLOT_SIZE // 2, config.SLOT_SIZE, config.SLOT_SIZE)
            self.draw_item(surface, self.dragging_item, ghost, config.font_small)

        # Tooltip for combine slot items
        if self.hover_slot and not self.dragging_item:
            container, idx = self.hover_slot
            if container == "combine":
                item = self.combine_slots[idx]
                if item:
                    self.draw_tooltip(surface, item)

        # Message (overrides parent message position slightly)
        if self.message:
            surface.blit(config.font_small.render(self.message, True, config.RED), (20, config.WIDTH - 28))


    # override mouse motion to include combine slots
    def handle_mouse_motion(self, pos):
        # check combine slots first
        for i, r in enumerate(self.combine_slot_rects):
            if r.collidepoint(pos):
                self.hover_slot = ("combine", i)
                return
        # otherwise fall back to inventory handling
        super().handle_mouse_motion(pos)


    # override mouse down to include combine slot clicks and combine button
    def handle_mouse_down(self, pos, button):
        # scrolling and tabs still handled by parent
        if button in (4, 5):
            super().handle_mouse_down(pos, button)
            return

        # check combine button
        if button == 1 and self.combine_btn_rect.collidepoint(pos):
            self.attempt_combine()
            return

        # check combine slot right/left clicks
        if button == 1 or button == 3:
            for i, r in enumerate(self.combine_slot_rects):
                if r.collidepoint(pos):
                    item = self.combine_slots[i]
                    # right-click: open split menu if stackable (reuse parent's split logic)
                    if button == 3 and item and item.get("quantity", 1) > 1 and item.get("stackable", True):
                        self.split_popup = {"item": item, "container": "combine", "index": i, "pos": pos}
                        return
                    # left-click: start dragging from combine slot
                    if button == 1 and item:
                        self.dragging_item = item
                        self.dragging_from = ("combine", i)
                        self.combine_slots[i] = None
                        return

        # not a combine-specific click -> let parent handle (this will also handle clicking inventory tabs)
        super().handle_mouse_down(pos, button)


    # override the split popup handling to support combine container
    def handle_split_choice(self, choice_index):
        """Helper to be used if you want to separate split logic; currently integrated into parent split code.
           Not strictly necessary; kept here in case of later refactor.
        """
        pass


    # override mouse up to let items be dropped into combine slots
    def handle_mouse_up(self, pos, button):
        # if not dragging, nothing to do
        if not self.dragging_item:
            return

        dragging_item = self.dragging_item
        dragging_from = self.dragging_from

        # 1) Check if dropped onto a combine slot
        for i, r in enumerate(self.combine_slot_rects):
            if r.collidepoint(pos):
                dest_item = self.combine_slots[i]
                # If empty slot, place one stack (or entire dragged stack)
                if dest_item is None:
                    self.combine_slots[i] = dragging_item
                else:
                    # If can stack, merge quantities
                    if self.can_stack(dragging_item, dest_item):
                        dest_item["quantity"] += dragging_item.get("quantity", 1)
                    else:
                        # swap with origin if origin exists
                        if dragging_from:
                            src_name, src_idx = dragging_from
                            if src_name == "combine":
                                # place dest back to origin combine slot and place dragging into target
                                self.combine_slots[src_idx] = dest_item
                                self.combine_slots[i] = dragging_item
                            else:
                                # swap back into origin container
                                src = self.get_container(src_name)
                                src[src_idx] = dest_item
                                self.combine_slots[i] = dragging_item
                        else:
                            # trying to drop a new item from nowhere onto occupied combine slot -> reject
                            self.message = f"Cannot place {dragging_item['name']} onto {dest_item['name']}."
                            # place dragged back into inventory
                            self.add_item_to_inventory(dragging_item)
                self._clear_drag()
                return

        # 2) Not combine slot: allow dropping back into inventory/hotbar/equip via parent logic
        # We'll mimic parent behavior for visible inventory/hotbar/equip, so we can place items back properly.

        dest = None
        # visible inventory
        for rect, idx in getattr(self, "visible_slot_map", []):
            if rect.collidepoint(pos):
                dest = ("inventory", idx)
                break

        # Equipment slots
        if not dest:
            for i in range(len(config.EQUIP_SLOTS)):
                rect = pygame.Rect(config.EQUIP_START_X, config.EQUIP_START_Y + i*(config.SLOT_SIZE+config.EQUIP_SLOT_GAP), config.SLOT_SIZE, config.SLOT_SIZE)
                if rect.collidepoint(pos):
                    dest = ("equip", i)
                    break

        # Hotbar
        if not dest:
            for i in range(config.HOTBAR_SLOTS):
                rect = pygame.Rect(config.HOTBAR_START_X + i*(config.SLOT_SIZE+config.PADDING), config.HOTBAR_START_Y, config.SLOT_SIZE, config.SLOT_SIZE)
                if rect.collidepoint(pos):
                    dest = ("hotbar", i)
                    break

        # Dropped outside any slot: return to origin or add to inventory
        if not dest:
            if dragging_from:
                src = None
                try:
                    src = self.get_container(dragging_from[0])
                except Exception:
                    src = None
                if src is not None and isinstance(dragging_from[1], int):
                    # place back into origin container (inventory/hotbar/equip)
                    src[dragging_from[1]] = dragging_item
                else:
                    # origin was combine or None -> try to put into inventory
                    if not self.add_item_to_inventory(dragging_item):
                        self.message = "No space to place item!"
            else:
                # origin none (new item), try to add to inventory
                if not self.add_item_to_inventory(dragging_item):
                    self.message = "Inventory full!"
            self._clear_drag()
            return

        # handle drop into inventory/hotbar/equip (same logic as InventorySystem.handle_mouse_up)
        d_cont_name, d_idx = dest
        dest_cont = self.get_container(d_cont_name)
        dest_item = dest_cont[d_idx]

        # Only allow drops on visible inventory slots
        if d_cont_name == "inventory":
            visible_indices = [idx for _, idx in self.visible_slot_map]
            if d_idx not in visible_indices:
                self.message = "Cannot drop here: slot not visible!"
                # return dragged item to origin
                if dragging_from:
                    src = self.get_container(dragging_from[0])
                    src[dragging_from[1]] = dragging_item
                else:
                    self.add_item_to_inventory(dragging_item)
                self._clear_drag()
                return

        # Dropped onto empty slot
        if dest_item is None:
            dest_cont[d_idx] = dragging_item
        else:
            if self.can_stack(dragging_item, dest_item):
                dest_item["quantity"] += dragging_item["quantity"]
            else:
                if dragging_from:
                    src_name, src_idx = dragging_from
                    src_cont = None
                    try:
                        src_cont = self.get_container(src_name)
                    except Exception:
                        src_cont = None
                    if src_cont is not None:
                        src_cont[src_idx] = dest_item
                        dest_cont[d_idx] = dragging_item
                    else:
                        # origin was combine (should not happen here because we handled combine above),
                        # but try to put destination back to inventory
                        if not self.add_item_to_inventory(dragging_item):
                            self.message = f"Cannot merge {dragging_item['name']} with {dest_item['name']}!"
                            dest_cont[d_idx] = dest_item
                else:
                    if not self.add_item_to_inventory(dragging_item):
                        self.message = f"Cannot merge {dragging_item['name']} with {dest_item['name']}!"
                        dest_cont[d_idx] = dest_item  # keep original in place

        self._clear_drag()


    # combine logic: consume one of each item in combine slots and create a new potion
    def attempt_combine(self):
        # Gather non-empty ingredients
        ingredients = [it for it in self.combine_slots if it]
        if len(ingredients) < 2:
            self.message = "Need at least 2 ingredients to combine."
            return

        # Basic recipe resolution:
        # For now, if Database has a recipe system you'd hook into it here.
        # As a fallback we auto-generate a potion using the ingredient names.
        ing_names = [it["name"] for it in ingredients]
        # simple name: join sorted unique ingredient names
        base_name = " + ".join(sorted(set(ing_names)))
        potion_name = f"Potion of {base_name}"

        # Create potion dict minimal fields used by your inventory UI
        potion = {
            "name": potion_name,
            "type": "potion",
            "quantity": 1,
            # you can set a default spoil, image_path, color, etc.
            "spoil": 100,
            "stackable": True,
            "image_path": None,
            "color": (120, 200, 255),  # light bluish for potions
        }

        # Consume one quantity from each combine slot (if stack >1, decrement)
        for i, it in enumerate(self.combine_slots):
            if not it:
                continue
            if it.get("quantity", 1) > 1:
                it["quantity"] -= 1
                # keep the item in the combine slot with reduced qty
                self.combine_slots[i] = it
            else:
                # remove it
                self.combine_slots[i] = None

        # Add potion to player's inventory (use your add_item_to_inventory)
        added = self.add_item_to_inventory(potion)
        if not added:
            self.message = "Inventory full — could not store potion."

            # Try to restore 1 of each consumed ingredient using the same add function
            for it in ingredients:
                restored_item = {
                    "name": it["name"],
                    "type": it["type"],
                    "quantity": 1,
                    "stackable": it.get("stackable", True),
                    "image_path": it.get("image_path"),
                    "color": it.get("color"),
                    "spoil": it.get("spoil", 0)
                }

                # Try to add back with normal inventory stacking rules
                if not self.add_item_to_inventory(restored_item):
                    # If we still can't store, we just give up (same as your original)
                    break

            return
        else:
            # Optionally: you may want to persist to DB through a Database method if present
            # e.g., self.database.save_item(potion) — but we append to inventory which persists
            self.message = f"Created {potion_name}!"

    # small helper: allow external code to clear combine slots (useful for scene transitions)
    def clear_combine(self):
        self.combine_slots = [None, None, None]

    # override _clear_drag to ensure combine-from origin cleared correctly
    def _clear_drag(self):
        self.dragging_item = None
        self.dragging_from = None
