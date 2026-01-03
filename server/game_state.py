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
    grid = [[1 for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
    stack = [(0, 0)]
    grid[0][0] = 0
    
    while stack:
      cx, cy = stack[-1]
      neighbors = []
      for dx, dy in [(-2, 0), (2, 0), (0, -2), (0, 2)]:
        nx, ny = cx + dx, cy + dy
        if 0 <= nx < BOARD_SIZE and 0 <= ny < BOARD_SIZE and grid[ny][nx] == 1:
          neighbors.append((nx, ny, dx // 2, dy // 2))
      
      if neighbors:
        nx, ny, hx, hy = random.choice(neighbors)
        grid[ny][nx] = 0
        grid[cy + hy][cx + hx] = 0
        stack.append((nx, ny))
      else:
        stack.pop()

    for _ in range(int(BOARD_SIZE * BOARD_SIZE * 0.1)):
      rx, ry = random.randint(0, BOARD_SIZE-1), random.randint(0, BOARD_SIZE-1)
      if grid[ry][rx] == 1:
        grid[ry][rx] = 0

    while True:
      tx, ty = random.randint(5, 9), random.randint(5, 9)
      if grid[ty][tx] == 0:
        grid[ty][tx] = 2
        break

    grid[0][0] = 0 
    self.boards[player_id] = grid

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