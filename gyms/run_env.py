import gymnasium
import ik_gym  # noqa: F401  (importing the package registers the env)

env = gymnasium.make('ik_env/RobotBall-v0', render_mode="human")


obs, info = env.reset(seed=0)
for _ in range(1000):
    obs, reward, terminated, truncated, info = env.step(env.action_space.sample())
    if terminated or truncated:
        obs, info = env.reset()
env.close()
