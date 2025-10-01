import pygame
import time

class ToastManager:
    def __init__(self, screen, font):
        self.screen = screen
        self.font = font
        self.toasts = [] 

    def add_toast(self, text, duration=2.0):
        self.toasts.append({
            "text": text,
            "time": pygame.time.get_ticks(),
            "duration": duration * 1000  # convert to ms
        })

    def update(self):
        self.toasts = [
            t for t in self.toasts if pygame.time.get_ticks() - t["time"] < t["duration"]
        ]

    def draw(self, surface):
        y = 10
        for toast in self.toasts:
            surf = self.font.render(toast["text"], True, (255, 255, 255))
            rect = surf.get_rect(topleft=(10, y))
            surface.blit(surf, rect)
            y += rect.height + 5