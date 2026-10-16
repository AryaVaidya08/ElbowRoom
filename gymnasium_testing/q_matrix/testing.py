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