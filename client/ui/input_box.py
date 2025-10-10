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
        handled = False  # Track whether this box handled the event

        if event.type == pygame.MOUSEBUTTONDOWN:
            # Activate if clicked
            self.active = self.rect.collidepoint(event.pos)
            handled = True

        elif event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
                handled = True
            elif event.key in (pygame.K_RETURN, pygame.K_ESCAPE):
                # Ignore these keys but mark them as handled
                handled = True
            elif event.key == pygame.K_TAB:
                # Ignore but do NOT mark as handled — allow scene to manage tab switching
                handled = False
            else:
                if event.unicode.isprintable():
                    self.text += event.unicode
                    handled = True

        return handled

    def draw(self, surface):
        # Update color based on active state
        self.color = ACTIVE_COLOR if self.active else INACTIVE_COLOR

        # Draw label
        label_surf = self.font.render(self.label, True, TEXT_COLOR)
        surface.blit(label_surf, (self.rect.x, self.rect.y - self.font.get_height() - 5))

        # Draw box
        pygame.draw.rect(surface, self.color, self.rect, 2)

        # Draw text
        txt_surf = self.font.render(self.text, True, TEXT_COLOR)
        surface.blit(txt_surf, (self.rect.x + 5, self.rect.y + 10))
