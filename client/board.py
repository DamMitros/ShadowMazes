import sys, os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from common.constants import STYLE, COLORS

class BoardRenderer:
  @staticmethod
  def draw(canvas, grid, is_defense, player_pos):
    canvas.delete("all")
    cs = STYLE["cell_size"]
    
    for y in range(10):
      for x in range(10):
        x1, y1 = x * cs, y * cs
        x2, y2 = x1 + cs, y1 + cs
        val = grid[y][x]
        
        BoardRenderer._draw_cell(canvas, x1, y1, x2, y2, val, is_defense, cs)

    if not is_defense:
      BoardRenderer._draw_player(canvas, player_pos, cs)

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
  def _draw_player(canvas, pos, cs):
    px, py = pos[0] * cs, pos[1] * cs
    canvas.create_oval(px+4, py+4, px+cs-4, py+cs-4, 
                       fill=STYLE["accent_orange"], outline="white", width=2)