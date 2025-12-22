import pygame
import math

class GameCursor:
    def __init__(self):
        self.CHARGE_SPEED = .3
        self.RADIUS = 10
        self.THICKNESS = 3
        self.charge = 0
        self.cursor_image = pygame.image.load("assets/sprites/Middle Ages--cursor--SweezyCursors.png")
        SCALE = 0.1  # 50% size
        self.cursor_image = pygame.transform.smoothscale(self.cursor_image, (32, 32))
        self.cursor_rect = self.cursor_image.get_rect()

        self.overlay_image = pygame.image.load("assets/images/White/crosshair061.png").convert_alpha()
        self.overlay_image = pygame.transform.smoothscale( self.overlay_image, (32, 32) )
        self.overlay_rect = self.overlay_image.get_rect()

    def draw_arc(self, surface, color, center, radius, percent, thickness):
        end_angle = percent * 2 * math.pi
        steps = 60
        for i in range(steps):
            a1 = end_angle * i / steps
            a2 = end_angle * (i + 1) / steps
            p1 = ( center[0] + math.cos(a1) * radius, center[1] + math.sin(a1) * radius )
            p2 = ( center[0] + math.cos(a2) * radius, center[1] + math.sin(a2) * radius )
            pygame.draw.line(surface, color, p1, p2, thickness)

    def update(self, charging, dt):
        if charging:
            self.charge = min(1.0, self.charge + dt / self.CHARGE_SPEED)
        else:
            self.charge = 0.0

    def draw(self, screen, menu_active=True):
        mx, my = pygame.mouse.get_pos()


        if not menu_active:
            pygame.draw.circle(screen, (255, 255, 255), (mx, my), self.RADIUS, 1)

            if self.charge > 0:
                self.draw_arc(screen, (50, 200, 255), (mx, my), self.RADIUS, self.charge, self.THICKNESS)
            screen.blit(self.overlay_image, (mx - self.overlay_rect.width // 2, my - self.overlay_rect.height // 2))
        else:
            screen.blit(self.cursor_image, (mx, my))
