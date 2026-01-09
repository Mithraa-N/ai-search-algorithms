import random
import heapq
import datetime

class MazeGenerator:
    def __init__(self, width=20, height=20, seed=None):
        self.width = width
        self.height = height
        self.grid = []
        self.start = (0, 0)
        self.goal = (width - 1, height - 1)
        self.seed = seed
        # Use a local random instance for determinism
        self.rng = random.Random(seed) if seed is not None else random.Random()

    def generate_maze(self):
        # 1 = Wall, 0 = Path
        self.grid = [[1 for _ in range(self.width)] for _ in range(self.height)]

        # Recursive Backtracking
        stack = [(0, 0)]
        self.grid[0][0] = 0
        
        while stack:
            current_r, current_c = stack[-1]
            options = []
            
            # Check 4 directions for 2-step jumps
            directions = [(-2, 0), (2, 0), (0, -2), (0, 2)]
            
            for dr, dc in directions:
                nr, nc = current_r + dr, current_c + dc
                if 0 <= nr < self.height and 0 <= nc < self.width:
                    if self.grid[nr][nc] == 1: # If unvisited (wall)
                        options.append((nr, nc, dr, dc))
            
            if options:
                nr, nc, dr, dc = self.rng.choice(options)
                # Knock down the wall between
                self.grid[current_r + dr // 2][current_c + dc // 2] = 0
                self.grid[nr][nc] = 0
                stack.append((nr, nc))
            else:
                stack.pop()

        # Ensure Start and Goal
        self.grid[0][0] = 'S'
        self.grid[self.height - 1][self.width - 1] = 'G'
        
        # Ensure Goal reachability if blocked by wall on even grid
        if self.grid[self.height - 1][self.width - 2] == 1 and self.grid[self.height - 2][self.width - 1] == 1:
             self.grid[self.height - 1][self.width - 2] = 0
        
        return self.grid
    
    def place_items(self, level):
        """
        Place Traps: T (Spike), F (Fog), X (Time)
        Place Powerups: P (Shield), B (Speed), V (Vision)
        """
        # Calculate item counts based on level
        # Traps increase with level
        num_traps = int(level * 1.5) + 2
        # Powerups slightly decrease or stay constant
        num_powerups = max(2, 5 - int(level * 0.2))
        
        empty_cells = []
        for r in range(self.height):
            for c in range(self.width):
                if self.grid[r][c] == 0: # Only place on paths
                    # Don't place too close to start (grace zone)
                    if (r + c) > 3: 
                        empty_cells.append((r, c))
                        
        self.rng.shuffle(empty_cells)
        
        traps = ['T', 'F', 'X']
        powerups = ['P', 'B', 'V']
        
        # Place Traps
        for _ in range(min(num_traps, len(empty_cells))):
            r, c = empty_cells.pop()
            # Distribution: Level 1-3 mostly simple, 4+ complex
            if level <= 3:
                trap_type = 'X' # Time trap is mild
            else:
                trap_type = self.rng.choice(traps)
            
            self.grid[r][c] = trap_type

        # Place Powerups
        for _ in range(min(num_powerups, len(empty_cells))):
            r, c = empty_cells.pop()
            p_type = self.rng.choice(powerups)
            self.grid[r][c] = p_type
            
        return self.grid

def generate_level(level, seed=None):
    # Dynamic size based on level
    size = 11 + (level - 1) * 2
    if size > 31: size = 31 # Cap size
    
    gen = MazeGenerator(size, size, seed=seed)
    gen.generate_maze()
    return gen.place_items(level)
