import socket, threading, json, sys, os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from common.constants import HOST, PORT, BUFFER_SIZE

class GameClient:
  def __init__(self, message_callback, disconnect_callback):
    self.sock = None
    self.running = False
    self.message_callback = message_callback
    self.disconnect_callback = disconnect_callback

  def connect(self):
    try:
      self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      self.sock.connect((HOST, PORT))
      self.running = True
      threading.Thread(target=self._listen, daemon=True).start()
      return True
    except Exception as e:
      print(f"[NET ERROR] {e}")
      return False

  def send(self, msg_type, payload=None):
    if not self.running or not self.sock: return
    
    msg = {"type": msg_type}
    if payload:
      msg.update(payload)
      
    try:
      data = json.dumps(msg).encode('utf-8')
      self.sock.sendall(data)
    except Exception as e:
      print(f"[SEND ERROR] {e}")

  def _listen(self):
    while self.running:
      try:
        data = self.sock.recv(BUFFER_SIZE)
        if not data: break

        decoded = data.decode('utf-8')
        for part in decoded.split('}{'):
          if not part.startswith('{'): part = '{' + part
          if not part.endswith('}'): part = part + '}'
          try:
            msg = json.loads(part)
            self.message_callback(msg)
          except: pass
      except: break
    
    self.running = False
    self.disconnect_callback()
    if self.sock: self.sock.close()