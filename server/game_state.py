import random

BOARD_SIZE = 10
MAZE_LENGTH = 30
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

  def generate_random_board(self, player_id):
    # TODO: Zaimplementować prawdziwą generację labiryntu
    # Na razie tymczasowo
    self.boards[player_id] = [[0] * BOARD_SIZE for _ in range(BOARD_SIZE)]
    
    tx, ty = random.randint(0, 9), random.randint(0, 9)
    self.boards[player_id][ty][tx] = 2 

    for _ in range(20):
      wx, wy = random.randint(0, 9), random.randint(0, 9)
      if (wx, wy) != (tx, ty) and (wx, wy) != (0, 0):
        self.boards[player_id][wy][wx] = 1

  def validate_move(self, player_id, direction):
    if self.winner is not None:
      return {"status": "GAME_OVER", "winner": self.winner}

    if player_id != self.turn:
      return {"status": "NOT_YOUR_TURN"}

    x, y = self.positions[player_id]

    new_x, new_y = x, y
    if direction == "UP": new_y -= 1
    elif direction == "DOWN": new_y += 1
    elif direction == "LEFT": new_x -= 1
    elif direction == "RIGHT": new_x += 1

    if not (0 <= new_x < BOARD_SIZE and 0 <= new_y < BOARD_SIZE):
      return {"status": "BLOCKED", "x": x, "y": y}
    
    opponent_id = 1 if player_id == 0 else 0
    cell_type = self.boards[opponent_id][new_y][new_x]

    if cell_type == 1:
      self.turn = opponent_id
      return {"status": "WALL_HIT", "x": x, "y": y, "next_turn": self.turn}
    
    self.positions[player_id] = (new_x, new_y)
    
    if cell_type == 2:
      self.winner = player_id
      return {"status": "TREASURE_FOUND", "winner": player_id, "x": new_x, "y": new_y}

    return {"status": "MOVED", "x": new_x, "y": new_y}