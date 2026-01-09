import time
import datetime
from .maze_generator import generate_level
from .solvers import solve_astar, solve_bfs, solve_dfs
from .data_manager import DataManager

class GameState:
    def __init__(self):
        self.data_manager = DataManager()
        self.grid = []
        self.player_pos = (0, 0)
        self.start_pos = (0, 0)
        self.goal_pos = (0, 0)
        
        # Progression
        self.path_for_display = [] 
        self.mode = "Standard"
        self.current_level = 1
        self.total_score = 0
        self.inventory = []
        self.hints_remaining = 999
        self.player_name = "Player"
        
        # Ghost
        self.ghost_enabled = False
        self.optimal_path_sequence = [] # List of coords
        
        # State Flags (initialized in _init_level_state)
        self.moves = 0
        self.start_time = 0
        self.elapsed_final = 0
        self.is_game_over = False
        self.fog_moves_remaining = 0
        self.has_shield = False
        self.speed_boost_moves = 0
        self.vision_moves = 0
        
        self.load_level(1)

    def set_player_name(self, name):
        self.player_name = name if name else "Player"
        return f"Welcome, {self.player_name}!"

    def start_new_game(self):
        self.mode = "Standard"
        self.current_level = 1
        self.total_score = 0
        self.inventory = []
        self.hints_remaining = 999
        self.load_level(1)
        return self.get_display_grid()

    def start_daily_challenge(self):
        self.mode = "Daily"
        date_str = datetime.date.today().isoformat()
        self.current_level = 10 
        self.total_score = 0
        self.inventory = []
        self.hints_remaining = 3 
        
        self.grid = generate_level(self.current_level, seed=date_str)
        
        self._init_level_state()
        
        return f"Daily ({date_str}) Started! Streak: {self.data_manager.get_streak_info()[0]}", self.get_display_grid()

    def load_level(self, level):
        self.grid = generate_level(level)
        self.current_level = level
        self._init_level_state()

    def _init_level_state(self):
        self.height = len(self.grid)
        self.width = len(self.grid[0])
        self.moves = 0
        self.start_time = time.time()
        self.path_for_display = []
        self.is_game_over = False
        self.fog_moves_remaining = 0
        self.speed_boost_moves = 0
        self.vision_moves = 0
        self.elapsed_final = 0
        
        # Preserve inventory and shield across levels in standard mode
        if self.mode == "Daily":
            self.has_shield = False
        
        # Find start/goal
        for r in range(self.height):
            for c in range(self.width):
                if self.grid[r][c] == 'S':
                    self.start_pos = (r, c)
                elif self.grid[r][c] == 'G':
                    self.goal_pos = (r, c)
        
        self.player_pos = self.start_pos
        
        # Pre-calc optimal path for Ghost
        full_path = solve_astar(self.grid, self.start_pos, self.goal_pos)
        self.optimal_path_sequence = full_path if full_path else []

    def next_level(self):
        if self.mode == "Daily":
            return "Challenge Complete. Check Leaderboard!", self.get_display_grid()
            
        self.total_score += self.calculate_score()
        self.current_level += 1
        self.load_level(self.current_level)
        return f"Level {self.current_level}", self.get_display_grid()

    def toggle_ghost(self):
        self.ghost_enabled = not self.ghost_enabled
        status = "ON" if self.ghost_enabled else "OFF"
        return f"Ghost Replay {status}", self.get_display_grid()

    def move_player(self, direction):
        if self.is_game_over:
            return "Game Over!", self.get_display_grid()

        r, c = self.player_pos
        dr, dc = 0, 0
        
        if direction == "Up": dr = -1
        elif direction == "Down": dr = 1
        elif direction == "Left": dc = -1
        elif direction == "Right": dc = 1
        
        nr, nc = r + dr, c + dc
        msg = "Moving..."
        
        if 0 <= nr < self.height and 0 <= nc < self.width:
            cell = self.grid[nr][nc]
            
            if cell == 1: 
                return "Blocked!", self.get_display_grid()
                
            self.player_pos = (nr, nc)
            self.moves += 1
            
            if self.fog_moves_remaining > 0: self.fog_moves_remaining -= 1
            if self.speed_boost_moves > 0: self.speed_boost_moves -= 1
            if self.vision_moves > 0: self.vision_moves -= 1
            
            # --- CELL INTERACTIONS ---
            if cell == 'G':
                self.is_game_over = True
                self.elapsed_final = time.time() - self.start_time
                self.total_score = self.calculate_score()
                
                # Update Data
                if self.mode == "Daily":
                    streak = self.data_manager.update_streak()
                    # Apply streak bonus? 
                    streak_bonus = min(streak * 100, 1000)
                    self.total_score += streak_bonus
                    msg = f"DAILY COMPLETE! Score: {self.total_score} (Streak Bonus +{streak_bonus})"
                else:
                    msg = f"Level Complete! Score: {self.total_score}"
                    
                # Save to Leaderboard
                elapsed = int(self.elapsed_final)
                hints_used = (3 - self.hints_remaining) if self.mode == "Daily" else 0
                self.data_manager.add_score(self.mode, self.player_name, self.total_score, elapsed, self.moves, hints_used)
                
            elif cell == 'T': 
                if self.has_shield:
                    self.has_shield = False
                    self.inventory.remove('Shield')
                    self.grid[nr][nc] = 0
                    msg = "Shield blocked Spike!"
                else:
                    self.player_pos = self.start_pos
                    penalty = 100 if self.mode == "Daily" else 50
                    self.total_score -= penalty
                    msg = "SPIKE! Reset to Start."
            elif cell == 'F':
                if self.has_shield:
                    self.has_shield = False
                    self.inventory.remove('Shield')
                    self.grid[nr][nc] = 0
                    msg = "Shield blocked Fog!"
                else:
                    self.fog_moves_remaining = 10
                    self.grid[nr][nc] = 0
                    msg = "FOG TRAP!"
            elif cell == 'X':
                if self.has_shield:
                    self.has_shield = False
                    self.inventory.remove('Shield')
                    self.grid[nr][nc] = 0
                    msg = "Shield blocked Time Trap!"
                else:
                    self.start_time -= 10
                    self.grid[nr][nc] = 0
                    msg = "TIME WARP! +10s."
            elif cell == 'P':
                self.has_shield = True
                self.inventory.append('Shield')
                self.grid[nr][nc] = 0
                msg = "Got Shield!"
            elif cell == 'B':
                self.speed_boost_moves = 10
                self.grid[nr][nc] = 0
                msg = "Speed Boost!"
            elif cell == 'V':
                self.vision_moves = 10
                self.solve("A*")
                self.grid[nr][nc] = 0
                msg = "AI Vision!"
                
            return msg, self.get_display_grid()
        
        return "Boundary!", self.get_display_grid()

    def get_display_grid(self):
        # MAPPINGS
        # 0=Path -> 0
        # 1=Wall -> 1
        # Player -> 2
        # Start -> 3
        # Goal -> 4
        # Hint -> 5
        # Ghost -> 6
        # T -> 10, F -> 11, X -> 12
        # P -> 20, B -> 21, V -> 22
        # FOG -> 99
        
        display = []
        
        # Ghost Logic: Show ghost at index 'moves' of optimal path
        ghost_pos = None
        if self.ghost_enabled and self.optimal_path_sequence:
            idx = min(self.moves, len(self.optimal_path_sequence) - 1)
            ghost_pos = self.optimal_path_sequence[idx]
        
        for r in range(self.height):
            row_data = []
            for c in range(self.width):
                # Fog check
                if self.fog_moves_remaining > 0:
                    dist = abs(r - self.player_pos[0]) + abs(c - self.player_pos[1])
                    if dist > 2:
                        row_data.append(99)
                        continue
                
                cell = self.grid[r][c]
                code = 0
                if cell == 1: code = 1
                elif cell == 'S': code = 3
                elif cell == 'G': code = 4
                elif cell == 'T': code = 10
                elif cell == 'F': code = 11
                elif cell == 'X': code = 12
                elif cell == 'P': code = 20
                elif cell == 'B': code = 21
                elif cell == 'V': code = 22
                
                # Ghost Overlay
                if ghost_pos == (r, c) and code not in [1, 2]: # Don't overwrite player or wall
                    code = 6
                
                # Hint Overlay
                if (r,c) in self.path_for_display and code == 0:
                   code = 5
                   
                row_data.append(code)
            display.append(row_data)

        # Player
        pr, pc = self.player_pos
        display[pr][pc] = 2
        
        return display

    def calculate_score(self):
        elapsed = time.time() - self.start_time
        optimal_len = len(self.optimal_path_sequence) if self.optimal_path_sequence else self.moves
        efficiency = (optimal_len / max(1, self.moves)) * 100
        time_penalty = int(elapsed) * 1
        
        base_score = 1000 * (self.current_level * 0.5)
        if self.mode == "Daily": base_score = 5000
        
        level_score = int(base_score * (efficiency/100) - time_penalty)
        return max(0, level_score)

    def get_metrics(self):
        elapsed = int(time.time() - self.start_time) if not self.is_game_over else int(self.elapsed_final or (time.time() - self.start_time))
        curr_score = self.calculate_score()
        items = " ".join(self.inventory) if self.inventory else "None"
        
        mode_str = f"Mode: {self.mode}"
        if self.mode == "Daily":
            streak = self.data_manager.get_streak_info()[0]
            mode_str += f" | 🔥 Streak: {streak} | Hints: {self.hints_remaining}"
            
        return f"{mode_str} | Level: {self.current_level} | Moves: {self.moves} | Time: {elapsed}s | Score: {curr_score}"

    def solve(self, algorithm):
        if self.mode == "Daily":
            if self.hints_remaining <= 0: return "No hints left!"
            self.hints_remaining -= 1
            
        if algorithm == "BFS": path = solve_bfs(self.grid, self.player_pos, self.goal_pos)
        elif algorithm == "DFS": path = solve_dfs(self.grid, self.player_pos, self.goal_pos)
        else: path = solve_astar(self.grid, self.player_pos, self.goal_pos)
            
        if path:
            self.path_for_display = path[1:]
            penalty = 50 * self.current_level if self.mode != "Daily" else 500
            self.total_score -= penalty
            return f"Hint Used. Penalty: {penalty}"
        return "No path!"
