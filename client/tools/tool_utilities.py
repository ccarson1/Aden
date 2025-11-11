import config
import pygame

class ToolUtilities:
    
    def __init__(self):
        pass

    def print_click_position(self, mouse_pos, cam_rect):
        """
        Prints the world coordinates of the mouse click.
        
        Args:
            mouse_pos (tuple): (x, y) position from pygame.mouse.get_pos()
        """

        world_x = mouse_pos[0] + cam_rect.x
        world_y = mouse_pos[1] + cam_rect.y
        print(f"Clicked at world coordinates: ({world_x}, {world_y})")

    


    

    def draw_debug_boundaries(self, local_player, temp_surface, cam_rect, current_map):

        def draw_collision_tiles(surface, cam_rect, current_map):
            """
            Draws the collision rectangles for debugging.
            """
            if not current_map:
                return

            # Draw colliders in red
            for collider in current_map.colliders:
                rect = collider["rect"]
                pygame.draw.rect(
                    surface,
                    (255, 0, 0),  # red
                    pygame.Rect(
                        rect.x - cam_rect.x,
                        rect.y - cam_rect.y,
                        rect.width,
                        rect.height
                    ),
                    2  # thickness
                )

            # Draw opaque tiles in blue
            for tile in current_map.opaque_tiles:
                rect = tile["rect"]
                pygame.draw.rect(
                    surface,
                    (0, 0, 255),  # blue
                    pygame.Rect(
                        rect.x - cam_rect.x,
                        rect.y - cam_rect.y,
                        rect.width,
                        rect.height
                    ),
                    2
                )

            # Draw elevation colliders in green
            for tile in current_map.elevation_colliders:
                rect = tile["rect"]
                pygame.draw.rect(
                    surface,
                    (0, 255, 0),  # green
                    pygame.Rect(
                        rect.x - cam_rect.x,
                        rect.y - cam_rect.y,
                        rect.width,
                        rect.height
                    ),
                    2
                )

        # Draw player's hitbox for debugging
        if config.PLAYER_SHOW_HITBOX:
            player_rect = local_player.rect  # or self.local_player.hitbox if you have that
            pygame.draw.rect(
                temp_surface,
                (0, 255, 255),  # cyan
                pygame.Rect(
                    player_rect.x - cam_rect.x,
                    player_rect.y - cam_rect.y,
                    player_rect.width,
                    player_rect.height
                ),
                2  # line thickness
            )

        # Draw regular foreground layer (unchanged and always after player in original code)
        current_map.draw(
            temp_surface,
            offset=(-cam_rect.x, -cam_rect.y),
            draw_only=["foreground"]
        )


        # Draw collision tiles for debugging
        if config.SHOW_COLLISION_TILES:
            draw_collision_tiles(temp_surface, cam_rect, current_map)