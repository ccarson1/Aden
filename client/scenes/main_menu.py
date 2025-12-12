import pygame
from client.ui.button import Button
from client.ui.input_box import InputBox
import os
import config
import socket
import time
import local_server

class MainMenu:
    def __init__(self, scene_manager, font, width, height):
        self.scene_manager = scene_manager
        self.font = font
        self.width = width
        self.height = height

        button_w, button_h = 200, 50
        spacing = 20
        center_x = (self.width - button_w) // 2
        start_y = 200

        # Buttons
        self.login_button = Button(center_x, start_y + 120 + spacing, button_w, button_h, "Login", font)
        self.new_char_button = Button(center_x, start_y + 180 + spacing, button_w, button_h, "New Character", font)
        self.start_local_server_button = Button(center_x, start_y + 240 + spacing, button_w, button_h, "Local Server", font)

        # Inputs
        self.host_input = InputBox(center_x, start_y, 200, 40, "HOST", font, text=config.HOST)
        self.port_input = InputBox(center_x, start_y + 60 + spacing, 200, 40, "PORT", font, text=str(config.AUTH_PORT))

        self.focusable = [self.host_input, self.port_input, self.login_button, self.new_char_button, self.start_local_server_button]
        self.focus_index = 0
        self._set_focus(0)
        
        path = os.path.join("assets", "images", "mountain_fixed.png")
        print(f"[DEBUG] Loading background: {path}")
        self.background_image = pygame.image.load(path)
        self.background_image = pygame.transform.scale(self.background_image, (self.width, self.height))

        self.scene_manager.server_info["ip"]
        self.scene_manager.server_info["port"]

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
            if isinstance(current, Button):
                if current == self.login_button:
                    self._login_action()
                elif current == self.new_char_button:
                    self._new_char_action()
                elif current == self.start_local_server_button:
                    self._start_local_server_action()

        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.login_button.is_clicked(event.pos):
                self._login_action()
            elif self.new_char_button.is_clicked(event.pos):
                self._new_char_action()
            elif self.start_local_server_button.is_clicked(event.pos):
                self._start_local_server_action()

    # def _login_action(self):
    #     host = self.host_input.text.strip()
    #     try:
    #         port = int(self.port_input.text.strip())
    #     except ValueError:
    #         port = 50880
    #     config.save_network_settings(host, port)
    #     self.scene_manager.switch_scene("login")

    # def _new_char_action(self):
    #     host = self.host_input.text.strip()
    #     try:
    #         port = int(self.port_input.text.strip())
    #     except ValueError:
    #         port = 50880
    #     config.save_network_settings(host, port)
    #     self.scene_manager.switch_scene("create")


    def _login_action(self):
        host = self.host_input.text.strip()
        try:
            port = int(self.port_input.text.strip())
        except ValueError:
            port = 50880

        # Update server info
        self.scene_manager.server_info["ip"] = host
        self.scene_manager.server_info["port"] = port

        # Switch to login scene (do not reconnect yet)
        self.scene_manager.switch_scene("login")


    def _new_char_action(self):
        host = self.host_input.text.strip()
        try:
            port = int(self.port_input.text.strip())
        except ValueError:
            port = 50880

        self.scene_manager.server_info["ip"] = host
        self.scene_manager.server_info["port"] = port

        self.scene_manager.network.reconnect(host, port)

        self.scene_manager.switch_scene("create")

    
    def wait_for_server(self, host, port, timeout=5.0):
        if not host:  # fallback if host is empty
            host = "127.0.0.1"
        start = time.time()
        while time.time() - start < timeout:
            try:
                s = socket.create_connection((host, port), timeout=0.5)
                s.close()
                return True
            except (ConnectionRefusedError, OSError):
                time.sleep(0.1)
        return False

    def _start_local_server_action(self):
        host = self.host_input.text.strip()
        try:
            port = int(self.port_input.text.strip())
        except ValueError:
            port = 50880

        self.scene_manager.server_info["ip"] = host
        self.scene_manager.server_info["port"] = port

        # Start servers
        auth_proc, main_proc = local_server.run_servers()
        self.scene_manager.auth_proc = auth_proc
        self.scene_manager.main_proc = main_proc

        # Wait for startup
        if self.wait_for_server(host, port):
            print("[INFO] Server is ready")
        else:
            print("[WARN] Server did not start in time")

        self.scene_manager.switch_scene("login")


    def update(self, dt):
        pass

    def draw(self, surface):
        surface.blit(self.background_image, (0,0))
        for item in self.focusable:
            item.draw(surface)
