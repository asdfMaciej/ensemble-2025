from enum import IntEnum

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


def field_weight(field: FieldType) -> int:
    # Emulating switch-case using if/elif statements
    if field == FieldType.SPACE:
        return 0
    elif field == FieldType.ASTEROID:
        return float('inf')
    elif field == FieldType.IONIZED_FIELD:
        return -5
    elif not field.is_occupied() and field.is_planet():
        return float('inf')
    elif field == FieldType.UNDEFINED:
        return 0
    else:
        # Default case
        return 0


def find_distance(point1: [int, int], point2: [int, int]) -> int:
    return (abs(point1[0] - point2[0])**2 + abs(point1[1] - point2[1])**2) ** 0.5


import random


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
                immediate_cost = (find_distance(new_pos, end) +
                                  field_weight(FieldType.decode_tile(map_data[x][y])) - jump)
            if immediate_cost == float('inf'):
                continue

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
        return best_seq[0]
    else:
        # No valid move found. You may choose to return None or a default value.
        return (0, 0)




