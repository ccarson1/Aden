def interpolate_player(player, dt):
    """
    Smoothly move a player from their current position (x, y)
    toward their target position (target_x, target_y) at a fixed speed.
    Instantly teleport if the target map changed.
    
    Args:
        player: Player object with x, y, prev_x, prev_y, target_x, target_y, current_map
        dt: Time delta in seconds since last update
    """

    # Make sure target coordinates exist
    if not hasattr(player, "target_x") or not hasattr(player, "target_y"):
        player.target_x = player.x
        player.target_y = player.y

    # Check for map teleport (target != current)
    if hasattr(player, "prev_map") and player.prev_map != player.current_map:
        # Instant jump on map switch
        player.x = player.target_x
        player.y = player.target_y
        player.prev_x = player.x
        player.prev_y = player.y
        player.prev_map = player.current_map
        return

    # Default speed (units per second)
    speed = getattr(player, "speed", 200.0)

    # Compute distance
    dx = player.target_x - player.x
    dy = player.target_y - player.y
    dist = (dx**2 + dy**2) ** 0.5

    if dist > 0:
        move_dist = min(dist, speed * dt)
        player.x += dx / dist * move_dist
        player.y += dy / dist * move_dist

    # Update previous map for next tick
    player.prev_map = getattr(player, "current_map", player.prev_map)