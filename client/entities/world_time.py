# client/entities/world_time.py
import time
import pygame

class WorldTime:
    """
    Handles accelerated in-game time based on server UTC time.
    1 real second = 1 in-game minute.
    Provides formatted time string and lighting alpha values.
    """

    def __init__(self):
        self.current_time = "00:00"

    def update(self, server_time_str):
        """
        Convert server-provided UTC time to accelerated game time.
        """
        try:
            h, m, s = map(int, server_time_str.split(":"))

            # Total real seconds since midnight
            total_seconds = h * 3600 + m * 60 + s

            # Accelerated: 1 real second = 1 in-game minute
            total_game_minutes = total_seconds

            game_hours = (total_game_minutes // 60) % 24
            game_minutes = total_game_minutes % 60

            self.current_time = f"{game_hours:02d}:{game_minutes:02d}"
        except Exception:
            self.current_time = "00:00"

    def get_light_alpha(self):
        """
        Convert current_time (HH:MM) to overlay alpha.
        0 = day, 180 = night.
        """
        try:
            h, m = map(int, self.current_time.split(":"))
            total_minutes = h * 60 + m

            # Define thresholds
            dawn_start  = 5 * 60   # 05:00
            day_start   = 6 * 60   # 06:00
            dusk_start  = 18 * 60  # 18:00
            night_start = 19 * 60  # 19:00

            if day_start <= total_minutes < dusk_start:
                return 0  # Day

            elif dusk_start <= total_minutes < night_start:
                # Fade into night
                progress = (total_minutes - dusk_start) / 60
                return int(progress * 180)

            elif dawn_start <= total_minutes < day_start:
                # Fade into day
                progress = (total_minutes - dawn_start) / 60
                return int((1 - progress) * 180)

            else:
                return 180  # Night
        except Exception:
            return 0
        
    
    def draw(self, surface, current_map, camera):
        """
        Draw overlay based on current time.
        """
        alpha = self.get_light_alpha()
        if alpha > 0:
            # Base night overlay
            overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
            overlay.fill((0, 0, 50, alpha))  # night blue

            # Light tiles reduce darkness
            for rect, radius in getattr(current_map, "light_tiles", []):
                light_surf = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)

                # Radial gradient: center = brightest, edges = dim
                for r in range(radius, 0, -1):
                    t = r / radius  # 1 at edge, 0 at center
                    fade = int(alpha * ((1 - t) ** 2))  # quadratic: center stronger
                    pygame.draw.circle(
                        light_surf,
                        (0, 0, 0, fade),
                        (radius, radius),
                        r
                    )

                # Subtract from overlay to clear darkness
                overlay.blit(
                    light_surf,
                    (rect.centerx - radius - camera.rect.x,
                    rect.centery - radius - camera.rect.y),
                    special_flags=pygame.BLEND_RGBA_SUB
                )

            # Apply overlay
            surface.blit(overlay, (0, 0))
