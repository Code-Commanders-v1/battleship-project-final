from stable_baselines3 import DQN
from battleship_env import BattleshipEnv

# Create the environment
env = BattleshipEnv()

# Initialize the DQN model
model = DQN("MlpPolicy", env, verbose=1)

# Train the model
model.learn(total_timesteps=10000)

# Save the model
model.save("battleship_dqn")

# Test the trained model
obs = env.reset()
for _ in range(100):
    action, _states = model.predict(obs)
    obs, rewards, done, info = env.step(action)
    env.render()
    if done:
        print("Game Over!")
        break