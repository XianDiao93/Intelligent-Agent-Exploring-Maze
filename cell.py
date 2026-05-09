from Enum.tiles import TileType
from Enum.directions import Direction

class Cell:
    def __init__(self, row, col):
        self.row = row
        self.col = col
        self.U = True
        self.D = True
        self.L = True
        self.R = True
        self.tileType = TileType.PATH
        self.isVisited = False

    def get_pos(self):
        return (self.row, self.col)
    
    def get_tile_type(self):
        return self.tileType
    
    def set_tile_type(self, tileType):
        self.tileType = tileType

    def get_walls(self):
        return [self.U, self.D, self.L, self.R]
    
    def remove_wall(self, direction):
        if direction == Direction.UP:
            self.U = False
        elif direction == Direction.DOWN:
            self.D = False
        elif direction == Direction.LEFT:
            self.L = False
        elif direction == Direction.RIGHT:
            self.R = False
