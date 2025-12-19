class MenuScreen:
    """Base class for all menu screens"""
    def __init__(self, name):
        self.name = name
        self.visible = True

        # shared UI state for all menu screens
        self.hover_slot = None
        self.dragging_item = None
        self.dragging_from = None
        self.split_popup = None
        self.message = ""
        
    def draw(self, surface): pass
    def handle_mouse_down(self, pos, button): pass
    def handle_mouse_up(self, pos, button): pass
    def handle_mouse_motion(self, pos): pass
    def handle_key_down(self, key): pass
