

class InfoDisplay:

    def __init__(self, player, font):
        self.player = player
        self.font = font

    def display_player_name(self, surface, cam_rect):
        name_surface = self.font.render(self.player.name, True, (255, 255, 0))
        name_rect = name_surface.get_rect(center=(self.player.x - cam_rect.x + self.player.frame_w // 2, self.player.y - cam_rect.y - 10))
        surface.blit(name_surface, name_rect)

    def display_remote_player_name(self, surface, draw_x, draw_y, cam_rect, p):
        name_surface = self.font.render(p.name, True, (255, 255, 255))
        name_rect = name_surface.get_rect(center=(draw_x - cam_rect.x + p.frame_w // 2, draw_y - cam_rect.y - 10))
        surface.blit(name_surface, name_rect)