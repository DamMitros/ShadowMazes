import socket, threading, json, time

from game_state import GameState

HOST = '127.0.0.1' 
PORT = 65432
MAX_PLAYERS = 2

class MazeServer:
  def __init__(self):
    self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.server_socket.bind((HOST, PORT))
    self.server_socket.listen(MAX_PLAYERS)
    self.clients = []
    self.lock = threading.Lock()
    self.game = GameState()
    print(f"[START] Server listening on {HOST}:{PORT}")

  def broadcast(self, message, exclude_client=None):
    json_msg = json.dumps(message)
    with self.lock:
      for client in self.clients:
        if client != exclude_client:
          try:
            client.sendall(json_msg.encode('utf-8'))
          except:
            # self.clients.remove(client)
            pass

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
        data = conn.recv(1024)
        if not data:
          break
        
        try:
          msg = json.loads(data.decode('utf-8'))
          print(f"[MOVE] Player {player_id}: {msg}")

          if msg.get("type") == "MOVE":
            direction = msg.get("direction")
 
            with self.lock:
              result = self.game.validate_move(player_id, direction)
                        
            response = {"type": "MOVE_RESULT", "payload": result}
            self.send_to_client(conn, response)

            if result["status"] in ["MOVED", "WALL_HIT", "TREASURE_FOUND"]:
              opponent_msg = {
                "type": "OPPONENT_ACTION",
                "player_id": player_id,
                "result": result
              }
              self.broadcast(opponent_msg, exclude_client=conn)

            if result.get("status") == "TREASURE_FOUND":
              print(f"[GAME OVER] Winner: Player {player_id}")
              self.broadcast({"type": "GAME_OVER", "winner": player_id})
        except json.JSONDecodeError:
          print(f"[ERROR] Invalid JSON format from player {player_id}")

    except ConnectionResetError:
      print(f"[Error] Connection with player {player_id} lost")
    finally:
      conn.close()
      with self.lock:
        if conn in self.clients:
          self.clients.remove(conn)
      print(f"[THE END] Player {player_id} disconnected")

  def start_game_logic(self):
    print("[GAME] Initializing game boards")
    with self.lock:
      self.game.generate_random_board(0)
      self.game.generate_random_board(1)
      current_turn = self.game.turn

    start_msg = {
      "type": "GAME_START",
      "turn": current_turn,
      "board_size": 10
    }
    self.broadcast(start_msg)
    print(f"[GAME] Game started. Turn: Player {current_turn}")

  def start(self):
    player_id = 0
    while len(self.clients) < MAX_PLAYERS:
      conn, addr = self.server_socket.accept()
      with self.lock:
        self.clients.append(conn)
      
      thread = threading.Thread(target=self.handle_client, args=(conn, addr, player_id))
      thread.start()
      player_id += 1
      
      print(f"[INFO] Active players: {len(self.clients)}/{MAX_PLAYERS}")

    print("[INFO] Max players reached. Starting game.")
    time.sleep(1)
    self.start_game_logic()

    try:
      while True:
        time.sleep(1)
    except KeyboardInterrupt:
      print("\n[SHUTDOWN] Server stopping...")

if __name__ == "__main__":
  server = MazeServer()
  server.start()