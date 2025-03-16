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
    

import random

class ShipICBMv2(AbstractShip):
    def __init__(self, side: int):
        self.side = side
        self.target = []
        self.move_count = 0
        self.visited = set()
        self.last_position = None
        self.stuck_counter = 0

    def set_target(self, target):
        self.target = target

    def get_actions(self, obs: dict, ship_data: Tuple) -> List[Optional[Action]]:
        map_data = obs['map']
        ship_id, x, y, hp, fire_cooldown, move_cooldown = ship_data

        self.move_count += 1

        # Check if the ship hasn't moved (stuck in same cell).
        if self.last_position == (x, y):
            self.stuck_counter += 1
        else:
            self.stuck_counter = 0
        self.last_position = (x, y)

        #print(self.target)
        if(len(self.target) == 0):
            return []
        # Use our path-finding function.
        visited, move = find_path([x, y], self.target, map_data, self.visited)
        direction, step = move

        # If we receive a default move (0, 0) or have been stuck for more than 3 moves,
        # then reset the visited set and choose a random move to try to break the blockade.
        if (direction, step) == (0, 0) or self.stuck_counter > 3:
            self.visited = set()  # Reset visited to allow re-exploration.
            direction = random.choice([0, 1, 2, 3])
            step = 1
            self.stuck_counter = 0

        # Update the visited set.
        self.visited = visited

        return [Move(ship_id=ship_id, direction=direction, speed=step)]

    def destructor(self, obs: dict) -> List[Action]:
        # If our ICBM has been destroyed, and we have >= 200 gold,
        # we can automatically build a new ship.
        if can_build_ship(obs):
            return [Construction(ships_count=1)]
        return []


class ShipDefender(AbstractShip):
    def __init__(self, is_even_id: bool, side: int):
        self.side = side
        self.retreat = False
        self.is_even_id = is_even_id
        self.home_planet = (None, None)
        # Keep track of each ship's move count.
        self.move_count = 0
        # Set to True on the first call to get_action.
        self.is_first_turn = True
        self.ready_to_shoot = False
        # Data points for top and bottom players.
        # For top players, we assume lower x values (e.g., x < 50);
        # for bottom players, higher x values.
        self.data_points = [
            {
                "moves": [0, 1],
                "threshold1": 90,  # e.g., if x < 10: use one move
                "threshold2": 85   # if 10 <= x < 15: use another
            },
            {
                "moves": [2, 3],
                "threshold1": 10,  # for bottom players, if x > 90: use one move
                "threshold2": 15   # if 85 < x <= 90: use another
            }
        ]
        # Default to top-player data (will be updated on first turn).
        self.current_data_points = self.data_points[0]
        # This flag will be set based on the starting ship position.
        self.is_player1 = None


    def get_actions(self, obs: dict, ship_data: Tuple) -> List[Optional[Action]]:
        if self.home_planet[0] is None:
            for planet in obs.get('planets_occupation', []):
                if planet[0] == 9 and planet[1] == 9:
                    self.home_planet = ((9, 9), planet[2])
                elif planet[0] == 90 and planet[1] == 90:
                    self.home_planet = ((90, 90), planet[2])
                break

        ship_id, x, y, hp, fire_cooldown, move_cooldown = ship_data
    
        ships_actions = []

        # On the first turn, determine starting side.
        if self.retreat:
            planet_x, planet_y = self.home_planet[0]
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

        if is_our_home_planet_occupied(obs, self.home_planet) and count_building_resources(obs) < 100:
            planet_x, planet_y = self.home_planet[0]
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

        if self.is_player1:
            if self.is_even_id:
                if self.ready_to_shoot:
                    result_action = Shoot(ship_id=ship_id, direction=1)
                elif x<16:
                    result_action = Move(ship_id=ship_id, direction=0, speed=2)
                elif y<9:
                    result_action = Move(ship_id=ship_id, direction=1, speed=2)
                else:
                    result_action = Move(ship_id=ship_id, direction=1, speed=1)
                    self.ready_to_shoot = True
            else:
                if self.ready_to_shoot:
                    result_action = Shoot(ship_id=ship_id, direction=0)
                elif x>6:
                    result_action = Move(ship_id=ship_id, direction=2, speed=2)
                elif y<16:
                    result_action = Move(ship_id=ship_id, direction=1, speed=2)
                else:
                    result_action = Move(ship_id=ship_id, direction=0, speed=1)
                    self.ready_to_shoot = True
        else:
            if self.is_even_id:
                if self.ready_to_shoot:
                    result_action = Shoot(ship_id=ship_id, direction=3)
                elif x>82:
                    result_action = Move(ship_id=ship_id, direction=2, speed=2)
                elif y<90:
                    result_action = Move(ship_id=ship_id, direction=1, speed=2)
                else:
                    result_action = Move(ship_id=ship_id, direction=3, speed=1)
                    self.ready_to_shoot = True
            else:
                if self.ready_to_shoot:
                    result_action = Shoot(ship_id=ship_id, direction=2)
                elif x<94:
                    result_action = Move(ship_id=ship_id, direction=0, speed=2)
                elif y>85:
                    result_action = Move(ship_id=ship_id, direction=3, speed=2)
                else:
                    result_action = Move(ship_id=ship_id, direction=2, speed=1)
                    self.ready_to_shoot = True
        if increase_move_count:
            self.move_count += 1

        return [result_action]

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
        self.move_count = 0

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
                    #rint(f"our x: {x}, our y: {y}, we can crash into planet: {planet_is_free} at position {planet_x}, {planet_y}")
                    #input("")
                    
        if self.seen_planet is not None:
            #print(f"Our ship is travellign from {x}, {y} to {self.seen_planet}")

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
        #print(self.ship_travelled_in_current_direction)

        return [Move(ship_id=ship_id, direction=self.DIRECTIONS[self.move_direction], speed=2)]

    def destructor(self, obs: dict) -> List[Action]:
        return []


