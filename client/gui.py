import tkinter as tk, sys, os
from tkinter import messagebox

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from common.constants import STYLE
from common.protocol import *
from client import GameClient
from board import BoardRenderer
from input_handler import InputHandler
from screens import ScreenManager
from state import ClientGameState

class GameClientGUI:
  def __init__(self, root):
    self.root = root
    self.root.title("Shadow Mazes | Client")
    self.root.geometry("900x600")
    self.root.configure(bg=STYLE["bg_dark"])

    self.screens = ScreenManager(self.root)
    self.state = ClientGameState()
    self.client = GameClient(self._safe_handle_message, self._safe_on_disconnect)
    self.input = InputHandler(self.client, self)

    self._init_layout()
    self.input.bind_controls(self.root)
    self._connect()

  def _init_layout(self):
    hdr = tk.Frame(self.root, bg=STYLE["bg_dark"], pady=10)
    hdr.pack(fill="x", padx=20)
    tk.Label(hdr, text="SHADOW MAZES", font=STYLE["font_header"], 
             fg=STYLE["accent_orange"], bg=STYLE["bg_dark"]).pack(side="left")
    self.lbl_status = tk.Label(hdr, text="CONNECTING...", font=STYLE["font_main"], 
                               fg=STYLE["text_dim"], bg=STYLE["bg_dark"])
    self.lbl_status.pack(side="right")

    main = tk.Frame(self.root, bg=STYLE["bg_dark"])
    main.pack(expand=True, fill="both", padx=20, pady=10)

    game = tk.Frame(main, bg=STYLE["bg_panel"], bd=1, relief="solid")
    game.pack(side="left", expand=True, fill="both", padx=(0, 10))

    board_cont = tk.Frame(game, bg=STYLE["bg_panel"])
    board_cont.pack(expand=True, pady=20)

    def mk_sect(col, txt, color):
      f = tk.Frame(board_cont, bg=STYLE["bg_panel"])
      f.grid(row=0, column=col, padx=20)
      tk.Label(f, text=txt, fg=color, bg=STYLE["bg_panel"], font=STYLE["font_mono"]).pack(pady=5)
      c = tk.Canvas(f, width=302, height=302, bg="#000", highlightthickness=0)
      c.pack()
      return c

    self.canvas_def = mk_sect(0, "DEFENSE SECTOR", STYLE["text_dim"])
    tk.Label(board_cont, text="VS", fg="#333", bg=STYLE["bg_panel"], font=("Arial", 20)).grid(row=0, column=1)
    self.canvas_atk = mk_sect(2, "ATTACK RADAR", STYLE["accent_purple"])

    footer = tk.Frame(game, bg=STYLE["bg_panel"], pady=10)
    footer.pack(side="bottom", fill="x")
    self.lbl_steps = tk.Label(footer, text="ENERGY: 5/5", fg=STYLE["accent_orange"], 
                              bg=STYLE["bg_panel"], font=("Segoe UI", 12, "bold"))
    self.lbl_steps.pack()

    side = tk.Frame(main, bg=STYLE["bg_panel"], width=250)
    side.pack(side="right", fill="y")
    side.pack_propagate(False)
    tk.Label(side, text="CHAT", fg=STYLE["accent_orange"], bg=STYLE["bg_panel"], font=STYLE["font_mono"], pady=5).pack(fill="x")
    
    self.txt_log = tk.Text(side, bg="#050505", fg=STYLE["text_main"], font=STYLE["font_mono"], state="disabled", height=20, bd=0)
    self.txt_log.pack(expand=True, fill="both", padx=5, pady=5)
    self.txt_log.tag_config("sys", foreground="#00eaff")
    self.txt_log.tag_config("err", foreground="#ff3333")
    self.txt_log.tag_config("me", foreground=STYLE["accent_orange"])
    self.txt_log.tag_config("enemy", foreground=STYLE["accent_purple"])

    self.entry_chat = tk.Entry(side, bg="#222", fg="#fff", insertbackground="#fff", bd=0, font=STYLE["font_main"])
    self.entry_chat.pack(fill="x", padx=5, pady=10)

  def _connect(self):
    if self.client.connect():
      self.log("[SYS] Connected.", "sys")
    else:
      messagebox.showerror("Error", "Server not found!")
      self.root.destroy()

  def _safe_handle_message(self, msg):
    self.root.after(0, lambda: self.handle_message(msg))

  def _safe_on_disconnect(self):
    if not self.state.game_ended:
      self.root.after(0, self.screens.show_disconnect)

  def handle_message(self, msg):
    mtype = msg.get("type")
    
    if mtype == MSG_CONNECTED:
      self.state.player_id = msg.get("player_id")
      self.root.title(f"Shadow Mazes | Player {self.state.player_id}")
      self.log(f"[SYS] Connected to server as Player {self.state.player_id}.", "sys")
      self.screens.show_lobby(self.state.player_id)

    elif mtype == MSG_GAME_START:
      self.screens.clear()
      self.state.reset_for_new_game(msg.get("my_board"), msg.get("turn"))
      
      self.log("[SYS] Game Started!", "sys")
      self.update_ui()

    elif mtype == MSG_MOVE_RESULT:
      pl = msg.get("payload")
      st = pl.get("status")
      nx, ny = pl.get("x"), pl.get("y")
      
      self.state.update_attack_map(nx, ny, st)
      self.state.update_energy(st == STATUS_MOVED)
      
      if st == STATUS_WALL: self.log("Wall hit!", "err")
      elif st == STATUS_TREASURE: self.log("Treasure found!", "sys")

      self.state.check_turn_change(pl.get("next_turn"))
      self.update_ui()

    elif mtype == MSG_OPPONENT_ACTION:
      res = msg.get("result")

      ex = res.get("x")
      ey = res.get("y")

      if ex is not None and ey is not None:
        self.state.enemy_pos_def = [ex, ey]
      if res.get("status") == STATUS_WALL:
        self.log("Enemy hit wall.", "sys")
      
      self.state.check_turn_change(res.get("next_turn"))
      self.update_ui()

    elif mtype == MSG_CHAT:
      sender = msg.get("sender")
      tag = "me" if sender == self.state.player_id else "enemy"
      name = "You" if sender == self.state.player_id else "Enemy"
      self.log(f"<{name}> {msg.get('content')}", tag)

    elif mtype == MSG_GAME_OVER:
      w = msg.get("winner")
      reason = msg.get("reason")
      is_victory = (w == self.state.player_id)

      self.state.game_ended = True
      self.state.my_turn = False
      self.lbl_status.config(text="GAME OVER", fg="#fff")
      self.screens.show_game_over(is_victory, reason)
      self.log(f"GAME OVER. Winner: {w}", "sys")

  def update_ui(self):
    if self.state.my_turn:
      self.lbl_status.config(text="YOUR TURN", fg=STYLE["accent_orange"])
      self.canvas_atk.config(bg="#1a0505")
      self.canvas_def.config(bg="#000")
      self.lbl_steps.config(text=f"ENERGY: {self.state.steps_left}/5", fg=STYLE["accent_orange"])
    else:
      self.lbl_status.config(text="WAITING...", fg=STYLE["accent_alert"])
      self.canvas_atk.config(bg="#000")
      self.canvas_def.config(bg="#0a001a")
      self.lbl_steps.config(text="OPPONENT'S TURN", fg=STYLE["text_dim"])

    BoardRenderer.draw(self.canvas_def, self.state.my_def_grid, True, self.state.enemy_pos_def)
    BoardRenderer.draw(self.canvas_atk, self.state.my_atk_grid, False, self.state.my_pos_atk, self.state.pending_move)
    
  def log(self, msg, tag=None):
    self.txt_log.config(state="normal")
    self.txt_log.insert("end", msg+"\n", tag)
    self.txt_log.see("end")
    self.txt_log.config(state="disabled")

if __name__ == "__main__":
  root = tk.Tk()
  app = GameClientGUI(root)
  root.mainloop()