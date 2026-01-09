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


# State Constants
STATE_MENU = "MENU"
STATE_GAME = "GAME"
STATE_LEADERBOARD = "LEADERBOARD"

class PygameUI:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Maze Master: Evolution (Pygame Edition)")
        self.clock = pygame.time.Clock()
        
        # Fonts
        self.font = pygame.font.SysFont("Arial", 20)
        self.header_font = pygame.font.SysFont("Arial", 40, bold=True)
        self.sub_font = pygame.font.SysFont("Arial", 28)
        
        self.game = GameState()
        self.state = STATE_MENU
        
        self.cell_size = 30
        self.offset_x = 50
        self.offset_y = 100
        self.message = "Welcome!"
        
        # Menu Options
        self.selected_algo = "A*"
        self.selected_level = 1
        
        # Components
        self._init_buttons()

    def _init_buttons(self):
        # -- MENU BUTTONS --
        self.btn_algo_bfs = Button("BFS", 350, 300, 80, 40, lambda: self.set_algo("BFS"), (70,70,70))
        self.btn_algo_dfs = Button("DFS", 450, 300, 80, 40, lambda: self.set_algo("DFS"), (70,70,70))
        self.btn_algo_astar = Button("A*", 550, 300, 80, 40, lambda: self.set_algo("A*"), (70,70,70))
        
        self.btn_lvl_dec = Button("-", 400, 400, 40, 40, lambda: self.change_level(-1))
        self.btn_lvl_inc = Button("+", 540, 400, 40, 40, lambda: self.change_level(1))
        
        self.btn_start = Button("START GAME", 350, 500, 300, 60, self.start_custom_game, COLOR_START)
        self.btn_daily = Button("DAILY CHALLENGE", 350, 580, 300, 60, self.start_daily_menu, (230, 126, 34))
        self.btn_lb = Button("LEADERBOARD", 350, 660, 300, 60, lambda: self.set_state(STATE_LEADERBOARD), (52, 152, 219))
        
        # -- GAME BUTTONS --
        self.btn_menu_game = Button("Main Menu", 800, 50, 150, 40, lambda: self.set_state(STATE_MENU), (100, 100, 100))
        self.btn_ghost = Button("Toggle Ghost", 800, 200, 150, 40, self.cmd_toggle_ghost, COLOR_GHOST)
        self.btn_hint = Button("Hint", 800, 260, 150, 40, self.cmd_hint, COLOR_HINT)
        self.btn_next = Button("Next Level", 800, 320, 150, 40, self.cmd_next_level, COLOR_START)
        
        # -- LEADERBOARD BUTTONS --
        self.btn_lb_back = Button("Back", 50, 50, 100, 40, lambda: self.set_state(STATE_MENU), (100, 100, 100))
        self.btn_lb_refresh = Button("Refresh", 800, 50, 100, 40, lambda: None, (52, 152, 219)) # Refresh happens on draw

    def set_state(self, state):
        self.state = state

    def set_algo(self, algo):
        self.selected_algo = algo

    def change_level(self, delta):
        self.selected_level = max(1, self.selected_level + delta)

    def start_custom_game(self):
        self.game.load_level(self.selected_level)
        self.game.mode = "Standard"
        self.game.start_new_game()
        # Hack to enforce level choice because start_new_game resets it default
        self.game.current_level = self.selected_level
        self.game.load_level(self.selected_level) 
        
        self.state = STATE_GAME
        self.message = f"Level {self.selected_level} Started ({self.selected_algo})"

    def start_daily_menu(self):
        msg, _ = self.game.start_daily_challenge()
        self.message = msg
        self.state = STATE_GAME

    def cmd_toggle_ghost(self):
        msg, _ = self.game.toggle_ghost()
        self.message = msg
        
    def cmd_hint(self):
        msg = self.game.solve(self.selected_algo) # Use selected algo
        self.message = msg

    def cmd_next_level(self):
        if self.game.is_game_over:
             msg, _ = self.game.next_level()
             self.message = msg
        else:
             self.message = "Complete the level first!"

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            # Global Key shortcuts
            if event.type == pygame.KEYDOWN:
                if self.state == STATE_GAME:
                    direction = None
                    if event.key in [pygame.K_UP, pygame.K_w]: direction = "Up"
                    elif event.key in [pygame.K_DOWN, pygame.K_s]: direction = "Down"
                    elif event.key in [pygame.K_LEFT, pygame.K_a]: direction = "Left"
                    elif event.key in [pygame.K_RIGHT, pygame.K_d]: direction = "Right"
                    
                    if direction:
                        msg, _ = self.game.move_player(direction)
                        self.message = msg
            
            # Click Handling
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = event.pos
                if self.state == STATE_MENU:
                    self.btn_algo_bfs.check_click(mouse_pos)
                    self.btn_algo_dfs.check_click(mouse_pos)
                    self.btn_algo_astar.check_click(mouse_pos)
                    self.btn_lvl_dec.check_click(mouse_pos)
                    self.btn_lvl_inc.check_click(mouse_pos)
                    self.btn_start.check_click(mouse_pos)
                    self.btn_daily.check_click(mouse_pos)
                    self.btn_lb.check_click(mouse_pos)
                elif self.state == STATE_GAME:
                    self.btn_menu_game.check_click(mouse_pos)
                    self.btn_ghost.check_click(mouse_pos)
                    self.btn_hint.check_click(mouse_pos)
                    self.btn_next.check_click(mouse_pos)
                elif self.state == STATE_LEADERBOARD:
                    self.btn_lb_back.check_click(mouse_pos)

            # Hover Update
            if event.type == pygame.MOUSEMOTION:
                all_btns = []
                if self.state == STATE_MENU:
                     all_btns = [self.btn_algo_bfs, self.btn_algo_dfs, self.btn_algo_astar, 
                                 self.btn_lvl_dec, self.btn_lvl_inc, self.btn_start, 
                                 self.btn_daily, self.btn_lb]
                elif self.state == STATE_GAME:
                     all_btns = [self.btn_menu_game, self.btn_ghost, self.btn_hint, self.btn_next]
                elif self.state == STATE_LEADERBOARD:
                     all_btns = [self.btn_lb_back]
                
                for btn in all_btns:
                    btn.check_hover(event.pos)

    def draw(self):
        self.screen.fill(COLOR_BG)
        
        if self.state == STATE_MENU:
            self.draw_menu()
        elif self.state == STATE_GAME:
            self.draw_game()
        elif self.state == STATE_LEADERBOARD:
            self.draw_leaderboard()
            
        pygame.display.flip()

    def draw_menu(self):
        # Title
        title = self.header_font.render("MAZE MASTER: EVOLUTION", True, (0, 255, 255))
        self.screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 100))
        
        # 1. Algorithm Select
        lbl_algo = self.sub_font.render("Select Algorithm:", True, (200, 200, 200))
        self.screen.blit(lbl_algo, (350, 260))
        
        # Highlight Selected
        for btn in [self.btn_algo_bfs, self.btn_algo_dfs, self.btn_algo_astar]:
            # Temporarily change color if selected
            orig_col = btn.color
            if btn.text == self.selected_algo:
                btn.color = (46, 204, 113) # Green active
            else:
                btn.color = (70, 70, 70)
            btn.draw(self.screen, self.font)
            btn.color = orig_col # Reset logic (though simplistic) for next frame
            
        # 2. Level Select
        lbl_lvl = self.sub_font.render("Select Level:", True, (200, 200, 200))
        self.screen.blit(lbl_lvl, (350, 360))
        
        self.btn_lvl_dec.draw(self.screen, self.font)
        self.btn_lvl_inc.draw(self.screen, self.font)
        
        lvl_val = self.header_font.render(str(self.selected_level), True, (255, 255, 0))
        self.screen.blit(lvl_val, (480, 400))
        
        # 3. Main Buttons
        self.btn_start.draw(self.screen, self.sub_font)
        self.btn_daily.draw(self.screen, self.sub_font)
        self.btn_lb.draw(self.screen, self.sub_font)

    def draw_game(self):
        # Header
        stats = self.game.get_metrics()
        stats_surf = self.font.render(stats, True, (200, 200, 200))
        self.screen.blit(stats_surf, (50, 20))
        
        # Maze
        self._draw_maze()
        
        # Sidebar Buttons
        self.btn_menu_game.draw(self.screen, self.font)
        self.btn_ghost.draw(self.screen, self.font)
        self.btn_hint.text = f"Hint ({self.selected_algo})"
        self.btn_hint.draw(self.screen, self.font)
        self.btn_next.draw(self.screen, self.font)
        
        # Log
        msg_surf = self.font.render(f"Log: {self.message}", True, COLOR_HINT)
        self.screen.blit(msg_surf, (50, SCREEN_HEIGHT - 35))

    def draw_leaderboard(self):
        title = self.header_font.render("Hall of Fame", True, (255, 215, 0))
        self.screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 50))
        
        self.btn_lb_back.draw(self.screen, self.font)
        
        # Fetch Data (Optimized: fetch once or every frame? local json is fast enough for menu)
        # Display Standard and Daily Side by Side
        self._draw_lb_column("Daily Challenge", "Daily", 100)
        self._draw_lb_column("Standard Mode", "Standard", 500)

    def _draw_lb_column(self, title, mode, x_offset):
        head = self.sub_font.render(title, True, (52, 152, 219))
        self.screen.blit(head, (x_offset, 120))
        
        data = self.game.data_manager.get_leaderboard(mode)
        y = 170
        
        # Headers
        headers = ["Rank", "Name", "Score", "Time"]
        h_x = [0, 60, 200, 280]
        for i, h in enumerate(headers):
             txt = self.font.render(h, True, (150, 150, 150))
             self.screen.blit(txt, (x_offset + h_x[i], y))
        y += 30
        pygame.draw.line(self.screen, (100,100,100), (x_offset, y), (x_offset+350, y), 2)
        y += 10
        
        for i, entry in enumerate(data[:10]): # Top 10
             c = (255,255,255)
             if i == 0: c = (255, 215, 0) # Gold
             elif i == 1: c = (192, 192, 192) # Silver
             elif i == 2: c = (205, 127, 50) # Bronze
             
             self.screen.blit(self.font.render(f"#{i+1}", True, c), (x_offset+h_x[0], y))
             self.screen.blit(self.font.render(entry['name'][:10], True, c), (x_offset+h_x[1], y))
             self.screen.blit(self.font.render(str(entry['score']), True, c), (x_offset+h_x[2], y))
             self.screen.blit(self.font.render(f"{entry['time']}s", True, c), (x_offset+h_x[3], y))
             y += 25
             
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
