import gym
from gym import spaces
import numpy as np

class BattleshipEnv(gym.Env):
    def __init__(self):
        super(BattleshipEnv, self).__init__()
        
        # Define the board size and action/observation spaces
        self.board_size = 8
        self.action_space = spaces.Discrete(self.board_size * self.board_size)  # One action per cell
        self.observation_space = spaces.Box(low=0, high=1, shape=(self.board_size, self.board_size), dtype=np.int32)
        
        # Initialize the game state
        self.reset()

    def reset(self):
        """Reset the environment to the initial state."""
        self.player_board = np.zeros((self.board_size, self.board_size), dtype=np.int32)
        self.computer_board = np.zeros((self.board_size, self.board_size), dtype=np.int32)
        self.done = False
        return self.player_board

    def step(self, action):
        """Take a step in the environment."""
        row, col = divmod(action, self.board_size)
        
        # Example logic: Mark the cell as hit
        if self.computer_board[row, col] == 0:
            self.computer_board[row, col] = 1  # Mark as hit
            reward = 1  # Reward for a hit
        else:
            reward = -1  # Penalty for hitting the same cell
        
        # Check if the game is over
        self.done = np.all(self.computer_board == 1)
        
        return self.player_board, reward, self.done, {}

    def render(self, mode="human"):
        """Render the game board."""
        print("Player Board:")
        print(self.player_board)
        print("Computer Board:")
        print(self.computer_board)