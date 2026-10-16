import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

import gymnasium as gym
from agents import CartAgentDeep
from tqdm import tqdm
import pickle as pkl

TRAINING_NUM = 1000
MODEL_TYPE = ["end", "best"][1]
HIDDEN_DIM = 24

env = gym.make("CartPole-v1", render_mode="human", max_episode_steps=1000)

saved_model = pkl.load(open(f"gymnasium_testing/deep/saved_models/cartpole_v1_{TRAINING_NUM}_{MODEL_TYPE}.pkl", "rb"))
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

        running = not (term or trun)
        obs = next_obs

        steps += 1

    test_steps.append(steps)

print(TRAINING_NUM, MODEL_TYPE, test_steps, sum(test_steps) / len(test_steps))

#Always goes to the right side of the screen --> Modify reward function / loss function?

# 100 end [10, 9, 10, 9, 10, 10, 8, 9, 9, 10] 9.4
# 100 best [10, 10, 8, 9, 8, 10, 9, 9, 11, 10] 9.4
# 500 end [9, 9, 9, 9, 10, 8, 8, 8, 9, 10] 8.9
# 500 best [10, 10, 9, 10, 8, 9, 9, 9, 10, 9] 9.3
# 1000 end [171, 178, 173, 167, 175, 177, 172, 169, 182, 172] 173.6
# 1000 best [178, 179, 175, 170, 162, 177, 165, 170, 171, 172] 171.9