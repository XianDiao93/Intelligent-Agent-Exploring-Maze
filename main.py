# main.py
from experiment import Experiment
from Enum.conditions import Energy, Knowledge
from Enum.robots import Types
from Utils.utils import MAP_TYPES

if __name__ == "__main__":
    experiment = Experiment(
        # Experiment configuration
        # speed = 1  -> 0.1 s per step
        # speed = 2  -> 0.05 s per step
        # speed = 10 -> 0.01 s per step
        max_steps = 5000,
        speed = 5,
        title="Maze Experiment",

        # Map configuration
        # if you want to use randomly generated maps, set file_name to None and specify rows, cols, map_type, and num_of_lights as you want.
        # if you want to use pre-designed maps, 0 and 1 is 5*5 maps, 2 and 3 is 10*10 maps, 4 and 5 is 15*15 maps.
        file_name = "5.map",   # e.g., "0.map" for a 5*5 map, "2.map" for a 10*10 map, etc.
        rows = 15,
        cols = 20,
        map_type = MAP_TYPES[1],
        num_of_lights = 4,

        # Robot configuration
        robot_type = Types.MEMORY,
        num_robots = 100,

        # Knowledge configuration
        knowledge_condition = Knowledge.UNKNOWN,

        # Energy configuration
        energy_condition = Energy.LIMITED,
        energy_capacity = 1000,
        energy_per_step = 1,
        energy_intensity = 5,
    )

    experiment.run()