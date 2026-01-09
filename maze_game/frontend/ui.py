import gradio as gr
from backend.game_state import GameState

def render_board(display_grid):
    if not display_grid:
        return "<div>Start a new game</div>"
    
    html = '<div style="display: flex; justify-content: center; align-items: center; background-color: #222; padding: 10px; border-radius: 8px;">'
    html += '<table style="border-collapse: collapse; border: 2px solid #555;">'
    
    cell_size = "25px"
    if len(display_grid) > 20: cell_size = "20px"
    if len(display_grid) > 30: cell_size = "15px"
    
    for row in display_grid:
        html += '<tr>'
        for cell in row:
            color = "#ffffff"
            if cell == 1: color = "#1e1e1e" # Wall
            elif cell == 2: color = "#3b82f6" # Player
            elif cell == 3: color = "#22c55e" # Start
            elif cell == 4: color = "#ef4444" # Goal
            elif cell == 5: color = "#facc15" # Hint
            
            html += f'<td style="width: {cell_size}; height: {cell_size}; background-color: {color}; padding: 0; border: 1px solid #444;"></td>'
        html += '</tr>'
    html += '</table></div>'
    return html

def create_app():
    with gr.Blocks(theme=gr.themes.Soft(), title="Python Maze Solver") as app:
        
        state = gr.State(GameState())
        
        gr.Markdown("""
        # 🎮 Interactive AI Maze Game
        **Instructions**: use buttons to move (or WASD if we could bind keys, but buttons for now). Reach the **Red Goal**!   
        **Legends**: 🔵 Player | 🟢 Start | 🔴 Goal | ⚫ Wall | 🟡 AI Path
        """)
        
        with gr.Row():
            score_board = gr.Textbox(label="Game Stats", value="Moves: 0 | Time: 0s | Score: 0", interactive=False)
        
        with gr.Row():
            with gr.Column(scale=2):
                board_display = gr.HTML(label="Maze Board")
            
            with gr.Column(scale=1):
                with gr.Group():
                    gr.Markdown("### Controls")
                    with gr.Row():
                        up_btn = gr.Button("⬆️ Up")
                    with gr.Row():
                        left_btn = gr.Button("⬅️ Left")
                        right_btn = gr.Button("➡️ Right")
                    with gr.Row():
                        down_btn = gr.Button("⬇️ Down")
                
                with gr.Group():
                    gr.Markdown("### Game Settings")
                    difficulty = gr.Dropdown(["Easy", "Medium", "Hard"], value="Medium", label="Difficulty")
                    new_game_btn = gr.Button("🆕 New Game", variant="primary")
                    
                with gr.Group():
                    gr.Markdown("### AI Helper")
                    algo_selector = gr.Dropdown(["BFS", "DFS", "A*"], value="A*", label="Algorithm")
                    solve_btn = gr.Button("🤖 Show Hint/Path")
                    status_viz = gr.Textbox(label="Status", interactive=False)

        # Event Handlers
        
        def start_game(diff, game):
            game = GameState() # Reset
            grid = game.new_game(diff)
            return render_board(grid), game.get_metrics(), game, "Game Started!"

        new_game_btn.click(start_game, inputs=[difficulty, state], outputs=[board_display, score_board, state, status_viz])
        
        def move(direction, game):
            msg, grid = game.move_player(direction)
            return render_board(grid), game.get_metrics(), game, msg
            
        up_btn.click(move, inputs=[gr.State("Up"), state], outputs=[board_display, score_board, state, status_viz])
        down_btn.click(move, inputs=[gr.State("Down"), state], outputs=[board_display, score_board, state, status_viz])
        left_btn.click(move, inputs=[gr.State("Left"), state], outputs=[board_display, score_board, state, status_viz])
        right_btn.click(move, inputs=[gr.State("Right"), state], outputs=[board_display, score_board, state, status_viz])
        
        def solve(algo, game):
            msg = game.solve(algo)
            return render_board(game.get_display_grid()), game.get_metrics(), game, msg
            
        solve_btn.click(solve, inputs=[algo_selector, state], outputs=[board_display, score_board, state, status_viz])
        
        # Initialize on load
        app.load(start_game, inputs=[difficulty, state], outputs=[board_display, score_board, state, status_viz])
        
    return app
