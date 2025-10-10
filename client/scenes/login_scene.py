import pygame
from client.ui.input_box import InputBox
from client.ui.button import Button
import os
from client.network import network_auth
import config

class LoginScene:
    def __init__(self, scene_manager, font, width, height):
        self.scene_manager = scene_manager
        self.font = font
        self.width = width
        self.height = height

        # Sizes
        input_width, input_height = 300, 50
        button_width, button_height = 200, 50
        spacing = 40

        input_x = (self.width - input_width) // 2
        button_x = (self.width - button_width) // 2
        total_height = 2 * input_height + button_height + 2 * spacing
        start_y = (self.height - total_height) // 2

        # Inputs
        self.username_box = InputBox(input_x, start_y, input_width, input_height, "Username", font)
        self.password_box = InputBox(input_x, start_y + input_height + spacing, input_width, input_height, "Password", font)

        # Buttons
        self.next_button = Button(button_x, start_y + 2*input_height + 2*spacing, button_width, button_height, "Next", font)
        self.back_button = Button(button_x, start_y + 3*input_height + 3*spacing, button_width, button_height, "Back", font)

        # Focusable order: inputs + buttons
        self.focusable = [self.username_box, self.password_box, self.next_button, self.back_button]
        self.focus_index = 0
        self._set_focus(0)

        # Background
        path = os.path.join("assets", "images", "field_background.jpg")
        self.background_image = pygame.image.load(path)
        self.background_image = pygame.transform.scale(self.background_image, (self.width, self.height))

    def _set_focus(self, index):
        # Remove old focus
        for i, item in enumerate(self.focusable):
            if hasattr(item, "active"):
                item.active = False
            if hasattr(item, "focused"):
                item.focused = False

        # Set new focus
        item = self.focusable[index]
        if hasattr(item, "active"):
            item.active = True
        if hasattr(item, "focused"):
            item.focused = True

    def handle_event(self, event):
        # Let input boxes handle event first
        handled = False
        for box in self.focusable:
            if hasattr(box, "handle_event") and box.handle_event(event):
                handled = True

        # TAB navigation
        if not handled and event.type == pygame.KEYDOWN and event.key == pygame.K_TAB:
            shift = pygame.key.get_mods() & pygame.KMOD_SHIFT
            self.focus_index = (self.focus_index - 1 if shift else self.focus_index + 1) % len(self.focusable)
            self._set_focus(self.focus_index)

        # Enter on buttons
        if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
            current = self.focusable[self.focus_index]
            if isinstance(current, Button):
                if current == self.next_button:
                    self._next_action()
                elif current == self.back_button:
                    self._back_action()

        # Mouse click on buttons
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.next_button.is_clicked(event.pos):
                self._next_action()
            elif self.back_button.is_clicked(event.pos):
                self._back_action()

    def _next_action(self):
        username = self.username_box.text
        password = self.password_box.text

        # Use the server info entered by the user
        host = self.scene_manager.server_info.get("ip", config.HOST)
        port = self.scene_manager.server_info.get("port", config.AUTH_PORT)

        # Authenticate against auth server
        result = network_auth.authenticate(username, password, host=host, port=port)
        if result["status"] == "ok":
            token = result["token"]
            self.scene_manager.login_info = {"username": username, "password": password, "token": token}

            # Reconnect NetworkClient to the game server
            game_host = self.scene_manager.server_info.get("ip", config.HOST)
            game_port = self.scene_manager.server_info.get("port", config.PORT)
            self.scene_manager.network.reconnect(game_host, game_port)

            self.scene_manager.switch_scene("server")
        else:
            print("[ERROR] Invalid login!")

    def _back_action(self):
        self.scene_manager.switch_scene("main_menu")

    def update(self, dt):
        pass

    def draw(self, surface):
        surface.blit(self.background_image, (0,0))
        for item in self.focusable:
            item.draw(surface)
