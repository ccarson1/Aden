import pygame
from client.ui.button import Button
import os

class MainMenu:
    def __init__(self, scene_manager, font, width, height):
        self.scene_manager = scene_manager
        self.font = font  # save font instance
        self.width = width
        self.height = height

        button_width = 200
        button_height = 50
        spacing = 20  # space between buttons

        # Center X coordinate
        center_x = (self.width - button_width) // 2

        # Start Y so both buttons are vertically centered
        total_height = (2 * button_height) + spacing
        start_y = (self.height - total_height) // 2

        self.login_button = Button(center_x, start_y, button_width, button_height, "Login", self.font)
        self.new_char_button = Button(center_x, start_y + button_height + spacing, button_width, button_height, "New Character", self.font)

        # Load background
        path = os.path.join("assets", "images", "field_background.jpg")
        self.background_image = pygame.image.load(path)
        self.background_image = pygame.transform.scale(self.background_image, (self.width, self.height))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = event.pos
            if self.login_button.is_clicked(pos):
                self.scene_manager.switch_scene("login")
            elif self.new_char_button.is_clicked(pos):
                self.scene_manager.switch_scene("create")

    def update(self, dt):
        pass

    def draw(self, surface):
        # Draw background first
        surface.blit(self.background_image, (0,0))
        self.login_button.draw(surface)
        self.new_char_button.draw(surface)
