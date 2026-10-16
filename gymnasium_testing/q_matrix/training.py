import gymnasium as gym
from agents import CartAgentQ
import numpy as np
from pprint import pprint
from tqdm import tqdm
import pickle as pkl
from matplotlib import pyplot as plt
from gymnasium.wrappers import RecordEpisodeStatistics, RecordVideo

LR = 0.1
N_EPISODES = 50000
START_E = 1.0
FINAL_E = 0.1
E_DECAY = 0.0001
DISCOUNT = 0.99

env = gym.make("CartPole-v1")

agent = CartAgentQ(env, LR, START_E, E_DECAY, FINAL_E, DISCOUNT)

for episode_num in tqdm(range(N_EPISODES)):
    obs, i = env.reset()

    running = True

    while running:
        action = agent.get_action(obs)
        next_obs, reward, term, trun, i = env.step(action)
        
        agent.update(obs, action, reward, term, next_obs)

        running = not (term or trun)
        obs = next_obs

    agent.decay_epsilon()

pkl.dump(agent.q_table, open(f"gymnasium_testing/q_matrix/saved_models/cartpole_v1_{N_EPISODES}.pkl", "wb"))
    