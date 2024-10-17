import pygame
import random
import math

# Constants
WIDTH, HEIGHT = 1000, 1000
GRID_SIZE = 100
TILE_SIZE = WIDTH // GRID_SIZE
FPS = 60

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

pygame.init()

class Man:
    """Class representing the player character."""

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.attack = 0
        self.warmth = 100
        self.wet = False
        self.last_wet = 0
        self.last_ate = 0
        self.last_drank = 0
        self.inventory = {"wood": 0, "berries": 0, "water": 0, "stone": 0}
        self.health = 100
        self.thirst = 100
        self.energy = 100
        self.speed = 1
        self.crafting_skills = 0

    def is_hungry(self, current_time):
        """Check if the man is hungry based on time since last meal."""
        return current_time - self.last_ate > 30

    def is_thirsty(self, current_time):
        """Check if the man is thirsty based on time since last drink."""
        return current_time - self.last_drank > 20

    def get_hunger_level(self, current_time):
        """Return hunger level as a float between 0 and 1."""
        hunger_duration = current_time - self.last_ate
        hunger_level = 1.0 - min(1.0, max(0.0, hunger_duration / 100.0))
        return hunger_level

    def get_thirst_level(self, current_time):
        """Return thirst level as a float between 0 and 1."""
        thirst_duration = current_time - self.last_drank
        thirst_level = 1.0 - min(1.0, max(0.0, thirst_duration / 80.0))
        return thirst_level

    def move_to_spot(self, spot):
        """Move towards the given spot."""
        dx = spot[0] - self.x
        dy = spot[1] - self.y
        distance = math.sqrt(dx**2 + dy**2)
        
        if distance > 0:
            self.x += (dx / distance) * self.speed
            self.y += (dy / distance) * self.speed

        self.energy = max(0, self.energy - 0.1)

    def collect_resource(self, resource_type):
        """Collect a resource and add it to the inventory."""
        self.inventory[resource_type] += 1
        self.crafting_skills += 0.1

    def consume(self, item_type):
        """Consume an item from the inventory."""
        if self.inventory[item_type] > 0:
            self.inventory[item_type] -= 1
            if item_type == "berries":
                self.health = min(100, self.health + 10)
                self.last_ate = pygame.time.get_ticks() // 1000
            elif item_type == "water":
                self.thirst = min(100, self.thirst + 20)
                self.last_drank = pygame.time.get_ticks() // 1000

    def craft(self, item_type):
        """Craft an item using resources."""
        if item_type == "axe" and self.inventory["wood"] >= 3 and self.inventory["stone"] >= 2:
            self.inventory["wood"] -= 3
            self.inventory["stone"] -= 2
            self.attack += 5
            self.crafting_skills += 1
            return True
        return False

class Environment:
    """Class representing the game environment."""

    def __init__(self):
        self.trees = []
        self.berries = []
        self.water_sources = []
        self.stones = []
        self.create_tree_array()
        self.create_berry_array()
        self.create_water_sources()
        self.create_stone_array()

    def create_tree_array(self):
        """Initialize tree positions randomly on the grid."""
        for i in range(GRID_SIZE):
            for j in range(GRID_SIZE):
                if (i, j) != (50, 50) and random.random() < 0.01:
                    self.trees.append((i, j))

    def create_berry_array(self):
        """Initialize berry positions randomly on the grid."""
        for i in range(GRID_SIZE):
            for j in range(GRID_SIZE):
                if (i, j) != (50, 50) and random.random() < 0.002:
                    self.berries.append((i, j))

    def create_water_sources(self):
        """Initialize water sources randomly on the grid."""
        for i in range(GRID_SIZE):
            for j in range(GRID_SIZE):
                if (i, j) != (50, 50) and random.random() < 0.001:
                    self.water_sources.append((i, j))

    def create_stone_array(self):
        """Initialize stone positions randomly on the grid."""
        for i in range(GRID_SIZE):
            for j in range(GRID_SIZE):
                if (i, j) != (50, 50) and random.random() < 0.005:
                    self.stones.append((i, j))

    def find_closest_resource(self, man, resource_type):
        """Find the closest resource of a given type to the man."""
        resources = getattr(self, resource_type)
        if not resources:
            return None
        closest_resource = min(
            resources,
            key=lambda r: (r[0] - man.x) ** 2 + (r[1] - man.y) ** 2
        )
        return closest_resource

    def check_step(self, man, current_time):
        """Check if the man is on a resource and handle collection."""
        man_pos = (int(man.x), int(man.y))
        if man_pos in self.berries:
            man.collect_resource("berries")
            self.berries.remove(man_pos)
        elif man_pos in self.water_sources:
            man.collect_resource("water")
        elif man_pos in self.trees:
            man.collect_resource("wood")
        elif man_pos in self.stones:
            man.collect_resource("stone")
            self.stones.remove(man_pos)

