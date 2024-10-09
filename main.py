import pygame
import random
import json
import os

# Constants
WIDTH, HEIGHT = 1000, 1000
GRID_SIZE = 100
TILE_SIZE = WIDTH // GRID_SIZE
FPS = 2

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (240, 240, 240)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
DARK_GREEN = (34, 139, 34)
BROWN = (139, 69, 19)
LIGHT_BLUE = (0, 200, 255)
YELLOW = (255, 255, 0)

class Man:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.last_ate = 0
        self.last_drank = 0
        self.health = 200
        self.stamina = 200
        self.inventory = {"wood": 0, "stone": 0, "berries": 0}
        self.weapon = None
        self.current_task = None  # New attribute to track the current task

    def is_hungry(self, current_time):
        return current_time - self.last_ate > 30

    def is_thirsty(self, current_time):
        return current_time - self.last_drank > 25

    def get_hunger_level(self, current_time):
        return self._get_resource_level(current_time - self.last_ate, 200.0)

    def get_thirst_level(self, current_time):
        return self._get_resource_level(current_time - self.last_drank, 200.0)
    
    @staticmethod
    def _get_resource_level(duration, max_duration):
        return 1.0 - min(1.0, max(0.0, duration / max_duration))

    def move_to_spot(self, spot):
        self.x += (spot[0] > self.x) - (spot[0] < self.x)
        self.y += (spot[1] > self.y) - (spot[1] < self.y)
        self.stamina = max(0, self.stamina - 1)

    def rest(self):
        self.stamina = min(100, self.stamina + 5)

    def attack(self, target):
        damage = 10 if self.weapon else 5
        target.health -= damage
        self.stamina = max(0, self.stamina - 10)

class Wolf:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.health = 50

    def move_to_spot(self, spot):
        self.x += (spot[0] > self.x) - (spot[0] < self.x)
        self.y += (spot[1] > self.y) - (spot[1] < self.y)

class Environment:
    def __init__(self):
        self.trees = set()
        self.berries = set()
        self.water_sources = set()
        self.stones = set()
        self.wolves = []
        self.removed_berries = {}  # New: Track removed berries
        self._create_environment()

    def _create_environment(self):
        for i in range(GRID_SIZE):
            for j in range(GRID_SIZE):
                if (i, j) != (50, 50):
                    if random.random() < 0.01:
                        self.trees.add((i, j))
                    elif random.random() < 0.002:
                        self.berries.add((i, j))
                    elif random.random() < 0.001:
                        self.water_sources.add((i, j))
                    elif random.random() < 0.005:
                        self.stones.add((i, j))

        for _ in range(2):
            self.wolves.append(Wolf(random.randint(0, GRID_SIZE-1), random.randint(0, GRID_SIZE-1)))

    def find_closest(self, origin, items):
        if not items:
            return None
        # Convert set to list if it's a set
        items_list = list(items) if isinstance(items, set) else items
        if isinstance(items_list[0], Wolf):
            return min(items_list, key=lambda item: (item.x - origin.x) ** 2 + (item.y - origin.y) ** 2)
        else:
            return min(items_list, key=lambda item: (item[0] - origin.x) ** 2 + (item[1] - origin.y) ** 2)

    def check_step(self, man, current_time):
        pos = (man.x, man.y)
        if pos in self.berries:
            man.last_ate = current_time
            man.inventory["berries"] += 1
            self.berries.remove(pos)
            self.removed_berries[pos] = current_time  # New: Track when berry was removed
        elif pos in self.water_sources:
            man.last_drank = current_time
        elif pos in self.trees:
            man.inventory["wood"] += 1
        elif pos in self.stones:
            man.inventory["stone"] += 1
            self.stones.remove(pos)

    def respawn_berries(self, current_time):
        berries_to_respawn = []
        for pos, removal_time in self.removed_berries.items():
            if current_time - removal_time > 300:  # Respawn after 5 minutes (300 seconds)
                berries_to_respawn.append(pos)
        
        for pos in berries_to_respawn:
            self.berries.add(pos)
            del self.removed_berries[pos]

class Weather:
    def __init__(self):
        self.conditions = ["clear", "rainy", "stormy"]
        self.current_condition = "clear"
        self.change_time = 0

    def update(self, current_time):
        if current_time - self.change_time > 300:
            self.current_condition = random.choice(self.conditions)
            self.change_time = current_time

