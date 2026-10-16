import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

import gymnasium as gym
from agents import CartAgentDeep
from tqdm import tqdm
import pickle as pkl
import torch
import torch.nn as nn

LR = 0.001
BATCH_SIZE = 32

DISCOUNT_RATE = 0.9
SYNC_RATE = 10
REPLAY_SIZE = 1000

N_EPISODES = 1000
HIDDEN_DIM = 24

START_E = 1
DECAY_E = 1.0 / N_EPISODES

MAX_STEPS = 1000

#Raised Max Limit
env = gym.make("CartPole-v1", max_episode_steps=MAX_STEPS)

agent = CartAgentDeep(env, LR, DISCOUNT_RATE, SYNC_RATE, REPLAY_SIZE, 
                      BATCH_SIZE, START_E, DECAY_E, HIDDEN_DIM)

loss_func = nn.MSELoss()
optimizer = torch.optim.Adam(agent.policy_network.parameters(), lr=LR)

episode_history = []
most_steps = 0
best_model = None

for episode_num in tqdm(range(N_EPISODES)):
    obs, i = env.reset()

    running = True

    step_count = 0
    episode_steps = 0

    while running:
        action = agent.get_action(obs)
        next_obs, reward, term, trun, i = env.step(action)
        
        step_count = agent.update(obs, action, next_obs, reward, term,
                                  loss_func, optimizer, step_count)

        obs = next_obs
        step_count += 1
        episode_steps += 1

        running = not (term or trun)

    if episode_num % 10 == 0:
        print(f"Episode {episode_num}: steps={episode_steps}, epsilon={agent.e:.3f}")

    if episode_steps > most_steps:
        most_steps = episode_steps
        best_model = agent.policy_network.state_dict()

    episode_history.append(episode_num)

    #Early Stopping
    if len(episode_history) > 10 and sum(episode_history[-10:]) == MAX_STEPS * 10:
        break

env.close()
        
pkl.dump(agent.policy_network.state_dict(), open(f"gymnasium_testing/deep/saved_models/cartpole_v1_{N_EPISODES}_end.pkl", "wb"))
pkl.dump(best_model, open(f"gymnasium_testing/deep/saved_models/cartpole_v1_{N_EPISODES}_best.pkl", "wb"))
    