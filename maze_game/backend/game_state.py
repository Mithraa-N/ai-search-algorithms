import time
import datetime
from .maze_generator import generate_level
from .solvers import solve_astar, solve_bfs, solve_dfs

class GameState:
    def __init__(self):
        self.grid = []
        self.player_pos = (0, 0)
        self.start_pos = (0, 0)
        self.goal_pos = (0, 0)
        
        # Progression
        self.current_level = 1
        self.moves = 0
        self.total_score = 0
        self.start_time = 0
        self.elapsed_final = 0
        self.is_game_over = False
        
        # State Flags
        self.fog_moves_remaining = 0
        self.has_shield = False
        self.speed_boost_moves = 0
        self.vision_moves = 0
        
        # Item Lists (Collected) for UI
        self.inventory = [] 
        
        self.path_for_display = [] 
        self.mode = "Standard"

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
        # Seed based on date
        self.current_level = 10 # Hard difficulty for daily
        self.total_score = 0
        self.inventory = []
        self.hints_remaining = 3 # Limited hints
        
        # Load level with specific seed
        self.grid = generate_level(self.current_level, seed=date_str)
        
        self.height = len(self.grid)
        self.width = len(self.grid[0])
        self.moves = 0
        self.start_time = time.time()
        self.path_for_display = []
        self.is_game_over = False
        self.fog_moves_remaining = 0
        self.speed_boost_moves = 0
        self.vision_moves = 0
        
        # Determine optimal for comparison now
        self.daily_optimal = len(solve_astar(self.grid, (0,0), (self.height-1, self.width-1))) # approx
        
        # Find start/goal
        for r in range(self.height):
            for c in range(self.width):
                if self.grid[r][c] == 'S':
                    self.start_pos = (r, c)
                elif self.grid[r][c] == 'G':
                    self.goal_pos = (r, c)
        
        self.player_pos = self.start_pos
        return f"Daily Challenge ({date_str}) Started!", self.get_display_grid()

    def load_level(self, level):
        self.grid = generate_level(level)
        self.height = len(self.grid)
        self.width = len(self.grid[0])
        self.current_level = level
        
        # Reset Level State
        self.moves = 0
        self.start_time = time.time()
        self.path_for_display = []
        self.is_game_over = False
        self.fog_moves_remaining = 0
        self.speed_boost_moves = 0
        self.vision_moves = 0
        # Preserve inventory? User request didn't specify, but usually yes for "game".
        # Let's keep shield/inventory across levels.
        
        # Find start/goal
        for r in range(self.height):
            for c in range(self.width):
                if self.grid[r][c] == 'S':
                    self.start_pos = (r, c)
                elif self.grid[r][c] == 'G':
                    self.goal_pos = (r, c)
        
        self.player_pos = self.start_pos

    def next_level(self):
        if self.mode == "Daily":
            return "Challenge Complete. Check Score!", self.get_display_grid()
            
        self.total_score += self.calculate_score()
        self.current_level += 1
        self.load_level(self.current_level)
        return f"Level {self.current_level}", self.get_display_grid()

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
            
            if cell == 1: # Wall
                return "Blocked!", self.get_display_grid()
                
            # Valid Move
            self.player_pos = (nr, nc)
            self.moves += 1
            
            # Decrement Effects
            if self.fog_moves_remaining > 0: self.fog_moves_remaining -= 1
            if self.speed_boost_moves > 0: self.speed_boost_moves -= 1
            if self.vision_moves > 0: self.vision_moves -= 1
            
            # Handle Interaction
            if cell == 'G':
                self.is_game_over = True
                if self.mode == "Daily":
                    self.total_score = self.calculate_score()
                    msg = f"DAILY COMPLETE! Score: {self.total_score}"
                else:
                    msg = "Goal Reached! Click Next Level."
            elif cell == 'T': # Spike
                if self.has_shield:
                    self.has_shield = False
                    self.inventory.remove('Shield')
                    self.grid[nr][nc] = 0 # Remove trap
                    msg = "Shield blocked Spike!"
                else:
                    self.player_pos = self.start_pos
                    # Higher penalty in daily?
                    penalty = 100 if self.mode == "Daily" else 50
                    self.total_score -= penalty
                    msg = "SPIKE! Reset to Start."
            elif cell == 'F': # Fog
                if self.has_shield:
                    self.has_shield = False
                    self.inventory.remove('Shield')
                    self.grid[nr][nc] = 0
                    msg = "Shield blocked Fog!"
                else:
                    self.fog_moves_remaining = 10
                    self.grid[nr][nc] = 0 # Remove after trigger
                    msg = "FOG TRAP! Visibility reduced."
            elif cell == 'X': # Time
                if self.has_shield:
                    self.has_shield = False
                    self.inventory.remove('Shield')
                    self.grid[nr][nc] = 0
                    msg = "Shield blocked Time Trap!"
                else:
                    self.start_time -= 10 # Add 10s penalty (elapsed checks now-start, so decrease start to increase elapsed)
                    self.grid[nr][nc] = 0
                    msg = "TIME WARP! +10s penalty."
            
            elif cell == 'P': # Shield
                self.has_shield = True
                self.inventory.append('Shield')
                self.grid[nr][nc] = 0
                msg = "Got Shield!"
            elif cell == 'B': # Speed
                self.speed_boost_moves = 10
                self.grid[nr][nc] = 0
                msg = "Speed Boost!"
            elif cell == 'V': # Vision
                self.vision_moves = 10
                self.solve("A*") # Auto trigger hint
                self.grid[nr][nc] = 0
                msg = "AI Vision Active!"
                
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
        # T -> 10, F -> 11, X -> 12
        # P -> 20, B -> 21, V -> 22
        # FOG -> 99
        
        display = []
        
        for r in range(self.height):
            row_data = []
            for c in range(self.width):
                # FOG LOGIC
                if self.fog_moves_remaining > 0:
                    dist = abs(r - self.player_pos[0]) + abs(c - self.player_pos[1])
                    if dist > 2:
                        row_data.append(99) # Fogged
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
                
                # Overlay Hint
                if (r,c) in self.path_for_display and code == 0:
                   code = 5
                   
                row_data.append(code)
            display.append(row_data)

        # Mark Player
        pr, pc = self.player_pos
        display[pr][pc] = 2
        
        return display

    def calculate_score(self):
        elapsed = time.time() - self.start_time
        # Speed boost reduces effective time for score calc? 
        # Actually logic says "Reduces time cost for next N moves"
        # Since I didn't implement move duration limits, let's say steps don't count towards score penalty?
        # Let's keep it simple: Raw time.
        
        optimal_solution = solve_astar(self.grid, self.start_pos, self.goal_pos)
        optimal_len = len(optimal_solution) if optimal_solution else self.moves
        
        efficiency = (optimal_len / max(1, self.moves)) * 100
        time_penalty = int(elapsed) * 1
        
        # Base score
        base_score = 1000 * (self.current_level * 0.5)
        if self.mode == "Daily":
            base_score = 5000 # Fixed high base for daily
        
        level_score = int(base_score * (efficiency/100) - time_penalty)
        return max(0, level_score) # Don't go below 0 for level but total can be negative? NO, keep 0 floor.
        
    def get_metrics(self):
        if self.is_game_over:
             elapsed = int(time.time() - self.start_time)
        else:
             elapsed = int(time.time() - self.start_time)
        
        # Current Level Score Prediction
        curr_score = self.calculate_score()
        items = " ".join(self.inventory) if self.inventory else "None"
        
        mode_str = f"Mode: {self.mode}"
        if self.mode == "Daily":
            mode_str += f" | Hints: {self.hints_remaining}"
            
        return f"{mode_str} | Level: {self.current_level} | Items: {items} | Moves: {self.moves} | Time: {elapsed}s | Est. Score: {curr_score}"

    def solve(self, algorithm):
        # Daily Restrictions
        if self.mode == "Daily":
            if self.hints_remaining <= 0:
                return "No hints remaining in Daily Mode!"
            self.hints_remaining -= 1
            if algorithm != "Hint": # Force just path visualization if requested, but penalty applies
                 # Ideally we don't allow "Solve" which usually means Auto-Play in some contexts. 
                 # Here "Solve" just shows path. 
                 # User Request: "AI auto-solve mode is disabled" -> Assuming the button won't autoplay but just show path.
                 pass
                 
        if algorithm == "BFS":
            path = solve_bfs(self.grid, self.player_pos, self.goal_pos)
        elif algorithm == "DFS":
            path = solve_dfs(self.grid, self.player_pos, self.goal_pos)
        else:
            path = solve_astar(self.grid, self.player_pos, self.goal_pos)
            
        if path:
            self.path_for_display = path[1:]
            penalty = 50 * self.current_level
            if self.mode == "Daily":
                penalty = 500 # Heavy penalty
            self.total_score -= penalty
            return f"Path found {algorithm}. Penalty: {penalty}"
        return "No path found!"
