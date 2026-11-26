import math
import random
import gradio as gr


def is_winner(b, player):
  win_combos = [
      [0, 1, 2],
      [3, 4, 5],
      [6, 7, 8],
      [0, 3, 6],
      [1, 4, 7],
      [2, 5, 8],
      [0, 4, 8],
      [2, 4, 6],
  ]
  return any(
      b[c[0]] == b[c[1]] == b[c[2]] == player for c in win_combos
  )


def is_board_full(b):
  return " " not in b


def get_empty_cells(b):
  return [i for i, cell in enumerate(b) if cell == " "]


def minimax(b, depth, alpha, beta, is_maximizing, ai_sym, player_sym):
  if is_winner(b, ai_sym):
    return 10 - depth
  if is_winner(b, player_sym):
    return depth - 10
  if is_board_full(b):
    return 0

  if is_maximizing:
    max_eval = -math.inf
    for cell in get_empty_cells(b):
      b[cell] = ai_sym
      eval_score = minimax(
          b, depth + 1, alpha, beta, False, ai_sym, player_sym
      )
      b[cell] = " "
      max_eval = max(max_eval, eval_score)
      alpha = max(alpha, eval_score)
      if beta <= alpha:
        break
    return max_eval
  else:
    min_eval = math.inf
    for cell in get_empty_cells(b):
      b[cell] = player_sym
      eval_score = minimax(
          b, depth + 1, alpha, beta, True, ai_sym, player_sym
      )
      b[cell] = " "
      min_eval = min(min_eval, eval_score)
      beta = min(beta, eval_score)
      if beta <= alpha:
        break
    return min_eval


def best_move(b, ai_sym, player_sym):
  best_val = -math.inf
  move = -1
  for cell in get_empty_cells(b):
    b[cell] = ai_sym
    eval_score = minimax(b, 0, -math.inf, math.inf, False, ai_sym, player_sym)
    b[cell] = " "
    if eval_score > best_val:
      best_val = eval_score
      move = cell
  return move


def format_score(scores, player_sym):
  return f"""
    <div class="scoreboard">
        <div class="score-box player">Ти ({player_sym}): <span>{scores['Ti']}</span></div>
        <div class="score-box draw">Равенства: <span>{scores['D']}</span></div>
        <div class="score-box ai">Бот: <span>{scores['Bot']}</span></div>
    </div>
    """


def format_status(text, state_type="info"):
  return f'<div class="status-banner {state_type}">{text}</div>'


def handle_click(index, board, game_over, scores, player_sym, ai_sym):
  if game_over or board[index] != " ":
    return (
        board,
        game_over,
        scores,
        player_sym,
        ai_sym,
        format_status(
            "Избери свободна клетка или натисни Нова игра!", "warning"
        ),
        format_score(scores, player_sym),
        *[gr.update(value=c) for c in board],
    )

  board[index] = player_sym
  if is_winner(board, player_sym):
    scores["Ti"] += 1
    return (
        board,
        True,
        scores,
        player_sym,
        ai_sym,
        format_status("🎉 Честито! Ти победи.", "win"),
        format_score(scores, player_sym),
        *[gr.update(value=c) for c in board],
    )
  if is_board_full(board):
    scores["D"] += 1
    return (
        board,
        True,
        scores,
        player_sym,
        ai_sym,
        format_status("🤝 Равенство! Добра игра.", "draw"),
        format_score(scores, player_sym),
        *[gr.update(value=c) for c in board],
    )

  ai_idx = best_move(board, ai_sym, player_sym)
  board[ai_idx] = ai_sym
  if is_winner(board, ai_sym):
    scores["Bot"] += 1
    return (
        board,
        True,
        scores,
        player_sym,
        ai_sym,
        format_status("🤖 Ботът спечели! Опитай отново.", "lose"),
        format_score(scores, player_sym),
        *[gr.update(value=c) for c in board],
    )
  if is_board_full(board):
    scores["D"] += 1
    return (
        board,
        True,
        scores,
        player_sym,
        ai_sym,
        format_status("🤝 Равенство! Добра игра.", "draw"),
        format_score(scores, player_sym),
        *[gr.update(value=c) for c in board],
    )

  return (
      board,
      False,
      scores,
      player_sym,
      ai_sym,
      format_status(f"Твой ред е ({player_sym}) — избери клетка", "info"),
      format_score(scores, player_sym),
      *[gr.update(value=c) for c in board],
  )


def reset_game(scores):
  empty_board = [" "] * 9
  player_sym = random.choice(["X", "O"])
  ai_sym = "O" if player_sym == "X" else "X"

  if ai_sym == "X":
    ai_idx = best_move(empty_board, ai_sym, player_sym)
    empty_board[ai_idx] = ai_sym
    status_msg = (
        f"Нова игра! Ботът е (X) и започна пръв. Сега е твой ред ({player_sym})."
    )
  else:
    status_msg = f"Нова игра! Вие сте ({player_sym}) и започвате пръв."

  return (
      empty_board,
      False,
      scores,
      player_sym,
      ai_sym,
      format_status(status_msg, "info"),
      format_score(scores, player_sym),
      *[gr.update(value=c) for c in empty_board],
  )


