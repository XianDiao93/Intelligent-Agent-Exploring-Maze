from enum import Enum

class TileType(Enum):
    START = 0
    GOAL = 1
    PATH = 2
    LIGHT = 3
    REWARD = 4