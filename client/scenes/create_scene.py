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

        self.char_box = InputBox(input_x, start_y, input_width, input_height, "Character Name", font)
        self.username_box = InputBox(input_x, start_y + input_height + spacing, input_width, input_height, "Username", font)
        self.password_box = InputBox(input_x, start_y + (2 * input_height) + (2 * spacing), input_width, input_height, "Password", font)
        self.next_button = Button(input_x, start_y + (3 * input_height) + (3 * spacing), input_width, input_height, "Next", font)
        self.back_button = Button(input_x, start_y + (4 * input_height) + (4 * spacing), input_width, input_height, "Back", font)
        self.input_boxes = [self.char_box, self.username_box, self.password_box]

        # Load background
        path = os.path.join("assets", "images", "field_background.jpg")
        self.background_image = pygame.image.load(path)
        self.background_image = pygame.transform.scale(self.background_image, (self.width, self.height))


    def handle_event(self, event):
        for box in self.input_boxes:
            box.handle_event(event)
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.next_button.is_clicked(event.pos):
                char_name = self.char_box.text
                username = self.username_box.text
                password = self.password_box.text
                result = network_auth.create_account(char_name, username, password)
                if result["status"] == "ok":
                    self.scene_manager.login_info = result 
                    self.scene_manager.create_info = {
                        "char_name": char_name,
                        "username": username,
                        "password": password
                    }
                    self.scene_manager.switch_scene("server")
                else:
                    print("[ERROR] Account creation failed!", result)

            if self.back_button.is_clicked(event.pos):
                self.scene_manager.switch_scene("main_menu")

    def update(self, dt):
        pass

    def draw(self, surface):
        # Draw background first
        surface.blit(self.background_image, (0,0))
        for box in self.input_boxes:
            box.draw(surface)
        self.next_button.draw(surface)
        self.back_button.draw(surface)
