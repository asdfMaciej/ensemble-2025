from gymnasium.envs.registration import register

register(
    id="OctoSpace-v0",
    entry_point="octospace.envs:OctoSpaceEnv",
)
