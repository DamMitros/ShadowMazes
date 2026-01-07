import sys, os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from common.protocol import MSG_MOVE, MSG_CHAT

class InputHandler:
  def __init__(self, client_network, gui_ref):
    self.net = client_network
    self.gui = gui_ref

  def bind_controls(self, root):
    root.bind("<Up>", lambda e: self.send_move("UP"))
    root.bind("<Down>", lambda e: self.send_move("DOWN"))
    root.bind("<Left>", lambda e: self.send_move("LEFT"))
    root.bind("<Right>", lambda e: self.send_move("RIGHT"))

    self.gui.entry_chat.bind("<Return>", self.send_chat)

  def send_move(self, direction):
    if self.gui.state.my_turn and self.gui.state.steps_left > 0:
      self.net.send(MSG_MOVE, {"direction": direction})

  def send_chat(self, event=None):
    txt = self.gui.entry_chat.get()
    if txt:
      self.net.send(MSG_CHAT, {"content": txt})
      self.gui.log(f"<You> {txt}", "me")
      self.gui.entry_chat.delete(0, "end")