custom_css = """
body, .gradio-container {
    background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%) !important;
    font-family: 'Segoe UI', system-ui, sans-serif !important;
}
.main-card {
    max-width: 440px !important;
    margin: 20px auto !important;
    background: rgba(30, 41, 59, 0.85) !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    border-radius: 24px !important;
    padding: 28px !important;
    box-shadow: 0 20px 50px rgba(0, 0, 0, 0.5) !important;
}
.header-title {
    text-align: center;
    color: #f8fafc;
    margin-bottom: 4px;
    font-size: 26px;
    font-weight: 800;
}
.header-sub {
    text-align: center;
    color: #94a3b8;
    font-size: 13px;
    margin-bottom: 20px;
}
.scoreboard {
    display: flex;
    justify-content: space-between;
    gap: 10px;
    margin-bottom: 18px;
}
.score-box {
    flex: 1;
    background: #0f172a;
    border-radius: 12px;
    padding: 10px 8px;
    text-align: center;
    color: #cbd5e1;
    font-size: 13px;
    font-weight: 600;
    border: 1px solid rgba(255,255,255,0.06);
}
.score-box span {
    display: block;
    font-size: 20px;
    font-weight: 800;
    margin-top: 2px;
}
.score-box.player span { color: #38bdf8; }
.score-box.draw span { color: #94a3b8; }
.score-box.ai span { color: #f43f5e; }
.status-banner {
    text-align: center;
    padding: 12px;
    border-radius: 12px;
    font-weight: 600;
    font-size: 15px;
    margin-bottom: 18px;
}
.status-banner.info { background: rgba(56, 189, 248, 0.15); color: #7dd3fc; border: 1px solid rgba(56, 189, 248, 0.3); }
.status-banner.win { background: rgba(34, 197, 94, 0.2); color: #86efac; border: 1px solid rgba(34, 197, 94, 0.4); }
.status-banner.lose { background: rgba(244, 63, 94, 0.2); color: #fda4af; border: 1px solid rgba(244, 63, 94, 0.4); }
.status-banner.draw { background: rgba(148, 163, 184, 0.2); color: #e2e8f0; border: 1px solid rgba(148, 163, 184, 0.3); }
.status-banner.warning { background: rgba(245, 158, 11, 0.2); color: #fcd34d; border: 1px solid rgba(245, 158, 11, 0.4); }
.board-row {
    gap: 10px !important;
    margin-bottom: 10px !important;
    justify-content: center !important;
}
.cell-btn {
    height: 100px !important;
    min-width: 100px !important;
    max-width: 100px !important;
    font-size: 42px !important;
    font-weight: 900 !important;
    border-radius: 16px !important;
    background: #0f172a !important;
    border: 2px solid #334155 !important;
    color: #f8fafc !important;
}
.cell-btn:hover {
    transform: translateY(-2px) !important;
    border-color: #38bdf8 !important;
    background: #1e293b !important;
}
.reset-btn {
    margin-top: 14px !important;
    height: 48px !important;
    border-radius: 12px !important;
    font-size: 16px !important;
    font-weight: 700 !important;
    background: linear-gradient(90deg, #0284c7, #2563eb) !important;
    border: none !important;
    color: white !important;
}
footer { display: none !important; }
"""

with gr.Blocks(css=custom_css, title="Морски шах") as demo:
  with gr.Column(elem_classes="main-card"):
    gr.HTML(
        "<div class='header-title'>Морски шах</div><div"
        " class='header-sub'>Алгоритъм Minimax с алфа-бета отсичане</div>"
    )

    board_state = gr.State([" "] * 9)
    game_over_state = gr.State(False)
    scores_state = gr.State({"Ti": 0, "Bot": 0, "D": 0})
    player_sym_state = gr.State("X")
    ai_sym_state = gr.State("O")

    score_html = gr.HTML(format_score({"Ti": 0, "Bot": 0, "D": 0}, "X"))
    status_html = gr.HTML(
        format_status("Натисни 'Нова игра' за начало", "info")
    )

    buttons = []
    for row in range(3):
      with gr.Row(elem_classes="board-row"):
        for col in range(3):
          btn = gr.Button(value=" ", elem_classes="cell-btn")
          buttons.append(btn)

    for idx, btn in enumerate(buttons):
      btn.click(
          fn=lambda b, g, s, p, a, i=idx: handle_click(i, b, g, s, p, a),
          inputs=[
              board_state,
              game_over_state,
              scores_state,
              player_sym_state,
              ai_sym_state,
          ],
          outputs=[
              board_state,
              game_over_state,
              scores_state,
              player_sym_state,
              ai_sym_state,
              status_html,
              score_html,
              *buttons,
          ],
      )

    reset_btn = gr.Button("Нова игра", elem_classes="reset-btn")
    reset_btn.click(
        fn=reset_game,
        inputs=[scores_state],
        outputs=[
            board_state,
            game_over_state,
            scores_state,
            player_sym_state,
            ai_sym_state,
            status_html,
            score_html,
            *buttons,
        ],
    )

demo.launch(share=True)