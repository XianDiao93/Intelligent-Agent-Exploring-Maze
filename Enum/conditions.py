from enum import Enum

class Knowledge(Enum):
    FULLY_KNOWN = 0
    PARTIALLY_KNOWN = 1
    UNKNOWN = 2

class Energy(Enum):
    UNLIMITED = 0
    LIMITED = 1