class Menu:
    """Class to handle different menus in the game."""

    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.Font(None, 36)

    def open_in_game_menu(self, man):
        """Render the in-game menu."""
        menu_width = WIDTH - 200
        menu_height = HEIGHT // 2
        menu_x = (WIDTH - menu_width) - 100
        menu_y = (HEIGHT - menu_height) // 2

        # Create a surface for the menu
        menu_surface = pygame.Surface((menu_width, menu_height))
        menu_surface.fill(WHITE)

        # Draw a border around the menu
        pygame.draw.rect(menu_surface, BLACK, menu_surface.get_rect(), 2)

        # Display inventory
        inventory_text = f"Inventory: Wood: {man.inventory['wood']}, Berries: {man.inventory['berries']}, Water: {man.inventory['water']}, Stone: {man.inventory['stone']}"
        text_surf = self.font.render(inventory_text, True, BLACK)
        menu_surface.blit(text_surf, (20, 20))

        # Display stats
        stats_text = f"Health: {man.health}, Energy: {int(man.energy)}, Thirst: {int(man.thirst)}, Attack: {man.attack}"
        text_surf = self.font.render(stats_text, True, BLACK)
        menu_surface.blit(text_surf, (20, 60))

        # Display crafting skills
        crafting_text = f"Crafting Skills: {int(man.crafting_skills)}"
        text_surf = self.font.render(crafting_text, True, BLACK)
        menu_surface.blit(text_surf, (20, 100))

        # Blit the menu surface onto the main screen
        self.screen.blit(menu_surface, (menu_x, menu_y))

    def upgrade_menu(self):
        """Render the upgrade menu."""
        self.screen.fill(WHITE)

        # Draw a tree with icons
        tree_rect = pygame.Rect(WIDTH // 2 - 50, HEIGHT // 2 - 150, 100, 300)
        pygame.draw.rect(self.screen, DARK_GREEN, tree_rect)

        # Draw icons
        icon_color = RED
        for i in range(3):
            pygame.draw.circle(
                self.screen,
                icon_color,
                (WIDTH // 2, HEIGHT // 2 - 100 + i * 100),
                20
            )

        # Draw back button
        back_button = pygame.Rect(WIDTH // 2 - 100, HEIGHT - 100, 200, 50)
        self.draw_button("Back", back_button, GREEN, BLACK)

        return back_button

    def draw_button(self, text, rect, color, text_color):
        """Draw a button with text."""
        pygame.draw.rect(self.screen, color, rect)
        text_surf = self.font.render(text, True, text_color)
        text_rect = text_surf.get_rect(center=rect.center)
        self.screen.blit(text_surf, text_rect)

    def main_menu(self):
        """Render the main menu."""
        self.screen.fill(WHITE)
        play_button = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 - 60, 200, 50)
        upgrades_button = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 10, 200, 50)
        self.draw_button("Play", play_button, GREEN, BLACK)
        self.draw_button("Upgrades", upgrades_button, LIGHT_BLUE, BLACK)
        return play_button, upgrades_button

    def death_screen(self):
        """Render the death screen."""
        self.screen.fill(WHITE)
        large_font = pygame.font.Font(None, 72)
        text = large_font.render("You're Dead", True, BLACK)
        text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))
        self.screen.blit(text, text_rect)
        main_menu_button = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 25, 200, 50)
        self.draw_button("Main Menu", main_menu_button, GREEN, BLACK)
        return main_menu_button


