│
├─ server/
│   ├─ __init__.py
│   ├─ server.py           # Main server loop
│   ├─ network.py          # Handles socket connections
│   ├─ game_state.py       # Classes for Player, NPC, Enemy, Map
│   ├─ database.py         # Handles DB interactions
│   ├─ config.py           # Server config (port, IP, DB)
│   └─ utils.py            # Helper functions
│
├─ client/
│   ├─ __init__.py
│   ├─ main.py             # Launch game client
│   ├─ network.py          # Client socket communication
│   ├─ scenes/             # Modular game scenes
│   │    ├─ __init__.py
│   │    ├─ main_menu.py
│   │    ├─ game_scene.py
│   │    └─ ...            # Additional scenes
│   ├─ entities/           # Characters, NPCs, enemies
│   │    ├─ __init__.py
│   │    ├─ player.py
│   │    ├─ npc.py
│   │    └─ enemy.py
│   ├─ graphics/           # Sprites, animations
│   │    ├─ __init__.py
│   │    ├─ sprites.py
│   │    └─ animations.py
│   ├─ maps/               # Tiled map loader
│   │    ├─ __init__.py
│   │    └─ map_loader.py
│   ├─ ui/                 # UI elements (menus, HUD)
│   └─ config.py           # Client config (window size, etc.)
│
├─ assets/
│   ├─ images/
│   ├─ sprites/
│   └─ maps/
│
└─ README.md