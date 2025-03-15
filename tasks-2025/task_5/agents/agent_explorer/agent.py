# Skeleton for Agent class


class Agent:
    def __init__(self):
        self.isLeftPlanet = True
        self.side = 0
        self.down_move_counter = 0

    def get_action(self, obs: dict) -> dict:
        ships_actions = []
        construction = 1

        self.isLeftPlanet = obs['planets_occupation'][0][0] < 40
        print(self.isLeftPlanet)

        # Find the first unoccupied planet
        target_planet = None
        for planet in obs.get('planets_occupation', []):
            if planet[2] == 0:
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
                    dx = px - 1
                    dy = py - 1

                    move_side = self.get_move_side(x, y)
                    if move_side == 0:
                        direction = self.goDown(dy)
                    elif move_side == 1:
                        direction = self.goRight(dx)
                    elif move_side == 2:
                        direction = self.goLeft(dx)
                    else:
                        direction = self.goUp(dy)

                # Append move action with speed 1
                ships_actions.append([ship_id, 0, direction, 1])
                action_added = True
            # If can't move, try to fire
            elif fire_cooldown == 0:
                ships_actions.append([ship_id, 1, 0])
                action_added = True

        if obs['resources'][0] >= 400:
            construction = 1
        else:
            construction = 0

        return {
            "ships_actions": ships_actions,
            "construction": construction
        }

    def goRight(self, dx):
        direction = 0 if dx > 0 else 2
        return direction

    def goDown(self, dy):
        direction = 1 if dy > 0 else 3
        return direction

    def goLeft(self, dx):
        d = 2 if dx > 0 else 1
        return d

    def goUp(self, dy):
        d = 3 if dy > 1 else 3
        return d

    def get_move_side(self, x, y):
        if self.side == 0 and x != 99:
            return 1
        elif self.side == 0 and x == 99 and self.down_move_counter < 5:
            self.down_move_counter += 1
            return 0
        elif self.side == 0 and x == 99 and self.down_move_counter == 5:
            self.down_move_counter = 0
            self.side = 1
            return 2
        elif self.side == 1 and x != 1:
            return 2
        elif self.side == 1 and x == 1 and self.down_move_counter < 5:
            self.down_move_counter += 1
            return 0
        elif self.side == 1 and x == 1 and self.down_move_counter == 5:
            self.down_move_counter = 0
            self.side = 0
            return 1
        return 0

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
