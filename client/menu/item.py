import pygame
import os

class Item:
    def __init__(
        self, name, quantity, type, color, bonus=None, stackable=True,
        image_path=None, level=0, xp=0, max_xp=0, spoil=None
    ):
        self.name = name
        self.quantity = quantity
        self.type = type
        self.color = color
        self.bonus = bonus or {}
        self.stackable = stackable
        self.image_path = image_path
        self.level = level
        self.xp = xp
        self.max_xp = max_xp
        self.spoil = spoil

        # --- LOAD IMAGE ---
        if self.image_path and os.path.exists(self.image_path):
            self.image = pygame.image.load(self.image_path).convert_alpha()
        else:
            self.image = pygame.Surface((32, 32), pygame.SRCALPHA)
            self.image.fill((255, 0, 255))  # placeholder
            if self.image_path:
                print(f"[WARN] Item image not found: {self.image_path}")

    def __getitem__(self, key):
        return getattr(self, key)

    def __setitem__(self, key, value):
        setattr(self, key, value)

    def get(self, key, default=None):
        return getattr(self, key, default)

    def copy(self):
        return Item(
            self.name, self.quantity, self.type, self.color,
            self.bonus.copy(), self.stackable, self.image_path,
            self.level, self.xp, self.max_xp, self.spoil
        )