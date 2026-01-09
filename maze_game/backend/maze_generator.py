import random
import heapq

class MazeGenerator:
    def __init__(self, width=20, height=20):
        self.width = width
        self.height = height
        self.grid = []
        self.start = (0, 0)
        self.goal = (width - 1, height - 1)

    def generate_maze(self):
        # 1 = Wall, 0 = Path, S = Start, G = Goal
        # Initialize grid with all walls
        self.grid = [[1 for _ in range(self.width)] for _ in range(self.height)]

        # Recursive Backtracking algorithm
        def get_neighbors(r, c):
            neighbors = []
            if r > 1: neighbors.append((r - 2, c))
            if r < self.height - 2: neighbors.append((r + 2, c))
            if c > 1: neighbors.append((r, c - 2))
            if c < self.width - 2: neighbors.append((r, c + 2))
            return neighbors

        # Start from (0,0) - forcing odd coordinates to be paths usually helps in this alg, 
        # but let's adjust for 0-indexed strict grid.
        # Actually standard logic: 
        # Grid dimensions should ideally be odd for "rooms" and "walls" structure in strict recursive backtracking.
        # If input is even, we might have a thick wall at the edge. Let's force odd for internal logic if needed or handle boundary.
        # Let's simplify: Start at (0,0). Mark as 0. 
        # Keep a frontier or stick to finding unvisited neighbors 2 steps away.
        
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
                nr, nc, dr, dc = random.choice(options)
                # Knock down the wall between
                self.grid[current_r + dr // 2][current_c + dc // 2] = 0
                self.grid[nr][nc] = 0
                stack.append((nr, nc))
            else:
                stack.pop()

        # Ensure Start and Goal are open and set
        self.grid[0][0] = 'S'
        # Force goal to be reachable if it ended up isolated (unlikely with this algo but possible if even sized)
        # Actually with even sizes, the bottom-right might be a wall.
        # Let's clean up goal position. A simple way is to find the nearest 0 to (h-1, w-1) or just set (h-1, w-1) and neighbors to 0.
        
        self.grid[self.height - 1][self.width - 1] = 'G'
        
        # Connect goal if it's currently a wall (simple validity fix)
        if self.grid[self.height - 1][self.width - 2] == 1 and self.grid[self.height - 2][self.width - 1] == 1:
             self.grid[self.height - 1][self.width - 2] = 0

        # Also just in case the node itself was a wall (it was init as 1)
        # The algo usually visits "even" nodes (0,0), (0,2)... if we step by 2.
        # If width is even, width-1 is odd. 
        # Let's just ensure path connectivity by clearing a small area around goal if needed?
        # A clearer way: perform a check or just carve a path to the nearest open cell.
        # For this prototype, I'll allow walls to be broken to ensure the goal is open.
        
        return self.grid

    def get_neighbors(self, node):
        r, c = node
        neighbors = []
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            if 0 <= nr < self.height and 0 <= nc < self.width:
                if self.grid[nr][nc] != 1:
                    neighbors.append((nr, nc))
        return neighbors

def generate_maze_by_difficulty(difficulty):
    if difficulty == "Easy":
        gen = MazeGenerator(11, 11)
    elif difficulty == "Medium":
        gen = MazeGenerator(21, 21)
    elif difficulty == "Hard":
        gen = MazeGenerator(31, 31)
    else:
        gen = MazeGenerator(15, 15)
    
    return gen.generate_maze(), gen
