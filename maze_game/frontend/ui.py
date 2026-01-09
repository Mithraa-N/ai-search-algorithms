import gradio as gr
from backend.game_state import GameState

# Custom CSS for the board and animations
CUSTOM_CSS = """
.maze-board {
    position: relative;
    background: #1a1a2e;
    padding: 10px;
    border-radius: 12px;
    box-shadow: 0 0 20px rgba(0,0,0,0.5);
    margin: 0 auto;
    width: fit-content;
}

.maze-table {
    border-collapse: collapse;
    border-spacing: 0;
}

.cell {
    width: 25px;
    height: 25px;
    padding: 0;
    border-radius: 4px;
    transition: all 0.2s ease;
}

/* Wall */
.cell-1 {
    background: #16213e;
    box-shadow: inset 0 0 5px #000;
}

/* Path */
.cell-0 {
    background: #32344a; /* slightly lighter than wall for path */
}

/* Start */
.cell-3 {
    background: #2ecc71;
    box-shadow: 0 0 10px #2ecc71;
}

/* Goal */
.cell-4 {
    background: #e74c3c;
    box-shadow: 0 0 10px #e74c3c;
    animation: glow-red 1.5s infinite alternate;
}

/* Player */
.cell-2 {
    background: #3498db;
    box-shadow: 0 0 15px #3498db;
    border-radius: 50%;
    transform: scale(0.85);
    animation: bounce 0.5s infinite alternate;
}

/* AI Hint Path */
.cell-5 {
    background: #f1c40f;
    box-shadow: 0 0 8px #f1c40f;
    opacity: 0.6;
    border-radius: 50%;
    transform: scale(0.4);
}

@keyframes glow-red {
    from { box-shadow: 0 0 5px #e74c3c; }
    to { box-shadow: 0 0 20px #e74c3c; }
}

@keyframes bounce {
    from { transform: scale(0.8); }
    to { transform: scale(0.95); }
}

.win-overlay {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    background: rgba(0, 0, 0, 0.85);
    color: #ffd700;
    padding: 20px 40px;
    border-radius: 15px;
    text-align: center;
    border: 2px solid #ffd700;
    animation: pop-in 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    z-index: 100;
    pointer-events: none; /* Let clicks pass through if needed, though usually we want to block */
}

@keyframes pop-in {
    0% { transform: translate(-50%, -50%) scale(0); opacity: 0; }
    100% { transform: translate(-50%, -50%) scale(1); opacity: 1; }
}

.win-title {
    font-size: 2.5em;
    margin: 0 0 10px 0;
    text-shadow: 0 0 10px #e67e22;
}

.win-score {
    font-size: 1.2em;
    color: #fff;
}
"""

# JavaScript for Keyboard Events
KEYBOARD_JS = """
<script>
console.log("Keyboard listener injected");
document.addEventListener('keydown', function(event) {
    const keyMap = {
        'ArrowUp': 'btn-up',
        'w': 'btn-up', 'W': 'btn-up',
        'ArrowDown': 'btn-down',
        's': 'btn-down', 'S': 'btn-down',
        'ArrowLeft': 'btn-left',
        'a': 'btn-left', 'A': 'btn-left',
        'ArrowRight': 'btn-right',
        'd': 'btn-right', 'D': 'btn-right'
    };
    
    if (keyMap[event.key]) {
        const targetId = keyMap[event.key];
        const el = document.getElementById(targetId);
        if (el) {
            event.preventDefault(); // Prevent scrolling
            // Gradio often wraps the button in a div with the elem_id
            // So we check if the element itself is clickable or if it contains a button
            if (el.tagName === 'BUTTON') {
                el.click();
            } else {
                const btn = el.querySelector('button');
                if (btn) {
                    btn.click();
                } else {
                    // Fallback: try clicking the element itself if it's acting as a container
                    el.click();
                }
            }
        }
    }
});
</script>
"""

