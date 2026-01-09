import sys, os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from common.constants import STYLE, COLORS

class BoardRenderer:
  @staticmethod
  def draw(canvas, grid, is_defense, player_pos, pending_move=None):
    canvas.delete("all")
    cs = STYLE["cell_size"]
    
    for y in range(10):
      for x in range(10):
        x1, y1 = x * cs, y * cs
        x2, y2 = x1 + cs, y1 + cs
        val = grid[y][x]
        BoardRenderer._draw_cell(canvas, x1, y1, x2, y2, val, is_defense, cs)

    color = STYLE["accent_purple"] if is_defense else STYLE["accent_orange"]
    BoardRenderer._draw_player(canvas, player_pos, cs, color)

    if not is_defense and pending_move:
      BoardRenderer._draw_pending(canvas, player_pos, pending_move, cs)

  @staticmethod
  def _draw_cell(canvas, x1, y1, x2, y2, val, is_defense, cs):
    if is_defense:
      fill = COLORS["wall_def"] if val == 1 else COLORS["path_def"]
      canvas.create_rectangle(x1, y1, x2, y2, fill=fill, outline="#222")
      if val == 2:
        canvas.create_text(x1+cs/2, y1+cs/2, text="◈", fill=COLORS["treasure_glow"], font=("Arial", 14))
    else:
      if val == '?':
        canvas.create_rectangle(x1, y1, x2, y2, fill=COLORS["fog"], outline=COLORS["fog_line"])
        canvas.create_line(x1, y1, x2, y2, fill=COLORS["fog_line"])
      elif val == 1:
        canvas.create_rectangle(x1, y1, x2, y2, fill=COLORS["wall_atk"], outline="#f00")
      elif val == 0:
        canvas.create_rectangle(x1, y1, x2, y2, fill=COLORS["path_atk"], outline=STYLE["accent_purple"])
      elif val == 2:
        canvas.create_rectangle(x1, y1, x2, y2, fill=COLORS["path_atk"], outline=STYLE["accent_purple"])
        canvas.create_text(x1+cs/2, y1+cs/2, text="◈", fill=COLORS["treasure_gold"], font=("Arial", 14))

  @staticmethod
  def _draw_player(canvas, pos, cs, color):
    px, py = pos[0] * cs, pos[1] * cs
    canvas.create_oval(px+4, py+4, px+cs-4, py+cs-4, 
                      fill=color, outline="white", width=2)
  
  @staticmethod
  def _draw_pending(canvas, current_pos, direction, cs):
    dx, dy = 0, 0
    if direction == "UP": dy = -1
    elif direction == "DOWN": dy = 1
    elif direction == "LEFT": dx = -1
    elif direction == "RIGHT": dx = 1
    
    tx = current_pos[0] + dx
    ty = current_pos[1] + dy

    if 0 <= tx < 10 and 0 <= ty < 10:
      px, py = tx * cs, ty * cs
      canvas.create_oval(px+6, py+6, px+cs-6, py+cs-6, 
                         outline=STYLE["accent_orange"], width=3, dash=(4, 2))
      