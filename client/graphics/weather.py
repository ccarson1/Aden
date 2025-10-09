import pygame, random, math

class Rain:
    def __init__(self, width, height, density=50, fall_speed=5, wind=2,
                 drop_length=8, thickness=1, overlay_color=(30, 30, 40),
                 overlay_alpha=80, start_time=300000):  # milliseconds
        self.width = width
        self.height = height
        self.target_density = density  # final desired density
        self.current_density = 0       # start with no drops
        self.fall_speed = fall_speed
        self.wind = wind
        self.drop_length = drop_length
        self.thickness = thickness
        self.overlay_color = overlay_color
        self.overlay_alpha = overlay_alpha
        self.start_time = start_time   # time to reach full density (ms)
        self.start_ticks = pygame.time.get_ticks()  # time when rain started

        # Pre-generate full set of raindrops, but only use a subset at first
        self.all_drops = [
            [random.randint(0, self.width), random.randint(-self.height, 0)]
            for _ in range(self.target_density)
        ]

    def reset_drop(self, drop):
        """Respawn a raindrop depending on wind direction"""
        if self.wind > 0:
            if random.random() < 0.7:
                drop[0] = random.randint(0, self.width)
                drop[1] = random.randint(-20, -5)
            else:
                drop[0] = random.randint(-20, 0)
                drop[1] = random.randint(0, self.height)
        else:
            if random.random() < 0.7:
                drop[0] = random.randint(0, self.width)
                drop[1] = random.randint(-20, -5)
            else:
                drop[0] = random.randint(self.width, self.width + 20)
                drop[1] = random.randint(0, self.height)

    def update(self):
        """Move raindrops, and gradually increase density"""
        # --- Increase density over time ---
        elapsed = pygame.time.get_ticks() - self.start_ticks
        if elapsed < self.start_time:
            # Smooth linear interpolation from 0 to full density
            progress = elapsed / self.start_time
            self.current_density = int(self.target_density * progress)
        else:
            self.current_density = self.target_density

        # Update only the visible subset of drops
        for drop in self.all_drops[:self.current_density]:
            drop[0] += self.wind
            drop[1] += self.fall_speed

            if drop[1] > self.height or drop[0] < -50 or drop[0] > self.width + 50:
                self.reset_drop(drop)

    def draw(self, screen):
        """Draw rain and overcast overlay"""
        if self.overlay_alpha > 0:
            overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            overlay.fill((*self.overlay_color, self.overlay_alpha))
            screen.blit(overlay, (0, 0))

        raindrop_alpha = 80  # adjust for visibility
        raindrop_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

        # Draw only the currently active drops
        for drop in self.all_drops[:self.current_density]:
            pygame.draw.line(
                raindrop_surface,
                (200, 200, 255, raindrop_alpha),
                (drop[0], drop[1]),
                (drop[0] + self.wind * 2, drop[1] + self.drop_length),
                self.thickness
            )

        screen.blit(raindrop_surface, (0, 0))


class Snow:
    def __init__(self, width, height, density=100, fall_speed=1.5, wind=0.5,
                 min_size=2, max_size=5, overlay_color=(220, 220, 255),
                 overlay_alpha=40, start_time=3000):  # milliseconds
        self.width = width
        self.height = height
        self.target_density = density
        self.current_density = 0
        self.fall_speed = fall_speed
        self.wind = wind
        self.min_size = min_size
        self.max_size = max_size
        self.overlay_color = overlay_color
        self.overlay_alpha = overlay_alpha
        self.start_time = start_time
        self.start_ticks = pygame.time.get_ticks()

        # Pre-generate all flakes with individual properties
        self.all_flakes = []
        for _ in range(self.target_density):
            x = random.randint(0, self.width)
            y = random.randint(-self.height, 0)
            size = random.uniform(self.min_size, self.max_size)
            drift_phase = random.uniform(0, math.pi * 2)
            drift_speed = random.uniform(0.01, 0.03)
            self.all_flakes.append([x, y, size, drift_phase, drift_speed])

    def reset_flake(self, flake):
        """Respawn a snowflake above the screen"""
        flake[0] = random.randint(0, self.width)
        flake[1] = random.randint(-20, -5)
        flake[2] = random.uniform(self.min_size, self.max_size)
        flake[3] = random.uniform(0, math.pi * 2)
        flake[4] = random.uniform(0.01, 0.03)

    def update(self):
        """Move flakes and gradually increase density"""
        elapsed = pygame.time.get_ticks() - self.start_ticks
        if elapsed < self.start_time:
            progress = elapsed / self.start_time
            self.current_density = int(self.target_density * progress)
        else:
            self.current_density = self.target_density

        for flake in self.all_flakes[:self.current_density]:
            # Gentle falling and side-to-side motion
            flake[3] += flake[4]  # update phase
            flake[0] += math.sin(flake[3]) * self.wind
            flake[1] += self.fall_speed + flake[2] * 0.05  # bigger flakes fall slightly faster

            if flake[1] > self.height:
                self.reset_flake(flake)

    def draw(self, screen):
        """Draw snowflakes and soft sky overlay"""
        if self.overlay_alpha > 0:
            overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            overlay.fill((*self.overlay_color, self.overlay_alpha))
            screen.blit(overlay, (0, 0))

        snow_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

        for flake in self.all_flakes[:self.current_density]:
            alpha = 180  # opacity of snowflakes
            color = (255, 255, 255, alpha)
            pygame.draw.circle(snow_surface, color, (int(flake[0]), int(flake[1])), int(flake[2]))

        screen.blit(snow_surface, (0, 0))