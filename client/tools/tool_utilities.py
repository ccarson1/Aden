

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