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


