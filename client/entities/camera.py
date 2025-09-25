import pygame

class Camera:
    def __init__(self, width, height, zoom=1.0):
        self.width = width      # viewport width (screen)
        self.height = height    # viewport height (screen)
        self.zoom = zoom
        self.rect = pygame.Rect(0, 0, width, height)

    def apply(self, target_rect):
        """Convert world rect to screen rect"""
        return target_rect.move(-self.rect.x, -self.rect.y)

    def update(self, player, map_width, map_height):
        """Center camera on player but clamp inside map bounds"""

        # Target center (player position)
        target_x = player.rect.centerx
        target_y = player.rect.centery

        # Half viewport size
        half_w = self.rect.width // 2
        half_h = self.rect.height // 2

        # Move only when player crosses halfway
        if target_x > self.rect.centerx + 1:  
            self.rect.centerx = target_x
        elif target_x < self.rect.centerx - 1:
            self.rect.centerx = target_x

        if target_y > self.rect.centery + 1:
            self.rect.centery = target_y
        elif target_y < self.rect.centery - 1:
            self.rect.centery = target_y

        # Clamp inside map bounds
        self.rect.clamp_ip(pygame.Rect(0, 0, map_width, map_height))

    def world_to_screen(self, pos):
        """Convert world position to screen position"""
        return (pos[0] - self.rect.x, pos[1] - self.rect.y)