class Menu:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.Font(None, 36)

    def draw_button(self, text, rect, color, text_color):
        pygame.draw.rect(self.screen, color, rect)
        text_surf = self.font.render(text, True, text_color)
        text_rect = text_surf.get_rect(center=rect.center)
        self.screen.blit(text_surf, text_rect)

    def main_menu(self):
        self.screen.fill(WHITE)
        play_button = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 - 60, 200, 50)
        upgrades_button = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 10, 200, 50)
        load_button = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 80, 200, 50)
        self.draw_button("Play", play_button, GREEN, BLACK)
        self.draw_button("Upgrades", upgrades_button, LIGHT_BLUE, BLACK)
        self.draw_button("Load Game", load_button, YELLOW, BLACK)
        return play_button, upgrades_button, load_button

    def upgrade_menu(self, wood, stone):
        self.screen.fill(WHITE)
        craft_axe_button = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 - 60, 200, 50)
        craft_sword_button = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 10, 200, 50)
        back_button = pygame.Rect(WIDTH // 2 - 100, HEIGHT - 100, 200, 50)
        self.draw_button("Craft Axe (5 wood, 3 stone)", craft_axe_button, GREEN, BLACK)
        self.draw_button("Craft Sword (3 wood, 5 stone)", craft_sword_button, BLUE, BLACK)
        self.draw_button("Back", back_button, RED, BLACK)
        
        resources_text = f"Wood: {wood}, Stone: {stone}"
        text_surf = self.font.render(resources_text, True, BLACK)
        self.screen.blit(text_surf, (WIDTH // 2 - 100, HEIGHT // 2 - 120))
        
        return craft_axe_button, craft_sword_button, back_button

    def in_game_menu(self, inventory, current_task):
        menu_width, menu_height = WIDTH - 200, HEIGHT // 2
        menu_x, menu_y = (WIDTH - menu_width) - 100, (HEIGHT - menu_height) // 2
        menu_surface = pygame.Surface((menu_width, menu_height))
        menu_surface.fill(WHITE)
        pygame.draw.rect(menu_surface, BLACK, menu_surface.get_rect(), 2)
        
        inventory_text = [f"{item}: {count}" for item, count in inventory.items()]
        for i, text in enumerate(inventory_text):
            text_surf = self.font.render(text, True, BLACK)
            menu_surface.blit(text_surf, (20, 20 + i * 40))
        
        save_button = pygame.Rect(20, menu_height - 70, 160, 50)
        self.draw_button("Save Game", save_button, GREEN, BLACK)
        
        # Add task buttons
        tasks = ["None", "Mining", "Woodcutting", "Foraging", "Hunting"]
        button_width, button_height = 120, 40
        buttons = []
        for i, task in enumerate(tasks):
            button = pygame.Rect(200 + (i % 3) * (button_width + 10), 20 + (i // 3) * (button_height + 10), button_width, button_height)
            color = LIGHT_BLUE if task == current_task else GRAY
            self.draw_button(task, button, color, BLACK)
            buttons.append((task, button))
        
        self.screen.blit(menu_surface, (menu_x, menu_y))
        return pygame.Rect(menu_x + 20, menu_y + menu_height - 70, 160, 50), buttons

    def death_screen(self):
        self.screen.fill(WHITE)
        large_font = pygame.font.Font(None, 72)
        text = large_font.render("You're Dead", True, BLACK)
        text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))
        self.screen.blit(text, text_rect)
        main_menu_button = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 25, 200, 50)
        self.draw_button("Main Menu", main_menu_button, GREEN, BLACK)
        return main_menu_button

class GameState:
    MAIN_MENU = 'main_menu'
    IN_GAME = 'in_game'
    IN_GAME_MENU = 'in_game_menu'
    UPGRADE_MENU = 'upgrade_menu'
    DEATH_SCREEN = 'death_screen'

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Survival Game")
        self.clock = pygame.time.Clock()
        self.menu = Menu(self.screen)
        self.reset_game()
        self.state = GameState.MAIN_MENU
        self.running = True
        self.weather = Weather()

    def reset_game(self):
        self.man = Man(50, 50)
        self.environment = Environment()
        self.time = 0
        self.day = 0

    def draw_ui(self):
        bars = [
            (RED, self.man.get_hunger_level(self.time)),
            (BLUE, self.man.get_thirst_level(self.time)),
            (GREEN, self.man.health / 100),
            (YELLOW, self.man.stamina / 100)
        ]
        for i, (color, level) in enumerate(bars):
            bar_width, bar_height = 150, 20
            bar_x, bar_y = 10, 10 + i * (bar_height + 5)
            pygame.draw.rect(self.screen, GRAY, (bar_x, bar_y, bar_width, bar_height))
            pygame.draw.rect(self.screen, color, (bar_x, bar_y, int(bar_width * level), bar_height))

        day_text = f"Day: {self.day}"
        weather_text = f"Weather: {self.weather.current_condition}"
        font = pygame.font.Font(None, 24)
        day_surf = font.render(day_text, True, BLACK)
        weather_surf = font.render(weather_text, True, BLACK)
        self.screen.blit(day_surf, (WIDTH - 100, 10))
        self.screen.blit(weather_surf, (WIDTH - 150, 40))

    def draw_game(self):
        self.screen.fill(WHITE)
        self._draw_ground()
        self._draw_trees()
        self._draw_items(self.environment.berries, "B", RED)
        self._draw_items(self.environment.water_sources, "W", LIGHT_BLUE)
        self._draw_items(self.environment.stones, "S", GRAY)
        self._draw_man()
        self._draw_wolves()
        self.draw_ui()

    def _draw_ground(self):
        for i in range(GRID_SIZE):
            for j in range(GRID_SIZE):
                color = (0, random.randint(250, 255), 0)
                pygame.draw.rect(self.screen, color, (i * TILE_SIZE, j * TILE_SIZE, TILE_SIZE, TILE_SIZE))

    def _draw_trees(self):
        for tree in self.environment.trees:
            x, y = tree[0] * TILE_SIZE, tree[1] * TILE_SIZE
            pygame.draw.rect(self.screen, BROWN, (x + TILE_SIZE // 3, y, TILE_SIZE // 3, TILE_SIZE))
            pygame.draw.circle(self.screen, DARK_GREEN, (x + TILE_SIZE // 2, y), TILE_SIZE // 2)

    def _draw_items(self, items, text, color):
        font = pygame.font.Font(None, 15)
        for item in items:
            text_surf = font.render(text, True, color)
            text_rect = text_surf.get_rect(center=(item[0] * TILE_SIZE + TILE_SIZE // 2,
                                                   item[1] * TILE_SIZE + TILE_SIZE // 2))
            self.screen.blit(text_surf, text_rect)

    def _draw_man(self):
        font = pygame.font.Font(None, 15)
        text = font.render("M", True, BLACK)
        text_rect = text.get_rect(center=(self.man.x * TILE_SIZE + TILE_SIZE // 2,
                                          self.man.y * TILE_SIZE + TILE_SIZE // 2))
        self.screen.blit(text, text_rect)

    def _draw_wolves(self):
        font = pygame.font.Font(None, 15)
        for wolf in self.environment.wolves:
            text = font.render("W", True, RED)
            text_rect = text.get_rect(center=(wolf.x * TILE_SIZE + TILE_SIZE // 2,
                                              wolf.y * TILE_SIZE + TILE_SIZE // 2))
            self.screen.blit(text, text_rect)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and self.state in [GameState.IN_GAME, GameState.IN_GAME_MENU]:
                    self.state = GameState.IN_GAME_MENU if self.state == GameState.IN_GAME else GameState.IN_GAME
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self.handle_mouse_click(event.pos)

    def handle_mouse_click(self, mouse_pos):
        if self.state == GameState.MAIN_MENU:
            play_button, upgrades_button, load_button = self.menu.main_menu()
            if play_button.collidepoint(mouse_pos):
                self.reset_game()
                self.state = GameState.IN_GAME
            elif upgrades_button.collidepoint(mouse_pos):
                self.state = GameState.UPGRADE_MENU
            elif load_button.collidepoint(mouse_pos):
                self.load_game()
        elif self.state == GameState.UPGRADE_MENU:
            craft_axe_button, craft_sword_button, back_button = self.menu.upgrade_menu(self.man.inventory["wood"], self.man.inventory["stone"])
            if back_button.collidepoint(mouse_pos):
                self.state = GameState.MAIN_MENU
            elif craft_axe_button.collidepoint(mouse_pos):
                self.craft_item("axe")
            elif craft_sword_button.collidepoint(mouse_pos):
                self.craft_item("sword")
        elif self.state == GameState.IN_GAME_MENU:
            save_button, task_buttons = self.menu.in_game_menu(self.man.inventory, self.man.current_task)
            if save_button.collidepoint(mouse_pos):
                self.save_game()
            for task, button in task_buttons:
                if button.collidepoint(mouse_pos):
                    self.man.current_task = task if task != "None" else None
        elif self.state == GameState.DEATH_SCREEN:
            main_menu_button = self.menu.death_screen()
            if main_menu_button.collidepoint(mouse_pos):
                self.state = GameState.MAIN_MENU

    def craft_item(self, item):
        if item == "axe" and self.man.inventory["wood"] >= 5 and self.man.inventory["stone"] >= 3:
            self.man.inventory["wood"] -= 5
            self.man.inventory["stone"] -= 3
            self.man.weapon = "axe"
        elif item == "sword" and self.man.inventory["wood"] >= 3 and self.man.inventory["stone"] >= 5:
            self.man.inventory["wood"] -= 3
            self.man.inventory["stone"] -= 5
            self.man.weapon = "sword"

    def update_game(self):
        self.weather.update(self.time)
        
        if self.man.stamina < 20:
            self.man.rest()
        elif self.man.is_hungry(self.time):
            if self.man.inventory["berries"] > 0:
                self.man.inventory["berries"] -= 1
                self.man.last_ate = self.time
            else:
                food = self.environment.find_closest(self.man, self.environment.berries)
                if food:
                    self.man.move_to_spot(food)
        elif self.man.is_thirsty(self.time):
            water = self.environment.find_closest(self.man, self.environment.water_sources)
            if water:
                self.man.move_to_spot(water)
        else:
            self._perform_task()

        for wolf in self.environment.wolves:
            if abs(wolf.x - self.man.x) <= 1 and abs(wolf.y - self.man.y) <= 1:
                self.man.attack(wolf)
                if wolf.health <= 0:
                    self.environment.wolves.remove(wolf)
            else:
                wolf.move_to_spot((self.man.x, self.man.y))

        self.environment.check_step(self.man, self.time)
        self.environment.respawn_berries(self.time)

        if self._check_death():
            self.state = GameState.DEATH_SCREEN

        self.time += 1
        if self.time % (24 * 60) == 0:
            self.day += 1
        self.clock.tick(FPS)

    def _perform_task(self):
        if self.man.current_task == "Mining":
            stone = self.environment.find_closest(self.man, self.environment.stones)
            if stone:
                self.man.move_to_spot(stone)
            else:
                self._wander(self.man)
        elif self.man.current_task == "Woodcutting":
            tree = self.environment.find_closest(self.man, self.environment.trees)
            if tree:
                self.man.move_to_spot(tree)
            else:
                self._wander(self.man)
        elif self.man.current_task == "Foraging":
            berry = self.environment.find_closest(self.man, self.environment.berries)
            if berry:
                self.man.move_to_spot(berry)
            else:
                self._wander(self.man)
        elif self.man.current_task == "Hunting":
            wolf = self.environment.find_closest(self.man, self.environment.wolves)
            if wolf:
                self.man.move_to_spot((wolf.x, wolf.y))
            else:
                self._wander(self.man)
        else:
            self._wander(self.man)

    def _wander(self, entity):
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        dx, dy = random.choice(directions)
        new_x = (entity.x + dx) % GRID_SIZE
        new_y = (entity.y + dy) % GRID_SIZE
        if (new_x, new_y) not in self.environment.trees:
            entity.x, entity.y = new_x, new_y

    def _check_death(self):
        return self.man.health <= 0 or self.man.get_hunger_level(self.time) <= 0 or self.man.get_thirst_level(self.time) <= 0

    def save_game(self):
        game_state = {
            "man": {
                "x": self.man.x,
                "y": self.man.y,
                "last_ate": self.man.last_ate,
                "last_drank": self.man.last_drank,
                "health": self.man.health,
                "stamina": self.man.stamina,
                "inventory": self.man.inventory,
                "weapon": self.man.weapon,
                "current_task": self.man.current_task
            },
            "time": self.time,
            "day": self.day,
            "weather": self.weather.current_condition
        }
        with open("savegame.json", "w") as f:
            json.dump(game_state, f)

    def load_game(self):
        if os.path.exists("savegame.json"):
            with open("savegame.json", "r") as f:
                game_state = json.load(f)
            
            self.man = Man(game_state["man"]["x"], game_state["man"]["y"])
            self.man.last_ate = game_state["man"]["last_ate"]
            self.man.last_drank = game_state["man"]["last_drank"]
            self.man.health = game_state["man"]["health"]
            self.man.stamina = game_state["man"]["stamina"]
            self.man.inventory = game_state["man"]["inventory"]
            self.man.weapon = game_state["man"]["weapon"]
            self.man.current_task = game_state["man"]["current_task"]
            
            self.time = game_state["time"]
            self.day = game_state["day"]
            self.weather.current_condition = game_state["weather"]
            
            self.environment = Environment()
            self.state = GameState.IN_GAME

    def run(self):
        while self.running:
            self.handle_events()
            if self.state == GameState.MAIN_MENU:
                self.menu.main_menu()
            elif self.state == GameState.UPGRADE_MENU:
                self.menu.upgrade_menu(self.man.inventory["wood"], self.man.inventory["stone"])
            elif self.state == GameState.IN_GAME_MENU:
                self.menu.in_game_menu(self.man.inventory, self.man.current_task)
            elif self.state == GameState.IN_GAME:
                self.update_game()
                self.draw_game()
            elif self.state == GameState.DEATH_SCREEN:
                self.menu.death_screen()
            pygame.display.flip()
        pygame.quit()

if __name__ == "__main__":
    game = Game()
    game.run()