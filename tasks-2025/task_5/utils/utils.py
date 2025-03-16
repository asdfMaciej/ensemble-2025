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
        print("warning - home planet not detected")
        return False 

    for planet in obs['planets_occupation']:
        if planet[0] == home_planet[0][0] and planet[1] == home_planet[0][1]:
            return planet[2] != home_planet[1]

    print("error - home planet not found")
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
        return 2
    elif field == FieldType.IONIZED_FIELD:
        return -10
    elif not field.is_occupied() and field.is_planet() and field :
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
    if depth == 0:
        return ([], find_distance(start, end))

    num_rows = len(map_data)
    num_cols = len(map_data[0]) if num_rows > 0 else 0
    best_seq = None
    best_cost = float('inf')

    # Determine possible jump distances.
    possible_jumps = [1, 2]
    if FieldType.decode_tile(map_data[start[0]][start[1]]) == FieldType.IONIZED_FIELD:
        possible_jumps.append(3)

    # Define a factor to heavily penalize walking away from the target.
    backward_penalty_factor = 100

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
            # Out-of-bounds or already visited? Skip this move.
            if x < 0 or x >= num_rows or y < 0 or y >= num_cols or (x, y) in visited:
                continue
            else:
                # Calculate the Manhattan distance from the new position and the current position.
                new_distance = find_distance(new_pos, end)
                current_distance = find_distance(start, end)
                # Immediate cost: distance + field weight minus jump bonus.
                immediate_cost = (new_distance +
                                  field_weight(FieldType.decode_tile(map_data[x][y]), new_distance) - jump)
                # If moving away from the target, add a penalty proportional to the difference.
                if new_distance > current_distance:
                    immediate_cost += (new_distance - current_distance) * backward_penalty_factor

            # If the new position is the target, return immediately.
            if new_pos == end:
                return ([new_pos], -float('inf'))

            # Recurse: update visited (copy to avoid side effects) and simulate further moves.
            new_visited = set(visited)
            new_visited.add((x, y))
            subsequent_moves, subsequent_cost = search_move(new_pos, end, map_data, new_visited, depth - 1)
            total_cost = immediate_cost + subsequent_cost

            # Update best sequence, with random tie-breaking if costs are equal.
            if total_cost < best_cost:
                best_cost = total_cost
                best_seq = [(direction, jump)] + subsequent_moves
            elif total_cost == best_cost:
                if random.choice([True, False]):
                    best_seq = [(direction, jump)] + subsequent_moves

    if best_seq is None:
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
        return [visited, best_seq[0]]
    else:
        return [visited, (0, 0)]
