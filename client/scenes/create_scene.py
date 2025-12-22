# import pygame
# from client.ui.input_box import InputBox
# from client.ui.button import Button
# import os
# from client.network import network_auth

# class CreateScene:
#     def __init__(self, scene_manager, font, width, height):
#         self.scene_manager = scene_manager
#         self.font = font
#         self.width = width
#         self.height = height 

#         # Sizes
#         input_width, input_height = 300, 50
#         button_width, button_height = 200, 50
#         spacing = 40

#         input_x = (self.width - input_width) // 2
#         button_x = (self.width - button_width) // 2
#         total_height = 3 * input_height + 2*button_height + 4 * spacing
#         start_y = (self.height - total_height) // 2

#         # Inputs
#         self.char_box = InputBox(input_x, start_y, input_width, input_height, "Character Name", font)
#         self.username_box = InputBox(input_x, start_y + input_height + spacing, input_width, input_height, "Username", font)
#         self.password_box = InputBox(input_x, start_y + 2*input_height + 2*spacing, input_width, input_height, "Password", font)

#         # Buttons
#         self.next_button = Button(input_x, start_y + 3*input_height + 3*spacing, input_width, input_height, "Next", font)
#         self.back_button = Button(input_x, start_y + 4*input_height + 4*spacing, input_width, input_height, "Back", font)

#         # Focusable order
#         self.focusable = [self.char_box, self.username_box, self.password_box, self.next_button, self.back_button]
#         self.focus_index = 0
#         self._set_focus(0)

#         # Background
#         path = os.path.join("assets", "images", "field_background.jpg")
#         self.background_image = pygame.image.load(path)
#         self.background_image = pygame.transform.scale(self.background_image, (self.width, self.height))

#     def _set_focus(self, index):
#         # Reset previous focus
#         for i, item in enumerate(self.focusable):
#             if hasattr(item, "active"):
#                 item.active = False
#             if hasattr(item, "focused"):
#                 item.focused = False

#         # Set new focus
#         item = self.focusable[index]
#         if hasattr(item, "active"):
#             item.active = True
#         if hasattr(item, "focused"):
#             item.focused = True

#     def handle_event(self, event):
#         # Let input boxes handle events first
#         handled = False
#         for item in self.focusable:
#             if hasattr(item, "handle_event") and item.handle_event(event):
#                 handled = True

#         # TAB / Shift+TAB navigation
#         if not handled and event.type == pygame.KEYDOWN and event.key == pygame.K_TAB:
#             shift = pygame.key.get_mods() & pygame.KMOD_SHIFT
#             self.focus_index = (self.focus_index - 1 if shift else self.focus_index + 1) % len(self.focusable)
#             self._set_focus(self.focus_index)

#         # Enter key for buttons
#         if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
#             current = self.focusable[self.focus_index]
#             if isinstance(current, Button):
#                 if current == self.next_button:
#                     self._next_action()
#                 elif current == self.back_button:
#                     self._back_action()

#         # Mouse clicks
#         if event.type == pygame.MOUSEBUTTONDOWN:
#             if self.next_button.is_clicked(event.pos):
#                 self._next_action()
#             elif self.back_button.is_clicked(event.pos):
#                 self._back_action()

#     def _next_action(self):
#         char_name = self.char_box.text
#         username = self.username_box.text
#         password = self.password_box.text
#         result = network_auth.create_account(char_name, username, password)
#         if result["status"] == "ok":
#             self.scene_manager.login_info = result
#             self.scene_manager.create_info = {
#                 "char_name": char_name,
#                 "username": username,
#                 "password": password
#             }
#             self.scene_manager.switch_scene("server")
#         else:
#             print("[ERROR] Account creation failed!", result)

#     def _back_action(self):
#         self.scene_manager.switch_scene("main_menu")

#     def update(self, dt):
#         pass

#     def draw(self, surface):
#         surface.blit(self.background_image, (0,0))
#         for item in self.focusable:
#             item.draw(surface)


import pygame
from client.ui.input_box import InputBox
from client.ui.button import Button
import os
from client.network import network_auth

