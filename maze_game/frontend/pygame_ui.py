import pygame
import sys
import time
import math
import random
from backend.game_state import GameState

# --- CONSTANTS & COLORS (NEON THEME) ---
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 800
FPS = 60

# Palette
COLOR_BG = (10, 15, 30)       # Deep Blue
COLOR_ACCENT_1 = (0, 255, 255) # Cyan
COLOR_ACCENT_2 = (255, 0, 255) # Magenta
COLOR_ACCENT_3 = (46, 204, 113) # Neon Green
COLOR_TEXT_MAIN = (255, 255, 255)
COLOR_TEXT_DIM = (150, 160, 180)
COLOR_PANEL = (20, 30, 50, 200) # Semi-transparent

# Game Colors
COLOR_WALL = (20, 30, 60)
COLOR_PATH = (40, 50, 80)
COLOR_PLAYER = (0, 255, 255)
COLOR_GHOST = (180, 80, 255)
COLOR_START = (0, 255, 127)
COLOR_GOAL = (255, 50, 80)
COLOR_HINT = (255, 215, 0)

# State Constants
STATE_MENU = "MENU"
STATE_GAME = "GAME"
STATE_LEADERBOARD = "LEADERBOARD"

class AnimatedButton:
    def __init__(self, text, x, y, w, h, func, base_color, text_color=COLOR_TEXT_MAIN):
        self.rect = pygame.Rect(x, y, w, h)
        self.original_rect = self.rect.copy()
        self.text = text
        self.func = func
        
        self.base_color = base_color
        self.hover_color = tuple(min(c + 40, 255) for c in base_color)
        self.current_color = list(base_color)
        
        self.text_color = text_color
        self.hover_scale = 1.05
        self.current_scale = 1.0
        self.is_hovered = False
        self.is_pressed = False
        self.is_selected = False # New state

    def check_hover(self, pos):
        self.is_hovered = self.rect.collidepoint(pos)

    def check_click(self, pos):
        if self.is_hovered and self.func:
            self.click_effect()
            self.func()

    def click_effect(self):
        self.current_scale = 0.95

    def update(self):
        # Color Transition
        # If selected, pulse or stay bright
        target = self.hover_color if (self.is_hovered or self.is_selected) else self.base_color
        for i in range(3):
            self.current_color[i] += (target[i] - self.current_color[i]) * 0.2
            
        # Scale Transition
        target_scale = 1.0
        if self.is_selected: target_scale = 1.1 # Stay slightly larger if selected
        elif self.is_hovered: target_scale = 1.05
        if self.is_pressed: target_scale = 0.95
        
        self.current_scale += (target_scale - self.current_scale) * 0.2
        
        # Apply Scale
        w = int(self.original_rect.width * self.current_scale)
        h = int(self.original_rect.height * self.current_scale)
        self.rect = pygame.Rect(0, 0, w, h)
        self.rect.center = self.original_rect.center
        
        self.is_pressed = False

    def draw(self, surface, font):
        # Draw Shadow
        shadow_rect = self.rect.copy()
        shadow_rect.y += 4
        pygame.draw.rect(surface, (0,0,0, 100), shadow_rect, border_radius=12)
        
        # Draw Main Rect
        pygame.draw.rect(surface, self.current_color, self.rect, border_radius=12)
        
        # Selection Glow
        if self.is_selected:
             # Outer Glow
             glow_rect = self.rect.inflate(6, 6)
             pygame.draw.rect(surface, (255, 255, 255, 150), glow_rect, width=3, border_radius=15)
        elif self.is_hovered:
            pygame.draw.rect(surface, (255,255,255, 100), self.rect, width=2, border_radius=12)
        
        # Text
        text_surf = font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)


# Particle System
class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.vx = random.uniform(-2, 2)
        self.vy = random.uniform(-2, 2)
        self.lifetime = 1.0 # seconds
        self.start_time = time.time()
        self.size = random.randint(2, 5)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        elapsed = time.time() - self.start_time
        return elapsed < self.lifetime

    def draw(self, surface):
        elapsed = time.time() - self.start_time
        alpha = int(255 * (1 - elapsed / self.lifetime))
        if alpha < 0: alpha = 0
        s = pygame.Surface((self.size*2, self.size*2), pygame.SRCALPHA)
        pygame.draw.circle(s, (*self.color, alpha), (self.size, self.size), self.size)
        surface.blit(s, (self.x - self.size, self.y - self.size))

