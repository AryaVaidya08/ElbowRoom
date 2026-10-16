from gymnasium.envs.registration import register

register(
    id="ik_env/RobotBall-v0",
    entry_point="ik_gym.enviorment:IkEnv",
    max_episode_steps=10_000,
    kwargs={"width": 500, "height": 450, "floor_height": 100},
)