class CreateScene:
    def __init__(self, scene_manager, font, width, height):
        self.scene_manager = scene_manager
        self.font = font
        self.width = width
        self.height = height 

        # Load background
        bg_path = os.path.join("assets", "images", "field_background.jpg")
        self.background_image = pygame.image.load(bg_path)
        self.background_image = pygame.transform.scale(self.background_image, (self.width, self.height))

        # Panel settings
        self.panel_width = int(self.width * 0.75)
        self.panel_height = int(self.height * 0.65)
        self.panel_x = (self.width - self.panel_width) // 2
        self.panel_y = (self.height - self.panel_height) // 2
        self.panel_surface = pygame.Surface((self.panel_width, self.panel_height), pygame.SRCALPHA)
        self.panel_surface.fill((0, 0, 0, 180))  # semi-transparent black

        # ------------------------------
        # DESCRIPTION PANEL (NEW)
        # ------------------------------
        self.desc_height = int(self.height * 0.18)
        self.desc_rect = pygame.Rect(
            self.panel_x,
            self.panel_y + self.panel_height + 20,
            self.panel_width,
            self.desc_height
        )

        # Class descriptions
        self.class_descriptions = {
            "mage": "A powerful spellcaster with high magic damage but low defense.",
            "warrior": "A sturdy frontline fighter with balanced strength and defense.",
            "archer": "A ranged attacker excelling at speed and precision.",
            "knight": "A heavily armored protector with exceptional durability.",
            "assassin": "A stealthy, agile killer with high burst damage.",
            "healer": "A supportive class with healing and protective magic."
        }

        # Default description
        self.description_text = self.class_descriptions["mage"]

        # Two-column layout inside panel
        margin = 40
        col_width = (self.panel_width // 2) - margin * 2

        left_x = self.panel_x + margin
        right_x = self.panel_x + self.panel_width // 2 + margin
        start_y = self.panel_y + margin

        # ------------------------------
        # CLASS CAROUSEL CONFIG
        # ------------------------------
        self.classes = ["mage", "warrior", "archer", "knight", "assassin", "healer"]
        self.class_index = 0

        # Load class images
        self.class_images = {}
        for c in self.classes:
            img_path = os.path.join("assets", "classes", f"{c}.png")
            img = pygame.image.load(img_path).convert_alpha()
            self.class_images[c] = pygame.transform.scale(img, (250, 250))

        self.carousel_center_x = left_x + col_width // 2
        self.carousel_center_y = start_y + 200

        # Carousel buttons
        self.left_button = Button(self.carousel_center_x - 180, self.carousel_center_y + 130, 80, 40, "<", font)
        self.right_button = Button(self.carousel_center_x + 100, self.carousel_center_y + 130, 80, 40, ">", font)

        # ------------------------------
        # INPUT FIELDS (RIGHT COLUMN)
        # ------------------------------
        input_width = col_width
        input_height = 50
        spacing = 20

        cy = start_y

        self.char_box = InputBox(right_x, cy, input_width, input_height, "Character Name", font)
        cy += input_height + spacing

        self.username_box = InputBox(right_x, cy, input_width, input_height, "Username", font)
        cy += input_height + spacing

        self.password_box = InputBox(right_x, cy, input_width, input_height, "Password", font)
        cy += input_height + spacing * 2

        # Buttons under inputs
        self.back_button = Button(right_x, cy, input_width // 2 - 10, input_height, "Back", font)
        self.next_button = Button(right_x + input_width // 2 + 10, cy, input_width // 2 - 10, input_height, "Next", font)

        # Focus order
        self.focusable = [
            self.char_box, self.username_box, self.password_box,
            self.next_button, self.back_button,
            self.left_button, self.right_button
        ]

        self.focus_index = 0
        self._set_focus(0)

    # ------------------------------
    # DESCRIPTION UPDATE (NEW)
    # ------------------------------
    def _update_description(self):
        cls = self.classes[self.class_index]
        self.description_text = self.class_descriptions.get(cls, "")

    # ------------------------------
    # FOCUS HANDLING
    # ------------------------------
    def _set_focus(self, index):
        for item in self.focusable:
            if hasattr(item, "active"):
                item.active = False
            if hasattr(item, "focused"):
                item.focused = False

        focused_item = self.focusable[index]
        if hasattr(focused_item, "active"):
            focused_item.active = True
        if hasattr(focused_item, "focused"):
            focused_item.focused = True

    # ------------------------------
    # CAROUSEL LOGIC
    # ------------------------------
    def _carousel_left(self):
        self.class_index = (self.class_index - 1) % len(self.classes)
        self._update_description()

    def _carousel_right(self):
        self.class_index = (self.class_index + 1) % len(self.classes)
        self._update_description()

    def get_selected_class(self):
        return self.classes[self.class_index]

    # ------------------------------
    # INPUT HANDLING
    # ------------------------------
    def handle_event(self, event):
        handled = False

        # Input fields first
        for item in self.focusable:
            if hasattr(item, "handle_event") and item.handle_event(event):
                handled = True

        # TAB navigation
        if not handled and event.type == pygame.KEYDOWN and event.key == pygame.K_TAB:
            shift = pygame.key.get_mods() & pygame.KMOD_SHIFT
            if shift:
                self.focus_index = (self.focus_index - 1) % len(self.focusable)
            else:
                self.focus_index = (self.focus_index + 1) % len(self.focusable)
            self._set_focus(self.focus_index)

        # ENTER key activates buttons
        if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
            curr = self.focusable[self.focus_index]
            if curr == self.next_button:
                self._next_action()
            elif curr == self.back_button:
                self._back_action()

        # Arrow keys for carousel
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                self._carousel_left()
            elif event.key == pygame.K_RIGHT:
                self._carousel_right()

        # Mouse
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.left_button.is_clicked(event.pos):
                self._carousel_left()
            elif self.right_button.is_clicked(event.pos):
                self._carousel_right()
            elif self.next_button.is_clicked(event.pos):
                self._next_action()
            elif self.back_button.is_clicked(event.pos):
                self._back_action()

    # ------------------------------
    # BUTTON ACTIONS
    # ------------------------------
    def _next_action(self):
        char_name = self.char_box.text
        username = self.username_box.text
        password = self.password_box.text
        class_type = self.get_selected_class()

        result = network_auth.create_account(char_name, username, password, class_type)

        if result["status"] == "ok":
            self.scene_manager.login_info = result
            self.scene_manager.create_info = {
                "char_name": char_name,
                "username": username,
                "password": password,
                "class": class_type
            }
            self.scene_manager.switch_scene("server")
        else:
            print("[ERROR] Account creation failed!", result)

    def _back_action(self):
        self.scene_manager.switch_scene("main_menu")

    def update(self, dt):
        pass

    # ------------------------------
    # DRAWING
    # ------------------------------
    def draw(self, surface):
        # Background
        surface.blit(self.background_image, (0, 0))

        # UI Panel
        surface.blit(self.panel_surface, (self.panel_x, self.panel_y))

        # ------------------------------
        # Left Column: CLASS CAROUSEL
        # ------------------------------
        class_name = self.classes[self.class_index]
        img = self.class_images[class_name]

        ix = self.carousel_center_x - img.get_width() // 2
        iy = self.carousel_center_y - img.get_height() // 2 - 40
        surface.blit(img, (ix, iy))

        # Class name
        text = self.font.render(class_name.capitalize(), True, (255, 255, 255))
        surface.blit(text, (self.carousel_center_x - text.get_width() // 2, iy + img.get_height() + 10))

        # Buttons
        self.left_button.draw(surface)
        self.right_button.draw(surface)

        # Right Column: Inputs
        self.char_box.draw(surface)
        self.username_box.draw(surface)
        self.password_box.draw(surface)

        self.back_button.draw(surface)
        self.next_button.draw(surface)

        # ------------------------------
        # DESCRIPTION PANEL (DRAW)
        # ------------------------------
        pygame.draw.rect(surface, (0, 0, 0, 200), self.desc_rect, border_radius=12)
        pygame.draw.rect(surface, (255, 255, 255), self.desc_rect, 2, border_radius=12)

        # Wrapped description text
        self._draw_wrapped_text(surface, self.description_text, self.desc_rect.x + 20, self.desc_rect.y + 20, self.desc_rect.width - 40)
        # Draw the game cursor
        self.scene_manager.game_cursor.draw(surface)

    # Draw multiline text
    def _draw_wrapped_text(self, surface, text, x, y, max_width):
        words = text.split(" ")
        line = ""
        for word in words:
            test = line + word + " "
            if self.font.size(test)[0] < max_width:
                line = test
            else:
                surface.blit(self.font.render(line, True, (255,255,255)), (x, y))
                y += self.font.get_height() + 4
                line = word + " "
        surface.blit(self.font.render(line, True, (255,255,255)), (x, y))
