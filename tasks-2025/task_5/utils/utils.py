from enum import IntEnum
from matplotlib.style.core import available


def constructor(self: object) -> None:
    self.foo = "bar"

def outside_function(self: object) -> None:
    print(self.foo)

def add(a: int, b: int) -> int:
    return a + b

def count_building_resources(obs: dict) -> int:
    resources = []
    for resource_value in obs['resources']:
        resources.append(resource_value)
    
    return min(resources)

def can_build_ships(obs: dict, ship_count: int = 1) -> bool:
    # TODO: check if it's actually 99 due to the game logic ordering thingy
    building_resources = count_building_resources(obs)
    return building_resources >= (ship_count * 100)

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

def is_our_home_planet_occupied(obs: dict) -> bool:
    return False  # TODO - implement this and react to it by creating a ship

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


def field_weight(field: FieldType) -> int:
        weights = {
            FieldType.SPACE: 0,
            FieldType.ASTEROID: 4,
            FieldType.IONIZED_FIELD: -2,
            FieldType.PLANET_PLAYER_1: 100,
            FieldType.PLANET_PLAYER_2: 100,
        }

        return weights[field]


def find_path(start: [int, int], end: [int, int], map_data: list[list[int]], visited=None) -> (int, int):
    """
    Determine the best move from start to end on a grid with weighted fields,
    while penalizing longer jump distances and avoiding revisiting cells.

    Moves:
      0: UP    -> (start[0] - jump, start[1])
      1: RIGHT -> (start[0], start[1] + jump)
      2: DOWN  -> (start[0] + jump, start[1])
      3: LEFT  -> (start[0], start[1] - jump)

    The cost for a move is calculated as:
         jump_penalty + find_distance(move, end) + field_weight(move's cell)
    with a jump_penalty equal to the jump length.

    A move going out-of-bounds or to a previously visited cell gets an infinite cost.

    Args:
        start (list[int, int]): Current position.
        end (list[int, int]): Target position.
        map_data (list[list[int]]): Grid with cell weights.
        visited (set, optional): Set of visited cells as (x, y) tuples.

    Returns:
        (int, int): A tuple (direction, jump) for the best move.
    """
    if visited is None:
        visited = set()
    # Mark the current cell as visited
    visited.add(tuple(start))

    # Determine possible jump distances.
    possible_jumps = [1, 2]
    if FieldType.decode_tile(map_data[start[0]][start[1]]) == FieldType.IONIZED_FIELD:
        possible_jumps.append(3)

    # For each allowed jump, define possible moves in order: UP, RIGHT, DOWN, LEFT.
    possible_moves = [(
        [
            (start[0] - x, start[1]),  # UP
            (start[0], start[1] + x),  # RIGHT
            (start[0] + x, start[1]),  # DOWN
            (start[0], start[1] - x)  # LEFT
        ],
        x  # jump distance
    ) for x in possible_jumps]

    num_rows = len(map_data)
    num_cols = len(map_data[0]) if num_rows > 0 else 0

    best_moves = []

    for moves, jump in possible_moves:
        costs = []
        for move in moves:
            x, y = move
            if x < 0 or x >= num_rows or y < 0 or y >= num_cols or (x, y) in visited:
                cost = float('inf')
            else:
                cost = find_distance(move, end) + field_weight(FieldType.decode_tile(map_data[x][y])) - jump
            costs.append(cost)
        best_direction_index = min(range(len(costs)), key=lambda i: costs[i])
        best_cost = costs[best_direction_index]
        best_moves.append((best_direction_index, jump, best_cost))

    # Choose the overall best move among all jump groups.
    best_overall = min(best_moves, key=lambda t: t[2])
    best_direction, best_step, _ = best_overall

    return (best_direction, best_step)