class InputBox:
    def __init__(self, x, y, w, h, text=''):
        self.rect = pygame.Rect(x, y, w, h)
        self.color_active = COLOR_ACCENT_1
        self.color_inactive = (50, 50, 70)
        self.color = self.color_inactive
        self.text = text
        self.active = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.active = not self.active
            else:
                self.active = False
            self.color = self.color_active if self.active else self.color_inactive
        if event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_RETURN:
                    self.active = False
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    if len(self.text) < 15:
                        self.text += event.unicode
                self.color = self.color_active if self.active else self.color_inactive

    def draw(self, screen, font):
        # Background
        pygame.draw.rect(screen, (10, 20, 40), self.rect, border_radius=8)
        # Border
        pygame.draw.rect(screen, self.color, self.rect, 2, border_radius=8)
        # Text
        txt_surface = font.render(self.text, True, COLOR_TEXT_MAIN)
        screen.blit(txt_surface, (self.rect.x+10, self.rect.y+10))
        if not self.text and not self.active:
            placeholder = font.render("Enter Name...", True, (100, 100, 120))
            screen.blit(placeholder, (self.rect.x+10, self.rect.y+10))

class PygameUI:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Maze Master: Evolution Premium")
        self.clock = pygame.time.Clock()
        
        # Fonts
        self.font = pygame.font.SysFont("Verdana", 16)
        self.btn_font = pygame.font.SysFont("Verdana", 18, bold=True)
        self.header_font = pygame.font.SysFont("Verdana", 48, bold=True)
        self.sub_font = pygame.font.SysFont("Verdana", 24)
        self.desc_font = pygame.font.SysFont("Verdana", 14, italic=True)
        
        self.game = GameState()
        self.state = STATE_MENU
        
        self.message = "Welcome to the Neon Maze."
        self.bg_offset = 0
        
        # Particles
        self.particles = []
        
        # Transition
        self.fade_alpha = 0
        self.fade_target = 0
        
        # Menu Selectors
        self.selected_algo = "A*"
        self.selected_level = 1
        
        self.name_input = InputBox(SCREEN_WIDTH//2 - 150, 460, 300, 45, self.game.player_name)
        
        self._init_buttons()

    def _init_buttons(self):
        # Helper to center X
        cx = SCREEN_WIDTH // 2
        
        # MENU
        # Distinct Colors for Algos
        col_bfs = (52, 152, 219) # Blue
        col_dfs = (155, 89, 182) # Purple
        col_astar = (241, 196, 15) # Gold
        
        self.menu_buttons = [
            # Algo Row - Larger and Spaced
            AnimatedButton("BFS", cx - 150, 280, 120, 50, lambda: self.set_algo("BFS"), col_bfs),
            AnimatedButton("DFS", cx, 280, 120, 50, lambda: self.set_algo("DFS"), col_dfs),
            AnimatedButton("A*", cx + 150, 280, 120, 50, lambda: self.set_algo("A*"), col_astar),
            
            # Level Row
            AnimatedButton("-", cx - 80, 410, 50, 40, lambda: self.change_level(-1), (80, 50, 50)),
            AnimatedButton("+", cx + 80, 410, 50, 40, lambda: self.change_level(1), (50, 80, 50)),
            
            # Main Actions
            AnimatedButton("START GAME", cx, 550, 300, 60, self.start_custom_game, COLOR_ACCENT_3, (20,20,20)),
            AnimatedButton("DAILY CHALLENGE", cx, 630, 300, 60, self.start_daily_menu, COLOR_ACCENT_2, (20,20,20)),
            AnimatedButton("HALL OF FAME", cx, 710, 300, 60, lambda: self.set_state(STATE_LEADERBOARD), COLOR_ACCENT_1, (20,20,20))
        ]
        
        # GAME
        bx = 820
        self.game_buttons = [
            AnimatedButton("Main Menu", bx, 50, 140, 40, lambda: self.set_state(STATE_MENU), (100, 50, 50)),
            AnimatedButton("Toggle Ghost", bx, 200, 140, 40, self.cmd_toggle_ghost, COLOR_GHOST),
            AnimatedButton("Hint", bx, 260, 140, 40, self.cmd_hint, COLOR_HINT, (20,20,20)),
            AnimatedButton("Next Level", bx, 320, 140, 40, self.cmd_next_level, COLOR_ACCENT_3, (20,20,20))
        ]
        
        # LEADERBOARD
        self.lb_buttons = [
            AnimatedButton("Back", 80, 50, 100, 40, lambda: self.set_state(STATE_MENU), (100, 50, 50))
        ]

    # --- ACTIONS ---
    def set_state(self, state):
        self.fade_alpha = 0
        self.state = state
    def set_algo(self, algo): self.selected_algo = algo
    def change_level(self, d): self.selected_level = max(1, self.selected_level + d)
    
    def start_custom_game(self):
        self.game.player_name = self.name_input.text if self.name_input.text else "Player"
        self.game.mode = "Standard"
        self.game.current_level = self.selected_level
        self.game.load_level(self.selected_level)
        self.set_state(STATE_GAME)
        self.message = f"Level {self.selected_level} - {self.selected_algo}"
        
    def start_daily_menu(self):
        self.game.player_name = self.name_input.text if self.name_input.text else "Player"
        msg, _ = self.game.start_daily_challenge()
        self.message = msg
        self.set_state(STATE_GAME)
        
    def cmd_toggle_ghost(self): self.message, _ = self.game.toggle_ghost()
    def cmd_hint(self): self.message = self.game.solve(self.selected_algo)
    def cmd_next_level(self):
         if self.game.is_game_over: self.message, _ = self.game.next_level()
         else: self.message = "Complete the level first!"
    
    def spawn_particles(self, x, y, color, count=10):
        for _ in range(count):
            self.particles.append(Particle(x, y, color))

    # --- INPUT ---
    def handle_input(self):
        events = pygame.event.get()
        active_btns = []
        if self.state == STATE_MENU: active_btns = self.menu_buttons
        elif self.state == STATE_GAME: active_btns = self.game_buttons
        elif self.state == STATE_LEADERBOARD: active_btns = self.lb_buttons
        
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            
            if self.state == STATE_MENU:
                self.name_input.handle_event(event)

            if event.type == pygame.MOUSEMOTION:
                for btn in active_btns: btn.check_hover(event.pos)
            
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for btn in active_btns: btn.check_click(event.pos)
                
            if event.type == pygame.KEYDOWN and self.state == STATE_GAME:
                d = None
                if event.key in [pygame.K_UP, pygame.K_w]: d = "Up"
                elif event.key in [pygame.K_DOWN, pygame.K_s]: d = "Down"
                elif event.key in [pygame.K_LEFT, pygame.K_a]: d = "Left"
                elif event.key in [pygame.K_RIGHT, pygame.K_d]: d = "Right"
                if d:
                    msg, _ = self.game.move_player(d)
                    self.message = msg
                    # Visual feedback
                    grid = self.game.get_display_grid()
                    # Approx center of player for particles
                    max_w, max_h = 700, 600
                    rows, cols = self.game.height, self.game.width
                    cell_size = min(max_w // cols, max_h // rows, 40)
                    r, c = self.game.player_pos
                    px = 50 + c * cell_size + cell_size//2
                    py = 100 + r * cell_size + cell_size//2
                    self.spawn_particles(px, py, COLOR_PLAYER, 5)
                    
                    if "Goal" in msg or "COMPLETE" in msg:
                        self.spawn_particles(px, py, COLOR_START, 50)

    # --- DRAWING ---
    def draw_bg_grid(self):
        self.bg_offset = (self.bg_offset + 0.5) % 40
        spacing = 40
        cols = SCREEN_WIDTH // spacing + 2
        rows = SCREEN_HEIGHT // spacing + 2
        
        # Vertical Lines
        for x in range(cols):
            x_pos = x * spacing - 10
            alpha = max(0, 50 - abs(x_pos - SCREEN_WIDTH/2) * 0.1) # Fade edges
            pygame.draw.line(self.screen, (20, 30, 60), (x_pos, 0), (x_pos, SCREEN_HEIGHT))
            
        # Horizontal Lines (Moving)
        for y in range(rows):
            y_pos = y * spacing + self.bg_offset - 40
            pygame.draw.line(self.screen, (20, 30, 60), (0, y_pos), (SCREEN_WIDTH, y_pos))

    def draw_glass_panel(self, x, y, w, h):
        s = pygame.Surface((w,h), pygame.SRCALPHA)
        s.fill(COLOR_PANEL)
        pygame.draw.rect(s, (100, 150, 255, 30), s.get_rect(), width=1) # Border
        self.screen.blit(s, (x,y))

    def draw(self):
        self.screen.fill(COLOR_BG)
        self.draw_bg_grid()
        
        if self.state == STATE_MENU: self.draw_menu()
        elif self.state == STATE_GAME: self.draw_game()
        elif self.state == STATE_LEADERBOARD: self.draw_leaderboard()
        
        # Particles
        self.particles = [p for p in self.particles if p.update()]
        for p in self.particles: p.draw(self.screen)
        
        # Buttons Update & Draw
        active_btns = []
        if self.state == STATE_MENU: active_btns = self.menu_buttons
        elif self.state == STATE_GAME: active_btns = self.game_buttons
        elif self.state == STATE_LEADERBOARD: active_btns = self.lb_buttons
        
        for btn in active_btns:
            # Logic for selection state in menu
            if self.state == STATE_MENU and btn.text in ["BFS", "DFS", "A*"]:
                btn.is_selected = (btn.text == self.selected_algo)
                
            btn.update()
            btn.draw(self.screen, self.btn_font)
            
        pygame.display.flip()

    def draw_menu(self):
        # Pulse Title
        scale = 1.0 + math.sin(time.time() * 2) * 0.02
        title = self.header_font.render("MAZE MASTER", True, COLOR_ACCENT_1)
        subtitle = self.sub_font.render("EVOLUTION", True, COLOR_ACCENT_2)
        
        tx, ty = SCREEN_WIDTH//2, 80
        tr_rect = title.get_rect(center=(tx, ty))
        self.screen.blit(title, tr_rect)
        self.screen.blit(subtitle, subtitle.get_rect(center=(tx, ty + 50)))
        
        # Panel for Menu
        self.draw_glass_panel(SCREEN_WIDTH//2 - 270, 200, 540, 580)
        
        # 1. Algorithm Select
        t_algo = self.sub_font.render("CHOOSE YOUR PATHFINDER", True, COLOR_TEXT_DIM)
        self.screen.blit(t_algo, t_algo.get_rect(center=(SCREEN_WIDTH//2, 230)))
        
        # Algo Description
        desc = ""
        if self.selected_algo == "BFS": desc = "Breadth-First Search: Guarantees the shortest path."
        elif self.selected_algo == "DFS": desc = "Depth-First Search: Explores deep paths quickly."
        elif self.selected_algo == "A*": desc = "A-Star: The most efficient smart AI solver."
        
        d_surf = self.desc_font.render(desc, True, COLOR_ACCENT_3)
        self.screen.blit(d_surf, d_surf.get_rect(center=(SCREEN_WIDTH//2, 330)))
        
        # 2. Level Select
        t_lvl = self.sub_font.render(f"STARTING LEVEL: {self.selected_level}", True, COLOR_TEXT_DIM)
        self.screen.blit(t_lvl, t_lvl.get_rect(center=(SCREEN_WIDTH//2, 380)))
        
        # 3. Name Input
        t_name = self.font.render("IDENTITY:", True, COLOR_TEXT_DIM)
        self.screen.blit(t_name, (SCREEN_WIDTH//2 - 150, 440))
        self.name_input.draw(self.screen, self.btn_font)


    def draw_game(self):
        # Top Bar
        self.draw_glass_panel(20, 20, 700, 60)
        stats = self.game.get_metrics()
        s_surf = self.font.render(stats, True, COLOR_TEXT_MAIN)
        self.screen.blit(s_surf, (40, 40))
        
        # Maze
        self._draw_maze()
        
        # Log Bar
        self.draw_glass_panel(20, SCREEN_HEIGHT - 50, 960, 40)
        msg_surf = self.font.render(f"> {self.message}", True, COLOR_ACCENT_1)
        self.screen.blit(msg_surf, (40, SCREEN_HEIGHT - 40))

    def _draw_maze(self):
        rows, cols = self.game.height, self.game.width
        max_w, max_h = 700, 600
        cell_size = min(max_w // cols, max_h // rows, 40)
        
        off_x = 50
        off_y = 100
        
        grid = self.game.get_display_grid()
        
        for r in range(rows):
            for c in range(cols):
                x = off_x + c * cell_size
                y = off_y + r * cell_size
                rect = (x, y, cell_size, cell_size)
                
                code = grid[r][c]
                col = COLOR_PATH
                if code == 1: col = COLOR_WALL
                elif code == 10: col = (100, 50, 50) # T
                elif code == 3: col = (20, 60, 40) # S
                elif code == 4: col = (60, 20, 20) # G
                
                pygame.draw.rect(self.screen, col, rect)
                pygame.draw.rect(self.screen, (30,40,70), rect, 1)
                
                # Items
                cx, cy = x + cell_size//2, y + cell_size//2
                if code == 2: # Player
                    # Glow
                    pygame.draw.circle(self.screen, (0, 100, 100), (cx, cy), cell_size//2 + 4)
                    pygame.draw.circle(self.screen, COLOR_PLAYER, (cx, cy), cell_size//2 - 2)
                elif code == 6: # Ghost
                     s = pygame.Surface((cell_size, cell_size), pygame.SRCALPHA)
                     pygame.draw.circle(s, (*COLOR_GHOST, 150), (cell_size//2, cell_size//2), cell_size//3)
                     self.screen.blit(s, (x,y))
                elif code == 10: self._draw_icon("T", cx, cy, (255, 100, 100))
                elif code == 20: self._draw_icon("S", cx, cy, COLOR_ACCENT_2)
                elif code == 5: # Hint
                    pygame.draw.circle(self.screen, COLOR_HINT, (cx, cy), 4)

    def _draw_icon(self, char, x, y, color):
        t = self.font.render(char, True, color)
        self.screen.blit(t, t.get_rect(center=(x,y)))

    def draw_leaderboard(self):
        title = self.header_font.render("HALL OF FAME", True, COLOR_HINT)
        self.screen.blit(title, title.get_rect(center=(SCREEN_WIDTH//2, 60)))
        
        self.draw_glass_panel(50, 120, 420, 600)
        self.draw_glass_panel(530, 120, 420, 600)
        
        self._draw_lb_list("Daily Challenge", "Daily", 60)
        self._draw_lb_list("Standard Mode", "Standard", 540)
        
        # Draw buttons (Back)
        for btn in self.lb_buttons:
            btn.update()
            btn.draw(self.screen, self.btn_font)

    def _draw_lb_list(self, title, mode, x):
        h = self.sub_font.render(title, True, COLOR_ACCENT_1)
        self.screen.blit(h, (x + 20, 140))
        
        data = self.game.data_manager.get_leaderboard(mode)
        y = 200
        for i, d in enumerate(data[:15]):
            col = COLOR_TEXT_MAIN
            if i==0: col = (255, 215, 0)
            elif i==1: col = (200, 200, 220)
            elif i==2: col = (205, 127, 50)
            
            txt = f"#{i+1} {d['name'][:10]} - {d['score']}"
            s = self.font.render(txt, True, col)
            self.screen.blit(s, (x + 20, y))
            y += 30

    def run(self):
        while True:
            self.handle_input()
            self.draw()
            self.clock.tick(FPS)

if __name__ == "__main__":
    PygameUI().run()
