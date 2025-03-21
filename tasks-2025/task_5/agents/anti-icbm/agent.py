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

class ShipDefender: 
    def __init__(self, side: int):
        self.side = side 

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

        if self.is_player1:
            if ship_id%2 == 0:
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
            if ship_id%2 == 0:
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

    def get_action(self, obs: dict) -> dict:
        ships_count = len(obs['allied_ships'])
        # print(f"Ships count: {ships_count}")
        
        actions: List[Action] = []

        visited_ids = {ship_id: False for ship_id in self.ships.keys()}
        for n, ship_data in enumerate(obs['allied_ships']):
            ship_id = ship_data[0]
            if ship_id not in self.ships:
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
        if ships_count < 4:
            construction_max = 1
        else:
            construction_max = 0
            
        

        # Let's always build ships if we have safety net
        # if can_build_ship_with_safety_net(obs):
        #     construction_max = max(1, construction_max)

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
