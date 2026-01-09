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


# Add Ghost style and Hidden Utilities
CUSTOM_CSS += """
.cell-6 { background: #9b59b6; opacity: 0.5; border-radius: 50%; transform: scale(0.6); box-shadow: 0 0 10px #9b59b6; }

/* Hide buttons but keep them clickable by JS */
#btn-up, #btn-down, #btn-left, #btn-right {
    opacity: 0 !important;
    height: 1px !important;
    width: 1px !important;
    margin: 0 !important;
    padding: 0 !important;
    overflow: hidden !important;
    position: absolute !important;
    pointer-events: none !important;
}
"""

def render_leaderboard(data):
    if not data:
        return "<div style='color:white; padding:20px;'>No records yet.</div>"
    
    html = """
    <table style='width:100%; border-collapse:collapse; color:white;'>
    <tr style='background:#34495e; text-align:left;'>
        <th style='padding:10px;'>Rank</th>
        <th style='padding:10px;'>Player</th>
        <th style='padding:10px;'>Score</th>
        <th style='padding:10px;'>Time</th>
        <th style='padding:10px;'>Moves</th>
        <th style='padding:10px;'>Date</th>
    </tr>
    """
    for i, entry in enumerate(data):
        bg = "#2c3e50" if i % 2 == 0 else "#22313f"
        html += f"""
        <tr style='background:{bg}; border-bottom:1px solid #444;'>
            <td style='padding:8px;'>#{i+1}</td>
            <td style='padding:8px; font-weight:bold; color:#3498db;'>{entry['name']}</td>
            <td style='padding:8px; color:#f1c40f;'>{entry['score']}</td>
            <td style='padding:8px;'>{entry['time']}s</td>
            <td style='padding:8px;'>{entry['moves']}</td>
            <td style='padding:8px; font-size:0.9em; color:#95a5a6;'>{entry['date']}</td>
        </tr>
        """
    html += "</table>"
    return html

def create_app():
    theme = gr.themes.Soft(primary_hue="blue", neutral_hue="slate").set(
        body_background_fill="#0f172a", block_background_fill="#1e293b",
        block_border_width="0px", background_fill_primary="#0f172a"
    )

    with gr.Blocks(theme=theme, css=CUSTOM_CSS, title="Maze Master: Evolution") as app:
        gr.HTML(KEYBOARD_JS)
        state = gr.State(GameState())
        
        with gr.Row():
            gr.Markdown("# 🏆 Maze Master: Evolution")
        
        with gr.Row():
            status_bar = gr.Textbox(label="Mission Status", interactive=False, elem_id="status_box")
        
        with gr.Tabs():
            with gr.Tab("🎮 Game"):
                with gr.Row():
                    name_input = gr.Textbox(label="Player Name", placeholder="Enter your name...", scale=3)
                    save_name_btn = gr.Button("💾 Set Name", scale=1)

                with gr.Row():
                    with gr.Column(scale=2):
                        board_display = gr.HTML(label="Game Board")
                    
                    with gr.Column(scale=1):
                        gr.Markdown("### Controls")
                        gr.Markdown("*(Use Arrow Keys or WASD to Move. Click on the game area first!)*")
                        
                        # Hidden Buttons for JS Hook - Clean IDs, hidden via CSS
                        with gr.Row(): 
                            up_btn = gr.Button("⬆️", elem_id="btn-up")
                            left_btn = gr.Button("⬅️", elem_id="btn-left")
                            right_btn = gr.Button("➡️", elem_id="btn-right")
                            down_btn = gr.Button("⬇️", elem_id="btn-down")
                        
                        with gr.Group():
                            next_level_btn = gr.Button("🚀 Start / Next Level", variant="primary")
                            daily_btn = gr.Button("📅 Daily Challenge", variant="secondary")
                            
                        gr.Markdown("### Tools")
                        ghost_btn = gr.Button("👻 Toggle Ghost Replay")
                        algo_selector = gr.Dropdown(["BFS", "DFS", "A*"], value="A*", label="Algorithm")
                        solve_btn = gr.Button("🔍 Hint")
                        game_msg = gr.Textbox(label="System Log", interactive=False)

            with gr.Tab("🏅 Leaderboard"):
                with gr.Row():
                    lb_refresh = gr.Button("🔄 Refresh Rankings")
                with gr.Row():
                    with gr.Column():
                        gr.Markdown("### 📅 Daily Challenge Top 50")
                        daily_lb = gr.HTML()
                    with gr.Column():
                        gr.Markdown("### 🌌 All-Time Legends")
                        normal_lb = gr.HTML()

        # Logic
        
        def save_name(name, game):
            msg = game.set_player_name(name)
            return game, msg
        save_name_btn.click(save_name, inputs=[name_input, state], outputs=[state, game_msg])
        name_input.submit(save_name, inputs=[name_input, state], outputs=[state, game_msg])

        def start_or_next(game):
            if game.is_game_over:
                msg, grid = game.next_level()
            else:
                grid = game.start_new_game()
                msg = "New Game Started"
            return render_board(grid), game.get_metrics(), game, msg

        next_level_btn.click(start_or_next, inputs=[state], outputs=[board_display, status_bar, state, game_msg])
        
        def start_daily(game):
            msg, grid = game.start_daily_challenge()
            return render_board(grid), game.get_metrics(), game, msg

        daily_btn.click(start_daily, inputs=[state], outputs=[board_display, status_bar, state, game_msg])
        
        def toggle_ghost(game):
            msg, grid = game.toggle_ghost()
            return render_board(grid), game.get_metrics(), game, msg
        ghost_btn.click(toggle_ghost, inputs=[state], outputs=[board_display, status_bar, state, game_msg])

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
            # Pass level_complete to ensure overlay logic works if game over
            return render_board(game.get_display_grid(), level_complete=game.is_game_over), game.get_metrics(), game, msg
        solve_btn.click(solve, inputs=[algo_selector, state], outputs=[board_display, status_bar, state, game_msg])
        
        def update_lbs(game):
            d_data = game.data_manager.get_leaderboard("Daily")
            n_data = game.data_manager.get_leaderboard("Standard")
            return render_leaderboard(d_data), render_leaderboard(n_data)
        
        lb_refresh.click(update_lbs, inputs=[state], outputs=[daily_lb, normal_lb])
        
        # Init
        app.load(start_or_next, inputs=[state], outputs=[board_display, status_bar, state, game_msg])
        app.load(update_lbs, inputs=[state], outputs=[daily_lb, normal_lb])
        
    return app
