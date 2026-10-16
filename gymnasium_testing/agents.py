from collections import deque
import gymnasium as gym
from models import SimpleDQN
import numpy as np
import torch
import random

class CartAgentQ:
    def __init__(self, env : gym.Env, lr, initial_e, e_decay, final_e, discount_factor = 0.95, q_table = None):
        self.env = env

        self.pos_space = np.linspace(-2.4, 2.4, 10)
        self.vel_space = np.linspace(-4, 4, 10)
        self.ang_space = np.linspace(-.2095, 0.2095, 10)
        self.ang_vel_space = np.linspace(-4, 4, 10)

        if q_table is None:
            self.q_table = np.zeros((
                len(self.pos_space) + 1,
                len(self.vel_space) + 1,
                len(self.ang_space) + 1,
                len(self.ang_vel_space) + 1,
                self.env.action_space.n
            ))
        else:
            self.q_table = q_table

        self.lr = lr
        self.discount_factor = discount_factor

        self.e = initial_e
        self.e_decay = e_decay
        self.final_e = final_e

        self.training_error = []

    def get_states(self, obs):
        pos_state = np.digitize(obs[0], self.pos_space)
        vel_state = np.digitize(obs[1], self.vel_space)
        ang_state = np.digitize(obs[2], self.ang_space)
        ang_vel_state = np.digitize(obs[3], self.ang_vel_space)

        return pos_state, vel_state, ang_state, ang_vel_state

    def get_action(self, obs):
        pos_state, vel_state, ang_state, ang_vel_state = self.get_states(obs)

        if self.e != None and np.random.random() < self.e:
            return self.env.action_space.sample()
        else:
            return np.argmax(self.q_table[pos_state, vel_state, ang_state, ang_vel_state, :])

    def update(self, obs: tuple, action, reward, terminated, next_obs: tuple):
        pos_state, vel_state, ang_state, ang_vel_state = self.get_states(obs)
        new_pos_state, new_vel_state, new_ang_state, new_ang_vel_state = self.get_states(next_obs)

        self.q_table[pos_state, vel_state, ang_state, ang_vel_state, action] =  self.q_table[pos_state, vel_state, ang_state, ang_vel_state, action] + self.lr * (
            reward + self.discount_factor * np.max(self.q_table[new_pos_state, new_vel_state, new_ang_state, new_ang_vel_state, :]) - self.q_table[pos_state, vel_state, ang_state, ang_vel_state, action]
        )

    def decay_epsilon(self):
        self.e = max(self.final_e, self.e - self.e_decay)

class ExperienceReplay:
    def __init__(self, max_len):
        self.memory = deque([], maxlen=max_len)

    def append(self, transition):
        self.memory.append(transition)

    def sample(self, sample_size):
        return random.sample(self.memory, sample_size)

    def __len__(self):
        return len(self.memory)

class CartAgentDeep:
    def __init__(self, env : gym.Env, lr, discount, sync_rate, replay_size, 
                 batch_size, start_e, decay_e, hidden_channels):
        self.env = env
        self.lr = lr
        self.discount = discount
        self.sync_rate = sync_rate
        self.batch_size = batch_size

        self.e = start_e
        self.decay_e = decay_e

        self.in_channels = 4
        self.hidden_channels = hidden_channels
        self.out_channels = 2

        self.policy_network = SimpleDQN(self.in_channels, self.hidden_channels, self.out_channels)
        self.target_network = SimpleDQN(self.in_channels, self.hidden_channels, self.out_channels)
        self.target_network.load_state_dict(self.policy_network.state_dict())

        self.memory = ExperienceReplay(replay_size)

    def get_action(self, obs):
        if self.e != None and np.random.random() < self.e:
            return self.env.action_space.sample()
        else:
            with torch.no_grad():
                return self.policy_network(torch.tensor(obs)).argmax().item()

    def get_reward(self, reward, state, type):
        if type == "linear_distance":
            return reward - abs(state[0])
        elif type == "ratio_distance":
            return reward - (abs(state[0]) / 2.4)

        return reward

    def optimize(self, mini_batch, loss_func, optimizer):
        policy_list = []
        target_list = []

        for state, action, new_state, reward, terminated in mini_batch:
            if terminated:
                target = torch.tensor(reward, dtype=float)
            else:
                with torch.no_grad():
                    target = torch.tensor(
                        reward + self.discount * self.target_network(torch.tensor(new_state)).max(),
                        dtype=float
                    )

            policy_q = self.policy_network(torch.tensor(state))
            policy_list.append(policy_q)

            target_q = self.target_network(torch.tensor(state))
            target_q[action] = target
            target_list.append(target_q)

        loss = loss_func(torch.stack(policy_list), torch.stack(target_list))

        optimizer.zero_grad()
        loss.backward()
        optimizer.step()


    def update(self, state, action, new_state, reward, term, 
               loss_func, optimizer, step_count):
        self.memory.append((state, action, new_state, reward, term))

        if len(self.memory) > self.batch_size:
            mini_batch = self.memory.sample(self.batch_size)
            self.optimize(mini_batch, loss_func, optimizer)

            self.decay_epi()

            if step_count > self.sync_rate:
                self.target_network.load_state_dict(self.policy_network.state_dict())
                return -1

        return step_count

    def decay_epi(self):
        self.e = max(self.e - self.decay_e, 0.05)

