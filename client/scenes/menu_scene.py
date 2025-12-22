# client/scenes/menu_scene.py
import pygame
from client.menu.menu_manager import MenuManager
from client.menu.menu_screen import MenuScreen
from client.menu.cooking_screen import CookingScreen
from client.menu.enchanting_screen import EnchantingScreen
from client.menu.skills_screen import SkillsScreen
from client.menu.guild_screen import GuildScreen
from client.menu.quests_screen import QuestsScreen
from client.network import client
from client.menu.game_menu_screen import GameMenuScreen
from client.menu.alchemy_screen import AlchemyScreen
from client.menu.crafting_screen import CraftingScreen
from client.menu.main import SettingsScreen
import config

class MenuScene:
    def __init__(self, inventory):
        self.manager = MenuManager()
        
        # Register existing screens (unchanged)
        self.manager.add_screen(GameMenuScreen(inventory))
        self.manager.add_screen(inventory)
        self.manager.add_screen(AlchemyScreen())
        self.manager.add_screen(CraftingScreen())
        self.manager.add_screen(CookingScreen())
        self.manager.add_screen(SkillsScreen())
        self.manager.add_screen(EnchantingScreen())
        self.manager.add_screen(GuildScreen())
        self.manager.add_screen(QuestsScreen())
        self.manager.add_screen(SettingsScreen())

        self.manager.switch_screen("Menu")
        self.active = False  # overlay toggle

    def open(self):
        self.active = True

    def close(self):
        self.active = False

    def handle_event(self, event):
        # if not self.active:
        #     return

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.close()  # Close the menu on ESC
            elif event.key == pygame.K_m:
                if self.active:
                    if self.manager.active_screen == "Menu":
                        self.close()
                    else:
                        self.manager.active_screen = "Menu"
                else:
                    self.open()
                    self.manager.active_screen = "Menu"
            elif event.key == pygame.K_i:
                if self.active:
                    if self.manager.active_screen == "Inventory":
                        self.close()
                    else:
                        self.manager.active_screen = "Inventory"
                else:
                    self.open()
                    self.manager.active_screen = "Inventory"
            elif event.key == pygame.K_h:
                if self.active:
                    if self.manager.active_screen == "Alchemy":
                        self.close()
                    else:
                        self.manager.active_screen = "Alchemy"
                else:
                    self.open()
                    self.manager.active_screen = "Alchemy"
            elif event.key == pygame.K_c:
                if self.active:
                    if self.manager.active_screen == "Crafting":
                        self.close()
                    else:
                        self.manager.active_screen = "Crafting"
                else:
                    self.open()
                    self.manager.active_screen = "Crafting"
            elif event.key == pygame.K_k:
                if self.active:
                    if self.manager.active_screen == "Cooking":
                        self.close()
                    else:
                        self.manager.active_screen = "Cooking"
                else:
                    self.open()
                    self.manager.active_screen = "Cooking"
            elif event.key == pygame.K_l:
                if self.active:
                    if self.manager.active_screen == "Skills":
                        self.close()
                    else:
                        self.manager.active_screen = "Skills"
                else:
                    self.open()
                    self.manager.active_screen = "Skills"
            elif event.key == pygame.K_e:
                if self.active:
                    if self.manager.active_screen == "Enchanting":
                        self.close()
                    else:
                        self.manager.active_screen = "Enchanting"
                else:
                    self.open()
                    self.manager.active_screen = "Enchanting"
            elif event.key == pygame.K_g:
                if self.active:
                    if self.manager.active_screen == "Guild":
                        self.close()
                    else:
                        self.manager.active_screen = "Guild"
                else:
                    self.open()
                    self.manager.active_screen = "Guild"
            elif event.key == pygame.K_q:
                if self.active:
                    if self.manager.active_screen == "Quests":
                        self.close()
                    else:
                        self.manager.active_screen = "Quests"
                else:
                    self.open()
                    self.manager.active_screen = "Quests"
            elif event.key == pygame.K_j:
                if self.active:
                    if self.manager.active_screen == "Settings":
                        self.close()
                    else:
                        self.manager.active_screen = "Settings"
                else:
                    self.open()
                    self.manager.active_screen = "Settings"

        if event.type == pygame.MOUSEMOTION:
            self.manager.handle_mouse_motion(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            self.manager.handle_nav_click(event.pos)
            self.manager.handle_mouse_down(event.pos, event.button)
        elif event.type == pygame.MOUSEBUTTONUP:
            self.manager.handle_mouse_up(event.pos, event.button)

    def update(self, dt):
        pass  # menu doesn’t need game logic

    def draw(self, screen):
        if self.active:
            self.manager.draw(screen)
