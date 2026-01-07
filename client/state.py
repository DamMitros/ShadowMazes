from common.constants import BOARD_SIZE

class ClientGameState:
  def __init__(self):
    self.player_id = None
    self.my_turn = False
    self.steps_left = 5
    self.game_ended = False
    
    self.my_def_grid = [[0] * BOARD_SIZE for _ in range(BOARD_SIZE)]
    self.my_atk_grid = [['?' for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
    
    self.my_pos_atk = [0, 0]
    self.enemy_pos_def = [0, 0]

  def reset_for_new_game(self, my_board, start_turn):
    self.my_def_grid = my_board
    self.my_turn = (start_turn == self.player_id)
    self.steps_left = 5
    self.game_ended = False
    
    self.my_atk_grid = [['?' for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
    self.my_atk_grid[0][0] = 0
    self.my_pos_atk = [0, 0]
    self.enemy_pos_def = [0, 0]

  def update_energy(self, is_move_successful):
    if is_move_successful:
      self.steps_left -= 1
      
  def update_attack_map(self, x, y, status):
    if status == "MOVED":
      self.my_atk_grid[y][x] = 0
      self.my_pos_atk = [x, y]
    elif status == "WALL_HIT":
      self.my_atk_grid[y][x] = 1
    elif status == "TREASURE_FOUND":
      self.my_atk_grid[y][x] = 2
      self.my_pos_atk = [x, y]

  def check_turn_change(self, next_turn):
    if next_turn is not None:
      is_now_my_turn = (next_turn == self.player_id)

      if is_now_my_turn and not self.my_turn:
        self.steps_left = 5
      
      self.my_turn = is_now_my_turn