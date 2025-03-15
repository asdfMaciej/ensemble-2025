import pytest 


# Import all the functions from utils.py
from task_5.utils.utils import *

class TestAgent:
    pass

def test_constructor():
    agent = TestAgent()
    assert agent is not None
    constructor(agent)
    # No error happened - assert in pytest

def test_path_finding():
    # UP - 0
    # RIGHT - 1
    # DOWN - 2
    # LEFT - 3
    map_data = [[FieldType.SPACE, FieldType.ASTEROID, FieldType.ASTEROID], [FieldType.SPACE, FieldType.IONIZED_FIELD, FieldType.ASTEROID], [FieldType.IONIZED_FIELD, FieldType.PLANET_PLAYER_1, FieldType.SPACE]]

    test_cases = [
        {'start': [0, 0], 'expected': (2,2)},  # Expected move: DOWN, 2
        {'start': [2, 0], 'expected': (1, 2)},  # Expected move: LEFT
    ]

    for test_case in test_cases:
        path = find_path(test_case['start'], [2, 2], map_data)
        assert path == test_case['expected']


def test_resource_counting():
    assert count_building_resources({"resources": [50, 30, 120, 150]}) == 30
    assert count_building_resources({"resources": [0, 0, 0, 0]}) == 0
    assert count_building_resources({"resources": [1, 1, 1, 1]}) == 1
    assert count_building_resources({"resources": [1, 2, 3, 4]}) == 1
    assert count_building_resources({"resources": [40, 20, 10, 5]}) == 5
    assert count_building_resources({"resources": [10, 10, 10, 100]}) == 10

def test_can_build_ship():
    assert can_build_ship({"resources": [50, 30, 120, 150]}) == False
    assert can_build_ship({"resources": [0, 0, 0, 0]}) == False
    assert can_build_ship({"resources": [1, 1, 1, 1]}) == False
    assert can_build_ship({"resources": [1, 2, 3, 4]}) == False
    assert can_build_ship({"resources": [40, 20, 10, 5]}) == False
    assert can_build_ship({"resources": [10, 10, 10, 100]}) == False
    assert can_build_ship({"resources": [99, 99, 99, 99]}) == False 
    assert can_build_ship({"resources": [100, 100, 100, 100]}) == True

def test_maximum_ships_we_can_build_with_safety_net():
    assert maximum_ships_we_can_build_with_safety_net({"resources": [50, 30, 120, 150]}) == 0
    assert maximum_ships_we_can_build_with_safety_net({"resources": [0, 0, 0, 0]}) == 0
    assert maximum_ships_we_can_build_with_safety_net({"resources": [1, 1, 1, 1]}) == 0
    assert maximum_ships_we_can_build_with_safety_net({"resources": [1, 2, 3, 4]}) == 0
    assert maximum_ships_we_can_build_with_safety_net({"resources": [40, 20, 10, 5]}) == 0
    assert maximum_ships_we_can_build_with_safety_net({"resources": [10, 10, 10, 100]}) == 0
    assert maximum_ships_we_can_build_with_safety_net({"resources": [99, 99, 99, 99]}) == 0 
    assert maximum_ships_we_can_build_with_safety_net({"resources": [100, 100, 100, 100]}) == 0
    assert maximum_ships_we_can_build_with_safety_net({"resources": [199, 199, 199, 199]}) == 0 
    assert maximum_ships_we_can_build_with_safety_net({"resources": [200, 200, 200, 200]}) == 1

def test_can_build_ship_with_safety_net():
    assert can_build_ship_with_safety_net({"resources": [50, 30, 120, 150]}) == False
    assert can_build_ship_with_safety_net({"resources": [0, 0, 0, 0]}) == False
    assert can_build_ship_with_safety_net({"resources": [1, 1, 1, 1]}) == False
    assert can_build_ship_with_safety_net({"resources": [1, 2, 3, 4]}) == False
    assert can_build_ship_with_safety_net({"resources": [40, 20, 10, 5]}) == False
    assert can_build_ship_with_safety_net({"resources": [10, 10, 10, 100]}) == False
    assert can_build_ship_with_safety_net({"resources": [99, 99, 99, 99]}) == False
    assert can_build_ship_with_safety_net({"resources": [100, 100, 100, 100]}) == False
    assert can_build_ship_with_safety_net({"resources": [199, 199, 199, 199]}) == False
    assert can_build_ship_with_safety_net({"resources": [200, 200, 200, 200]}) == True

