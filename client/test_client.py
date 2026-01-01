import socket, threading, json, sys

HOST = '127.0.0.1'
PORT = 65432

class TestClient:
  def __init__(self):
    try:
      self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      self.sock.connect((HOST, PORT))
      print(f"[CONNECTED] Established connection to server {HOST}:{PORT}")
    except ConnectionRefusedError:
      print("[ERROR] Cannot connect to server. Make sure server.py is running.")
      sys.exit()

  def receive_messages(self):
    while True:
      try:
        data = self.sock.recv(1024)
        if not data:
          print("\n[DISCONNECTED] Server closed the connection.")
          self.sock.close()
          sys.exit()
        
        try:
          message = json.loads(data.decode('utf-8'))
          print(f"\n[SERWER]: {message}")
          print("Your move (JSON) > ", end='', flush=True)
        except json.JSONDecodeError:
          print(f"\n[RAW DATA]: {data.decode('utf-8')}")

      except OSError:
        break

  def start(self):
    recv_thread = threading.Thread(target=self.receive_messages, daemon=True)
    recv_thread.start()

    print("Write a message (e.g., move) and press ENTER. Type 'exit' to quit.")

    while True:
      msg_input = input("Your move (JSON) > ")
      
      if msg_input.lower() == 'exit':
        break
      
      try:
        json.loads(msg_input) 
        msg_to_send = msg_input
      except json.JSONDecodeError:
        msg_to_send = json.dumps({"type": "CHAT", "content": msg_input})

      try:
        self.sock.sendall(msg_to_send.encode('utf-8'))
      except BrokenPipeError:
        print("[ERROR] Connection lost.")
        break

    self.sock.close()
    print("[THE END] Client closed.")

if __name__ == "__main__":
  client = TestClient()
  client.start()