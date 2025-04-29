# Battleship Game

This project is a Battleship game implemented in Python. It includes both single-player and multiplayer modes, with AI and reinforcement learning capabilities using Stable-Baselines3.

---

## Features

1. **Single-Player Mode**:
   - Play against an AI opponent with adjustable difficulty levels (`easy`, `medium`, `hard`).
   - AI uses strategies ranging from random targeting to advanced targeting.

2. **Multiplayer Mode**:
   - Play against another player over a network using a server-client architecture.

3. **Reinforcement Learning (RL)**:
   - AI can be trained using Stable-Baselines3 to improve its gameplay.
   - A custom Gym environment is provided for training the AI.

4. **Graphical User Interface (GUI)**:
   - Built with Tkinter for an interactive and user-friendly experience.

---

## Project Structure

```
battleship-game/
├── battleship.py           # Multiplayer Battleship game (server-client architecture)
├── battleship-vs-ai.py     # Single-player Battleship game with AI
├── battleship_env.py       # Custom Gym environment for RL training
├── train_agent.py          # Script to train the AI using Stable-Baselines3
├── battleship_dqn.zip      # Pre-trained DQN model (generated after training)
├── server.py               # Server implementation for multiplayer mode
└── __pycache__/            # Compiled Python files
```

---
## Requirements

- Python 3.8 or higher
- Required Python libraries:
  - `stable-baselines3`
  - `gym`
  - `numpy`
  - `tkinter` (comes pre-installed with Python on most systems)

Install the required libraries using:

```bash
pip install stable-baselines3[extra] numpy
```

---

## How to Run

### 1. Single-Player Mode (vs AI)
Run the following command to play against the AI:

```bash
python battleship-vs-ai.py
```

### 2. Multiplayer Mode
#### Start the Server:
Run the server script to host the game:

```bash
python server.py
```

#### Start the Client:
Run the client script to connect to the server:

```bash
python battleship.py
```

You will need to provide the server's IP address and port when prompted.

### 3. Train the AI
To train the AI using reinforcement learning, run:

```bash
python train_agent.py
```

This will train a DQN model and save it as `battleship_dqn.zip`.

---

## AI Training Details

The AI is trained using **Stable-Baselines3** with a custom Gym environment (`battleship_env.py`). The environment defines the game logic, including states, actions, and rewards.

### Training Script
The `train_agent.py` script trains a DQN (Deep Q-Network) model:

```python
from stable_baselines3 import DQN
from battleship_env import BattleshipEnv

env = BattleshipEnv()
model = DQN("MlpPolicy", env, verbose=1)
model.learn(total_timesteps=10000)
model.save("battleship_dqn")
```

---

## Files Overview

### `battleship-vs-ai.py`
- Implements the single-player mode with AI.
- Loads the trained DQN model (`battleship_dqn.zip`) to predict AI moves.

### `battleship.py`
- Implements the multiplayer mode using a server-client architecture.
- Players take turns attacking each other's boards.

### `battleship_env.py`
- Defines a custom Gym environment for the Battleship game.
- Used for training the AI with reinforcement learning.

### `train_agent.py`
- Trains the AI using Stable-Baselines3.
- Saves the trained model as `battleship_dqn.zip`.

### `server.py`
- Implements the server for multiplayer mode.
- Handles communication between two players.

---

## How to Play

### Single-Player Mode
1. Place your ships on the board by clicking on the cells.
2. Toggle ship orientation (horizontal/vertical) using the "Orientation" button.
3. Attack the enemy's board by clicking on the cells.
4. The game ends when all ships of one side are sunk.

### Multiplayer Mode
1. Start the server (`server.py`) and wait for two players to connect.
2. Each player places their ships and takes turns attacking.
3. The game ends when all ships of one player are sunk.

---

## Future Improvements

- Enhance AI strategies using advanced reinforcement learning techniques.
- Add more visual effects and animations to the GUI.
- Implement a leaderboard for multiplayer mode.
- Add support for saving and loading game progress.

---

## License

This project is licensed under the MIT License. Feel free to use and modify it as needed.

---

## Author

Developed by Melek Kefi and MohamedAmine Rouatbi. Contributions are welcome!