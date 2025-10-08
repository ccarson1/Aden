import time
import pygame

class PlayerController:
    def __init__(self, player):
        self.player = player
        # Input history for client-side prediction and reconciliation
        self.input_history = []
        self.current_map = None
        self.moving = False
        self.frozen = False

    def capture_input(self):
        """
        Capture the current keyboard state for movement controls.

        Returns:
            dict: Dictionary representing directional input state.
                  Keys: "w", "s", "a", "d"; values: True if pressed.
        """
        keys = pygame.key.get_pressed()
        input_state = {
            "w": keys[pygame.K_w],
            "s": keys[pygame.K_s],
            "a": keys[pygame.K_a],
            "d": keys[pygame.K_d],
        }
        return input_state
        


    def apply_input(self, dt, current_map):
        """
        Apply movement input locally for client-side prediction.
        
        Args:
            input_state (dict): Current directional inputs.
            dt (float): Time delta since last frame (seconds).

        Returns:
            bool: True if the player moved this frame, False otherwise.
        """
        input_state = self.capture_input()
        dx = input_state["d"] - input_state["a"]
        dy = input_state["s"] - input_state["w"]
        moving = dx != 0 or dy != 0

        # Move the player with collision detection
        if current_map:
            self.player.move(dx, dy, dt, current_map.colliders)
            #current_map = self.current_map

        # Record input with timestamp for server reconciliation
        timestamp = time.time()
        self.input_history.append((timestamp, input_state))
        self.moving = moving

        return moving
    
    def check_portals(self, current_map, scene_manager):
        """
        Check if the local player is colliding with any portals on the current map.
        If so, send a portal enter request to the server.
        """
        if not current_map or self.frozen:
            return

        portal = current_map.get_portal_at(self.player.rect)
        if portal:
            print(f"[INFO] Portal triggered: {portal.target_map}")
            self.frozen = True  # freeze player immediately
            scene_manager.start_fade("game", portal)  #
    
    def update_remote_players(self, dt, client):
        """
        Smoothly interpolate all remote players toward their server-reported target positions.
        """
        for player in client.players.values():
            # Initialize render positions if they don't exist
            if not hasattr(player, "render_x"):
                player.render_x = player.x
                player.render_y = player.y

            # Initialize target positions if missing
            if not hasattr(player, "target_x"):
                player.target_x = player.x
            if not hasattr(player, "target_y"):
                player.target_y = player.y

            # Interpolation speed (units per second)
            speed = getattr(player, "speed", 200.0)

            # Compute distance to target
            dx = player.target_x - player.render_x
            dy = player.target_y - player.render_y
            dist = (dx**2 + dy**2)**0.5

            if dist > 0:
                move_dist = min(dist, speed * dt)
                player.render_x += dx / dist * move_dist
                player.render_y += dy / dist * move_dist
    
    def update(self, dt, current_map, players, client, scene_manager, camera):
        if self.frozen:
            # --- Still update remote players so they animate correctly ---
            self.update_remote_players(dt, client)
            for p in players.values():
                if p.current_map == self.player.current_map and p.moving:
                    p.update_animation(dt, moving=True)

            # --- Still send position to server (optional, keeps sync) ---
            client.send_move(
                self.player.x,
                self.player.y,
                self.player.direction,
                self.moving,
                scene_manager.server_info["ip"],
                scene_manager.server_info["port"]
            )

            # --- Still let camera follow player for fade transitions ---
            if current_map:
                map_width = current_map.tmx_data.width * current_map.tmx_data.tilewidth
                map_height = current_map.tmx_data.height * current_map.tmx_data.tileheight
                camera.update(self.player, map_width, map_height)

            # --- Skip portals & input while frozen ---
            return

        # --- Normal behavior when not frozen ---
        self.check_portals(current_map, scene_manager)
        self.apply_input(dt, current_map)

        # --- Interpolate local player towards server ---
        if hasattr(self.player, "server_x"):
            dx = self.player.server_x - self.player.x
            dy = self.player.server_y - self.player.y
            dist = (dx**2 + dy**2)**0.5

            max_snap = 64
            if dist > max_snap:
                self.player.x = self.player.server_x
                self.player.y = self.player.server_y
            else:
                correction_factor = 0.1
                self.player.x += dx * correction_factor
                self.player.y += dy * correction_factor

        # --- Remote players ---
        self.update_remote_players(dt, client)
        for p in players.values():
            if p.current_map == self.player.current_map and p.moving:
                p.update_animation(dt, moving=True)

        # --- Send local move packet ---
        client.send_move(
            self.player.x,
            self.player.y,
            self.player.direction,
            self.moving,
            scene_manager.server_info["ip"],
            scene_manager.server_info["port"]
        )

        # --- Camera follow ---
        if current_map:
            map_width = current_map.tmx_data.width * current_map.tmx_data.tilewidth
            map_height = current_map.tmx_data.height * current_map.tmx_data.tileheight
            camera.update(self.player, map_width, map_height)

        # --- Opaque tile fade ---
        if current_map and hasattr(current_map, "opaque_tiles"):
            colliding = any(self.player.rect.colliderect(r) for r in current_map.opaque_tiles)
            target_alpha = 150 if colliding else 255
            fade_speed = 300 * dt

            if current_map.opaque_alpha < target_alpha:
                current_map.opaque_alpha = min(target_alpha, current_map.opaque_alpha + fade_speed)
            elif current_map.opaque_alpha > target_alpha:
                current_map.opaque_alpha = max(target_alpha, current_map.opaque_alpha - fade_speed)

    
    def draw(self, temp_surface, cam_rect, players):
        """
        Draw the player on the given surface.

        Args:
            surface (pygame.Surface): The surface to draw the player on.
        """
        

        # --- Step 3: Draw remote players with offset ---

        for p in players.values():
            # if p.current_map != self.player.current_map:
            #     continue  # skip players in other maps

            # Skip remote players that have no map or different map
            # This is still in testing for a multiplayer visibility issue (I001)
            if not hasattr(p, "current_map") or p.current_map != self.player.current_map:
                continue


            frame = p.frames[p.direction][p.anim_frame]

            draw_x = getattr(p, "render_x", p.x)
            draw_y = getattr(p, "render_y", p.y)

            temp_surface.blit(frame, (draw_x - cam_rect.x, draw_y - cam_rect.y))

        # --- Step 4: Draw local player ---
        frame = self.player.frames[self.player.direction][self.player.anim_frame]
        temp_surface.blit(frame, (self.player.x - cam_rect.x, self.player.y - cam_rect.y))
        