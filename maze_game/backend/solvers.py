from collections import deque
import heapq

# Define weights
COST_MOVE = 1
COST_TRAP = 20 # High cost to avoid traps
COST_START_GOAL = 1
COST_POWERUP = 1 # Normal cost, or strictly prefer? A* needs heuristic consistency. 
# Identifying "bad" cells
TRAPS = ['T', 'F', 'X']

def get_neighbors(grid, r, c, rows, cols):
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    for dr, dc in directions:
        nr, nc = r + dr, c + dc
        if 0 <= nr < rows and 0 <= nc < cols:
            cell = grid[nr][nc]
            # 1 is wall. Everything else is walkable (traps/items)
            if cell != 1:
                yield (nr, nc)

def solve_astar(grid, start, goal):
    rows = len(grid)
    cols = len(grid[0])
    
    pq = [] 
    heapq.heappush(pq, (0, 0, start))
    
    came_from = {start: None}
    cost_so_far = {start: 0}
    
    while pq:
        _, current_cost, current = heapq.heappop(pq)
        
        if current == goal:
            break
            
        for next_node in get_neighbors(grid, current[0], current[1], rows, cols):
            nr, nc = next_node
            cell_content = grid[nr][nc]
            
            # Determine movement cost
            step_cost = COST_MOVE
            if cell_content in TRAPS:
                step_cost = COST_TRAP
                
            new_cost = current_cost + step_cost
            
            if next_node not in cost_so_far or new_cost < cost_so_far[next_node]:
                cost_so_far[next_node] = new_cost
                priority = new_cost + heuristic(next_node, goal)
                heapq.heappush(pq, (priority, new_cost, next_node))
                came_from[next_node] = current
                
    return reconstruct_path(came_from, start, goal)

def solve_bfs(grid, start, goal):
    # BFS ignores weights, so it will hit traps if they are shortest path
    rows = len(grid)
    cols = len(grid[0])
    queue = deque([start])
    visited = {start: None} 
    
    while queue:
        current = queue.popleft()
        if current == goal:
            break
        
        for next_node in get_neighbors(grid, current[0], current[1], rows, cols):
            if next_node not in visited:
                visited[next_node] = current
                queue.append(next_node)
                
    return reconstruct_path(visited, start, goal)

def solve_dfs(grid, start, goal):
    rows = len(grid)
    cols = len(grid[0])
    stack = [start]
    visited = {start: None}
    
    while stack:
        current = stack.pop()
        if current == goal:
            break
        
        for next_node in get_neighbors(grid, current[0], current[1], rows, cols):
            if next_node not in visited:
                visited[next_node] = current
                stack.append(next_node)
    
    return reconstruct_path(visited, start, goal)

def heuristic(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def reconstruct_path(visited, start, goal):
    if goal not in visited:
        return []
        
    current = goal
    path = []
    while current != start:
        path.append(current)
        current = visited[current]
    path.append(start)
    path.reverse()
    return path
