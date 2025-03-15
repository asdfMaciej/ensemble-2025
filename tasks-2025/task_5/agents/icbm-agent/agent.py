from task_5.utils.utils import * # DO NOT TOUCH THIS FIRST LINE!!!
import random
from dataclasses import dataclass
from typing import Optional, Tuple, List
from abc import ABC

SIDE_LEFT = 0
SIDE_RIGHT = 1

class Action(ABC):
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

class ShipICBM: 
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


    def decode_tile(self, tile_value: int) -> dict:
        """
        Decode an 8-bit encoded map tile.

        Parameters:
            tile_value (int): The encoded value of the tile.
                              -1 indicates the tile is not visible.

        Returns:
            dict: Contains:
                  - 'visible': bool, True if the tile is visible.
                  - 'tile_type': int, the lower 6 bits representing the tile type.
                  - 'owned_by_player1': bool, True if bit 6 is set.
                  - 'owned_by_player2': bool, True if bit 7 is set.
        """
        if tile_value == -1:
            return {"visible": False}

        tile_type = tile_value & 63
        owned_by_player1 = (tile_value & 64) == 64
        owned_by_player2 = (tile_value & 128) == 128

        return {
            "visible": True,
            "tile_type": tile_type,
            "owned_by_player1": owned_by_player1,
            "owned_by_player2": owned_by_player2
        }

    def find_available_planets(self, map_data: list) -> list:
        """
        Find available planets on the map and return their coordinates.
        (A planet is defined as a visible tile with tile_type 9 that is not owned.)
        """
        available_planets = []
        for row_idx, row in enumerate(map_data):
            for col_idx, tile in enumerate(row):
                if tile == -1:
                    continue
                tile_info = self.decode_tile(tile)
                if tile_info["visible"] and tile_info["tile_type"] == 9 and not (
                        tile_info["owned_by_player1"] or tile_info["owned_by_player2"]):
                    available_planets.append((row_idx, col_idx))
        return available_planets

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

class ShipExplorer:
    def __init__(self, side: int):
        self.side = side 

    def get_actions(self, obs: dict, ship_data: Tuple) -> List[Optional[Action]]:
        ship_id, x, y, hp, fire_cooldown, move_cooldown = ship_data

        return []

    def destructor(self, obs: dict) -> List[Action]:
        return []


class Ship: 
    def __init__(self, side: int, role: Optional[str] = None):
        self.role = role
        self.side = side 
        self.icbm = ShipICBM(side=side)
        self.explorer = ShipExplorer(side=side)

        # By default, the ship should be a ballistic missile
        if not self.role:
            self.role = 'icbm'
    
    def get_actions(self, obs: dict, ship_data: Optional[Tuple]) -> List[Action]:
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
        else:
            raise ValueError(f"Invalid role: {self.role}")

class Agent:
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
                pass # ship decided to do nothing
        
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
