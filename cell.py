from Enum.tiles import TileType
from Enum.directions import Direction

class Cell:
    def __init__(self, row, col):
        # Position
        self.row = row
        self.col = col

        # Walls
        # True = wall exists, False = no wall
        self.U = True
        self.D = True
        self.L = True
        self.R = True

        # Tile type
        # START / GOAL / PATH / LIGHT
        self.tileType = TileType.PATH  

        # Temporary flag used during maze generation/search
        self.isVisited = False

    def get_pos(self):
        return (self.row, self.col)
    
    def get_tile_type(self):
        return self.tileType

    def set_tile_type(self, tile_type):
        self.tileType = tile_type


    # Get direction from this cell to an adjacent cell
    def get_direction_to(self, other_cell):
        if self.row == other_cell.row:
            if self.col == other_cell.col + 1:
                return Direction.LEFT
            elif self.col == other_cell.col - 1:
                return Direction.RIGHT
        elif self.col == other_cell.col:
            if self.row == other_cell.row + 1:
                return Direction.UP
            elif self.row == other_cell.row - 1:
                return Direction.DOWN
        
        raise ValueError(f"Cells {self} and {other_cell} are not adjacent.")


    # Return walls in order: [UP, DOWN, LEFT, RIGHT]
    def get_walls(self):
        return [self.U, self.D, self.L, self.R]

    # Check if there's a wall in the given direction
    def has_wall(self, direction):
        if direction == Direction.UP:
            return self.U
        elif direction == Direction.DOWN:
            return self.D
        elif direction == Direction.LEFT:
            return self.L
        elif direction == Direction.RIGHT:
            return self.R

        raise ValueError(f"Invalid direction: {direction}")

    # Remove wall in the given direction
    def remove_wall(self, direction):
        if direction == Direction.UP:
            self.U = False
        elif direction == Direction.DOWN:
            self.D = False
        elif direction == Direction.LEFT:
            self.L = False
        elif direction == Direction.RIGHT:
            self.R = False
        else:
            raise ValueError(f"Invalid direction: {direction}")

    # Add wall in the given direction
    def add_wall(self, direction):
        if direction == Direction.UP:
            self.U = True
        elif direction == Direction.DOWN:
            self.D = True
        elif direction == Direction.LEFT:
            self.L = True
        elif direction == Direction.RIGHT:
            self.R = True
        else:
            raise ValueError(f"Invalid direction: {direction}")


    def reset_visit(self):
        self.isVisited = False
