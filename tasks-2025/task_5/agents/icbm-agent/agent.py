from task_5.utils.utils import *  # DO NOT TOUCH THIS FIRST LINE!!!

from abc import ABC
from dataclasses import dataclass
from typing import Optional, Tuple, List



SIDE_LEFT = 0
SIDE_RIGHT = 1


class Action(ABC):
    pass


class AbstractShip(ABC):
    def get_actions(self, obs: dict, ship_data: Tuple) -> List[Optional[Action]]:
        pass
    pass

@dataclass
class Shoot(Action):
    """
    DON'T SHOOT! WE'RE A PEACEFUL TEAM!
    """

    ship_id: int
    direction: int
    """ 
    0 - right
    1 - down
    2 - left 
    3 - up
    """

    def to_game_format(self) -> object:
        return [self.ship_id, 1, self.direction]


@dataclass
class Move(Action):
    ship_id: int
    direction: int
    """ 
    0 - right
    1 - down
    2 - left 
    3 - up
    """

    speed: int
    """1-3"""

    def to_game_format(self) -> object:
        return [self.ship_id, 0, self.direction, self.speed]


@dataclass
class Construction(Action):
    ships_count: int
    """
    0-10
    """

class ShipICBM(AbstractShip):
    def __init__(self, side: int):
        self.side = side

        # Keep track of each ship's move count.
        self.move_count = 0
        # Set to True on the first call to get_action.
        self.is_first_turn = True
        # Data points for top and bottom players.
        # For top players, we assume lower x values (e.g., x < 50);
        # for bottom players, higher x values.
        self.data_points = [
            {
                "moves": [0, 1],
                "threshold1": 90,  # e.g., if x < 10: use one move
                "threshold2": 85  # if 10 <= x < 15: use another
            },
            {
                "moves": [2, 3],
                "threshold1": 10,  # for bottom players, if x > 90: use one move
                "threshold2": 15  # if 85 < x <= 90: use another
            }
        ]
        # Default to top-player data (will be updated on first turn).
        self.current_data_points = self.data_points[0]
        # This flag will be set based on the starting ship position.
        self.is_player1 = None

    def get_actions(self, obs: dict, ship_data: Tuple) -> List[Optional[Action]]:
        ship_id, x, y, hp, fire_cooldown, move_cooldown = ship_data

        ships_actions = []

        # On the first turn, determine starting side.
        if self.is_first_turn:
            # Use the first allied ship to decide.
            # Here we assume that if x < 50 the player starts on top; otherwise on bottom.
            if x < 50:
                self.is_player1 = True
                self.current_data_points = self.data_points[0]
            else:
                self.is_player1 = False
                self.current_data_points = self.data_points[1]
            self.is_first_turn = False

        increase_move_count = True
        result_action = None
        # Use different logic for top (is_player1) vs bottom players.
        if self.is_player1:
            # For top players: lower x values.
            if x < self.current_data_points['threshold1']:
                # If x is very low, use a move from our move list with direction 2.
                move_code = self.current_data_points['moves'][self.move_count % len(self.current_data_points['moves'])]
                result_action = Move(ship_id=ship_id, direction=move_code, speed=2)
            elif self.current_data_points['threshold1'] <= x < self.current_data_points['threshold2']:
                move_code = self.current_data_points['moves'][self.move_count % len(self.current_data_points['moves'])]
                result_action = Move(ship_id=ship_id, direction=move_code, speed=2)
            else:  # x >= threshold2
                result_action = Move(ship_id=ship_id, direction=1, speed=2)
                increase_move_count = False
        else:
            # For bottom players: higher x values.
            if x > self.current_data_points['threshold1']:
                move_code = self.current_data_points['moves'][self.move_count % len(self.current_data_points['moves'])]
                ships_actions.append([ship_id, 0, move_code, 2])
                result_action = Move(ship_id=ship_id, direction=move_code, speed=2)
            elif self.current_data_points['threshold2'] < x <= self.current_data_points['threshold1']:
                move_code = self.current_data_points['moves'][self.move_count % len(self.current_data_points['moves'])]
                result_action = Move(ship_id=ship_id, direction=move_code, speed=2)
            else:  # x <= threshold2
                ships_actions.append([ship_id, 0, 3, 2])
                result_action = Move(ship_id=ship_id, direction=3, speed=2)
                increase_move_count = False

        if increase_move_count:
            self.move_count += 1

        return [result_action]

    def destructor(self, obs: dict) -> List[Action]:
        # If our ICBM has been destroyed, and we have >= 200 gold,
        # we can automatically build a new ship.
        if can_build_ship(obs):
            return [Construction(ships_count=1)]

        return []
