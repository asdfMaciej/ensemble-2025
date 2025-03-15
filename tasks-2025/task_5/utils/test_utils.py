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






