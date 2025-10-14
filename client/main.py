import pygame
from client.scene_manager import SceneManager
import config
import local_server
import atexit

pygame.init()


# Create a font instance to pass to UI elements
FONT_SIZE = config.FONT_SIZE
MAIN_FONT = pygame.font.SysFont(None, FONT_SIZE)

WIDTH, HEIGHT = config.WIDTH, config.HEIGHT
# Default flags (software surface)
flags = 0

# Check if hardware acceleration is available
info = pygame.display.Info()
if hasattr(info, "hw") and info.hw:  # hardware surfaces supported
    flags |= pygame.HWSURFACE | pygame.DOUBLEBUF
else:
    # fallback to software rendering
    print("[INFO] Hardware acceleration not available — using CPU mode.")

# Optional: use fullscreen or resizable flags if you like
# flags |= pygame.RESIZABLE

screen = pygame.display.set_mode((WIDTH, HEIGHT), flags)
pygame.display.set_caption("Aden")



scene_manager = SceneManager(MAIN_FONT)
clock = pygame.time.Clock()

atexit.register(local_server.stop_servers)


running = True
while running:
    dt = clock.tick(60) / 1000
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        scene_manager.current_scene.handle_event(event)

    scene_manager.update(dt)
    scene_manager.draw(screen)
    pygame.display.flip()

local_server.stop_servers()
pygame.quit()
