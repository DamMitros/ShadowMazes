import tkinter as tk, sys, os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from common.constants import STYLE, COLORS

class ScreenManager:
  def __init__(self, root):
    self.root = root
    self.current_overlay = None

  def clear(self):
    if self.current_overlay:
      self.current_overlay.destroy()
      self.current_overlay = None

  def _create_base_overlay(self):
    self.clear()
    self.current_overlay = tk.Frame(self.root, bg="#050505")
    self.current_overlay.place(relx=0, rely=0, relwidth=1, relheight=1)
    self.current_overlay.bind("<Button-1>", lambda e: "break")
    return self.current_overlay

  def _create_center_frame(self, parent, bg_color="#140f0f"):
    frame = tk.Frame(parent, bg=bg_color, bd=2, relief="solid")
    frame.place(relx=0.5, rely=0.5, anchor="center")
    return frame

  def _add_action_buttons(self, parent):
    btn_frame = tk.Frame(parent, bg="#140f0f")
    btn_frame.pack(pady=20)

    tk.Button(btn_frame, text="EXIT", command=self.root.destroy,
              bg="#333", fg="white", font=("Segoe UI", 12), relief="flat", padx=20, pady=5)\
              .pack(side="left", padx=10)

    tk.Button(btn_frame, text="RESTART APP", 
              command=lambda: os.execl(sys.executable, sys.executable, *sys.argv),
              bg=STYLE["accent_orange"], fg="black", font=("Segoe UI", 12, "bold"), 
              relief="flat", padx=20, pady=5).pack(side="left", padx=10)

  def show_lobby(self, player_id):
    overlay = self._create_base_overlay()
    overlay.configure(bg=STYLE["bg_dark"])
    
    center = tk.Frame(overlay, bg=STYLE["bg_dark"])
    center.place(relx=0.5, rely=0.5, anchor="center")

    tk.Label(center, text="SHADOW MAZES", font=("Courier New", 50, "bold"), 
             fg=STYLE["accent_orange"], bg=STYLE["bg_dark"]).pack(pady=(0, 10))

    tk.Label(center, text="MULTIPLAYER LOBBY", font=("Segoe UI", 16, "bold"), 
             fg="#444", bg=STYLE["bg_dark"]).pack(pady=(0, 40))

    status_frame = tk.Frame(center, bg="#1a1a1a", padx=40, pady=20, bd=1, relief="solid")
    status_frame.pack()

    tk.Label(status_frame, text=f"CONNECTED AS PLAYER {player_id}", 
             font=("Consolas", 12), fg=STYLE["accent_purple"], bg="#1a1a1a").pack()

    tk.Label(status_frame, text="WAITING FOR OPPONENT...", 
             font=("Segoe UI", 14), fg="#fff", bg="#1a1a1a").pack(pady=(10, 0))

    tk.Label(center, text="Game will start automatically when player 2 connects.", 
             font=("Segoe UI", 10, "italic"), fg="#666", bg=STYLE["bg_dark"]).pack(pady=30)

  def show_game_over(self, is_victory, reason=None):
    overlay = self._create_base_overlay()
    center = self._create_center_frame(overlay)

    txt = "VICTORY!" if is_victory else "DEFEAT"
    color = COLORS["treasure_gold"] if is_victory else STYLE["accent_alert"]
    
    if reason == "OPPONENT_DISCONNECTED":
      sub_txt = "Opponent surrendered (Disconnected)."
    else:
      sub_txt = "You found the treasure!" if is_victory else "Enemy found your treasure."

    tk.Label(center, text=txt, fg=color, bg="#140f0f", 
             font=("Courier New", 40, "bold")).pack(padx=60, pady=(40, 10))
    
    tk.Label(center, text=sub_txt, fg=STYLE["text_main"], bg="#140f0f",
             font=STYLE["font_main"]).pack(pady=(0, 30))

    self._add_action_buttons(center)

  def show_disconnect(self):
    overlay = self._create_base_overlay()
    center = self._create_center_frame(overlay)

    tk.Label(center, text="CONNECTION LOST", fg=STYLE["accent_alert"], bg="#140f0f", 
             font=("Courier New", 30, "bold")).pack(padx=40, pady=(30, 10))
    
    tk.Label(center, text="Server disconnected or unreachable.", fg="#888", bg="#140f0f",
             font=STYLE["font_main"]).pack(pady=(0, 30))

    self._add_action_buttons(center)