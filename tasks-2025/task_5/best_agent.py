
from enum import IntEnum
import random

def constructor(self: object) -> None:
    self.foo = "bar"

def outside_function(self: object) -> None:
    print(self.foo)

def add(a: int, b: int) -> int:
    return a + b

def count_building_resources(obs: dict) -> int:
    resources = []
    for i in range(4):
        resources.append(obs['resources'][i])

    return min(resources)

def can_build_ships(obs: dict, ship_count: int = 1) -> bool:
    # TODO: check if it's actually 99 due to the game logic ordering thingy
    building_resources = count_building_resources(obs)
    result = building_resources >= (ship_count * 100)
    #print(f"Checking if i can build {ship_count} ships with {building_resources} resources - {result}")
    return result

def can_build_ship(obs: dict) -> bool:
    return can_build_ships(obs, 1)

def can_build_ship_with_safety_net(obs: dict) -> bool:
    # Save 100 resources for an emergency ship
    return can_build_ships(obs, 2)

def maximum_ships_we_can_build(obs: dict) -> int:
    building_resources = count_building_resources(obs)
    return max(0, building_resources // 100)

def maximum_ships_we_can_build_with_safety_net(obs: dict) -> int:
    building_resources = count_building_resources(obs)
    return max(0, (building_resources - 100) // 100)

def is_our_home_planet_occupied(obs: dict, home_planet) -> bool:
    """Tuple - (x, y), default value"""
    if home_planet[0] is None:
        #print("warning - home planet not detected")
        return False 

    for planet in obs['planets_occupation']:
        if planet[0] == home_planet[0][0] and planet[1] == home_planet[0][1]:
            return planet[2] != home_planet[1]

    #print("error - home planet not found")
    return False

class FieldType(IntEnum):
    OCCUPIED_PLAYER1 = 0b01000000
    OCCUPIED_PLAYER2 = 0b10000000

    SPACE = 0b00000000
    PLANET_NO_RESOURCES = 0b00000001
    ASTEROID = 0b00000010
    ROUGH_LAND = 0b00000011
    IONIZED_FIELD = 0b00000100

    RESOURCE_1 = 0b00001001  # 9

    RESOURCE_2 = 0b00010001  # 17

    RESOURCE_3 = 0b00011001  # 25

    RESOURCE_4 = 0b00111001  # 57

    UNDEFINED = -1

    PLANET_PLAYER_1 = PLANET_NO_RESOURCES | OCCUPIED_PLAYER1  # 65
    PLANET_PLAYER_2 = PLANET_NO_RESOURCES | OCCUPIED_PLAYER2  # 129

    PLANET_RESOURCE_1_PLAYER1 = RESOURCE_1 | OCCUPIED_PLAYER1
    PLANET_RESOURCE_2_PLAYER1 = RESOURCE_2 | OCCUPIED_PLAYER1
    PLANET_RESOURCE_3_PLAYER1 = RESOURCE_3 | OCCUPIED_PLAYER1
    PLANET_RESOURCE_4_PLAYER1 = RESOURCE_4 | OCCUPIED_PLAYER1

    PLANET_RESOURCE_1_PLAYER2 = RESOURCE_1 | OCCUPIED_PLAYER2  # 137
    PLANET_RESOURCE_2_PLAYER2 = RESOURCE_2 | OCCUPIED_PLAYER2  # 137
    PLANET_RESOURCE_3_PLAYER2 = RESOURCE_3 | OCCUPIED_PLAYER2  # 153
    PLANET_RESOURCE_4_PLAYER2 = RESOURCE_4 | OCCUPIED_PLAYER2



    UNDEFINED_PLAYER_1 = 0b01000011  # 67
    UNDEFINED_PLAYER_2 = 0b10000011  # 131

    def is_occupied(self):
        return (self & FieldType.OCCUPIED_PLAYER1) or (self & FieldType.OCCUPIED_PLAYER2)

    def is_planet(self) -> bool:
        return (self & 0b00000001) == FieldType.PLANET_NO_RESOURCES

    @classmethod
    def decode_tile(cls, value: int) -> 'FieldType':
        try:
            return cls(value)
        except ValueError:
            return None

def find_distance(point1: [int, int], point2: [int, int]) -> int:
    return abs(point1[0] - point2[0]) + abs(point1[1] - point2[1])


def field_weight(field: FieldType, distance) -> int:
    # Emulating switch-case using if/elif statements
    if field == FieldType.SPACE:
        return 0
    elif field == FieldType.ASTEROID:
        return 70
    elif field == FieldType.IONIZED_FIELD:
        return -20
    elif field.is_planet() and distance > 10:
        return 1200
    elif not field.is_occupied() and field.is_planet():
        return 9000
    elif field == FieldType.UNDEFINED:
        return 0
    else:
        # Default case
        return 0

def search_move(start, end, map_data, visited, depth):
    """
    Recursively search for a sequence of moves from start toward end.

    Returns a tuple:
      (list of moves [(direction, jump), ...], cumulative cost)

    Base case: when depth is 0, no further moves are simulated.
    """
    # Base case: no further simulation
    if depth == 0:
        # Use the Manhattan distance as a heuristic cost.
        return ([], find_distance(start, end))

    num_rows = len(map_data)
    num_cols = len(map_data[0]) if num_rows > 0 else 0
    best_seq = None
    best_cost = float('inf')

    # Determine possible jump distances.
    possible_jumps = [1, 2]
    # Check if current cell is ionized.
    if FieldType.decode_tile(map_data[start[0]][start[1]]) == FieldType.IONIZED_FIELD:
        possible_jumps.append(3)

    # For each jump, try all four directions.
    # Moves: 0: UP, 1: RIGHT, 2: DOWN, 3: LEFT.
    for jump in possible_jumps:
        moves = [
            ((start[0] + jump, start[1]), 0),  # UP
            ((start[0], start[1] + jump), 1),  # RIGHT
            ((start[0] - jump, start[1]), 2),  # DOWN
            ((start[0], start[1] - jump), 3)   # LEFT
        ]
        for (new_pos, direction) in moves:
            x, y = new_pos
            # Out-of-bounds or already visited? Assign infinite cost.
            if x < 0 or x >= num_rows or y < 0 or y >= num_cols or (x, y) in visited:
                immediate_cost = float('inf')
            else:
                # Immediate cost: weighted Manhattan distance plus cell weight, minus jump bonus.
                distance = find_distance(new_pos, end)
                immediate_cost = (find_distance(new_pos, end) +
                                  field_weight(FieldType.decode_tile(map_data[x][y]), distance) - jump)
            if immediate_cost == float('inf'):
                continue
            if new_pos == end:
                return ([new_pos], -float('inf'))

            # Recurse: update visited (copy to avoid side effects) and simulate further moves.
            new_visited = set(visited)
            new_visited.add((x, y))
            subsequent_moves, subsequent_cost = search_move(new_pos, end, map_data, new_visited, depth - 1)
            total_cost = immediate_cost + subsequent_cost

            # Update best sequence, using random tie-breaking if costs are equal.
            if total_cost < best_cost:
                best_cost = total_cost
                best_seq = [(direction, jump)] + subsequent_moves
            elif total_cost == best_cost:
                if random.choice([True, False]):
                    best_seq = [(direction, jump)] + subsequent_moves

    if best_seq is None:
        # No valid move found; return an empty sequence and use the heuristic cost.
        return ([], find_distance(start, end))

    return (best_seq, best_cost)


def find_path(start: [int, int], end: [int, int], map_data: list[list[int]], visited=None, depth=4) -> (int, int):
    """
    Determine the best move from start to end on a grid with weighted fields,
    while penalizing longer jump distances and avoiding revisiting cells.
    Additionally, this version simulates 'depth' moves into the future to choose the best immediate move.

    Moves:
      0: UP    -> (start[0] - jump, start[1])
      1: RIGHT -> (start[0], start[1] + jump)
      2: DOWN  -> (start[0] + jump, start[1])
      3: LEFT  -> (start[0], start[1] - jump)

    The cost for a move is calculated as:
         (find_distance(move, end) * 2 + field_weight(move's cell) - jump)
    A move going out-of-bounds or to a previously visited cell gets an infinite cost.

    Args:
        start (list[int, int]): Current position.
        end (list[int, int]): Target position.
        map_data (list[list[int]]): Grid with cell weights.
        visited (set, optional): Set of visited cells as (x, y) tuples.
        depth (int, optional): Number of future steps to simulate.

    Returns:
        (int, int): A tuple (direction, jump) for the best immediate move.
    """
    if visited is None:
        visited = set()
    visited.add(tuple(start))

    best_seq, _ = search_move(start, end, map_data, visited, depth)
    if best_seq:
        # Return the immediate move (direction, jump) from the best sequence.
        return [visited,best_seq[0]]
    else:
        # No valid move found. You may choose to return None or a default value.
        return [visited, (0, 0)]




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
    LAST_POSITIONS_MAX_COUNT = 20

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
        #if self.role == 'explorer' and self.move_count == 250:
        #    self.role = 'icbmv2'

        if self.role == 'backdoor' and self.move_count == 200:
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
        """Tuple - (x, y), default value"""
        self.icbm_created = False
    

    def get_role(self, ship_id: int):
        # TODO: Create defenders if 2 not present
        if ship_id == 0:
            return 'icbm', False
        elif ship_id == 1:
            return 'backdoor', False

        if self.defenders['even'] is None:
            return 'defender', True
        elif self.defenders['odd'] is None:
            return 'defender', False
        
        if not self.explorer_created:
            self.explorer_created = True
            return 'explorer', False

        #self.icbm_created = True
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
