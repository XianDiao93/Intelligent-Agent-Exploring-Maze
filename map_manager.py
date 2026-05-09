import random
import os
from Utils.utils import MAP_TYPES
from Utils.config import MAP_PATH
from maze import Maze
from Enum.tiles import TileType

# public functions
# public interface for loading a map from file, which returns a maze object
def get_map(filename):

    lines = load_lines(filename)
    map_data = convert_to_map(lines)
    maze = Maze.convert_to_maze(map_data)

    return maze

# public interface for creating a new map, which generates a maze and saves it to file
def create_map(rows, cols, isSave = True, seed = None, map_type = MAP_TYPES[0]):
    maze = generate_map(rows, cols, seed, map_type)

    if isSave:

        index = 0

        while True:
            filename = f"{index}.map"
            filepath = os.path.join(MAP_PATH, filename)

            if not os.path.exists(filepath):
                break

            index += 1

        save_lines(maze, filename)

    return maze




# private functions
# convert lines from file to map(a 3d list of cell states)
def convert_to_map(lines):
    map_data = []

    for line in lines:
        row_data = []

        for cell_data in line:
            if len(cell_data) != 5:
                raise ValueError(f"Invalid cell data: {cell_data}")

            cell_state = []

            for char in cell_data:
                if not char.isdigit():
                    raise ValueError(f"Invalid character in cell data: {cell_data}")

                cell_state.append(int(char))

            row_data.append(cell_state)

        map_data.append(row_data)

    return map_data

# convert map to lines for saving to file
def convert_to_lines(map_data):

    lines = []

    for row in map_data:

        line_parts = []

        for cell in row:

            if len(cell) != 5:
                raise ValueError(f"Invalid cell format: {cell}")

            cell_string = ""

            for value in cell:
                cell_string += str(value)

            line_parts.append(cell_string)

        line = " ".join(line_parts)

        lines.append(line)

    return lines

# maze generation algorithms
def generate_map(rows, cols, seed=None, map_type=MAP_TYPES[0]):

    if seed is not None:
        random.seed(seed)

    maze = Maze(rows, cols)

    # choose start and goal
    start_cell = maze.get_cell(0, 0)
    goal_cell = maze.get_cell(rows - 1, cols - 1)

    start_cell.tileType = TileType.START
    goal_cell.tileType = TileType.GOAL

    # DFS stack
    current = start_cell
    current.isVisited = True

    stack = [current]

    while stack:

        current = stack[-1]

        unvisited = maze.get_unvisited_neighbours(current)

        if unvisited:
            next_cell = random.choice(unvisited)

            maze.connect_cells(current, next_cell)

            next_cell.isVisited = True
            stack.append(next_cell)

        else:
            stack.pop()

    # optional special tiles
    available_tiles = []

    for row in range(rows):
        for col in range(cols):
            cell = maze.get_cell(row, col)

            if cell.tileType == TileType.PATH:
                available_tiles.append(cell)

    if TileType.LIGHT in map_type and available_tiles:
        light_cell = random.choice(available_tiles)
        light_cell.tileType = TileType.LIGHT
        available_tiles.remove(light_cell)

    if TileType.REWARD in map_type and available_tiles:
        reward_cell = random.choice(available_tiles)
        reward_cell.tileType = TileType.REWARD
        available_tiles.remove(reward_cell)

    return maze

# save lines to file, filename should be in the format of "map_name.map"
def save_lines(maze, filename):
    map_data = maze.convert_to_map()
    lines = convert_to_lines(map_data)

    try:
        with open(os.path.join(MAP_PATH, filename), "w") as file:
            for line in lines:
                file.write(line + "\n")
    except Exception as e:
        print(f"Error while saving map: {e}")

# load lines from file, filename should be in the format of "map_name.map"
def load_lines(filename):
    lines = []

    try:
        with open(os.path.join(MAP_PATH, filename), "r") as file:

            for line in file:
                line = line.strip()

                if line == "":
                    continue

                row = line.split()
                lines.append(row)
    except FileNotFoundError:
        print(f"Map file not found: {filename}")
    except PermissionError:
        print(f"No permission to read file: {filename}")
    except Exception as e:
        print(f"Error while loading map: {e}")

    return lines