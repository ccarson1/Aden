
# HOST = "127.0.0.1"
# PORT = 50880
# AUTH_PORT = 50900
# TIMEOUT = 1.0
# PRR = 1.0 # Player Removal Rate
# #BUFFER_SIZE = 1024
# BUFFER_SIZE = 4096
# UPDATE_RATE = 0.05
# TIMEOUT = 5.0
# WIDTH = 1200
# HEIGHT = 800
# FONT_SIZE = 32
# TOAST_FONT_SIZE = 24
# BUTTON_COLOR = (100, 100, 255)
# TEXT_COLOR = (255, 255, 255)

# #auth
# TOKEN_CACHE_TTL = 30  # seconds
# TOKEN_TIMEOUT = 5  # seconds to wait for auth server response
# token_cache = {}

# #Game Save
# DB_REFRESH_INTERVAL = 60 
# SAVE_INTERVAL = 30 

import configparser
import os

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

