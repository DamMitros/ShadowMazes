class RequestHandler:
  def __init__(self, server_ref):
    self.server = server_ref

  def handle_message(self, msg, player_id, conn):
    msg_type = msg.get("type")
    
    if msg_type == "MOVE":
      return self._handle_move(msg, player_id, conn)
    elif msg_type == "CHAT":
      return self._handle_chat(msg, player_id, conn)
    
    return True

  def _handle_move(self, msg, player_id, conn):
    if not self.server.game_running:
      return True

    direction = msg.get("direction")
    print(f"[MOVE] Player {player_id}: {direction}")

    with self.server.lock:
      if not self.server.game_running: return True
      if self.server.game:
        result = self.server.game.validate_move(player_id, direction)
      else:
        return True

    response = {"type": "MOVE_RESULT", "payload": result}
    self.server.send_to_client(conn, response)
    status = result["status"]

    if status in ["MOVED", "WALL_HIT", "TREASURE_FOUND"]:
      opponent_msg = {
        "type": "OPPONENT_ACTION",
        "player_id": player_id,
        "result": result
      }
      self.server.broadcast(opponent_msg, exclude_client=conn)

    if status == "TREASURE_FOUND":
      print(f"[GAME OVER] Winner: Player {player_id}")
      self.server.broadcast({"type": "GAME_OVER", "winner": player_id})
      with self.server.lock:
        self.server.game_running = False
    
    return True

  def _handle_chat(self, msg, player_id, conn):
    print(f"[CHAT] Player {player_id}: {msg.get('content')}")
    chat_msg = {
      "type": "CHAT",
      "sender": player_id,
      "content": msg.get("content")
    }
    self.server.broadcast(chat_msg, exclude_client=conn)
    return True
  