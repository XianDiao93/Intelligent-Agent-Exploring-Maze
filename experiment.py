import tkinter as tk
import os
import time
import matplotlib.pyplot as plt
from pathlib import Path

from robots import create_robot

from Enum.tiles import TileType
from Enum.conditions import Knowledge, Energy
from Utils.utils import TILE_COLORS, MAP_TYPES
from Utils.config import DEFAULT_EXPERIMENT_CONFIG

CELL_SIZE = 50
WALL_WIDTH = 3

IMAGE_CACHE = {}


def rgb_to_hex(rgb):
    return "#{:02x}{:02x}{:02x}".format(*rgb)


def load_tile_images():
    resource_dir = Path("resources")

    target_size = int(CELL_SIZE * 0.6)
    original_size = 1000
    scale = max(1, original_size // target_size)

    light_path = Path(os.path.join(resource_dir, "light_bulb.png"))

    if light_path.exists():
        img = tk.PhotoImage(file=str(light_path))
        img = img.subsample(scale, scale)
        IMAGE_CACHE["light"] = img

# Draw cells
def draw_cell(canvas, cell):
    x1 = cell.col * CELL_SIZE
    y1 = cell.row * CELL_SIZE
    x2 = x1 + CELL_SIZE
    y2 = y1 + CELL_SIZE

    # Base tile colour
    fill_color = rgb_to_hex(TILE_COLORS[cell.tileType])

    # Draw floor
    canvas.create_rectangle(
        x1, y1, x2, y2,
        fill=fill_color,
        outline=""
    )

    # Draw tile content
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

# Draw the entire maze
def draw_maze(canvas, maze):
    for row in range(maze.rows):
        for col in range(maze.cols):
            cell = maze.get_cell(row, col)
            draw_cell(canvas, cell)

# Draw robots on top of the maze
def draw_robots(canvas, robots):
    for index, robot in enumerate(robots):
        robot.draw(
            canvas=canvas,
            cell_size=CELL_SIZE,
        )


class Experiment:
    def __init__(
        self,
        # Experiment configuration
        max_steps = DEFAULT_EXPERIMENT_CONFIG["max_steps"],
        speed = DEFAULT_EXPERIMENT_CONFIG["speed"],
        title = DEFAULT_EXPERIMENT_CONFIG["title"],

        # Map configuration
        file_name = DEFAULT_EXPERIMENT_CONFIG["file_name"],
        rows = DEFAULT_EXPERIMENT_CONFIG["rows"],
        cols = DEFAULT_EXPERIMENT_CONFIG["cols"],
        map_type = DEFAULT_EXPERIMENT_CONFIG["map_type"],
        num_of_lights = DEFAULT_EXPERIMENT_CONFIG["num_of_lights"],

        # Robot configuration
        robot_type = DEFAULT_EXPERIMENT_CONFIG["robot_type"],
        num_robots = DEFAULT_EXPERIMENT_CONFIG["num_robots"],

        # Knowledge configuration
        knowledge_condition = DEFAULT_EXPERIMENT_CONFIG["knowledge_condition"],

        # Energy configuration
        energy_condition = DEFAULT_EXPERIMENT_CONFIG["energy_condition"],
        energy_capacity = DEFAULT_EXPERIMENT_CONFIG["energy_capacity"],
        energy_per_step = DEFAULT_EXPERIMENT_CONFIG["energy_per_step"],
        energy_intensity = DEFAULT_EXPERIMENT_CONFIG["energy_intensity"],
    ):
        self.max_steps = max_steps
        self.speed = speed
        self.title = title

        # Map configuration
        self.file_name = file_name
        self.rows = rows
        self.cols = cols
        self.map_type = map_type

        # Default: one light per 25 cells, can be overridden by specifying num_of_lights
        if num_of_lights is None:
            num_of_lights = rows * cols // 25
        self.num_of_lights = num_of_lights

        # Robot configuration
        self.robot_type = robot_type
        self.num_robots = num_robots

        # Knowledge configuration
        self.knowledge_condition = knowledge_condition

        # Energy configuration
        self.energy_condition = energy_condition
        self.energy_capacity = energy_capacity
        self.energy_per_step = energy_per_step
        self.energy_intensity = energy_intensity

        # Runtime state
        self.robots = []
        self.maze = None
        self.steps = 0

        # Tkinter UI
        self.root = tk.Tk()
        self.root.title(self.title)

        load_tile_images()

        self.status_label = tk.Label(
            self.root,
            text=f"Steps: {self.steps}",
            font=("Arial", 14)
        )
        self.status_label.pack()

        self.canvas = tk.Canvas(
            self.root,
            width=self.cols * CELL_SIZE,
            height=self.rows * CELL_SIZE,
            bg="white"
        )
        self.canvas.pack()

        self.is_closed = False
        self.root.protocol("WM_DELETE_WINDOW", self.close)

    def load_map(self, filename = None):
        if filename is not None:
            from map_manager import get_map
            return get_map(filename)
        else:
            from map_manager import create_map
            return create_map(
                rows = self.rows,
                cols = self.cols,
                isSave = False,
                seed = None,
                map_type = self.map_type,
                num_lights = self.num_of_lights
            )
        
    def resize_window(self):
        if self.maze is None:
            return

        canvas_width = self.maze.cols * CELL_SIZE
        canvas_height = self.maze.rows * CELL_SIZE

        # Resize canvas
        self.canvas.config(
            width=canvas_width,
            height=canvas_height
        )

        # Update geometry calculations
        self.root.update_idletasks()

        # Prevent user from resizing window manually
        self.root.resizable(False, False)
    
    def generate_robots(self):
        robots = []

        start_cell = self.maze.get_start_cell()
        use_energy = (self.energy_condition == Energy.LIMITED)

        # Determine what knowledge to provide to the robots
        goal_cell = None
        maze = None

        if self.knowledge_condition == Knowledge.PARTIALLY_KNOWN:
            goal_cell = self.maze.get_goal_cell()

        elif self.knowledge_condition == Knowledge.FULLY_KNOWN:
            maze = self.maze

        for i in range(self.num_robots):
            robot = create_robot(
                robot_type = self.robot_type,
                name = f"Robot {i + 1}",
                start_cell = start_cell,
                use_energy = use_energy,
                energy_capacity = self.energy_capacity,
                energy_per_step = self.energy_per_step,
                goal_cell = goal_cell,
                maze = maze
            )
            robots.append(robot)

        return robots


    def render(self, robots=None, status_text=None):
        if self.is_closed:
            return

        # Only redraw robots
        self.canvas.delete("robot")

        if robots is not None:
            draw_robots(self.canvas, robots)

        if status_text is None:
            success_count = sum(robot.success for robot in robots) if robots else 0
            failed_count = sum(robot.failed for robot in robots) if robots else 0

            status_text = (
                f"Steps: {self.steps} | "
                f"Success: {success_count} | "
                f"Failed: {failed_count}"
            )

        self.status_label.config(text=status_text)


    def update(self):
        if self.is_closed:
            return True

        # Update all robots
        for robot in self.robots:
            cell = robot.get_current_cell()
            percept = {
                "accessible_cells": self.maze.get_accessible_neighbours(cell),
                "light_intensity": self.maze.get_light_intensity(cell)* self.energy_intensity
            }
            robot.update(percept)

        # Redraw GUI
        self.render(self.robots)

        # Process Tkinter events
        try:
            self.root.update()
        except tk.TclError:
            self.is_closed = True
            return True

        # Control simulation speed
        delay = 0.1 / max(self.speed, 0.01)
        time.sleep(delay)

        # Stop when all robots have finished
        return all(robot.success or robot.failed for robot in self.robots)


    def run(self):
        if self.is_closed:
            return

        # Load map and create robots
        if self.file_name is not None:
            map_type_index = next(
                key for key, value in MAP_TYPES.items()
                if value == self.map_type
            )

            self.maze = self.load_map(
                os.path.join(
                    str(map_type_index),
                    self.file_name
                )
            )
        else:
            self.maze = self.load_map()

        self.resize_window()

        self.robots = self.generate_robots()

        # Initial render
        draw_maze(self.canvas, self.maze)
        self.render(self.robots)

        # Main simulation loop
        while True:
            self.steps += 1

            finished = self.update()

            if finished or self.steps >= self.max_steps:
                break

        # Success rate
        total = len(self.robots)

        success_robots = [r for r in self.robots if r.success]
        failed_robots = [r for r in self.robots if r.failed]
        unfinished_robots = [
            r for r in self.robots
            if not r.success and not r.failed
        ]

        success_count = len(success_robots)
        failed_count = len(failed_robots)
        unfinished_count = len(unfinished_robots)

        success_rate = success_count / total * 100
        failed_rate = failed_count / total * 100
        unfinished_rate = unfinished_count / total * 100

        # Step statistics
        # (successful robots only)
        if success_robots:
            success_steps = [r.get_steps() for r in success_robots]

            steps_min = min(success_steps)
            steps_max = max(success_steps)
            steps_avg = sum(success_steps) / len(success_steps)
        else:
            steps_min = 0
            steps_max = 0
            steps_avg = 0

        # Energy statistics
        # (successful robots only)
        use_energy = (self.energy_condition == Energy.LIMITED)

        if use_energy and success_robots:
            success_energy = [r.get_energy() for r in success_robots]

            energy_min = min(success_energy)
            energy_max = max(success_energy)
            energy_avg = sum(success_energy) / len(success_energy)
        else:
            energy_min = 0
            energy_max = 0
            energy_avg = 0

        # Update final status label
        self.render(
            self.robots,
            status_text=(
                f"Finished | Steps: {self.steps} | "
                f"Success: {success_count} | "
                f"Failed: {failed_count} | "
                f"Unfinished: {unfinished_count}"
            )
        )

        # Plot results
        num_plots = 3 if use_energy else 2
        fig, axes = plt.subplots(1, num_plots, figsize=(5 * num_plots, 4))

        # If only 2 plots, axes is still indexable
        if num_plots == 2:
            ax1, ax2 = axes
        else:
            ax1, ax2, ax3 = axes


        # Add value labels on top of bars
        def add_value_labels(ax, fmt="{:.2f}"):
            for bar in ax.patches:
                height = bar.get_height()

                # Skip invalid values
                if height is None:
                    continue

                ax.annotate(
                    fmt.format(height),
                    (
                        bar.get_x() + bar.get_width() / 2,
                        height
                    ),
                    ha="center",
                    va="bottom",
                    fontsize=10,
                    xytext=(0, 3),
                    textcoords="offset points"
                )


        # Plot 1: Success rate
        ax1.bar(
            ["Success", "Failed", "Unfinished"],
            [success_rate, failed_rate, unfinished_rate]
        )
        ax1.set_ylim(0, 100)
        ax1.set_ylabel("Percentage (%)")
        ax1.set_title("Robot Outcomes")
        add_value_labels(ax1, "{:.1f}%")


        # Plot 2: Step statistics
        ax2.bar(
            ["Min", "Average", "Max"],
            [steps_min, steps_avg, steps_max]
        )
        ax2.set_ylabel("Steps")
        ax2.set_title("Successful Robots Steps")
        add_value_labels(ax2, "{:.1f}")


        # Plot 3: Energy statistics
        if use_energy:
            ax3.bar(
                ["Min", "Average", "Max"],
                [energy_min, energy_avg, energy_max]
            )
            ax3.set_ylabel("Remaining Energy")
            ax3.set_title("Successful Robots Energy")
            add_value_labels(ax3, "{:.1f}")


        plt.tight_layout()
        plt.show()

        # Close experiment window after plots are closed
        self.close()


    def close(self):
        if not self.is_closed:
            self.is_closed = True
            self.root.destroy()