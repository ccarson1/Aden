import pygame

ACTIVE_COLOR = (200, 200, 255)
INACTIVE_COLOR = (255, 255, 255)
TEXT_COLOR = (0, 0, 0)

class InputBox:
    def __init__(self, x, y, w, h, label, font, text=""):
        self.rect = pygame.Rect(x, y, w, h)
        self.label = label
        self.text = text
        self.font = font
        self.active = False
        self.color = INACTIVE_COLOR

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
            self.color = ACTIVE_COLOR if self.active else INACTIVE_COLOR
        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.key != pygame.K_RETURN:
                self.text += event.unicode

    def draw(self, surface):
        # Draw label
        label_surf = self.font.render(self.label, True, INACTIVE_COLOR)
        surface.blit(label_surf, (self.rect.x, self.rect.y - self.font.get_height() - 5))
        # Draw box
        pygame.draw.rect(surface, self.color, self.rect, 2)
        # Draw text
        txt_surf = self.font.render(self.text, True, TEXT_COLOR)
        surface.blit(txt_surf, (self.rect.x + 5, self.rect.y + 10))
