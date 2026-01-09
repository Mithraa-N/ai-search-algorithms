import pygame
import sys
import time
from backend.game_state import GameState

# --- CONSTANTS & COLORS (NEON THEME) ---
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 800
FPS = 30

# Colors
COLOR_BG = (15, 23, 42)       # Dark Blue #0f172a
COLOR_WALL = (22, 33, 62)     # Darker Blue/Grey #16213e
COLOR_PATH = (50, 52, 74)     # Path Color
COLOR_START = (46, 204, 113)  # Green #2ecc71
COLOR_GOAL = (231, 76, 60)    # Red #e74c3c
COLOR_PLAYER = (52, 152, 219) # Blue #3498db
COLOR_GHOST = (155, 89, 182)  # Purple #9b59b6
COLOR_HINT = (241, 196, 15)   # Yellow #f1c40f
COLOR_TEXT = (255, 255, 255)

# Item Colors
COLOR_SPIKE = (85, 85, 85)
COLOR_FOG_TRAP = (127, 140, 141)
COLOR_TIME_TRAP = (211, 84, 0)
COLOR_SHIELD = (142, 68, 173)
COLOR_SPEED = (41, 128, 185)
COLOR_VISION = (22, 160, 133)
COLOR_FOG_ACTIVE = (0, 0, 0)

class Button:
    def __init__(self, text, x, y, w, h, func, color=(70, 70, 70)):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.func = func
        self.color = color
        self.hover_color = (min(color[0]+30, 255), min(color[1]+30, 255), min(color[2]+30, 255))
        self.is_hovered = False

    def draw(self, surface, font):
        col = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(surface, col, self.rect, border_radius=5)
        text_surf = font.render(self.text, True, COLOR_TEXT)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def check_hover(self, pos):
        self.is_hovered = self.rect.collidepoint(pos)

    def check_click(self, pos):
        if self.is_hovered and self.func:
            self.func()

class PygameUI:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Maze Master: Evolution (Pygame Edition)")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 20)
        self.title_font = pygame.font.SysFont("Arial", 32, bold=True)
        
        self.game = GameState()
        self.cell_size = 30
        self.offset_x = 50
        self.offset_y = 100
        
        self.message = "Welcome! Use Arrow Keys to Move."
        
        # UI Elements
        self.buttons = []
        self._init_buttons()
        
    def _init_buttons(self):
        self.buttons = [
            Button("New Game", 800, 100, 150, 40, self.cmd_new_game, (46, 204, 113)),
            Button("Daily Challenge", 800, 160, 150, 40, self.cmd_daily, (230, 126, 34)),
            Button("Toggle Ghost", 800, 220, 150, 40, self.cmd_toggle_ghost, (155, 89, 182)),
            Button("Hint (A*)", 800, 280, 150, 40, self.cmd_hint, (241, 196, 15)),
        ]

    def cmd_new_game(self):
        if self.game.is_game_over:
             msg, _ = self.game.next_level()
        else:
             self.game.start_new_game()
             msg = "Standard Mode Started"
        self.message = msg

    def cmd_daily(self):
        msg, _ = self.game.start_daily_challenge()
        self.message = msg

    def cmd_toggle_ghost(self):
        msg, _ = self.game.toggle_ghost()
        self.message = msg
        
    def cmd_hint(self):
        msg = self.game.solve("A*")
        self.message = msg

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            elif event.type == pygame.MOUSEMOTION:
                for btn in self.buttons:
                    btn.check_hover(event.pos)
                    
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: # Left click
                    for btn in self.buttons:
                        btn.check_click(event.pos)
                        
            elif event.type == pygame.KEYDOWN:
                # Movement
                direction = None
                if event.key in [pygame.K_UP, pygame.K_w]: direction = "Up"
                elif event.key in [pygame.K_DOWN, pygame.K_s]: direction = "Down"
                elif event.key in [pygame.K_LEFT, pygame.K_a]: direction = "Left"
                elif event.key in [pygame.K_RIGHT, pygame.K_d]: direction = "Right"
                
                if direction:
                    msg, _ = self.game.move_player(direction)
                    self.message = msg
                    if "Goal" in msg or "COMPLETE" in msg:
                        # Auto next level logic or prompt? For now, user clicks button
                        pass

    def draw(self):
        self.screen.fill(COLOR_BG)
        
        # Header
        title = self.title_font.render("Maze Master: Evolution", True, COLOR_TEXT)
        self.screen.blit(title, (50, 30))
        
        stats = self.game.get_metrics()
        stats_surf = self.font.render(stats, True, (200, 200, 200))
        self.screen.blit(stats_surf, (50, 70))
        
        # Draw Maze
        self._draw_maze()
        
        # Sidebar/Status
        msg_surf = self.font.render(f"Log: {self.message}", True, COLOR_HINT)
        self.screen.blit(msg_surf, (50, SCREEN_HEIGHT - 40))
        
        # Buttons
        for btn in self.buttons:
            btn.draw(self.screen, self.font)
            
        pygame.display.flip()

    def _draw_maze(self):
        # Calculate cell size to fit max area
        max_w = 700
        max_h = 600
        cols = self.game.width
        rows = self.game.height
        
        size_w = max_w // cols
        size_h = max_h // rows
        self.cell_size = min(size_w, size_h, 40) # Cap at 40
        
        grid = self.game.get_display_grid()
        
        for r in range(rows):
            for c in range(cols):
                x = self.offset_x + c * self.cell_size
                y = self.offset_y + r * self.cell_size
                cell_code = grid[r][c]
                
                rect = (x, y, self.cell_size, self.cell_size)
                
                color = COLOR_PATH
                if cell_code == 1: color = COLOR_WALL
                elif cell_code == 3: color = COLOR_START
                elif cell_code == 4: color = COLOR_GOAL
                elif cell_code == 5: color = COLOR_HINT # Path Hint
                elif cell_code == 10: color = COLOR_SPIKE
                elif cell_code == 11: color = COLOR_FOG_TRAP
                elif cell_code == 12: color = COLOR_TIME_TRAP
                elif cell_code == 20: color = COLOR_SHIELD
                elif cell_code == 21: color = COLOR_SPEED
                elif cell_code == 22: color = COLOR_VISION
                elif cell_code == 99: color = COLOR_FOG_ACTIVE
                
                pygame.draw.rect(self.screen, color, rect)
                pygame.draw.rect(self.screen, (30,30,40), rect, 1) # Border
                
                # Overlays
                if cell_code == 2: # Player
                    pygame.draw.circle(self.screen, COLOR_PLAYER, (x + self.cell_size//2, y + self.cell_size//2), int(self.cell_size * 0.4))
                elif cell_code == 6: # Ghost
                    # Draw transparent-ish ghost? Pygame minimal alpha
                    s = pygame.Surface((self.cell_size, self.cell_size), pygame.SRCALPHA)
                    pygame.draw.circle(s, (*COLOR_GHOST, 100), (self.cell_size//2, self.cell_size//2), int(self.cell_size * 0.3))
                    self.screen.blit(s, (x,y))

                # Icons for items (Simple text for now)
                icon = None
                if cell_code == 10: icon = "T"
                elif cell_code == 12: icon = "X"
                elif cell_code == 20: icon = "S"
                
                if icon:
                   txt = self.font.render(icon, True, (255,255,255))
                   self.screen.blit(txt, (x+5, y+2))

    def run(self):
        while True:
            self.handle_input()
            self.draw()
            self.clock.tick(FPS)

if __name__ == "__main__":
    app = PygameUI()
    app.run()
