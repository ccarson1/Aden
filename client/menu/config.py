import pygame

pygame.init()

SCREEN_WIDTH, SCREEN_HEIGHT = 1100, 640
NAV_HEIGHT = 50

# --- Colors ---
WHITE = (255, 255, 255)
GRAY = (120, 120, 120)
DARK_GRAY = (40, 40, 40)
LIGHT_GRAY = (180, 180, 180)
YELLOW = (255, 255, 100)
RED = (220, 80, 80)
GREEN = (60, 200, 60)
BLUE = (60, 120, 220)
BLACK = (0, 0, 0)



# --- Window Setup ---

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("RPG Multi-Screen Inventory System")
# --- Fonts ---
font_small = pygame.font.SysFont("arial", 16)
font_medium = pygame.font.SysFont("arial", 24)
font_large = pygame.font.SysFont("arial", 30)

# --- Grid Settings ---
SLOT_SIZE = 72
PADDING = 10

INV_START_X = 80
INV_START_Y = 120

# Equipment layout (right side)
EQUIP_SLOTS = ["Weapon", "Armor", "Armor", "Accessory"]
EQUIP_START_X = 700
EQUIP_START_Y = 120
EQUIP_SLOT_GAP = 12

# Stats panel
STATS_PANEL_X = EQUIP_START_X + 180
STATS_PANEL_Y = EQUIP_START_Y - 20

# Hotbar layout (bottom)
HOTBAR_SLOTS = 10
HOTBAR_START_X = (SCREEN_WIDTH - (HOTBAR_SLOTS * (SLOT_SIZE + PADDING))) // 2
HOTBAR_START_Y = SCREEN_HEIGHT - SLOT_SIZE - 40

# global image cache
IMAGE_CACHE = {}

# --- Dummy Items ---
ITEM_COLORS = {
    "potion": (200, 60, 60),
    "ingredient": (60, 120, 200),
    "weapon": (180, 120, 60),
    "armor": (100, 100, 200),
    "material": (160, 80, 160),
    "accessory": (180, 180, 60),
    "misc": (120, 200, 120),
}

# --- Inventory & Containers ---
TOTAL_INV_SLOTS = 42
INV_COLS = 6
INV_ROWS = (TOTAL_INV_SLOTS + INV_COLS - 1) // INV_COLS
INV_WIDTH = 520
INV_HEIGHT = 370

# Dynamic inventory size
INV_PANEL_TOP_PADDING = 16
INV_PANEL_BOTTOM_PADDING = 32
TOTAL_INV_SLOTS = 42  # change this to any number


INV_ROWS = (TOTAL_INV_SLOTS + INV_COLS - 1) // INV_COLS  # calculate rows automatically


# --Crafting Screen ---
CFT_COLS = 4           # columns fixed
CFT_WIDTH = 340
CFT_HEIGHT = 480

# Crafting layout (right side)
CFT_SLOTS = ["Item 1", "Item 2", "Item 3", "Item 4"]
CFT_START_X = 500
CFT_START_Y = 120
CFT_SLOT_GAP = 12

# --- SQLite Setup ---
DB_FILE = "inventory.db"