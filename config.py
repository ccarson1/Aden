

import configparser
import os
import pygame

# Create parser and read INI
config = configparser.ConfigParser()
config_path = os.path.join(os.path.dirname(__file__), "config.ini")
config.read(config_path)

# Network
HOST = config.get("network", "HOST")
PORT = config.getint("network", "PORT")
AUTH_PORT = config.getint("network", "AUTH_PORT")
PRR = config.getfloat("network", "PRR")
BUFFER_SIZE = config.getint("network", "BUFFER_SIZE")
UPDATE_RATE = config.getfloat("network", "UPDATE_RATE")
TIMEOUT = config.getfloat("network", "TIMEOUT")

# Display
WIDTH = config.getint("display", "WIDTH")
HEIGHT = config.getint("display", "HEIGHT")
FONT_SIZE = config.getint("display", "FONT_SIZE")
DISPLAY_NAME_FONT_SIZE = config.getint("display", "DISPLAY_NAME_FONT_SIZE")
TOAST_FONT_SIZE = config.getint("display", "TOAST_FONT_SIZE")
BUTTON_COLOR = tuple(map(int, config.get("display", "BUTTON_COLOR").split(",")))
TEXT_COLOR = tuple(map(int, config.get("display", "TEXT_COLOR").split(",")))

# Menu
NAV_HEIGHT = config.getint("menu", "NAV_HEIGHT")

WHITE = (255, 255, 255)
GRAY = (120, 120, 120)
DARK_GRAY = (40, 40, 40)
LIGHT_GRAY = (180, 180, 180)
YELLOW = (255, 255, 100)
RED = (220, 80, 80)
GREEN = (60, 200, 60)
BLUE = (60, 120, 220)
BLACK = (0, 0, 0)



SLOT_SIZE = config.getint("menu", "SLOT_SIZE")
PADDING = config.getint("menu", "PADDING")

INV_START_X = config.getint("menu", "INV_START_X")
INV_START_Y = config.getint("menu", "INV_START_Y")

EQUIP_SLOTS = ["Weapon", "Armor", "Armor", "Accessory"]
EQUIP_START_X = config.getint("menu", "EQUIP_START_X")
EQUIP_START_Y = config.getint("menu", "EQUIP_START_Y")
EQUIP_SLOT_GAP = config.getint("menu", "EQUIP_SLOT_GAP")

STATS_PANEL_X = EQUIP_START_X + 180
STATS_PANEL_Y = EQUIP_START_Y - 20

HOTBAR_SLOTS = config.getint("menu", "HOTBAR_SLOTS")
HOTBAR_START_X = (WIDTH - (HOTBAR_SLOTS * (SLOT_SIZE + PADDING))) // 2
HOTBAR_START_Y = HEIGHT - SLOT_SIZE - 40

IMAGE_CACHE = image_cache = {}

ITEM_COLORS = {
    "potion": (200, 60, 60),
    "ingredient": (60, 120, 200),
    "weapon": (180, 120, 60),
    "armor": (100, 100, 200),
    "material": (160, 80, 160),
    "accessory": (180, 180, 60),
    "misc": (120, 200, 120),
}
TOTAL_INV_SLOTS = config.getint("menu", "TOTAL_INV_SLOTS")
INV_COLS = config.getint("menu", "INV_COLS")
INV_ROWS = (TOTAL_INV_SLOTS + INV_COLS - 1) // INV_COLS
INV_WIDTH = config.getint("menu", "INV_WIDTH")
INV_HEIGHT = config.getint("menu", "INV_HEIGHT")


INV_PANEL_TOP_PADDING = config.getint("menu", "INV_PANEL_TOP_PADDING")
INV_PANEL_BOTTOM_PADDING = config.getint("menu", "INV_PANEL_BOTTOM_PADDING")
TOTAL_INV_SLOTS = config.getint("menu", "TOTAL_INV_SLOTS")

INV_ROWS = (TOTAL_INV_SLOTS + INV_COLS - 1) // INV_COLS 

CFT_COLS = config.getint("menu", "CFT_COLS")
CFT_WIDTH = config.getint("menu", "CFT_WIDTH")
CFT_HEIGHT = config.getint("menu", "CFT_HEIGHT")

CFT_SLOTS = ["Item 1", "Item 2", "Item 3", "Item 4"]
CFT_START_X = config.getint("menu", "CFT_START_X")
CFT_START_Y = config.getint("menu", "CFT_START_Y")
CFT_SLOT_GAP = config.getint("menu", "CFT_SLOT_GAP")  

DB_FILE = "inventory.db"
print(f"DB_FILE: {DB_FILE}")

# Auth
TOKEN_CACHE_TTL = config.getint("auth", "TOKEN_CACHE_TTL")
token_cache = {}  # Initialize manually
CERT_DIR = config.get("auth", "cert_dir")

# Game Save
DB_REFRESH_INTERVAL = config.getint("game_save", "DB_REFRESH_INTERVAL")
SAVE_INTERVAL = config.getint("game_save", "SAVE_INTERVAL")

# Debug
SHOW_ENEMY_RECT = config.getboolean("debug", "SHOW_ENEMY_RECT")
SHOW_COLLISION_TILES = config.getboolean("debug", "SHOW_COLLISION_TILES")
PLAYER_SHOW_HITBOX = config.getboolean("debug", "PLAYER_SHOW_HITBOX")

def save_network_settings(host, port):
    config.set("network", "HOST", host)
    config.set("network", "PORT", str(port))
    with open(config_path, "w") as f:
        config.write(f)
    # Update module variables so code uses new values immediately
    global HOST, PORT
    HOST = host
    PORT = port

def get_network_address():
    return HOST, PORT

def init_fonts():
    global font_small, font_medium, font_large
    font_small = pygame.font.SysFont("arial", 16)
    font_medium = pygame.font.SysFont("arial", 24)
    font_large = pygame.font.SysFont("arial", 30)

ASSET_DIR = os.path.join(os.path.dirname(__file__), "client/menu")

def asset(path):
    full_path = os.path.join(ASSET_DIR, path.replace("/", os.sep))
    if not os.path.exists(full_path):
        print(f"[WARN] Asset not found: {full_path}")
    return full_path

