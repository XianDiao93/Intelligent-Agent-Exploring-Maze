import random
import heapq
from collections import deque

from Enum.tiles import TileType

TILE_COLORS = {
    TileType.START: (128, 128, 128),    # gray
    TileType.GOAL: (0, 200, 0),         # green
    TileType.PATH: (255, 255, 255),     # white
    TileType.LIGHT: (255, 255, 255),      # yellow
    # TileType.REWARD: (255, 215, 0)      # gold
}

MAP_TYPES = {
    0 : [TileType.START, TileType.GOAL, TileType.PATH],                                     # Basic map with start, goal, walls, and paths
    1 : [TileType.START, TileType.GOAL, TileType.PATH, TileType.LIGHT],                     # Map with light tiles that can be used for visibility or special effects
}


def bfs(maze, start_cell, target_cell):
    queue = deque([start_cell])
    parent = {start_cell: None}

    while queue:
        cell = queue.popleft()

        if cell == target_cell:
            break

        neighbours = maze.get_accessible_neighbours(cell)
        random.shuffle(neighbours)

        for neighbour in neighbours:
            if neighbour not in parent:
                parent[neighbour] = cell
                queue.append(neighbour)

    if target_cell not in parent:
        return None

    path = []
    cell = target_cell

    while cell is not None:
        path.append(cell)
        cell = parent[cell]

    path.reverse()
    return path




def a_star(maze, start_cell, target_cell):
    def heuristic(cell):
        return (
            abs(cell.row - target_cell.row)
            + abs(cell.col - target_cell.col)
        )


    open_set = []
    heapq.heappush(
        open_set,
        (heuristic(start_cell), random.random(), start_cell)
    )

    parent = {start_cell: None}
    g_score = {start_cell: 0}

    while open_set:
        _, _, current = heapq.heappop(open_set)

        if current == target_cell:
            break

        neighbours = maze.get_accessible_neighbours(current)
        random.shuffle(neighbours)

        for neighbour in neighbours:
            tentative_g = g_score[current] + 1

            if (
                neighbour not in g_score
                or tentative_g < g_score[neighbour]
            ):
                g_score[neighbour] = tentative_g
                parent[neighbour] = current

                f_score = tentative_g + heuristic(neighbour)

                heapq.heappush(
                    open_set,
                    (
                        f_score,
                        random.random(),
                        neighbour
                    )
                )

    if target_cell not in parent:
        return None

    path = []
    cell = target_cell

    while cell is not None:
        path.append(cell)
        cell = parent[cell]

    path.reverse()
    return path