class ShipICBMv2(AbstractShip):
    def __init__(self, side: int):
        self.side = side
        self.target = []
        self.move_count = 0
        self.visited = set()


    def get_actions(self, obs: dict, ship_data: Tuple) -> List[Optional[Action]]:
        map = obs['map']
        ship_id, x, y, hp, fire_cooldown, move_cooldown = ship_data

        if not self.target:
            if self.side == SIDE_LEFT:
                self.target = [90, 90]
            else:
                self.target = [10, 10]

        self.move_count += 1

        visited, move = find_path([x,y], self.target, map, self.visited)

        direction, step = move

        self.visited=visited
        return [Move(ship_id=ship_id, direction=direction, speed=step)]

    def destructor(self, obs: dict) -> List[Action]:
        # If our ICBM has been destroyed, and we have >= 200 gold,
        # we can automatically build a new ship.
        if can_build_ship(obs):
            return [Construction(ships_count=1)]
        return []

class ShipExplorer:
    # go right, down, left, down
    TOP_SIDE_DIRECTIONS = (0, 1, 2, 0)
    BOTTOM_SIDE_DIRECTIONS = (2, 3, 0, 3)
    TRAVEL_DISTANCE_UNTIL_DIRECTION_CHANGE = (85, 10, 85, 10)

    ship_travelled_in_current_direction = 0

    DIRECTIONS = None
    seen_planet = None 

    def __init__(self, side: int):
        self.side = side
        self.move_direction = 0

        if side == SIDE_LEFT: 
            self.DIRECTIONS = self.TOP_SIDE_DIRECTIONS
        else:
            self.DIRECTIONS = self.BOTTOM_SIDE_DIRECTIONS

    def get_actions(self, obs: dict, ship_data: Tuple) -> list[Move]:
        ship_id, x, y, hp, fire_cooldown, move_cooldown = ship_data
        
        if self.seen_planet is None:
            for planet in obs['planets_occupation']:
                # !!!!!!!!!!!!!! WARNING !!!!!!!!!!!!!!!!!!!!!!!
                # Y SWAPPED WITH X
                # BECAUSE PLANETS X, Y ARE SWAPPED
                # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!111

                planet_y, planet_x, occupation_progress = planet
                dx = planet_y - y
                dy = planet_x - x
                planet_is_free = occupation_progress == -1
                
                # TODO: fix me xD

                manhattan_distance = abs(dx) + abs(dy)
                if planet_is_free: 
                    #if manhattan_distance > 20:
                    #    print(f"Planet {planet_x}, {planet_y} is too far away ({manhattan_distance}) from our ship {x}, {y}")
                    #    input("")

                    # TODO: determine if the found planet is close by
                    self.seen_planet = (planet_x, planet_y)
                    print(f"our x: {x}, our y: {y}, we can crash into planet: {planet_is_free} at position {planet_x}, {planet_y}")
                    #input("")
                    
        if self.seen_planet is not None:
            print(f"Our ship is travellign from {x}, {y} to {self.seen_planet}")

            planet_x, planet_y = self.seen_planet
            dx = planet_x - x
            dy = planet_y - y

            planet_direction = None
            # Determine the direction to move towards the planet
            if abs(dx) > abs(dy):
                # Move horizontally
                if dx > 0:
                    planet_direction = 0  # Right
                else:
                    planet_direction = 2  # Left
            else:
                # Move vertically
                if dy > 0:
                    planet_direction = 1  # Down
                else:
                    planet_direction = 3  # Up
            
            
            return [Move(ship_id=ship_id, direction=planet_direction, speed=2)]

        switch_side = self.ship_travelled_in_current_direction >= self.TRAVEL_DISTANCE_UNTIL_DIRECTION_CHANGE[self.move_direction]
        if switch_side:
            self.ship_travelled_in_current_direction = 0
            self.move_direction = (self.move_direction + 1) % 4

        self.ship_travelled_in_current_direction += 1
        print(self.ship_travelled_in_current_direction)

        return [Move(ship_id=ship_id, direction=self.DIRECTIONS[self.move_direction], speed=2)]

    def destructor(self, obs: dict) -> List[Action]:
        return []

