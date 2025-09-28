import pygame
import time

class ToastMessage:
    def __init__(self, font, screen, duration=2, padding=10, bg_color=(0,0,0,150), text_color=(255,255,255)):
        self.font = font
        self.screen = screen
        self.duration = duration  # seconds
        self.padding = padding
        self.bg_color = bg_color
        self.text_color = text_color
        self.messages = []  # list of (text, start_time)

    def show(self, text):
        self.messages.append((text, time.time()))

    def draw(self):
        now = time.time()
        to_remove = []
        for i, (text, start_time) in enumerate(self.messages):
            elapsed = now - start_time
            if elapsed > self.duration:
                to_remove.append(i)
                continue

            # Render text
            text_surface = self.font.render(text, True, self.text_color)

            # Background rectangle
            rect = text_surface.get_rect(topleft=(self.padding, self.padding + i * (text_surface.get_height() + 5)))
            bg_surface = pygame.Surface((rect.width + self.padding*2, rect.height + self.padding//2), pygame.SRCALPHA)
            bg_surface.fill(self.bg_color)
            self.screen.blit(bg_surface, (rect.x - self.padding, rect.y - self.padding//4))
            
            # Draw text
            self.screen.blit(text_surface, rect)

        # Remove expired messages
        for i in reversed(to_remove):
            self.messages.pop(i)
