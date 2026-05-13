from Utils.utils import MAP_TYPES
from Enum.robots import Types
from Enum.conditions import Knowledge, Energy

MAP_PATH = "maps/"

LOW_ENERGY_THRESHOLD = 0.4
LIGHT_SEEK_PROBABILITY = 0.7        # 70% chance to go to light when low on energy
EXPLORATION_PROBABILITY = 0.4       # 40% chance to access a worse cell for exploration (when not seeking light)

# Experiment configuration
DEFAULT_EXPERIMENT_CONFIG = {
    # robot configuration
    "num_robots": 100,
    "robot_type": Types.REACTIVE,
    "use_energy": False,
    "energy_condition": Energy.UNLIMITED,
    "energy_capacity": 1000,
    "energy_per_step": 1,
    "energy_intensity": 5,

    # simulation configuration
    "max_steps": 5000,
    "speed": 5,

    # map configuration
    "file_name": None,
    "rows": 15,
    "cols": 15,
    "map_type": MAP_TYPES[0],
    "num_of_lights": 4,

    # knowledge configuration
    "knowledge_condition": Knowledge.FULLY_KNOWN,

    # visualization configuration
    "title": "Maze Experiment",
}