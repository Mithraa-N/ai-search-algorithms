import time
from .maze_generator import generate_maze_by_difficulty
from .solvers import solve_astar

class GameState:
    def __init__(self):
        self.grid = []
        self.player_pos = (0, 0)
        self.start_pos = (0, 0)
        self.goal_pos = (0, 0)
        self.moves = 0
        self.start_time = 0
        self.history = []
        self.difficulty = "Medium"
        self.is_game_over = False
        self.path_for_display = [] # For AI paths or hints
        self.score = 0
        
    def new_game(self, difficulty="Medium"):
        self.difficulty = difficulty
        self.grid, generator = generate_maze_by_difficulty(difficulty)
        self.height = len(self.grid)
        self.width = len(self.grid[0])
        
        # Find start and goal explicitly to be safe
        for r in range(self.height):
            for c in range(self.width):
                if self.grid[r][c] == 'S':
                    self.start_pos = (r, c)
                elif self.grid[r][c] == 'G':
                    self.goal_pos = (r, c)
        
        self.player_pos = self.start_pos
        self.moves = 0
        self.start_time = time.time()
        self.history = [self.player_pos]
        self.is_game_over = False
        self.path_for_display = []
        self.score = 0
        
        return self.get_display_grid()

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
        
        if 0 <= nr < self.height and 0 <= nc < self.width:
            if self.grid[nr][nc] != 1:
                self.player_pos = (nr, nc)
                self.moves += 1
                self.history.append(self.player_pos)
                
                if self.player_pos == self.goal_pos:
                    self.is_game_over = True
                    self.calculate_score()
                    return "Goal Reached! Score: " + str(self.score), self.get_display_grid()
                
                return "Moving...", self.get_display_grid()
            else:
                return "Blocked!", self.get_display_grid()
        
        return "Boundary!", self.get_display_grid()

    def get_display_grid(self):
        # Return a grid suitable for frontend visualization
        # We can map integers/strings to colors in frontend or return a color matrix here
        # Return a list of lists of colors or codes
        # Codes: 0=Path(white/light), 1=Wall(black), 2=Player(blue), 3=Start(green), 4=Goal(red), 5=Path(yellow)
        
        display = [[0 if cell != 1 else 1 for cell in row] for row in self.grid]
        
        # Mark Start and Goal in base layer if not overridden
        sx, sy = self.start_pos
        gx, gy = self.goal_pos
        display[sx][sy] = 3
        display[gx][gy] = 4
        
        # Mark AI Path
        for r, c in self.path_for_display:
            if display[r][c] not in [3, 4]: # Don't overwrite Start/Goal
                display[r][c] = 5 # Yellow path
                
        # Mark Player
        pr, pc = self.player_pos
        display[pr][pc] = 2
        
        return display

    def calculate_score(self):
        self.elapsed_final = time.time() - self.start_time
        # Simple score
        optimal_solution = solve_astar(self.grid, self.start_pos, self.goal_pos)
        optimal_len = len(optimal_solution) if optimal_solution else self.moves
        
        efficiency = (optimal_len / max(1, self.moves)) * 100
        time_penalty = int(self.elapsed_final) * 1
        
        self.score = int(1000 * (efficiency/100) - time_penalty)
        if self.score < 0: self.score = 0
        
    def get_metrics(self):
        if self.is_game_over:
             elapsed = int(self.elapsed_final)
        else:
             elapsed = int(time.time() - self.start_time)
             
        return f"Moves: {self.moves} | Time: {elapsed}s | Score: {self.score}"

    def solve(self, algorithm):
        from .solvers import solve_bfs, solve_dfs, solve_astar
        
        if algorithm == "BFS":
            path = solve_bfs(self.grid, self.player_pos, self.goal_pos)
        elif algorithm == "DFS":
            path = solve_dfs(self.grid, self.player_pos, self.goal_pos)
        else: # A*
            path = solve_astar(self.grid, self.player_pos, self.goal_pos)
            
        if path:
            self.path_for_display = path[1:] # Exclude current pos to not color over player immediately
            self.score -= 50 # Penalty for hint
            return f"Path found with {algorithm} (Length: {len(path)})"
        return "No path found!"
