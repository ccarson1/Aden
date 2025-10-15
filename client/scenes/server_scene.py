import pygame
from client.ui.input_box import InputBox
from client.ui.button import Button
import os
import config

class ServerScene:
    def __init__(self, scene_manager, font, width, height):
        self.scene_manager = scene_manager
        self.font = font
        self.width = width
        self.height = height

        input_w, input_h = 300, 50
        button_w, button_h = 200, 50
        spacing = 40
        input_x = (self.width - input_w) // 2
        button_x = (self.width - button_w) // 2
        start_y = (self.height - (2*input_h + button_h + 2*spacing)) // 2

        host = self.scene_manager.server_info.get("ip", config.HOST)

        self.ip_box = InputBox(input_x, start_y, input_w, input_h, "Server IP", font, host)
        self.port_box = InputBox(input_x, start_y + input_h + spacing, input_w, input_h, "Server Port", font, "50880")
        self.connect_button = Button(button_x, start_y + 2*input_h + 2*spacing, button_w, button_h, "Connect", font)

        self.focusable = [self.ip_box, self.port_box, self.connect_button]
        self.focus_index = 0
        self._set_focus(0)

        path = os.path.join("assets", "images", "mountain_fixed.png")
        self.background_image = pygame.image.load(path)
        self.background_image = pygame.transform.scale(self.background_image, (self.width, self.height))

    def _set_focus(self, index):
        for i, item in enumerate(self.focusable):
            if hasattr(item, "active"):
                item.active = False
            if hasattr(item, "focused"):
                item.focused = False
        item = self.focusable[index]
        if hasattr(item, "active"):
            item.active = True
        if hasattr(item, "focused"):
            item.focused = True

    def on_activate(self):
        # called whenever the scene is shown
        host = self.scene_manager.server_info.get("ip", config.HOST)
        port = self.scene_manager.server_info.get("auth_port", "50880")
        self.ip_box.text = host
        self.port_box.text = str(port)

    def handle_event(self, event):
        handled = False
        for item in self.focusable:
            if hasattr(item, "handle_event") and item.handle_event(event):
                handled = True

        if not handled and event.type == pygame.KEYDOWN and event.key == pygame.K_TAB:
            shift = pygame.key.get_mods() & pygame.KMOD_SHIFT
            self.focus_index = (self.focus_index - 1 if shift else self.focus_index + 1) % len(self.focusable)
            self._set_focus(self.focus_index)

        if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
            current = self.focusable[self.focus_index]
            if isinstance(current, Button) and current == self.connect_button:
                self._connect_action()

        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.connect_button.is_clicked(event.pos):
                self._connect_action()

    def _connect_action(self):
        ip = self.ip_box.text.strip()
        port = int(self.port_box.text.strip())

        # Save new values for later scenes
        self.scene_manager.server_info["ip"] = ip
        self.scene_manager.server_info["port"] = port

        config.save_network_settings(ip, port)
        # Start the game scene (client) with this server IP/PORT
        self.scene_manager.switch_scene("game")

    def update(self, dt):
        pass

    def draw(self, surface):
        surface.blit(self.background_image, (0,0))
        for item in self.focusable:
            item.draw(surface)
