import pygame
from client.ui.input_box import InputBox
from client.ui.button import Button
import os

class LoginScene:
    def __init__(self, scene_manager, font, width, height):
        self.scene_manager = scene_manager
        self.font = font 
        self.width = width
        self.height = height 
        # Sizes
        input_width, input_height = 300, 50
        button_width, button_height = 200, 50
        spacing = 40  # vertical spacing between elements

        # Center X positions
        input_x = (self.width - input_width) // 2
        button_x = (self.width - button_width) // 2

        # Total height of all elements (2 inputs + button + 2 spacings)
        total_height = (2 * input_height) + button_height + (2 * spacing)
        start_y = (self.height - total_height) // 2

        # Input fields
        self.username_box = InputBox(input_x, start_y, input_width, input_height, "Username", font)
        self.password_box = InputBox(input_x, start_y + input_height + spacing, input_width, input_height, "Password", font)

        # Button
        self.next_button = Button(button_x,
                                  start_y + (2 * input_height) + (2 * spacing),
                                  button_width,
                                  button_height,
                                  "Next",
                                  font)

        self.input_boxes = [self.username_box, self.password_box]

        # Load background
        path = os.path.join("assets", "images", "field_background.jpg")
        self.background_image = pygame.image.load(path)
        self.background_image = pygame.transform.scale(self.background_image, (self.width, self.height))

    def handle_event(self, event):
        for box in self.input_boxes:
            box.handle_event(event)
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.next_button.is_clicked(event.pos):
                self.scene_manager.login_info = {
                    "username": self.username_box.text,
                    "password": self.password_box.text
                }
                self.scene_manager.switch_scene("server")

    def update(self, dt):
        pass

    def draw(self, surface):
        # Draw background first
        surface.blit(self.background_image, (0,0))
        for box in self.input_boxes:
            box.draw(surface)
        self.next_button.draw(surface)
