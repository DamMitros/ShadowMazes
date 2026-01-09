import random

BOARD_SIZE = 10
MAX_MOVES = 5

class GameState:
  def __init__(self):
    # Plansze graczy: 0 - puste, 1 - ściana, 2 - skarb, 3 - start
    self.boards = {
      0: [[0 for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)],
      1: [[0 for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
    }
    self.positions = {
      0: (0, 0),
      1: (0, 0)
    }
    self.turn = 0
    self.winner = None
    self.moves_counter = 0

  def generate_random_board(self, player_id):
    while True:
      grid = [[1 for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]

      cx, cy = 0, 0
      grid[cy][cx] = 0
      path = [(cx, cy)]

      success = False
      for _ in range(29):
        neighbors = []
        for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
          nx, ny = cx + dx, cy + dy
          if 0 <= nx < BOARD_SIZE and 0 <= ny < BOARD_SIZE:
            if grid[ny][nx] == 1:
              neighbors.append((nx, ny))
        
        if not neighbors:
          break
        
        cx, cy = random.choice(neighbors)
        grid[cy][cx] = 0
        path.append((cx, cy))

      if len(path) == 30:
        ex, ey = path[-1]
        if ex == 0 or ex == BOARD_SIZE-1 or ey == 0 or ey == BOARD_SIZE-1:
          grid[ey][ex] = 2
          self.boards[player_id] = grid
          print(f"[GAME] Generated valid board for Player {player_id}")
          return

  def validate_move(self, player_id, direction):
    if self.winner is not None:
      return {"status": "GAME_OVER", "winner": self.winner}

    if player_id != self.turn:
      return {"status": "NOT_YOUR_TURN", "next_turn": self.turn}

    x, y = self.positions[player_id]
    new_x, new_y = x, y

    if direction == "UP": new_y -= 1
    elif direction == "DOWN": new_y += 1
    elif direction == "LEFT": new_x -= 1
    elif direction == "RIGHT": new_x += 1

    if not (0 <= new_x < BOARD_SIZE and 0 <= new_y < BOARD_SIZE):
      self.change_turn()
      return {"status": "WALL_HIT", "x": x, "y": y, "next_turn": self.turn}
    
    opponent_id = 1 if player_id == 0 else 0
    cell_type = self.boards[opponent_id][new_y][new_x]

    if cell_type == 1:
      self.change_turn()
      return {"status": "WALL_HIT", "x": x, "y": y, "next_turn": self.turn}
    
    self.positions[player_id] = (new_x, new_y)
    self.moves_counter += 1
    
    if cell_type == 2:
      self.winner = player_id
      return {"status": "TREASURE_FOUND", "winner": player_id, "x": new_x, "y": new_y, "next_turn": self.turn}

    status = "MOVED"
    if self.moves_counter >= MAX_MOVES:
      self.change_turn()

    return {"status": status, "x": new_x, "y": new_y, "next_turn": self.turn}

  def change_turn(self):
    self.turn = 1 if self.turn == 0 else 0
    self.moves_counter = 0