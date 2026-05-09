import tkinter as tk
from pathlib import Path

from map_manager import create_map
from Enum.tiles import TileType
from Utils.utils import MAP_TYPES, TILE_COLORS

CELL_SIZE = 50
WALL_WIDTH = 3

# Keep image references alive, otherwise Tkinter may garbage-collect them
IMAGE_CACHE = {}


def rgb_to_hex(rgb):
    return "#{:02x}{:02x}{:02x}".format(rgb[0], rgb[1], rgb[2])


def load_tile_images():
    """
    Load and resize images from:
        resources/coin.png
        resources/light_bulb.png
    """
    resource_dir = Path("resources")

    # Leave some margin inside each cell
    target_size = int(CELL_SIZE * 0.6)

    # PhotoImage only supports integer downsampling using subsample().
    # Assume original images are 1000x1000.
    original_size = 1000
    scale = max(1, original_size // target_size)

    # ----- Coin -----
    coin_path = resource_dir / "coin.png"
    if coin_path.exists():
        img = tk.PhotoImage(file=str(coin_path))
        img = img.subsample(scale, scale)
        IMAGE_CACHE["coin"] = img

    # ----- Light bulb -----
    light_path = resource_dir / "light_bulb.png"
    if light_path.exists():
        img = tk.PhotoImage(file=str(light_path))
        img = img.subsample(scale, scale)
        IMAGE_CACHE["light"] = img


def draw_cell(canvas, cell):
    x1 = cell.col * CELL_SIZE
    y1 = cell.row * CELL_SIZE
    x2 = x1 + CELL_SIZE
    y2 = y1 + CELL_SIZE

    # Default floor color from TILE_COLORS
    fill_color = rgb_to_hex(TILE_COLORS[cell.tileType])

    # LIGHT and REWARD use white background
    if cell.tileType in (TileType.LIGHT, TileType.REWARD):
        fill_color = "white"

    # Draw floor
    canvas.create_rectangle(
        x1, y1, x2, y2,
        fill=fill_color,
        outline=""
    )

    # Draw special content
    if cell.tileType == TileType.START:
        canvas.create_text(
            (x1 + x2) / 2,
            (y1 + y2) / 2,
            text="S",
            fill="white",
            font=("Arial", int(CELL_SIZE * 0.35), "bold")
        )

    elif cell.tileType == TileType.GOAL:
        canvas.create_text(
            (x1 + x2) / 2,
            (y1 + y2) / 2,
            text="G",
            fill="white",
            font=("Arial", int(CELL_SIZE * 0.35), "bold")
        )

    elif cell.tileType == TileType.REWARD:
        if "coin" in IMAGE_CACHE:
            canvas.create_image(
                (x1 + x2) / 2,
                (y1 + y2) / 2,
                image=IMAGE_CACHE["coin"]
            )
        else:
            canvas.create_text(
                (x1 + x2) / 2,
                (y1 + y2) / 2,
                text="$",
                fill="darkgreen",
                font=("Arial", int(CELL_SIZE * 0.35), "bold")
            )

    elif cell.tileType == TileType.LIGHT:
        if "light" in IMAGE_CACHE:
            canvas.create_image(
                (x1 + x2) / 2,
                (y1 + y2) / 2,
                image=IMAGE_CACHE["light"]
            )
        else:
            canvas.create_text(
                (x1 + x2) / 2,
                (y1 + y2) / 2,
                text="💡",
                font=("Arial", int(CELL_SIZE * 0.35))
            )

    # Draw walls
    if cell.U:
        canvas.create_line(x1, y1, x2, y1, width=WALL_WIDTH, fill="black")
    if cell.D:
        canvas.create_line(x1, y2, x2, y2, width=WALL_WIDTH, fill="black")
    if cell.L:
        canvas.create_line(x1, y1, x1, y2, width=WALL_WIDTH, fill="black")
    if cell.R:
        canvas.create_line(x2, y1, x2, y2, width=WALL_WIDTH, fill="black")


def draw_maze(canvas, maze):
    for row in range(maze.rows):
        for col in range(maze.cols):
            cell = maze.get_cell(row, col)
            draw_cell(canvas, cell)


def main():
    rows = 20
    cols = 20

    # Generate a maze with LIGHT and REWARD tiles
    maze = create_map(
        rows=rows,
        cols=cols,
        isSave=False,
        map_type=MAP_TYPES[3]
    )

    root = tk.Tk()
    root.title("Maze Generator")

    # Load images after Tk root is created
    load_tile_images()

    canvas = tk.Canvas(
        root,
        width=cols * CELL_SIZE,
        height=rows * CELL_SIZE,
        bg="white"
    )
    canvas.pack()

    draw_maze(canvas, maze)

    root.mainloop()


if __name__ == "__main__":
    main()