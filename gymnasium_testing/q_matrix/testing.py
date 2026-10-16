import gymnasium as gym
from agents import CartAgentQ
import numpy as np
from pprint import pprint
from tqdm import tqdm
import pickle as pkl
from gymnasium.wrappers import RecordEpisodeStatistics, RecordVideo

TRAINING_NUM = 50000

env = gym.make("CartPole-v1", render_mode="human")

saved_table = pkl.load(open(f"gymnasium_testing/q_matrix/saved_models/cartpole_v1_{TRAINING_NUM}.pkl", "rb"))
agent = CartAgentQ(env, None, None, None, None, None, saved_table)

test_steps = []

for episode_num in tqdm(range(10)):
    obs, i = env.reset()

    steps = 0 
    running = True
    while running:
        action = agent.get_action(obs)
        next_obs, reward, term, trun, i = env.step(action)

        running = not (term or trun)
        obs = next_obs

        steps += 1

    test_steps.append(steps)

print(TRAINING_NUM, test_steps, sum(test_steps) / len(test_steps))

# 100   [14, 55, 14, 59, 15, 53, 53, 14, 64, 60]            40.1
# 1000  [86, 110, 106, 108, 100, 126, 95, 88, 112, 115]     104.6
# 10000 [275, 309, 314, 247, 315, 302, 311, 298, 318, 326]  301.5
# 50000 [499, 471, 500, 500, 456, 500, 500, 500, 471, 450]  484.7 (MAX is 500 timesteps)