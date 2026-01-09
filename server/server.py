import socket, threading, json, time, random

from game_state import GameState
from request_handler import RequestHandler

HOST = '127.0.0.1' 
PORT = 65432
MAX_PLAYERS = 2

class MazeServer:
  def __init__(self):
    self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    self.server_socket.bind((HOST, PORT))
    self.server_socket.listen(MAX_PLAYERS)
    
    self.clients = []
    self.lock = threading.Lock()
    self.game = None
    self.game_running = False
    self.handler = RequestHandler(self)
    
    print(f"[START] Server listening on {HOST}:{PORT}")

  def _broadcast_internal(self, message, exclude_client=None):
    json_msg = json.dumps(message)
    for client in self.clients[:]: 
      if client != exclude_client:
        try:
          client.sendall(json_msg.encode('utf-8'))
        except:
          pass

  def broadcast(self, message, exclude_client=None):
    with self.lock:
      self._broadcast_internal(message, exclude_client)

  def send_to_client(self, client, message):
    try:
      client.sendall(json.dumps(message).encode('utf-8'))
    except:
      pass
    
  def handle_client(self, conn, addr, player_id):
    print(f"[CONNECTION] Player {player_id} connected from {addr}")
    
    welcome_msg = {"type": "CONNECTED", "player_id": player_id}
    self.send_to_client(conn, welcome_msg)

    try:
      while True:
        try:
          data = conn.recv(2048)
          if not data:
            raise ConnectionResetError("Empty data")
        
        except ConnectionResetError:
          print(f"[DISCONNECT] Player {player_id} disconnected unexpectedly.")
          with self.lock:
            if self.game_running:
              winner_id = 1 if player_id == 0 else 0
              print(f"[GAME OVER] Walkover! Winner: Player {winner_id}")
              walkover_msg = {
                "type": "GAME_OVER",
                "winner": winner_id,
                "reason": "OPPONENT_DISCONNECTED"
              }
              self._broadcast_internal(walkover_msg, exclude_client=conn)
              self.game_running = False 
          break
        
        except OSError:
          break 

        try:
          msg = json.loads(data.decode('utf-8'))
          self.handler.handle_message(msg, player_id, conn)

        except json.JSONDecodeError:
          print(f"[ERROR] Invalid JSON from player {player_id}")

    except Exception as e:
        print(f"[ERROR] Unexpected error in handler: {e}")
    finally:
      with self.lock:
        if conn in self.clients:
          self.clients.remove(conn)
      try:
        conn.close()
      except:
        pass
      print(f"[EXIT] Thread for Player {player_id} finished.")

  def start_round(self):
    print("[GAME] Generating maps for new round...")
    with self.lock:
      self.game = GameState()
      self.game.generate_random_board(0)
      self.game.generate_random_board(1)
      self.game.turn = random.choice([0, 1])
      self.game_running = True
      current_turn = self.game.turn

    with self.lock:
      for i, client in enumerate(self.clients):
        if i < 2:
          start_msg = {
            "type": "GAME_START",
            "turn": current_turn,
            "my_board": self.game.boards[i],
            "board_size": 10
          }
          self.send_to_client(client, start_msg)

    print(f"[GAME] Round started. Turn: Player {current_turn}")

    while self.game_running:
      with self.lock:
        if len(self.clients) < 2:
          print("[GAME] Player disconnected during game. Aborting round.")
          self.game_running = False
          break
      time.sleep(0.1)

    print("[GAME] Round finished. Preparing for restart...")
    time.sleep(2.0)
    
    with self.lock:
      for client in self.clients:
        try:
          client.close()
        except:
          pass
      self.clients.clear()

  def start(self):
    while True:
      print("\n--- NEW SESSION: WAITING FOR PLAYERS ---")
      self.clients = []
      player_id = 0

      while len(self.clients) < MAX_PLAYERS:
        try:
          conn, addr = self.server_socket.accept()
          with self.lock:
            self.clients.append(conn)
          
          thread = threading.Thread(target=self.handle_client, args=(conn, addr, player_id))
          thread.daemon = True
          thread.start()
          
          player_id += 1
          print(f"[LOBBY] Active players: {len(self.clients)}/{MAX_PLAYERS}")
        except Exception as e:
          print(f"[ERROR] Accept error: {e}")

      print("[LOBBY] Max players reached. Starting in 1s...")
      time.sleep(1)

      self.start_round()

      print("[SESSION] Cleaning up before next match...")
      time.sleep(2)

if __name__ == "__main__":
  server = MazeServer()
  try:
    server.start()
  except KeyboardInterrupt:
    print("\n[SHUTDOWN] Server stopped manually.")