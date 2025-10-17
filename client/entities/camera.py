import pygame

class Camera:
    def __init__(self, width, height, zoom=1.0):
        self.width = width      # viewport width (screen)
        self.height = height    # viewport height (screen)
        self.zoom = zoom
        self.rect = pygame.Rect(0, 0, width, height)
        self.initialized = False 

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

        if self.initialized == True:

            # Move only when player crosses halfway
            if target_x > self.rect.centerx + 1:  
                self.rect.centerx = target_x
            elif target_x < self.rect.centerx - 1:
                self.rect.centerx = target_x

            if target_y > self.rect.centery + 1:
                self.rect.centery = target_y
            elif target_y < self.rect.centery - 1:
                self.rect.centery = target_y

        else:
            print(f"Player x: {player.x}")
            print(f"Player y: {player.y}")
            self.rect.centerx = target_x
            self.rect.centery = target_y
            self.initialized = True
            

        # Clamp inside map bounds
        self.rect.clamp_ip(pygame.Rect(0, 0, map_width, map_height))

    def world_to_screen(self, pos):
        """Convert world position to screen position"""
        return (pos[0] - self.rect.x, pos[1] - self.rect.y)

# import pygame

# class Camera:
#     def __init__(self, width, height, zoom=1.0):
#         self.width = width      # viewport width (screen)
#         self.height = height    # viewport height (screen)
#         self.zoom = zoom
#         self.rect = pygame.Rect(0, 0, width, height)
#         self.initialized = False 

#     def apply(self, target_rect):
#         """Convert world rect to screen rect"""
#         return target_rect.move(-self.rect.x, -self.rect.y)

#     def update(self, player, map_width, map_height):
#         """Center camera on player but clamp inside map bounds"""
#         target_x = player.rect.centerx
#         target_y = player.rect.centery

#         # 🟢 Initialize camera to player center on first update
#         if not self.initialized:
#             self.rect.center = (target_x, target_y)
#             self.initialized = True
#         else:
#             # Move only when player crosses 1-pixel threshold
#             if abs(target_x - self.rect.centerx) > 1:
#                 self.rect.centerx = target_x
#             if abs(target_y - self.rect.centery) > 1:
#                 self.rect.centery = target_y

#         # Clamp inside map bounds
#         self.rect.clamp_ip(pygame.Rect(0, 0, map_width, map_height))

#     def world_to_screen(self, pos):
#         """Convert world position to screen position"""
#         return (pos[0] - self.rect.x, pos[1] - self.rect.y)

