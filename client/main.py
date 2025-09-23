import pygame
from client.scene_manager import SceneManager
import config

pygame.init()


# Create a font instance to pass to UI elements
FONT_SIZE = config.FONT_SIZE
MAIN_FONT = pygame.font.SysFont(None, FONT_SIZE)

WIDTH, HEIGHT = config.WIDTH, config.HEIGHT
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Aden")



scene_manager = SceneManager(MAIN_FONT)
clock = pygame.time.Clock()

running = True
while running:
    dt = clock.tick(60) / 1000
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        scene_manager.current_scene.handle_event(event)

    scene_manager.current_scene.update(dt)
    scene_manager.current_scene.draw(screen)
    pygame.display.flip()

pygame.quit()
