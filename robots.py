import random

from Enum.robots import Types
from Enum.tiles import TileType
from Enum.directions import Direction
from Utils.utils import bfs, a_star
from Utils.config import LOW_ENERGY_THRESHOLD, LIGHT_SEEK_PROBABILITY, EXPLORATION_PROBABILITY, DEFAULT_EXPERIMENT_CONFIG

# Base Brain class
class Brain:
    def __init__(self, name = "Brain"):
        self.name = name

        # Knowledge
        self.goal_cell = None
        self.maze = None

        # Robot state (injected by Robot)
        self.last_position = None
        self.use_energy = DEFAULT_EXPERIMENT_CONFIG["use_energy"]
        self.energy_capacity = DEFAULT_EXPERIMENT_CONFIG["energy_capacity"]
        self.get_energy = lambda: self.energy_capacity

    def set_knowledge(self, goal_cell, maze):
        self.goal_cell = goal_cell
        self.maze = maze

    def act(self, accessible_cells, current_cell):
        raise NotImplementedError


# Brain for reactive agent with different knowledge configurations
# Act based on the current percept without memory of past states.
class ReactiveBrain(Brain):
    def __init__(self):
        super().__init__("ReactiveBrain")

    # Reactive agent decision-making based on knowledge configuration
    # accessible_cells: list of Cell objects that the robot can move to from current_cell
    # current_cell: the Cell object where the robot currently is
    # Returns the chosen next cell to move to.
    #   Case 1: No goal knowledge, no map knowledge
    #   Case 2: Goal position known, map unknown
    #   Case 3: Goal unknown, full map known
    def act(self, accessible_cells, current_cell):
        # Case 1: No goal knowledge, no map knowledge
        # Strategy:
        # 1. If goal is adjacent, move directly to it.
        # 2. If energy is low, move to adjacent light source.
        # 3. Otherwise move randomly.
        if self.goal_cell is None and self.maze is None:
            # 1. If goal is adjacent, go directly to goal
            for cell in accessible_cells:
                if cell.get_tile_type() == TileType.GOAL:
                    return cell

            # 2. Low energy -> move to adjacent light source
            if self.use_energy:
                energy_ratio = self.get_energy() / self.energy_capacity

                if energy_ratio <= LOW_ENERGY_THRESHOLD:
                    for cell in accessible_cells:
                        if cell.get_tile_type() == TileType.LIGHT:
                            return cell

            # 3. Otherwise move randomly
            return random.choice(accessible_cells) if accessible_cells else None

        # Case 2: Goal position known, map unknown
        # Strategy:
        # 1. If energy is low and light is adjacent, prioritise recharging.
        # 2. Compute Manhattan distance to goal for each neighbouring cell.
        # 3. With some probability, deliberately choose a worse move to help escape local minima.
        # 4. Otherwise choose randomly among the best moves.
        elif self.goal_cell is not None and self.maze is None:

            if self.use_energy:
                energy_ratio = self.get_energy() / self.energy_capacity

                if energy_ratio <= LOW_ENERGY_THRESHOLD:
                    for cell in accessible_cells:
                        if cell.get_tile_type() == TileType.LIGHT:
                            return cell

            if not accessible_cells:
                return None


            cell_distances = []

            for cell in accessible_cells:
                distance = (
                    abs(cell.row - self.goal_cell.row)
                    + abs(cell.col - self.goal_cell.col)
                )
                cell_distances.append((cell, distance))


            cell_distances.sort(key = lambda x: x[1])

            best_distance = cell_distances[0][1]


            # With some probability, choose a worse move to encourage exploration
            if (
                len(cell_distances) > 1
                and random.random() < EXPLORATION_PROBABILITY
            ):
                worse_cells = [
                    cell
                    for cell, distance in cell_distances
                    if distance > best_distance
                ]

                if worse_cells:
                    return random.choice(worse_cells)

            # Otherwise, choose randomly among the best moves
            best_cells = [
                cell
                for cell, distance in cell_distances
                if distance == best_distance
            ]

            return random.choice(best_cells)

        # Case 3: Goal unknown, full map known
        # Strategy:
        # 1. If energy is low, seek out adjacent light sources.
        # 2. Compute shortest path to goal using BFS.
        elif self.goal_cell is None and self.maze is not None:
            target = self.maze.get_goal_cell()

            if self.use_energy:
                energy_ratio = self.get_energy() / self.energy_capacity

                if energy_ratio <= LOW_ENERGY_THRESHOLD:
                    # Find all light cells
                    light_cells = []

                    for row in self.maze.grid:
                        for cell in row:
                            if cell.get_tile_type() == TileType.LIGHT:
                                light_cells.append(cell)

                    # Choose nearest reachable light
                    nearest_light = None
                    nearest_distance = float("inf")

                    for light in light_cells:
                        path_to_light = bfs(self.maze, current_cell, light)

                        if path_to_light is not None:
                            distance = len(path_to_light)

                            if distance < nearest_distance:
                                nearest_distance = distance
                                nearest_light = light

                    if (
                        nearest_light is not None
                        and random.random() < LIGHT_SEEK_PROBABILITY
                    ):
                        target = nearest_light

            # Compute path to target using BFS
            path = bfs(self.maze, current_cell, target)

            if path is None:
                return None

            # path[0] = current_cell
            # path[1] = next step
            if len(path) >= 2:
                return path[1]

            # Already at target
            return current_cell

        # Fallback (should not reach here)
        else:
            return random.choice(accessible_cells) if accessible_cells else None


