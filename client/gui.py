import tkinter as tk, sys, os
from tkinter import messagebox

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from common.constants import COLORS, STYLE
from common.protocol import *
from client import GameClient
from board import BoardRenderer
from input_handler import InputHandler

class GameClientGUI:
  def __init__(self, root):
    self.root = root
    self.root.title("Shadow Mazes | Client")
    self.root.geometry("900x600")
    self.root.configure(bg=STYLE["bg_dark"])

    self.client = GameClient(self._safe_handle_message, self._safe_on_disconnect)
    self.input = InputHandler(self.client, self)

    self.player_id = None
    self.my_turn = False
    self.steps_left = 5
    self.my_def_grid = [[0]*10 for _ in range(10)]
    self.my_atk_grid = [['?' for _ in range(10)] for _ in range(10)]
    self.my_pos_atk = [0, 0]
    self.enemy_pos_def = [0, 0]

    self.current_overlay = None
    self.game_ended = False

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
    if not self.game_ended:
      self.root.after(0, self.show_disconnect_screen)

  def handle_message(self, msg):
    mtype = msg.get("type")
    
    if mtype == MSG_CONNECTED:
      self.player_id = msg.get("player_id")
      self.root.title(f"Shadow Mazes | Player {self.player_id}")
      self.log(f"[SYS] Connected to server as Player {self.player_id}.", "sys")
      self.show_lobby_screen()

    elif mtype == MSG_GAME_START:
      self.game_ended = False
      self._clear_overlay()

      self.my_def_grid = msg.get("my_board")
      turn = msg.get("turn")
      self.my_turn = (turn == self.player_id)
      self.steps_left = 5
      self.my_atk_grid[0][0] = 0
      self.log("[SYS] Game Started!", "sys")
      self.update_ui()

    elif mtype == MSG_MOVE_RESULT:
      pl = msg.get("payload")
      st = pl.get("status")
      nx, ny = pl.get("x"), pl.get("y")
      
      if st == STATUS_MOVED:
        self.my_pos_atk = [nx, ny]
        self.my_atk_grid[ny][nx] = 0
        self.steps_left -= 1
      elif st == STATUS_WALL:
        self.my_atk_grid[ny][nx] = 1
        self.log("Wall hit!", "err")
      elif st == STATUS_TREASURE:
        self.my_atk_grid[ny][nx] = 2
        self.my_pos_atk = [nx, ny]
        self.log("Treasure found!", "sys")

      self._check_turn(pl.get("next_turn"))
      self.update_ui()

    elif mtype == MSG_OPPONENT_ACTION:
      res = msg.get("result")
      if res.get("status") == STATUS_WALL:
        self.log("Enemy hit wall.", "sys")
      self._check_turn(res.get("next_turn"))
      self.update_ui()

    elif mtype == MSG_CHAT:
      sender = msg.get("sender")
      tag = "me" if sender == self.player_id else "enemy"
      name = "You" if sender == self.player_id else "Enemy"
      self.log(f"<{name}> {msg.get('content')}", tag)

    elif mtype == MSG_GAME_OVER:
      w = msg.get("winner")
      reason = msg.get("reason")
      is_victory = (w == self.player_id)

      self.game_ended = True
      self.my_turn = False
      self.lbl_status.config(text="GAME OVER", fg="#fff")
      self.show_game_over_screen(is_victory, reason)
      self.log(f"GAME OVER. Winner: {w}", "sys")

  def _check_turn(self, next_turn):
    if next_turn is not None:
      new_mine = (next_turn == self.player_id)
      if self.my_turn and not new_mine: self.log("Turn ended.", "sys")
      self.my_turn = new_mine
      if self.my_turn:
        self.steps_left = 5
        self.log("YOUR TURN!", "sys")

  def update_ui(self):
    if self.my_turn:
      self.lbl_status.config(text="YOUR TURN", fg=STYLE["accent_orange"])
      self.canvas_atk.config(bg="#1a0505")
      self.canvas_def.config(bg="#000")
      self.lbl_steps.config(text=f"ENERGY: {self.steps_left}/5", fg=STYLE["accent_orange"])
    else:
      self.lbl_status.config(text="WAITING...", fg=STYLE["accent_alert"])
      self.canvas_atk.config(bg="#000")
      self.canvas_def.config(bg="#0a001a")
      self.lbl_steps.config(text="OPPONENT'S TURN", fg=STYLE["text_dim"])

    BoardRenderer.draw(self.canvas_def, self.my_def_grid, True, self.enemy_pos_def)
    BoardRenderer.draw(self.canvas_atk, self.my_atk_grid, False, self.my_pos_atk)

  def _clear_overlay(self):
    if self.current_overlay:
      self.current_overlay.destroy()
      self.current_overlay = None

  def show_lobby_screen(self):
    self._clear_overlay()

    self.current_overlay = tk.Frame(self.root, bg=STYLE["bg_dark"])
    self.current_overlay.place(relx=0, rely=0, relwidth=1, relheight=1)
    self.current_overlay.bind("<Button-1>", lambda e: "break")

    center = tk.Frame(self.current_overlay, bg=STYLE["bg_dark"])
    center.place(relx=0.5, rely=0.5, anchor="center")

    tk.Label(center, text="SHADOW MAZES", font=("Courier New", 50, "bold"), 
             fg=STYLE["accent_orange"], bg=STYLE["bg_dark"]).pack(pady=(0, 10))

    tk.Label(center, text="MULTIPLAYER LOBBY", font=("Segoe UI", 16, "bold"), 
             fg="#444", bg=STYLE["bg_dark"]).pack(pady=(0, 40))

    status_frame = tk.Frame(center, bg="#1a1a1a", padx=40, pady=20, bd=1, relief="solid")
    status_frame.pack()

    tk.Label(status_frame, text="CONNECTED AS PLAYER " + str(self.player_id), 
             font=("Consolas", 12), fg=STYLE["accent_purple"], bg="#1a1a1a").pack()

    tk.Label(status_frame, text="WAITING FOR OPPONENT...", 
             font=("Segoe UI", 14), fg="#fff", bg="#1a1a1a").pack(pady=(10, 0))

    tk.Label(center, text="Game will start automatically when player 2 connects.", 
             font=("Segoe UI", 10, "italic"), fg="#666", bg=STYLE["bg_dark"]).pack(pady=30)

  def show_game_over_screen(self, is_victory, reason=None):
    self._clear_overlay()

    self.current_overlay = tk.Frame(self.root, bg="#050505")
    self.current_overlay.place(relx=0, rely=0, relwidth=1, relheight=1)
    self.current_overlay.bind("<Button-1>", lambda e: "break")

    center_frame = tk.Frame(self.current_overlay, bg="#140f0f", bd=2, relief="solid")
    center_frame.place(relx=0.5, rely=0.5, anchor="center")
    
    txt = "VICTORY!" if is_victory else "DEFEAT"
    color = COLORS["treasure_gold"] if is_victory else STYLE["accent_alert"]
    
    if reason == "OPPONENT_DISCONNECTED":
        sub_txt = "Opponent surrendered (Disconnected)."
    else:
        sub_txt = "You found the treasure!" if is_victory else "Enemy found your treasure."
    
    tk.Label(center_frame, text=txt, fg=color, bg="#140f0f", 
            font=("Courier New", 40, "bold")).pack(padx=60, pady=(40, 10))
    
    tk.Label(center_frame, text=sub_txt, fg=STYLE["text_main"], bg="#140f0f",
            font=STYLE["font_main"]).pack(pady=(0, 30))

    btn_frame = tk.Frame(center_frame, bg="#140f0f")
    btn_frame.pack(pady=20)

    tk.Button(btn_frame, text="EXIT GAME", command=self.root.destroy,
              bg="#333", fg="white", font=("Segoe UI", 12), relief="flat", padx=20, pady=5)\
              .pack(side="left", padx=10)

    tk.Button(btn_frame, text="RESTART APP", 
              command=lambda: os.execl(sys.executable, sys.executable, *sys.argv),
              bg=STYLE["accent_orange"], fg="black", font=("Segoe UI", 12, "bold"), 
              relief="flat", padx=20, pady=5).pack(side="left", padx=10)
    
  def show_disconnect_screen(self):
    self._clear_overlay()

    self.current_overlay = tk.Frame(self.root, bg="#050505")
    self.current_overlay.place(relx=0, rely=0, relwidth=1, relheight=1)
    self.current_overlay.bind("<Button-1>", lambda e: "break")

    center = tk.Frame(self.current_overlay, bg="#140f0f", bd=2, relief="solid")
    center.place(relx=0.5, rely=0.5, anchor="center")

    tk.Label(center, text="CONNECTION LOST", fg=STYLE["accent_alert"], bg="#140f0f", 
             font=("Courier New", 30, "bold")).pack(padx=40, pady=(30, 10))
    
    tk.Label(center, text="Server disconnected or unreachable.", fg="#888", bg="#140f0f",
             font=STYLE["font_main"]).pack(pady=(0, 30))

    btn_frame = tk.Frame(center, bg="#140f0f")
    btn_frame.pack(pady=20)

    tk.Button(btn_frame, text="EXIT", command=self.root.destroy,
              bg="#333", fg="white", font=("Segoe UI", 12), relief="flat", padx=20, pady=5)\
              .pack(side="left", padx=10)

    tk.Button(btn_frame, text="RESTART APP", 
              command=lambda: os.execl(sys.executable, sys.executable, *sys.argv),
              bg=STYLE["accent_orange"], fg="black", font=("Segoe UI", 12, "bold"), 
              relief="flat", padx=20, pady=5).pack(side="left", padx=10)
    
  def log(self, msg, tag=None):
    self.txt_log.config(state="normal")
    self.txt_log.insert("end", msg+"\n", tag)
    self.txt_log.see("end")
    self.txt_log.config(state="disabled")

if __name__ == "__main__":
  root = tk.Tk()
  app = GameClientGUI(root)
  root.mainloop()