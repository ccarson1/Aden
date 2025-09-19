import pygame
from client.ui.button import Button
from client.ui.input_box import InputBox
import os
import config

class MainMenu:
    def __init__(self, scene_manager, font, width, height):
        self.scene_manager = scene_manager
        self.font = font
        self.width = width
        self.height = height

        button_width = 200
        button_height = 50
        spacing = 20

        center_x = (self.width - button_width) // 2
        start_y = 200  # top padding

        # Buttons
        self.login_button = Button(center_x, start_y + 120 + spacing, button_width, button_height, "Login", font)
        self.new_char_button = Button(center_x, start_y + 180 + spacing, button_width, button_height, "New Character", font)

        # Input boxes for HOST and PORT
        self.host_input = InputBox(center_x, start_y, 200, 40, "HOST", font, text=config.HOST)
        self.port_input = InputBox(center_x, start_y + 60 + spacing, 200, 40, "PORT", font, text=str(config.PORT))
        self.input_boxes = [self.host_input, self.port_input]

        # Background
        path = os.path.join("assets", "images", "field_background.jpg")
        self.background_image = pygame.image.load(path)
        self.background_image = pygame.transform.scale(self.background_image, (self.width, self.height))

    def handle_event(self, event):
        # Update input boxes
        for box in self.input_boxes:
            box.handle_event(event)

        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = event.pos
            if self.login_button.is_clicked(pos):
                # Update config values from inputs
                config.HOST = self.host_input.text.strip()
                try:
                    config.PORT = int(self.port_input.text.strip())
                except ValueError:
                    config.PORT = 50880  # fallback
                self.scene_manager.switch_scene("login")

            elif self.new_char_button.is_clicked(pos):
                config.HOST = self.host_input.text.strip()
                try:
                    config.PORT = int(self.port_input.text.strip())
                except ValueError:
                    config.PORT = 50880
                self.scene_manager.switch_scene("create")

    def update(self, dt):
        pass

    def draw(self, surface):
        surface.blit(self.background_image, (0,0))
        for box in self.input_boxes:
            box.draw(surface)
        self.login_button.draw(surface)
        self.new_char_button.draw(surface)