# Brain for memory-based agent
class MemoryBrain(Brain):
    def __init__(self):
        super().__init__("MemoryBrain")

        # Cells that have been visited
        self.visited = set()

        # Light cells that have been discovered
        self.discovered_lights = set()

    # Memory-based agent decision-making based on knowledge configuration and memory of visited cells and discovered lights.
    # The strategy is more sophisticated than the reactive brain, as it can leverage memory to make informed decisions.
    # The decision logic is as follows:
    # 1. Update memory with current cell and visible light cells.
    # 2. If goal is adjacent, move directly to it.
    # 3. If energy is low, move to adjacent known light source.
    # 4. If goal is known but map is unknown, prefer unvisited cells that are closer to the goal.
    # 5. If goal is known and map is known, compute shortest path to goal and follow it, while also considering energy levels and known lights for detours.
    def act(self, accessible_cells, current_cell):
        self.visited.add(current_cell)

        for cell in accessible_cells:
            if cell.get_tile_type() == TileType.LIGHT:
                self.discovered_lights.add(cell)

        # Case 1: Goal unknown, map unknown
        # Strategy:
        # 1. If goal is adjacent, move directly to it.
        # 2. If energy is low, move to adjacent known light source.
        # 3. Prefer unvisited neighbouring cells to encourage exploration.
        # 4. If all neighbours visited, backtrack randomly.
        if self.goal_cell is None and self.maze is None:

            for cell in accessible_cells:
                if cell.get_tile_type() == TileType.GOAL:
                    return cell

            if self.use_energy:
                energy_ratio = self.get_energy() / self.energy_capacity

                if energy_ratio <= LOW_ENERGY_THRESHOLD:
                    visible_known_lights = [
                        cell for cell in accessible_cells
                        if cell in self.discovered_lights
                    ]

                    if visible_known_lights:
                        return random.choice(visible_known_lights)

            # Prefer unvisited cells to encourage exploration
            unvisited_cells = [
                cell for cell in accessible_cells
                if cell not in self.visited
            ]

            if unvisited_cells:
                return random.choice(unvisited_cells)

            # All neighbours visited, backtrack randomly
            return random.choice(accessible_cells) if accessible_cells else None

        # Case 2: Goal known, map unknown
        # Strategy:
        # 1. If goal is adjacent, move directly to it.
        # 2. If energy is low, move to adjacent known light source.
        # 3. Prefer unvisited cells that are closer to the goal.
        elif self.goal_cell is not None and self.maze is None:
            if self.use_energy:
                energy_ratio = self.get_energy() / self.energy_capacity

                if energy_ratio <= LOW_ENERGY_THRESHOLD:
                    visible_known_lights = [
                        cell for cell in accessible_cells
                        if cell in self.discovered_lights
                    ]

                    if visible_known_lights:
                        return random.choice(visible_known_lights)
                    
            unvisited_cells = [
                cell for cell in accessible_cells
                if cell not in self.visited
            ]

            candidate_cells = (
                unvisited_cells
                if unvisited_cells
                else accessible_cells
            )

            # Compute Manhattan distance to goal
            best_distance = float("inf")
            best_cells = []

            for cell in candidate_cells:
                distance = (
                    abs(cell.row - self.goal_cell.row)
                    + abs(cell.col - self.goal_cell.col)
                )

                if distance < best_distance:
                    best_distance = distance
                    best_cells = [cell]

                elif distance == best_distance:
                    best_cells.append(cell)

            return random.choice(best_cells)

        # Case 3: Goal unknown, map known
        # Strategy:
        # 1. If energy is low, seek out known light sources that are reachable.
        # 2. Compute shortest path to goal using A* and follow it.
        elif self.goal_cell is None and self.maze is not None:
            goal_cell = self.maze.get_goal_cell()
            target = goal_cell

            if self.use_energy and self.discovered_lights:
                energy_ratio = self.get_energy() / self.energy_capacity

                if (
                    energy_ratio <= LOW_ENERGY_THRESHOLD
                    and random.random() < LIGHT_SEEK_PROBABILITY
                ):
                    nearest_light = None
                    nearest_distance = float("inf")

                    for light in self.discovered_lights:
                        path_to_light = a_star(self.maze, self.current_cell, light)

                        if path_to_light is not None:
                            distance = len(path_to_light)

                            if distance < nearest_distance:
                                nearest_distance = distance
                                nearest_light = light

                    if nearest_light is not None:
                        target = nearest_light

            path = a_star(self.maze, self.current_cell, target)

            if path is None:
                return None

            # path[0] = current_cell
            # path[1] = next step
            if len(path) >= 2:
                return path[1]

            # Already at target
            return current_cell

        # Fallback (should not reach here)
        else:
            return random.choice(accessible_cells) if accessible_cells else None


