from task_5.utils.utils import * # DO NOT TOUCH THIS FIRST LINE!!!
import random
from dataclasses import dataclass
from typing import Optional, Tuple 

@dataclass
class Shoot: 
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
class Move:
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
class Build:
    ships_count: int 
    """
    0-10
    """

class ShipICBM: 
    def __init__(self):
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

    def get_action(self, obs: dict, ship_data: Optional[Tuple]) -> dict:
        if not ship_data: 
            return {
                "ships_actions": [],
                "construction": 1
            }

        ship_id, x, y, hp, fire_cooldown, move_cooldown = ship_data
    
        ships_actions = []
        ships = obs['allied_ships']
        
        """
        # If no ships, try to construct one.
        if len(ships) == 0:
            return {
                "ships_actions": [],
                "construction": 1
            }
        """

        # On the first turn, determine starting side.
        if self.is_first_turn:
            # Use the first allied ship to decide.
            ship_id, x, y, hp, fire_cooldown, move_cooldown = ships[0]
            # Here we assume that if x < 50 the player starts on top; otherwise on bottom.
            if x < 50:
                self.is_player1 = True
                self.current_data_points = self.data_points[0]
            else:
                self.is_player1 = False
                self.current_data_points = self.data_points[1]
            self.is_first_turn = False

        increase_move_count = True
        # Use different logic for top (is_player1) vs bottom players.
        if self.is_player1:
            # For top players: lower x values.
            if x < self.current_data_points['threshold1']:
                # If x is very low, use a move from our move list with direction 2.
                move_code = self.current_data_points['moves'][self.move_count % len(self.current_data_points['moves'])]
                ships_actions.append([ship_id, 0, move_code, 2])
            elif self.current_data_points['threshold1'] <= x < self.current_data_points['threshold2']:
                move_code = self.current_data_points['moves'][self.move_count % len(self.current_data_points['moves'])]
                ships_actions.append([ship_id, 0, move_code, 1])
            else:  # x >= threshold2
                ships_actions.append([ship_id, 0, 1, 2])
                increase_move_count = False 
        else:
            # For bottom players: higher x values.
            if x > self.current_data_points['threshold1']:
                move_code = self.current_data_points['moves'][self.move_count % len(self.current_data_points['moves'])]
                ships_actions.append([ship_id, 0, move_code, 2])
            elif self.current_data_points['threshold2'] < x <= self.current_data_points['threshold1']:
                move_code = self.current_data_points['moves'][self.move_count % len(self.current_data_points['moves'])]
                ships_actions.append([ship_id, 0, move_code, 1])
            else:  # x <= threshold2
                ships_actions.append([ship_id, 0, 3, 2])
                increase_move_count = False 

        if increase_move_count:
            self.move_count += 1

        return {
            "ships_actions": ships_actions,
            "construction": 0
        }

class ShipExplorer:
    def __init__(self):
        pass 

    def get_action(self, obs: dict, ship_data: Optional[Tuple]) -> dict:
        if ship_data:
            ship_id, x, y, hp, fire_cooldown, move_cooldown = ship_data

        return {
            "ships_actions": [],
            "construction": 0
        }


class Ship: 
    def __init__(self, role: Optional[str] = None):
        self.role = role
        self.icbm = ShipICBM()
        self.explorer = ShipExplorer()
    
    def get_action(self, obs: dict, ship_data: Optional[Tuple]) -> dict:
        # todo: starting role for new ship
        return self.icbm.get_action(obs, ship_data)

class Agent:
    def __init__(self):
        self.ship = Ship()

    def get_action(self, obs: dict) -> dict:
        ship_data = None if not len(obs['allied_ships']) else obs['allied_ships'][0]
        return self.ship.get_action(obs, ship_data)
    

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
