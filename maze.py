import random
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

    # basic cell access
    def get_cell(self, row, col):

        if 0 <= row < self.rows and 0 <= col < self.cols:
            return self.grid[row][col]

        return None

    # set cell type (start, goal, path, light, reward)    
    def set_cell_type(self, row, col, tile_type):

        cell = self.get_cell(row, col)

        if cell:
            cell.tileType = tile_type

    # get all neighbours of a cell (including visited ones)
    def get_neighbours(self, cell):

        neighbours = []

        row = cell.row
        col = cell.col

        directions = [
            (-1, 0),  # U
            (1, 0),   # D
            (0, -1),  # L
            (0, 1)    # R
        ]

        for dr, dc in directions:

            neighbour = self.get_cell(row + dr, col + dc)

            if neighbour is not None:
                neighbours.append(neighbour)

        return neighbours

    # get unvisited neighbours of a cell
    def get_unvisited_neighbours(self, cell):

        neighbours = []

        for neighbour in self.get_neighbours(cell):

            if not neighbour.isVisited:
                neighbours.append(neighbour)

        return neighbours

    # remove walls between two adjacent cells
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

    # convert maze to map(a 3d list of cell states)
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


    # convert map(a 3d list of cell states) to maze
    @classmethod
    def convert_to_maze(cls, map_data):
        if not map_data:
            raise ValueError("Empty map")
    
        rows = len(map_data)
        cols = len(map_data[0])

        for row in map_data:
            if len(row) != cols:
                raise ValueError("Map rows have different lengths")

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