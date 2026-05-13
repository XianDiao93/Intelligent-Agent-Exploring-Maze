from cell import Cell
from Enum.directions import Direction
from Enum.tiles import TileType

class Maze:
    def __init__(self, rows, cols):
        self.rows = rows
        self.cols = cols

        self.grid = []

        for row in range(rows):
            row_data = []

            for col in range(cols):
                row_data.append(Cell(row, col))

            self.grid.append(row_data)

    # Get the start cell
    def get_start_cell(self):
        return self.find_tile(TileType.START)

    # Get the goal cell
    def get_goal_cell(self):
        return self.find_tile(TileType.GOAL)

    # Get cell at (row, col)
    def get_cell(self, row, col):
        if 0 <= row < self.rows and 0 <= col < self.cols:
            return self.grid[row][col]

        return None

    # Set cell type (START, GOAL, PATH, LIGHT)
    def set_cell_type(self, row, col, tile_type):
        cell = self.get_cell(row, col)

        if cell is not None:
            cell.tileType = tile_type

    # Get all 4 adjacent neighbours (including walls)
    def get_neighbours(self, cell):
        neighbours = []

        row = cell.row
        col = cell.col

        directions = [
            (-1, 0),    # UP
            (1, 0),     # DOWN
            (0, -1),    # LEFT
            (0, 1)      # RIGHT
        ]

        for dr, dc in directions:
            neighbour = self.get_cell(row + dr, col + dc)

            if neighbour is not None:
                neighbours.append(neighbour)

        return neighbours

    # Get unvisited neighbours (used for maze generation)
    def get_unvisited_neighbours(self, cell):
        neighbours = []

        for neighbour in self.get_neighbours(cell):
            if not neighbour.isVisited:
                neighbours.append(neighbour)

        return neighbours

    # Connect two adjacent cells by removing the wall between them
    def connect_cells(self, cell1, cell2):
        row_diff = cell2.row - cell1.row
        col_diff = cell2.col - cell1.col

        # cell2 is above
        if row_diff == -1:
            cell1.remove_wall(Direction.UP)
            cell2.remove_wall(Direction.DOWN)

        # cell2 is below
        elif row_diff == 1:
            cell1.remove_wall(Direction.DOWN)
            cell2.remove_wall(Direction.UP)

        # cell2 is left
        elif col_diff == -1:
            cell1.remove_wall(Direction.LEFT)
            cell2.remove_wall(Direction.RIGHT)

        # cell2 is right
        elif col_diff == 1:
            cell1.remove_wall(Direction.RIGHT)
            cell2.remove_wall(Direction.LEFT)

    # Check if movement from cell in the given direction is possible (i.e. no wall)
    def can_move(self, cell, direction):
        if direction == Direction.UP:
            return not cell.U

        elif direction == Direction.DOWN:
            return not cell.D

        elif direction == Direction.LEFT:
            return not cell.L

        elif direction == Direction.RIGHT:
            return not cell.R

        return False

    # Get all accessible neighbours (i.e. no wall in between)
    def get_accessible_neighbours(self, cell):
        neighbours = []

        if not cell.U:
            neighbour = self.get_cell(cell.row - 1, cell.col)
            if neighbour is not None:
                neighbours.append(neighbour)

        if not cell.D:
            neighbour = self.get_cell(cell.row + 1, cell.col)
            if neighbour is not None:
                neighbours.append(neighbour)

        if not cell.L:
            neighbour = self.get_cell(cell.row, cell.col - 1)
            if neighbour is not None:
                neighbours.append(neighbour)

        if not cell.R:
            neighbour = self.get_cell(cell.row, cell.col + 1)
            if neighbour is not None:
                neighbours.append(neighbour)

        return neighbours
    
    # Calculate light intensity at a cell based on nearby LIGHT tiles and walls
    # Calculate light intensity at the given cell.

    # Rules:
    #     - If the cell itself is a LIGHT tile: intensity = 1.0
    #     - Manhattan distance 1: intensity = 0.5
    #     - Manhattan distance 2: intensity = 0.2
    #     - Greater than 2: intensity = 0.0

    # Walls block light completely. A light contributes only if there exists
    # a reachable path (through open walls) whose shortest path length is
    # equal to the Manhattan distance.

    # If multiple lights illuminate the same cell, the maximum intensity
    # is returned.
    def get_light_intensity(self, cell):
        from collections import deque

        # Intensity lookup table
        intensity_table = {
            0: 1.0,
            1: 0.5,
            2: 0.2
        }

        if cell.tileType == TileType.LIGHT:
            return 1.0

        max_intensity = 0.0

        for light_cell in self.get_light_cells():
            manhattan_distance = (
                abs(cell.row - light_cell.row) +
                abs(cell.col - light_cell.col)
            )

            if manhattan_distance > 2:
                continue

            # BFS to check whether shortest reachable path length
            # equals Manhattan distance (i.e. no wall detour)
            queue = deque([(light_cell, 0)])
            visited = {light_cell}
            reachable = False

            while queue:
                current, distance = queue.popleft()

                if distance > manhattan_distance:
                    continue

                if current == cell:
                    if distance == manhattan_distance:
                        reachable = True
                    break

                for neighbour in self.get_accessible_neighbours(current):
                    if neighbour not in visited:
                        visited.add(neighbour)
                        queue.append((neighbour, distance + 1))

            if reachable:
                intensity = intensity_table[manhattan_distance]
                max_intensity = max(max_intensity, intensity)

        return max_intensity

    # Find the nearest tile of the given type (e.g., START, GOAL, LIGHT) using BFS
    def find_tile(self, tile_type):
        for row in range(self.rows):
            for col in range(self.cols):
                cell = self.get_cell(row, col)

                if cell.tileType == tile_type:
                    return cell

        return None

    # Get all LIGHT cells in the maze
    def get_light_cells(self):
        lights = []

        for row in range(self.rows):
            for col in range(self.cols):
                cell = self.get_cell(row, col)

                if cell.tileType == TileType.LIGHT:
                    lights.append(cell)

        return lights


    # Convert maze to a 3D list and return it.
    # Each cell is stored as:
    # [U, D, L, R, tileType]
    def convert_to_map(self):
        map_data = []

        for row in range(self.rows):
            row_data = []

            for col in range(self.cols):
                cell = self.get_cell(row, col)

                cell_state = [
                    int(cell.U),
                    int(cell.D),
                    int(cell.L),
                    int(cell.R),
                    cell.tileType.value
                ]

                row_data.append(cell_state)

            map_data.append(row_data)

        return map_data

    # Convert a 3D list map_data back to a Maze object.
    # The map_data format is the same as the output of convert_to_map().
    @classmethod
    def convert_to_maze(cls, map_data):
        if not map_data:
            raise ValueError("Empty map")

        rows = len(map_data)
        cols = len(map_data[0])

        # Check rectangular shape
        for row in map_data:
            if len(row) != cols:
                raise ValueError("Broken map: inconsistent row lengths")

        maze = cls(rows, cols)

        for row in range(rows):
            for col in range(cols):
                data = map_data[row][col]

                if len(data) != 5:
                    raise ValueError(f"Invalid cell data: {data}")

                cell = maze.get_cell(row, col)

                cell.U = bool(data[0])
                cell.D = bool(data[1])
                cell.L = bool(data[2])
                cell.R = bool(data[3])

                cell.tileType = TileType(data[4])

        return maze