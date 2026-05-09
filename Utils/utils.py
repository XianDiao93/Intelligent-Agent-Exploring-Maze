from Enum.tiles import TileType

TILE_COLORS = {
    TileType.START: (128, 128, 128),    # gray
    TileType.GOAL: (0, 200, 0),         # green
    TileType.PATH: (255, 255, 255),     # white
    TileType.LIGHT: (255, 255, 0),      # yellow
    TileType.REWARD: (255, 215, 0)      # gold
}

MAP_TYPES = {
    0 : [TileType.START, TileType.GOAL, TileType.PATH],                                     # Basic map with start, goal, walls, and paths
    1 : [TileType.START, TileType.GOAL, TileType.PATH, TileType.LIGHT],                     # Map with light tiles that can be used for visibility or special effects
    2 : [TileType.START, TileType.GOAL, TileType.PATH, TileType.REWARD],                    # Map with reward tiles that can provide bonuses or points to the player
    3 : [TileType.START, TileType.GOAL, TileType.PATH, TileType.LIGHT, TileType.REWARD]     # Map with both light and reward tiles for a more complex and engaging gameplay experience
}