# Robot class representing the agent in the maze environment
class Robot:
    def __init__(
        self,
        name,
        brain,
        start_cell,
        energy_capacity = DEFAULT_EXPERIMENT_CONFIG["energy_capacity"],
        use_energy = DEFAULT_EXPERIMENT_CONFIG["use_energy"],
        energy_per_step = DEFAULT_EXPERIMENT_CONFIG["energy_per_step"],
        maze = None,
        goal_cell = None
    ):
        self.name = name
        self.brain = brain

        # Position
        self.current_cell = start_cell
        self.last_position = None

        # Facing direction
        self.direction = Direction.UP

        # Energy
        self.use_energy = use_energy
        self.energy_capacity = energy_capacity
        self.energy = energy_capacity
        self.energy_per_step = energy_per_step

        # State
        self.success = False
        self.failed = False
        self.steps = 0

        # Inject knowledge into brain
        self.brain.set_knowledge(goal_cell, maze)

        # Give brain access to robot state
        self._sync_brain_state()

    # Synchronise relevant robot state to brain (called after any state change)
    def _sync_brain_state(self):
        self.brain.last_position = self.last_position
        self.brain.use_energy = self.use_energy
        self.brain.energy_capacity = self.energy_capacity
        self.brain.get_energy = self.get_energy
        self.brain.current_cell = self.current_cell

    # Getters
    def get_current_cell(self):
        return self.current_cell

    def get_steps(self):
        return self.steps

    def get_energy(self):
        return self.energy

    # Update function called by environment each step with the current percept
    def update(self, percept):
        if self.success or self.failed:
            return None

        if self.energy <= 0:
            self.energy = 0
            self.failed = True
            return None

        if self.current_cell.get_tile_type() == TileType.GOAL:
            self.success = True
            return None

        # Decide and move
        self.act(percept["accessible_cells"], self.current_cell)
        self.steps += 1

        # Energy consumption
        if self.use_energy:
            self.energy -= self.energy_per_step

        # Recharge from light
        self.energy += percept["light_intensity"]

        # Cap energy at capacity
        if self.energy > self.energy_capacity:
            self.energy = self.energy_capacity

    # Decision-making function that calls the brain's act method and moves to the chosen cell
    def act(self, accessible_cells, current_cell):
        new_cell = self.brain.act(accessible_cells, current_cell)
        self.move_to(new_cell)

    # Move to a new cell and update direction based on the movement
    def move_to(self, new_cell):
        if new_cell is None or self.current_cell is None:
            return

        # Determine direction
        row_diff = new_cell.row - self.current_cell.row
        col_diff = new_cell.col - self.current_cell.col

        if row_diff == -1:
            self.direction = Direction.UP
        elif row_diff == 1:
            self.direction = Direction.DOWN
        elif col_diff == -1:
            self.direction = Direction.LEFT
        elif col_diff == 1:
            self.direction = Direction.RIGHT

        # Update position
        self.last_position = self.current_cell
        self.current_cell = new_cell

        # Synchronise state to brain
        self._sync_brain_state()

    # Draw the robot on a canvas (for visualization purposes)
    def draw(self, canvas, cell_size=50):
        if self.current_cell is None:
            return

        cell = self.current_cell

        # Cell boundaries
        cell_x1 = cell.col * cell_size
        cell_y1 = cell.row * cell_size
        cell_x2 = cell_x1 + cell_size
        cell_y2 = cell_y1 + cell_size

        # Robot body rectangle
        margin = cell_size * 0.15

        x1 = cell_x1 + margin
        y1 = cell_y1 + margin
        x2 = cell_x2 - margin
        y2 = cell_y2 - margin

        # Colour
        fill_color = "blue"
        if self.success:
            fill_color = "green"
        elif self.failed:
            fill_color = "red"

        # Draw body
        canvas.create_rectangle(
            x1, y1, x2, y2,
            fill = fill_color,
            outline = "black",
            width = 2,
            tags="robot"
        )

        # Direction indicator
        indicator_radius = cell_size * 0.07
        offset = cell_size * 0.12

        cx = (x1 + x2) / 2
        cy = (y1 + y2) / 2

        if self.direction == Direction.UP:
            cy = y1 + offset
        elif self.direction == Direction.DOWN:
            cy = y2 - offset
        elif self.direction == Direction.LEFT:
            cx = x1 + offset
        elif self.direction == Direction.RIGHT:
            cx = x2 - offset

        canvas.create_oval(
            cx - indicator_radius,
            cy - indicator_radius,
            cx + indicator_radius,
            cy + indicator_radius,
            fill = "red",
            outline = "",
            tags = "robot"
        )

    # Reset robot to initial state (optionally with a new start cell)
    def reset(self, start_cell=None):
        if start_cell is not None:
            self.current_cell = start_cell

        self.last_position = None
        self.direction = Direction.UP

        self.energy = self.energy_capacity
        self.success = False
        self.failed = False
        self.steps = 0

        self._sync_brain_state()

    # Get the result summary for this robot after a run
    def get_result(self):
        return {
            "name": self.name,
            "success": self.success,
            "failed": self.failed,
            "steps": self.steps,
            "energy_remaining": self.energy
        }



def create_robot(
    robot_type,
    name,
    start_cell,
    energy_capacity = DEFAULT_EXPERIMENT_CONFIG["energy_capacity"],
    use_energy = DEFAULT_EXPERIMENT_CONFIG["use_energy"],
    energy_per_step = DEFAULT_EXPERIMENT_CONFIG["energy_per_step"],
    maze = None,
    goal_cell = None
):
    if robot_type == Types.REACTIVE:
        brain = ReactiveBrain()

    elif robot_type == Types.MEMORY:
        brain = MemoryBrain()

    else:
        raise ValueError(f"Unknown robot type: {robot_type}")

    return Robot(
        name = name,
        brain = brain,
        start_cell = start_cell,
        energy_capacity = energy_capacity,
        use_energy = use_energy,
        energy_per_step = energy_per_step,
        maze = maze,
        goal_cell = goal_cell
    )