def render_board(display_grid, game_over=False, score=0):
    if not display_grid:
        return "<div style='color: white; text-align: center;'>Start a new game</div>"
    
    rows = len(display_grid)
    cols = len(display_grid[0])
    
    # Adjust cell size based on grid dimension
    cell_px = 30
    if rows > 15: cell_px = 25
    if rows > 25: cell_px = 20
    
    # Build HTML Board
    html = f'<div class="maze-board">'
    
    if game_over and score > 0: # Assuming score > 0 means win/completion in this context or we can check a flag
        # We can pass specific state like "WON" or "LOST"
        # For now, let's assume if game is over and we are at goal (handled by backend logic mostly), it's a win.
        # But let's rely on the simple Boolean for now.
        html += f"""
        <div class="win-overlay">
            <div class="win-title">🏆 VICTORY!</div>
            <div class="win-score">Final Score: {score}</div>
        </div>
        """
        
    html += '<table class="maze-table">'
    
    for row in display_grid:
        html += '<tr>'
        for cell in row:
            # cell is integer 0-5
            html += f'<td class="cell cell-{cell}" style="width: {cell_px}px; height: {cell_px}px;"></td>'
        html += '</tr>'
    html += '</table></div>'
    return html

def create_app():
    # Use a darker theme base
    theme = gr.themes.Soft(
        primary_hue="blue",
        neutral_hue="slate",
    ).set(
        body_background_fill="#0f172a",
        block_background_fill="#1e293b",
        block_border_width="0px",
        background_fill_primary="#0f172a"
    )

    with gr.Blocks(theme=theme, css=CUSTOM_CSS, title="Python Maze Solver") as app:
        
        # Inject JS for keyboard support
        gr.HTML(KEYBOARD_JS)
        
        state = gr.State(GameState())
        
        with gr.Row():
            gr.Markdown("""
            # 🎮 Neon Maze Runner
            **Controls**: Use **Arrow Keys** or **WASD** to move.
            **Goal**: Reach the <span style='color: #e74c3c; font-weight: bold;'>RED</span> target!
            """)
        
        with gr.Row():
            score_board = gr.Textbox(
                label="Mission Stats", 
                value="Moves: 0 | Time: 0s | Score: 0", 
                interactive=False,
                elem_classes="stats-box"
            )
        
        with gr.Row():
            with gr.Column(scale=2):
                board_display = gr.HTML(label="Game Board")
            
            with gr.Column(scale=1):
                gr.Markdown("### 🕹️ Command Center")
                
                with gr.Group():
                    with gr.Row():
                        up_btn = gr.Button("⬆️",  elem_id="btn-up")
                    with gr.Row():
                        left_btn = gr.Button("⬅️", elem_id="btn-left")
                        right_btn = gr.Button("➡️", elem_id="btn-right")
                    with gr.Row():
                        down_btn = gr.Button("⬇️", elem_id="btn-down")
                
                gr.Markdown("### ⚙️ System")
                difficulty = gr.Dropdown(["Easy", "Medium", "Hard"], value="Medium", label="Difficulty")
                new_game_btn = gr.Button("🆕 New Operation", variant="primary")
                    
                gr.Markdown("### 🤖 AI Assist")
                algo_selector = gr.Dropdown(["BFS", "DFS", "A*"], value="A*", label="Algorithm")
                solve_btn = gr.Button("🔍 Calculate Path")
                status_viz = gr.Textbox(label="System Log", interactive=False)

        # Logic
        
        def start_game(diff, game):
            game = GameState() # Reset
            grid = game.new_game(diff)
            # Reset score display
            return render_board(grid), game.get_metrics(), game, "Ready."

        new_game_btn.click(start_game, inputs=[difficulty, state], outputs=[board_display, score_board, state, status_viz])
        
        def move(direction, game):
            msg, grid = game.move_player(direction)
            is_over = game.is_game_over
            # If "Goal Reached" in msg, it's a win
            win = "Goal Reached" in msg
            return render_board(grid, game_over=win, score=game.score), game.get_metrics(), game, msg
            
        up_btn.click(move, inputs=[gr.State("Up"), state], outputs=[board_display, score_board, state, status_viz])
        down_btn.click(move, inputs=[gr.State("Down"), state], outputs=[board_display, score_board, state, status_viz])
        left_btn.click(move, inputs=[gr.State("Left"), state], outputs=[board_display, score_board, state, status_viz])
        right_btn.click(move, inputs=[gr.State("Right"), state], outputs=[board_display, score_board, state, status_viz])
        
        def solve(algo, game):
            msg = game.solve(algo)
            return render_board(game.get_display_grid(), game_over=game.is_game_over, score=game.score), game.get_metrics(), game, msg
            
        solve_btn.click(solve, inputs=[algo_selector, state], outputs=[board_display, score_board, state, status_viz])
        
        # Init
        app.load(start_game, inputs=[difficulty, state], outputs=[board_display, score_board, state, status_viz])
        
    return app
