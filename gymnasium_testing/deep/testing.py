import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

import gymnasium as gym
from agents import CartAgentDeep
from tqdm import tqdm
import pickle as pkl

TRAINING_NUM = 1000
MODEL_TYPE = ["end", "best"][1]
REWARD_TYPE = ["only_time", "linear_distance", "ratio_distance"][1]
HIDDEN_DIM = 24

env = gym.make("CartPole-v1", render_mode="human", max_episode_steps=1000)

saved_model = pkl.load(open(f"gymnasium_testing/deep/saved_models/{REWARD_TYPE}/cartpole_v1_{TRAINING_NUM}_{MODEL_TYPE}.pkl", "rb"))
agent = CartAgentDeep(env, None, None, None, None, 
                      None, None, None, HIDDEN_DIM)

agent.policy_network.load_state_dict(saved_model)

test_steps = []

for episode_num in tqdm(range(10)):
    obs, i = env.reset()

    steps = 0 
    running = True
    while running:
        action = agent.get_action(obs)
        next_obs, reward, term, trun, i = env.step(action)

        reward = agent.get_reward(reward, obs, REWARD_TYPE)

        running = not (term or trun)
        obs = next_obs

        steps += 1

    test_steps.append(steps)

print(TRAINING_NUM, MODEL_TYPE, test_steps, sum(test_steps) / len(test_steps))