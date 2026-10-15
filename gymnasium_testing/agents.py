from collections import defaultdict
import gymnasium as gym
import numpy as np

class CartAgent:
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