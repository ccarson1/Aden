import pygame, random

class Rain:
    def __init__(self, width, height, density=50, fall_speed=5, wind=2,
                 drop_length=8, thickness=1,
                 overlay_color=(30, 30, 40), overlay_alpha=80):
        self.width = width
        self.height = height
        self.density = density
        self.fall_speed = fall_speed
        self.wind = wind
        self.drop_length = drop_length
        self.thickness = thickness

        # cloudy overlay settings
        self.overlay_color = overlay_color
        self.overlay_alpha = overlay_alpha

        # initialize raindrops
        self.raindrops = []
        for _ in range(self.density):
            x = random.randint(0, self.width)
            y = random.randint(-self.height, 0)
            self.raindrops.append([x, y])

    def reset_drop(self, drop):
        """Respawn a raindrop depending on wind direction"""
        if self.wind > 0:  # blowing right → spawn top or left
            if random.random() < 0.7:  # 70% top, 30% left
                drop[0] = random.randint(0, self.width)
                drop[1] = random.randint(-20, -5)
            else:
                drop[0] = random.randint(-20, 0)
                drop[1] = random.randint(0, self.height)
        else:  # blowing left → spawn top or right
            if random.random() < 0.7:
                drop[0] = random.randint(0, self.width)
                drop[1] = random.randint(-20, -5)
            else:
                drop[0] = random.randint(self.width, self.width + 20)
                drop[1] = random.randint(0, self.height)

    def update(self):
        """Move raindrops and respawn out-of-bound ones"""
        for drop in self.raindrops:
            drop[0] += self.wind
            drop[1] += self.fall_speed

            if drop[1] > self.height or drop[0] < -50 or drop[0] > self.width + 50:
                self.reset_drop(drop)

    def draw(self, screen):
        """Draw rain and overcast overlay"""

        # --- Overlay first (dark cloudy sky) ---
        if self.overlay_alpha > 0:
            overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            overlay.fill((*self.overlay_color, self.overlay_alpha))
            screen.blit(overlay, (0, 0))

        # --- Then draw raindrops ---
        for drop in self.raindrops:
            pygame.draw.line(
                screen,
                (200, 200, 255),
                (drop[0], drop[1]),
                (drop[0] + self.wind * 2, drop[1] + self.drop_length),
                self.thickness
            )