class ShipBackdoor:
    # go right, down, left, down
    TOP_SIDE_DIRECTIONS = (2, 1, 0)
    BOTTOM_SIDE_DIRECTIONS = (0, 3, 2)

    DIRECTIONS = None
    seen_planet = None

    def __init__(self, side: int):
        self.side = side
        self.move_direction = 0
        self.move_count = 0
        self.enemy_planet = (None, None)

        if side == SIDE_LEFT:
            self.DIRECTIONS = self.TOP_SIDE_DIRECTIONS
        else:
            self.DIRECTIONS = self.BOTTOM_SIDE_DIRECTIONS

    def get_actions(self, obs: dict, ship_data: Tuple) -> list[Move]:
        ship_id, x, y, hp, fire_cooldown, move_cooldown = ship_data

        if self.enemy_planet[0] is None:
            if self.side == SIDE_LEFT:
                self.enemy_planet = (90, 90)
            else:
                self.enemy_planet = (9, 9)

        ### -----ATTACKING PLANET-----
        if self.move_count >= 1500:
            planet_x, planet_y = self.enemy_planet
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
        ### -----ATTACKING PLANET-----


        next_move = None
        if self.side == SIDE_LEFT:
            if x != 0 and y == 9:
                next_move= Move(ship_id=ship_id, direction=2, speed=2)
            elif x ==0 and y != 99:
             next_move=Move(ship_id=ship_id, direction=1, speed=2)
            elif y == 99:
                next_move=Move(ship_id=ship_id, direction=0, speed=2)
        else:
            if x != 99 and y == 90:
                next_move=Move(ship_id=ship_id, direction=0, speed=2)
            elif x == 99 and y != 0:
                next_move=Move(ship_id=ship_id, direction=3, speed=2)
            elif y == 0:
                next_move=Move(ship_id=ship_id, direction=2, speed=2)

        self.move_count += 1

        return [next_move]

    def destructor(self, obs: dict) -> List[Action]:
        return []

