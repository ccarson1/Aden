from client.menu.inventory import InventorySystem
from client.menu.menu_screen import MenuScreen
import config as config
import pygame
import sys


class GameMenuScreen(MenuScreen):
    def __init__(self, inventory: InventorySystem):
        super().__init__("Menu")
        self.inventory = inventory
        self.buttons = []
        self.create_buttons()

    def create_buttons(self):
        # x, y, width, height
        start_x = config.WIDTH // 2 - 80
        start_y = config.WIDTH // 2 - 60
        btn_w, btn_h = 160, 40
        gap = 20

        self.buttons = [
            {"label": "Save", "rect": pygame.Rect(start_x, start_y, btn_w, btn_h)},
            {"label": "Load", "rect": pygame.Rect(start_x, start_y + (btn_h + gap), btn_w, btn_h)},
            {"label": "Exit", "rect": pygame.Rect(start_x, start_y + 2*(btn_h + gap), btn_w, btn_h)},
        ]

    def draw(self, surface):
        width, height = surface.get_size()  # Use actual surface size

        # Dim background
        overlay = pygame.Surface((width, height), pygame.SRCALPHA)
        overlay.fill((0,0,0,180))  # 180 alpha
        surface.blit(overlay, (0, 0))

        # Center buttons dynamically
        btn_w, btn_h = 160, 40
        gap = 20
        start_x = width // 2 - btn_w // 2
        start_y = height // 2 - (btn_h*3 + gap*2)//2  # vertically center 3 buttons

        for i, btn in enumerate(self.buttons):
            btn["rect"] = pygame.Rect(
                start_x,
                start_y + i*(btn_h + gap),
                btn_w,
                btn_h
            )

            pygame.draw.rect(surface, config.GRAY, btn["rect"], border_radius=6)
            pygame.draw.rect(surface, config.WHITE, btn["rect"], 2, border_radius=6)

            txt = config.font_medium.render(btn["label"], True, config.WHITE)
            surface.blit(
                txt,
                (btn["rect"].centerx - txt.get_width()//2,
                btn["rect"].centery - txt.get_height()//2)
            )


    def handle_mouse_down(self, pos, button):
        if button != 1:  # only left click
            return
        for btn in self.buttons:
            if btn["rect"].collidepoint(pos):
                if btn["label"] == "Save":
                    self.inventory.database.save_to_db()
                elif btn["label"] == "Load":
                    self.inventory.database.load_from_db()
                elif btn["label"] == "Exit":
                    print("Exiting game...")
                    pygame.quit()
                    sys.exit()