class Ship:
    LAST_POSITIONS_MAX_COUNT = 20

    def __init__(self, side: int, role: Optional[str] = None):
        self.role = role
        self.side = side
        self.icbm = ShipICBM(side=side)
        self.explorer = ShipExplorer(side=side)
        self.icbmV2 = ShipICBMv2(side=side)

        self.last_positions = []

        # By default, the ship should be a ballistic missile
        if not self.role:
            self.role = 'icbmv2' # TODO: fix me

    def get_actions(self, obs: dict, ship_data: Tuple) -> List[Action]:
        ship_id, x, y, hp, fire_cooldown, move_cooldown = ship_data

        if len(self.last_positions) >= self.LAST_POSITIONS_MAX_COUNT:
            self.last_positions.pop(0)

        self.last_positions.append((x, y))

        if len(self.last_positions) >= self.LAST_POSITIONS_MAX_COUNT:
            # Check if the ship is stuck
            min_x, max_x = min(self.last_positions, key=lambda x: x[0])[0], max(self.last_positions, key=lambda x: x[0])[0]
            min_y, max_y = min(self.last_positions, key=lambda x: x[1])[1], max(self.last_positions, key=lambda x: x[1])[1]

            if abs(max_x - min_x) <= 2 and abs(max_y - min_y) <= 2:
                # Ship is stuck
                print(f"Our ship is stuck! x diff {abs(max_x - min_x)}, y diff {abs(max_y - min_y)}")
                if self.role == 'explorer':
                    self.role = 'icbmv2'     

        ship = self._get_current_ship()
        actions = ship.get_actions(obs, ship_data)

        # Ensure that ships don't return invalid data
        move_or_shoot_found = False
        filtered_actions = []
        for action in actions:
            if action and isinstance(action, (Move, Shoot)):
                if not move_or_shoot_found:
                    move_or_shoot_found = True
                else:
                    raise ValueError("Ship can only move or shoot once in a single turn.")
                    # TODO - if we push to production, create a failsafe to do something
            if action:
                filtered_actions.append(action)

        return actions

    def destructor(self, obs: dict) -> List[Action]:
        ship = self._get_current_ship()
        actions = ship.destructor(obs)
        # TODO: validate actions such as in get_actions if necessary
        return actions

    def _get_current_ship(self):
        if self.role == 'icbm':
            return self.icbm
        elif self.role == 'explorer':
            return self.explorer
        elif self.role == 'icbmv2':
            return self.icbmV2
        else:
            raise ValueError(f"Invalid role: {self.role}")


class Agent:
    side = None 
    def __init__(self, side: int):
        """ 
        :param side: Indicates whether the player is on left side (0) or right side (1)
        """
        self.side = side
        self.ships = {}
        self.home_planet = (None, None)
        self.first_run = True
        self.constructed_ships = 0
        """Tuple - (x, y), default value"""

    def get_action(self, obs: dict) -> dict:
        if self.home_planet[0] is None:
            for planet in obs.get('planets_occupation', []):
                if planet[0] == 9 and planet[1] == 9:
                    self.home_planet = ((9, 9), planet[2])
                elif planet[0] == 90 and planet[1] == 90:
                    self.home_planet = ((90, 90), planet[2])
                break

        ships_count = len(obs['allied_ships'])

        actions: List[Action] = []

        if self.first_run:
            self.first_run = False
            actions.append(Construction(ships_count=1))

        visited_ids = {ship_id: False for ship_id in self.ships.keys()}
        for n, ship_data in enumerate(obs['allied_ships']):
            ship_id = ship_data[0]
            if ship_id not in self.ships:
                self.constructed_ships += 1
                self.ships[ship_id] = Ship(side=self.side)
            visited_ids[ship_id] = True

            ship = self.ships[ship_id]
            actions.extend(ship.get_actions(obs, ship_data))

        # If we didn't process some ships from the map, they must have been destroyed

        for ship_id, visited in visited_ids.items():
            if not visited:
                destroyed_ship = self.ships.pop(ship_id, None)
                action = destroyed_ship.destructor(obs) if destroyed_ship else None
                actions.extend(action)
                del destroyed_ship

        # Merge actions and resolve conflicts
        ship_actions, construction_max = [], 0
        for action in actions:
            if isinstance(action, Construction):
                construction_max = max(construction_max, action.ships_count)

            elif isinstance(action, Action):
                ship_actions.append(action.to_game_format())

            else:
                pass  # ship decided to do nothing

        # If we don't have a ship, we must build one 
        if ships_count == 0:
            construction_max = max(1, construction_max)

        # Let's always build ships if we have safety net
        if can_build_ship_with_safety_net(obs):
            print("cranking out a ship just because we can")
            construction_max = maximum_ships_we_can_build_with_safety_net(obs)

        if is_our_home_planet_occupied(obs, self.home_planet):
            print("Our home planet is occupied - want to crank out a ship!")
            construction_max = maximum_ships_we_can_build_with_safety_net(obs)
        
        result = {
            "ships_actions": ship_actions,
            "construction": construction_max
        }

        return result

    def load(self, abs_path: str):
        """
        Load all necessary weights for the agent.
        """
        pass

    def eval(self):
        """
        Switch the agent to inference mode.
        """
        pass

    def to(self, device):
        """
        Move the agent to the specified device (e.g., GPU).
        """
        pass
