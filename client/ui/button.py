import pygame
import config

FONT_SIZE = config.FONT_SIZE
BUTTON_COLOR = config.BUTTON_COLOR
BUTTON_HIGHLIGHT_COLOR = (180, 180, 255)  # light highlight when focused
TEXT_COLOR = config.TEXT_COLOR

class Button:
    def __init__(self, x, y, w, h, text, font):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.font = font
        self.color = BUTTON_COLOR
        self.focused = False

    def draw(self, surface):
        color = BUTTON_HIGHLIGHT_COLOR if self.focused else self.color
        pygame.draw.rect(surface, color, self.rect)
        txt_surf = self.font.render(self.text, True, TEXT_COLOR)
        txt_rect = txt_surf.get_rect(center=self.rect.center)
        surface.blit(txt_surf, txt_rect)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)
