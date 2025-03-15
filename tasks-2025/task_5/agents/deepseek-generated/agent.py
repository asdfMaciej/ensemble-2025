from task_5.utils.utils import * # DO NOT TOUCH THIS FIRST LINE!!!

class Agent:
    def __init__(self):
        constructor(self)

    def get_action(self, obs: dict) -> dict:
        ships_actions = []
        construction = 0

        outside_function()

        # Find the first unoccupied planet
        target_planet = None
        for planet in obs.get('planets_occupation', []):
            if planet[2] == -1:  # Check if the planet is unoccupied
                target_planet = (planet[0], planet[1])
                break

        # Process each allied ship
        for ship in obs['allied_ships']:
            ship_id, x, y, hp, fire_cooldown, move_cooldown = ship
            action_added = False

            # Try to move if possible
            if move_cooldown == 0:
                direction = 0  # Default to right if no target
                if target_planet:
                    px, py = target_planet
                    dx = px - x
                    dy = py - y

                    # Determine direction based on largest distance
                    if abs(dx) >= abs(dy):
                        direction = 0 if dx > 0 else 2
                    else:
                        direction = 1 if dy > 0 else 3

                # Append move action with speed 1
                ships_actions.append([ship_id, 0, direction, 1])
                action_added = True
            # If can't move, try to fire
            elif fire_cooldown == 0:
                ships_actions.append([ship_id, 1, 0])
                action_added = True

        # Attempt to build one ship if resources are sufficient (assuming cost of 10)
        #if obs['resources'] >= 10:
        #    construction = 1

        return {
            "ships_actions": ships_actions,
            "construction": 0
        }


    def load(self, abs_path: str):
        """
        Function for loading all necessary weights for the agent. The abs_path is a path pointing to the directory,
        where the weights for the agent are stored, so remember to join it to any path while loading.

        :param abs_path:
        :return:
        """
        pass

    def eval(self):
        """
        With this function you should switch the agent to inference mode.

        :return:
        """
        pass

    def to(self, device):
        """
        This function allows you to move the agent to a GPU. Please keep that in mind,
        because it can significantly speed up the computations and let you meet the time requirements.

        :param device:
        :return:
        """
        pass
