import pygame
import random

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

pygame.init()


class Man:
    """Class representing the player character."""

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.attack = 0
        self.warmth = 0
        self.wet = False
        self.last_wet = 0
        self.last_ate = 0
        self.last_drank = 0

    def is_hungry(self, current_time):
        """Check if the man is hungry based on time since last meal."""
        return current_time - self.last_ate > 30

    def get_hunger_level(self, current_time):
        """Return hunger level as a float between 0 and 1."""
        hunger_duration = current_time - self.last_ate
        hunger_level = 1.0 - min(1.0, max(0.0, hunger_duration / 100.0))
        return hunger_level

    def move_to_spot(self, spot):
        """Move towards the given spot."""
        if self.x < spot[0]:
            self.x += 1
        elif self.x > spot[0]:
            self.x -= 1

        if self.y < spot[1]:
            self.y += 1
        elif self.y > spot[1]:
            self.y -= 1


class Environment:
    """Class representing the game environment."""

    def __init__(self):
        self.trees = []
        self.berries = []
        self.create_tree_array()
        self.create_berry_array()

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

    def find_closest_food(self, man):
        """Find the closest berry to the man."""
        if not self.berries:
            return None
        closest_berry = min(
            self.berries,
            key=lambda b: (b[0] - man.x) ** 2 + (b[1] - man.y) ** 2
        )
        return closest_berry

    def check_step(self, man, current_time):
        """Check if the man is on a berry and handle eating."""
        if (man.x, man.y) in self.berries:
            man.last_ate = current_time
            self.berries.remove((man.x, man.y))


class Menu:
    """Class to handle different menus in the game."""

    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.Font(None, 36)

    def open_in_game_menu(self):
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
        hunger_bar_width = 150
        hunger_bar_height = 20
        hunger_bar_x = 10
        hunger_bar_y = 10

        pygame.draw.rect(
            self.screen,
            GRAY,
            (hunger_bar_x, hunger_bar_y, hunger_bar_width, hunger_bar_height)
        )

        hunger_level = self.man.get_hunger_level(self.time)
        pygame.draw.rect(
            self.screen,
            RED,
            (
                hunger_bar_x,
                hunger_bar_y,
                int(hunger_bar_width * hunger_level),
                hunger_bar_height
            )
        )

        # Thirst Bar (Placeholder, as thirst_level is currently fixed)
        thirst_bar_width = 150
        thirst_bar_height = 20
        thirst_bar_x = 10
        thirst_bar_y = hunger_bar_y + hunger_bar_height + 5

        pygame.draw.rect(
            self.screen,
            GRAY,
            (thirst_bar_x, thirst_bar_y, thirst_bar_width, thirst_bar_height)
        )

        # Placeholder thirst level
        thirst_level = 1.0
        pygame.draw.rect(
            self.screen,
            BLUE,
            (
                thirst_bar_x,
                thirst_bar_y,
                int(thirst_bar_width * thirst_level),
                thirst_bar_height
            )
        )

    def draw_game(self):
        """Render the game screen."""
        self.screen.fill(WHITE)
        self.draw_ground()
        self.draw_trees()
        self.draw_berries()
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
            pygame.draw.rect(
                self.screen,
                DARK_GREEN,
                (x, y, TILE_SIZE, TILE_SIZE // 3)
            )

    def draw_berries(self):
        """Draw the berries."""
        berries_color = RED
        font = pygame.font.Font(None, 15)
        for berry in self.environment.berries:
            text = font.render("B", True, berries_color)
            text_rect = text.get_rect(
                center=(
                    berry[0] * TILE_SIZE + TILE_SIZE // 2,
                    berry[1] * TILE_SIZE + TILE_SIZE // 2
                )
            )
            self.screen.blit(text, text_rect)

    def draw_man(self):
        """Draw the man/player character."""
        font = pygame.font.Font(None, 15)
        text = font.render("M", True, BLACK)
        text_rect = text.get_rect(
            center=(
                self.man.x * TILE_SIZE + TILE_SIZE // 2,
                self.man.y * TILE_SIZE + TILE_SIZE // 2
            )
        )
        self.screen.blit(text, text_rect)

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
        hungry = self.man.is_hungry(self.time)

        if hungry:
            food_found = self.environment.find_closest_food(self.man)
            if food_found:
                self.man.move_to_spot(food_found)
        else:
            self.wander(self.man)

        self.environment.check_step(self.man, self.time)

        if self.check_death():
            self.state = GameState.DEATH_SCREEN

        self.time += 1
        self.clock.tick(FPS)

    def wander(self, entity):
        """Random wandering behavior for an entity."""
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        dx, dy = random.choice(directions)
        new_x = (entity.x + dx) % GRID_SIZE
        new_y = (entity.y + dy) % GRID_SIZE

        if (new_x, new_y) not in self.environment.trees:
            entity.x = new_x
            entity.y = new_y

    def check_death(self):
        """Check if the man has died."""
        hunger_level = self.man.get_hunger_level(self.time)
        if hunger_level <= 0:
            return True
        return False

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
                self.menu.open_in_game_menu()

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