class GameState:
    """Enumeration of possible game states."""
    MAIN_MENU = 'main_menu'
    IN_GAME = 'in_game'
    IN_GAME_MENU = 'in_game_menu'
    UPGRADE_MENU = 'upgrade_menu'
    DEATH_SCREEN = 'death_screen'


class Game:
    """Main Game class."""

    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Survival Game")
        self.clock = pygame.time.Clock()
        self.menu = Menu(self.screen)
        self.reset_game()
        self.state = GameState.MAIN_MENU
        self.running = True

    def reset_game(self):
        """Reset the game to initial state."""
        self.man = Man(50, 50)
        self.environment = Environment()
        self.time = 0

    def draw_ui(self):
        """Draw the user interface elements."""
        # Hunger Bar
        self.draw_status_bar("Hunger", self.man.get_hunger_level(self.time), RED, 10, 10)

        # Thirst Bar
        self.draw_status_bar("Thirst", self.man.get_thirst_level(self.time), BLUE, 10, 40)

        # Energy Bar
        self.draw_status_bar("Energy", self.man.energy / 100, YELLOW, 10, 70)

        # Health Bar
        self.draw_status_bar("Health", self.man.health / 100, GREEN, 10, 100)

    def draw_status_bar(self, label, value, color, x, y):
        """Draw a status bar with label."""
        bar_width = 150
        bar_height = 20
        font = pygame.font.Font(None, 24)

        pygame.draw.rect(self.screen, GRAY, (x, y, bar_width, bar_height))
        pygame.draw.rect(self.screen, color, (x, y, int(bar_width * value), bar_height))
        
        text = font.render(f"{label}: {int(value * 100)}%", True, BLACK)
        self.screen.blit(text, (x + bar_width + 10, y))

    def draw_game(self):
        """Render the game screen."""
        self.screen.fill(WHITE)
        self.draw_ground()
        self.draw_trees()
        self.draw_berries()
        self.draw_water_sources()
        self.draw_stones()
        self.draw_man()
        self.draw_ui()

    def draw_ground(self):
        """Draw the ground tiles."""
        for i in range(GRID_SIZE):
            for j in range(GRID_SIZE):
                color = (0, random.randint(250, 255), 0)
                pygame.draw.rect(
                    self.screen,
                    color,
                    (i * TILE_SIZE, j * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                )

    def draw_trees(self):
        """Draw the trees."""
        for tree in self.environment.trees:
            x = tree[0] * TILE_SIZE
            y = tree[1] * TILE_SIZE
            # Draw trunk
            pygame.draw.rect(
                self.screen,
                BROWN,
                (x + TILE_SIZE // 3, y, TILE_SIZE // 3, TILE_SIZE)
            )
            # Draw leaves
            pygame.draw.circle(
                self.screen,
                DARK_GREEN,
                (x + TILE_SIZE // 2, y),
                TILE_SIZE // 2
            )

    def draw_berries(self):
        """Draw the berries."""
        for berry in self.environment.berries:
            pygame.draw.circle(
                self.screen,
                RED,
                (berry[0] * TILE_SIZE + TILE_SIZE // 2, berry[1] * TILE_SIZE + TILE_SIZE // 2),
                TILE_SIZE // 4
            )

    def draw_water_sources(self):
        """Draw the water sources."""
        for water in self.environment.water_sources:
            pygame.draw.rect(
                self.screen,
                LIGHT_BLUE,
                (water[0] * TILE_SIZE, water[1] * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            )

    def draw_stones(self):
        """Draw the stones."""
        for stone in self.environment.stones:
            pygame.draw.circle(
                self.screen,
                GRAY,
                (stone[0] * TILE_SIZE + TILE_SIZE // 2, stone[1] * TILE_SIZE + TILE_SIZE // 2),
                TILE_SIZE // 3
            )

    def draw_man(self):
        """Draw the man/player character."""
        pygame.draw.circle(
            self.screen,
            BLACK,
            (int(self.man.x * TILE_SIZE + TILE_SIZE // 2), int(self.man.y * TILE_SIZE + TILE_SIZE // 2)),
            TILE_SIZE // 2
        )

    def handle_events(self):
        """Handle events based on the current game state."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if self.state == GameState.IN_GAME:
                        self.state = GameState.IN_GAME_MENU
                    elif self.state == GameState.IN_GAME_MENU:
                        self.state = GameState.IN_GAME
                elif event.key == pygame.K_e and self.state == GameState.IN_GAME:
                    self.man.consume("berries")
                elif event.key == pygame.K_q and self.state == GameState.IN_GAME:
                    self.man.consume("water")
                elif event.key == pygame.K_c and self.state == GameState.IN_GAME:
                    if self.man.craft("axe"):
                        print("Axe crafted!")

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = event.pos

                if self.state == GameState.MAIN_MENU:
                    play_button, upgrades_button = self.menu.main_menu()
                    if play_button.collidepoint(mouse_pos):
                        self.reset_game()
                        self.state = GameState.IN_GAME
                    elif upgrades_button.collidepoint(mouse_pos):
                        self.state = GameState.UPGRADE_MENU

                elif self.state == GameState.UPGRADE_MENU:
                    back_button = self.menu.upgrade_menu()
                    if back_button.collidepoint(mouse_pos):
                        self.state = GameState.MAIN_MENU

                elif self.state == GameState.IN_GAME_MENU:
                    # Handle in-game menu interactions
                    pass

                elif self.state == GameState.DEATH_SCREEN:
                    main_menu_button = self.menu.death_screen()
                    if main_menu_button.collidepoint(mouse_pos):
                        self.state = GameState.MAIN_MENU

    def update_game(self):
        """Update game logic."""
        current_time = pygame.time.get_ticks() // 1000
        hungry = self.man.is_hungry(current_time)
        thirsty = self.man.is_thirsty(current_time)

        if hungry and self.man.inventory["berries"] > 0:
            self.man.consume("berries")
        elif thirsty and self.man.inventory["water"] > 0:
            self.man.consume("water")
        elif hungry:
            food_found = self.environment.find_closest_resource(self.man, "berries")
            if food_found:
                self.man.move_to_spot(food_found)
        elif thirsty:
            water_found = self.environment.find_closest_resource(self.man, "water_sources")
            if water_found:
                self.man.move_to_spot(water_found)
        else:
            self.wander(self.man)

        self.environment.check_step(self.man, current_time)

        # Update man's stats
        self.man.health -= 0.01
        self.man.thirst -= 0.05
        if self.man.thirst <= 0:
            self.man.health -= 0.1

        if self.check_death():
            self.state = GameState.DEATH_SCREEN

        self.time = current_time
        self.clock.tick(FPS)

    def wander(self, entity):
        """Random wandering behavior for an entity."""
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        dx, dy = random.choice(directions)
        new_x = (entity.x + dx) % GRID_SIZE
        new_y = (entity.y + dy) % GRID_SIZE

        if (int(new_x), int(new_y)) not in self.environment.trees:
            entity.x = new_x
            entity.y = new_y
            entity.energy = max(0, entity.energy - 0.1)

    def check_death(self):
        """Check if the man has died."""
        return self.man.health <= 0

    def run(self):
        """Main game loop."""
        while self.running:
            self.handle_events()

            if self.state == GameState.MAIN_MENU:
                self.screen.fill(WHITE)
                self.menu.main_menu()

            elif self.state == GameState.UPGRADE_MENU:
                self.screen.fill(WHITE)
                self.menu.upgrade_menu()

            elif self.state == GameState.IN_GAME_MENU:
                self.draw_game()
                self.menu.open_in_game_menu(self.man)

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