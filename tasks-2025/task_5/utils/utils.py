
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