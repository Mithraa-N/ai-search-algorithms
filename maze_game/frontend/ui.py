import gradio as gr
from backend.game_state import GameState

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
.maze-table { border-collapse: collapse; border-spacing: 0; }
.cell {
    width: 25px; height: 25px; padding: 0; border-radius: 4px; transition: all 0.2s ease;
}

.cell-1 { background: #16213e; box-shadow: inset 0 0 5px #000; }
.cell-0 { background: #32344a; }
.cell-3 { background: #2ecc71; box-shadow: 0 0 10px #2ecc71; }
.cell-4 { background: #e74c3c; box-shadow: 0 0 10px #e74c3c; animation: glow-red 1.5s infinite alternate; }
.cell-2 { background: #3498db; box-shadow: 0 0 15px #3498db; border-radius: 50%; transform: scale(0.85); animation: bounce 0.5s infinite alternate; }
.cell-5 { background: #f1c40f; opacity: 0.6; border-radius: 50%; transform: scale(0.4); }

/* Traps */
.cell-10 { background: #555; border: 2px solid #e74c3c; border-radius: 0; position: relative; } /* Spike */
.cell-10::after { content: '⚠️'; font-size: 14px; position: absolute; left: 2px; top: 0; }

.cell-11 { background: #7f8c8d; opacity: 0.8; } /* Fog trap trigger */
.cell-11::after { content: '☁️'; font-size: 14px; position: absolute; left: 2px; top: 0; }

.cell-12 { background: #d35400; } /* Time trap */
.cell-12::after { content: '⏳'; font-size: 14px; position: absolute; left: 2px; top: 0; }

/* Powerups */
.cell-20 { background: #8e44ad; border-radius: 50%; } /* Shield */
.cell-20::after { content: '🛡️'; font-size: 14px; position: absolute; left: 2px; top: 0; }

.cell-21 { background: #2980b9; border-radius: 50%; } /* Speed */
.cell-21::after { content: '⚡'; font-size: 14px; position: absolute; left: 2px; top: 0; }

.cell-22 { background: #16a085; border-radius: 50%; } /* Vision */
.cell-22::after { content: '👁️'; font-size: 14px; position: absolute; left: 2px; top: 0; }

/* Effects */
.cell-99 { background: #000; opacity: 0.95; cursor: not-allowed; } /* Active Fog */

@keyframes glow-red { from { box-shadow: 0 0 5px #e74c3c; } to { box-shadow: 0 0 20px #e74c3c; } }
@keyframes bounce { from { transform: scale(0.8); } to { transform: scale(0.95); } }

.win-overlay {
    position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%);
    background: rgba(0, 0, 0, 0.9); color: #ffd700; padding: 20px 40px;
    border-radius: 15px; text-align: center; border: 2px solid #ffd700;
    z-index: 100;
}
"""

KEYBOARD_JS = """
<script>
console.log("Keyboard listener injected");
document.addEventListener('keydown', function(event) {
    const keyMap = {
        'ArrowUp': 'btn-up', 'w': 'btn-up', 'W': 'btn-up',
        'ArrowDown': 'btn-down', 's': 'btn-down', 'S': 'btn-down',
        'ArrowLeft': 'btn-left', 'a': 'btn-left', 'A': 'btn-left',
        'ArrowRight': 'btn-right', 'd': 'btn-right', 'D': 'btn-right'
    };
    if (keyMap[event.key]) {
        const el = document.getElementById(keyMap[event.key]);
        if (el) {
            event.preventDefault();
            if (el.tagName === 'BUTTON') el.click();
            else {
                const btn = el.querySelector('button');
                if (btn) btn.click();
                else el.click();
            }
        }
    }
});
</script>
"""

def render_board(display_grid, level_complete=False):
    if not display_grid: return "<div>Loading...</div>"
    
    rows = len(display_grid)
    cols = len(display_grid[0])
    cell_px = 30 if rows <= 15 else 20
    
    html = '<div class="maze-board">'
    
    if level_complete:
        html += """
        <div class="win-overlay">
            <h2>LEVEL COMPLETE!</h2>
            <p>Click 'Next Level' to continue.</p>
        </div>
        """
        
    html += '<table class="maze-table">'
    for row in display_grid:
        html += '<tr>'
        for cell in row:
            html += f'<td class="cell cell-{cell}" style="width: {cell_px}px; height: {cell_px}px;"></td>'
        html += '</tr>'
    html += '</table></div>'
    return html

def create_app():
    theme = gr.themes.Soft(primary_hue="blue", neutral_hue="slate").set(
        body_background_fill="#0f172a", block_background_fill="#1e293b",
        block_border_width="0px", background_fill_primary="#0f172a"
    )

    with gr.Blocks(theme=theme, css=CUSTOM_CSS, title="Maze Master Pro") as app:
        gr.HTML(KEYBOARD_JS)
        state = gr.State(GameState())
        
        with gr.Row():
            gr.Markdown("# 🎮 Maze Master: Evolution")
        
        with gr.Row():
            status_bar = gr.Textbox(label="Mission Status", interactive=False, elem_id="status_box")
        
        with gr.Row():
            with gr.Column(scale=2):
                board_display = gr.HTML(label="Game Board")
            
            with gr.Column(scale=1):
                gr.Markdown("### Controls")
                with gr.Row():
                    up_btn = gr.Button("⬆️", elem_id="btn-up")
                with gr.Row():
                    left_btn = gr.Button("⬅️", elem_id="btn-left")
                    right_btn = gr.Button("➡️", elem_id="btn-right")
                with gr.Row():
                    down_btn = gr.Button("⬇️", elem_id="btn-down")
                
                with gr.Group():
                    next_level_btn = gr.Button("🚀 Next Level / Start", variant="primary")
                    
                gr.Markdown("### AI Tools")
                algo_selector = gr.Dropdown(["BFS", "DFS", "A*"], value="A*", label="Algorithm")
                solve_btn = gr.Button("🔍 Scan Path")
                game_msg = gr.Textbox(label="System Log", interactive=False)

        def start_or_next(game):
            # If game over, next level. Else restart.
            if game.is_game_over:
                msg, grid = game.next_level()
            else:
                grid = game.start_new_game()
                msg = "New Game Started"
            return render_board(grid), game.get_metrics(), game, msg

        def start_daily(game):
            msg, grid = game.start_daily_challenge()
            return render_board(grid), game.get_metrics(), game, msg

        with gr.Row():
             with gr.Column(scale=1):
                 next_level_btn.click(start_or_next, inputs=[state], outputs=[board_display, status_bar, state, game_msg])
             with gr.Column(scale=1):
                 daily_btn = gr.Button("📅 Daily Challenge", variant="secondary")
                 daily_btn.click(start_daily, inputs=[state], outputs=[board_display, status_bar, state, game_msg])
        
        def move(direction, game):
            msg, grid = game.move_player(direction)
            is_win = game.is_game_over
            return render_board(grid, level_complete=is_win), game.get_metrics(), game, msg
            
        up_btn.click(move, inputs=[gr.State("Up"), state], outputs=[board_display, status_bar, state, game_msg])
        down_btn.click(move, inputs=[gr.State("Down"), state], outputs=[board_display, status_bar, state, game_msg])
        left_btn.click(move, inputs=[gr.State("Left"), state], outputs=[board_display, status_bar, state, game_msg])
        right_btn.click(move, inputs=[gr.State("Right"), state], outputs=[board_display, status_bar, state, game_msg])
        
        def solve(algo, game):
            msg = game.solve(algo)
            return render_board(game.get_display_grid(), level_complete=game.is_game_over), game.get_metrics(), game, msg
            
        solve_btn.click(solve, inputs=[algo_selector, state], outputs=[board_display, status_bar, state, game_msg])
        
        app.load(start_or_next, inputs=[state], outputs=[board_display, status_bar, state, game_msg])
        
    return app
