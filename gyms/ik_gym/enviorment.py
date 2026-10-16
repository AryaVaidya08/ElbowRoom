from typing import Optional
import numpy as np
import math
import random
import sys
from pathlib import Path
import gymnasium as gym
import pygame

# ik_sim lives at <project root>/ik_sim; its modules import each other as top-level (`utils`, `sprites`)
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "ik_sim"))
import utils
from sprites.robot import Robot, JOINT_RADIUS
from sprites.ball import Ball
from sprites.goal import Goal

DT = 1 / 60              # same timestep as the sim's 60 fps clock
TARGET_STEP = 5          # pixels the target moves per unit of action
MAX_STEPS = 10_000

TOP_Y, BOTTOM_Y = 180, 310
TOP_LEFT_X, TOP_RIGHT_X = 15, 435
BOTTOM_LEFT_X, BOTTOM_RIGHT_X = 0, 450
EXCLUDE_X_MIN, EXCLUDE_X_MAX = 165, 275

FLOOR_COLOR = (200, 200, 200)

class IkEnv(gym.Env):
    metadata = {"render_modes": ["human"], "render_fps": 60}

    def __init__(self, width : int, height : int, floor_height : int, render_mode: Optional[str] = None):
        assert render_mode is None or render_mode in self.metadata["render_modes"]
        self.render_mode = render_mode
        self.window = None
        self.clock = None
        self.width = width
        self.height = height
        self.floor_height = floor_height

        self._agent_target = np.array([-1, -1], dtype=np.int32)
        self._agent_location = np.array([-1, -1], dtype=np.int32)
        self._agent_grabbing = np.array([-1],    dtype=np.int32)
        self._ball_location = np.array([-1, -1], dtype=np.int32)
        self._ball_velocity = np.array([-1, -1], dtype=np.float32)
        self._goal_topleft = np.array([-1, -1], dtype=np.int32)
        self._goal_location = np.array([-1, -1], dtype=np.int32)

        self.action_space = gym.spaces.Dict({
            "agent_target_x" : gym.spaces.Discrete(3, start=-1),
            "agent_target_y" : gym.spaces.Discrete(3, start=-1),
            "agent_grab" : gym.spaces.Discrete(2)
        })

        self.observation_space = gym.spaces.Dict({
            "agent_target_pos" : gym.spaces.Box(0, width, shape=(2,), dtype=np.int32),
            "agent_pos" : gym.spaces.Box(0, width, shape=(2,), dtype=np.int32),
            "agent_grab" : gym.spaces.Box(0, 1, shape=(1,), dtype=np.int32),
            "ball_pos" : gym.spaces.Box(0, width, shape=(2,), dtype=np.int32),
            "ball_vel" : gym.spaces.Box(-np.inf, np.inf, shape=(2,), dtype=np.float32),
            "goal_pos" : gym.spaces.Box(0, width, shape=(2,), dtype=np.int32)
        })

        self.steps = -1

    def _get_obs(self):
        return {
            "agent_target_pos" : self._agent_target.copy(),
            "agent_pos" : self._agent_location.copy(),
            "agent_grab" : self._agent_grabbing.copy(),
            "ball_pos" : self._ball_location.copy(),
            "ball_vel" : self._ball_velocity.copy(),
            "goal_pos" : self._goal_location.copy()
        }

    def _get_info(self):
        return {
            "ball_distance": np.linalg.norm(self._ball_location - self._goal_location, ord=1),
            "agent_distance" : np.linalg.norm(self._agent_location - self._ball_location, ord=1)
        }

    def random_goal(self):
        while True:
            y = random.uniform(TOP_Y, BOTTOM_Y)
            x = random.uniform(BOTTOM_LEFT_X, BOTTOM_RIGHT_X)

            # Skip the excluded vertical band
            if EXCLUDE_X_MIN <= x <= EXCLUDE_X_MAX:
                continue

            # Check against the slanted sides
            t = (y - TOP_Y) / (BOTTOM_Y - TOP_Y)
            left = TOP_LEFT_X + t * (BOTTOM_LEFT_X - TOP_LEFT_X)
            right = TOP_RIGHT_X + t * (BOTTOM_RIGHT_X - TOP_RIGHT_X)

            if left <= x <= right:
                return [int(x), int(y)]


    def random_ball(self):
        r = 10

        while True:
            x = random.randint(r, self.width - r)
            y = random.randint(r, self.height - self.floor_height - r)

            # Goal boundaries
            gx, gy = self._goal_topleft
            goal_left = gx
            goal_right = gx + 50
            goal_top = gy
            goal_bottom = gy + 50

            # Ball's bounding box
            ball_left = x - r
            ball_right = x + r
            ball_top = y - r
            ball_bottom = y + r

            # Check whether the ball overlaps the goal's bounding box
            overlaps_goal = (
                ball_right > goal_left
                and ball_left < goal_right
                and ball_bottom > goal_top
                and ball_top < goal_bottom
            )

            # Check whether the ball is directly above the goal
            directly_above = (
                ball_right > goal_left
                and ball_left < goal_right
                and ball_bottom <= goal_top
            )

            if not overlaps_goal and not directly_above:
                return np.array([x, y], dtype=np.int32)

    def reset(self, seed: Optional[int] = None, options: Optional[dict] = None):
        super().reset(seed=seed)

        randomX = int((self.np_random.random() * 400) + 50)
        randomY = int((self.np_random.random() * 200) + 150)

        # same sim objects as full_simulation.py, drawn onto an offscreen surface
        self._surface = pygame.Surface((self.width, self.height))

        self._robot = Robot([randomX, randomY], -1)
        self._update_tip()
        self._agent_target = np.array([randomX, randomY], dtype=np.int32)

        self._agent_grabbing = np.array([0],    dtype=np.int32)

        top_left = self.random_goal()
        self._goal_topleft = np.array([top_left[0], top_left[1]], dtype=np.int32)
        self._goal_location = np.array([self._goal_topleft[0] + 25, self._goal_topleft[1] + 32.5], dtype=np.int32)
        self._goal = Goal(self._surface, top_left)

        self._ball_location = self.random_ball()
        self._ball_velocity = np.array([0, 0], dtype=np.float32)
        self._ball = Ball(self._surface, [float(self._ball_location[0]), float(self._ball_location[1])],
                          self.height - self.floor_height)
        # Ball.update draws itself every call; only render() should draw
        self._ball.draw = lambda: None

        self.steps = 0

        if self.render_mode == "human":
            self.render()

        return self._get_obs(), self._get_info()

    def _update_tip(self):
        elbow = self._robot.calculate_elbow_pos(self._robot.alpha)
        self._robot.tip = self._robot.calculate_tip_pos(elbow, self._robot.alpha, self._robot.beta)
        self._agent_location = np.array(self._robot.tip, dtype=np.int32)

    def step(self, action):
        robot, ball, goal = self._robot, self._ball, self._goal

        self._agent_target[0] = np.clip(
            self._agent_target[0] + int(action["agent_target_x"]) * TARGET_STEP, 0, self.width
        )
        self._agent_target[1] = np.clip(
            self._agent_target[1] + int(action["agent_target_y"]) * TARGET_STEP, 0, self.height - self.floor_height
        )

        # move the arm toward the target (it may not be able to reach it in one step)
        old_pose = (robot.alpha, robot.beta)
        robot.update([int(self._agent_target[0]), int(self._agent_target[1])], DT)

        # grab: 1 = want to hold the ball, 0 = want to release it. Grabbing needs the tip on the ball.
        holding = bool(self._agent_grabbing[0])
        if action["agent_grab"] == 0:
            holding = False
        elif not holding and math.dist(robot.tip, ball.pos) <= JOINT_RADIUS + utils.BALL_RADIUS:
            holding = True

        if holding:
            # a held ball can't be pushed through the box walls: freeze the arm instead
            new_elbow = robot.calculate_elbow_pos(robot.alpha)
            new_tip = robot.calculate_tip_pos(new_elbow, robot.alpha, robot.beta)
            if goal.hits_wall(new_tip):
                robot.alpha, robot.beta = old_pose

        elbow = robot.calculate_elbow_pos(robot.alpha)
        robot.tip = robot.calculate_tip_pos(elbow, robot.alpha, robot.beta)

        # update ball position and velocity
        ball.update(DT, holding, robot)
        if not holding:
            goal.collide_ball(ball)

        self._agent_grabbing[0] = int(holding)
        self._agent_location = np.array(robot.tip, dtype=np.int32)
        self._ball_location = np.array(ball.pos, dtype=np.int32)
        self._ball_velocity = np.array(ball.vel, dtype=np.float32)

        self.steps += 1

        # ball's centre is inside the green zone
        terminated = bool(goal.scored(ball))

        truncated = self.steps >= MAX_STEPS

        # small time penalty, shaped by how far the ball is from the goal, big bonus for scoring
        ball_to_goal = np.linalg.norm(self._ball_location - self._goal_location)
        reward = 100.0 if terminated else -0.01 - 0.001 * ball_to_goal

        observation = self._get_obs()
        info = self._get_info()

        if self.render_mode == "human":
            self.render()

        return observation, reward, terminated, truncated, info

    def render(self):
        if self.render_mode != "human":
            return

        if self.window is None:
            pygame.init()
            self.window = pygame.display.set_mode((self.width, self.height))
            pygame.display.set_caption("Elbow Room")
            self.clock = pygame.time.Clock()

        self.window.fill((0, 0, 0))
        pygame.draw.rect(self.window, FLOOR_COLOR,
                         pygame.Rect((0, self.height - self.floor_height), (self.width, self.floor_height)))

        self._robot.draw(self.window)
        Ball.draw(self._ball)  # the instance's draw is a no-op, call the class's directly
        self._goal.update()

        self._ball.screen = self._goal.screen = self.window
        pygame.event.pump()
        pygame.display.flip()
        self.clock.tick(self.metadata["render_fps"])

    def close(self):
        if self.window is not None:
            pygame.display.quit()
            pygame.quit()
            self.window = None