class Ship:
    LAST_POSITIONS_MAX_COUNT = 40

    def __init__(self, is_even_id: bool, side: int, role: Optional[str] = None):
        self.role = role
        self.side = side
        self.icbm = ShipICBM(side=side)
        self.explorer = ShipExplorer(side=side)
        self.icbmV2 = ShipICBMv2(side=side)
        self.defender = ShipDefender(is_even_id=is_even_id, side=side)
        self.backdoor = ShipBackdoor(side=side)

        self.move_count = 0
        self.last_positions = []

        # By default, the ship should be a ballistic missile
        if not self.role:
            self.role = 'defender' # FIXME: fix me

    start_pos = None

    def get_actions(self, obs: dict, ship_data: Tuple) -> List[Action]:
        ship_id, x, y, hp, fire_cooldown, move_cooldown = ship_data
        if self.start_pos is None:
            targets = [[10, 10], [90, 90]]
            distances = [find_distance(distance, [x,y]) for distance in targets]
            self.start_pos = targets[distances.index(min(distances))]

            self.icbmV2.target =  targets[distances.index(max(distances))]


        if len(self.last_positions) >= self.LAST_POSITIONS_MAX_COUNT:
            self.last_positions.pop(0)

        self.last_positions.append((x, y))

        if len(self.last_positions) >= self.LAST_POSITIONS_MAX_COUNT:
            # Check if the ship is stuck
            min_x, max_x = min(self.last_positions, key=lambda x: x[0])[0], max(self.last_positions, key=lambda x: x[0])[0]
            min_y, max_y = min(self.last_positions, key=lambda x: x[1])[1], max(self.last_positions, key=lambda x: x[1])[1]

            if abs(max_x - min_x) <= 3 and abs(max_y - min_y) <= 3:
                # Ship is stuck
                #print(f"Our ship is stuck! x diff {abs(max_x - min_x)}, y diff {abs(max_y - min_y)}")
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

        self.move_count += 1
        # todo: uncomment when pathfinding is fixed
        #if self.role == 'explorer' and self.move_count > 100:
        #    self.role = 'icbmv2'

        if self.role == 'backdoor' and self.move_count >= 200:
            self.role = 'icbmv2'
        
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
        elif self.role == 'defender':
            return self.defender
        elif self.role == 'backdoor':
            return self.backdoor
        else:
            raise ValueError(f"Invalid role: {self.role}")


class Agent:
    side = None 
    def __init__(self, side: int):
        """ 
        :param side: Indicates whether the player is on left side (0) or right side (1)
        """
        if side == 2:
            side = 0
        self.side = side
        self.ships = {}
        self.home_planet = (None, None)
        self.first_run = True
        self.constructed_ships = 0
        self.explorer_created = False 
        self.defenders = {"even": None, "odd": None}
        self.explorer = None
        """Tuple - (x, y), default value"""
        self.icbm_created = False
    

    def get_role(self, ship_id: int):
        # TODO: Create defenders if 2 not present
        if ship_id == 0:
            return 'icbm', False
        elif ship_id == 1:
            return 'icbm', False

        if self.defenders['even'] is None:
            return 'defender', True

        """
        if self.defenders['even'] is None:
            return 'defender', True
        elif self.defenders['odd'] is None:
            return 'defender', False
        
        if not self.explorer_created:
            self.explorer_created = True
            return 'explorer', False
        """
        #self.icbm_created = True
        if self.constructed_ships % 3 == 0 and self.explorer is None:
            return 'explorer', False
        return 'icbm', False

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
                role, is_even_id = self.get_role(self.constructed_ships)
                self.ships[ship_id] = Ship(is_even_id=is_even_id, side=self.side, role=role)
                if role == 'defender':
                    if is_even_id:
                        self.defenders['even'] = ship_id
                    if not is_even_id:
                        self.defenders['odd'] = ship_id
                if role == 'explorer':
                    self.explorer = ship_id
                self.constructed_ships += 1
            visited_ids[ship_id] = True

            ship = self.ships[ship_id]
            actions.extend(ship.get_actions(obs, ship_data))

        # If we didn't process some ships from the map, they must have been destroyed

        for ship_id, visited in visited_ids.items():
            if not visited:
                destroyed_ship = self.ships.pop(ship_id, None)
                action = destroyed_ship.destructor(obs) if destroyed_ship else None
                actions.extend(action)

                if self.defenders['even'] == ship_id:
                    self.defenders['even'] = None
                if self.defenders['odd'] == ship_id:
                    self.defenders['odd'] = None
                if self.explorer == ship_id:
                    self.explorer = None
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

        """
        # If we don't have a ship, we must build one 
        if ships_count == 0:
            construction_max = max(1, construction_max)

        # Let's always build ships if we have safety net
        if can_build_ship(obs):
            #print("cranking out a ship just because we can")
            construction_max = maximum_ships_we_can_build(obs)

        if is_our_home_planet_occupied(obs, self.home_planet):
            #print("Our home planet is occupied - want to crank out a ship!")
            construction_max = maximum_ships_we_can_build(obs)
        """
        construction_max = max(1, construction_max)
        # ALWAYS BUILD SHIPS!!!!!!!!
        # MORE SHIPS!

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
