import numpy as np
from PIL import Image, ImageDraw
import random
from collections import deque
import os

# --- Constants ---
WALL_VALUE = 0  # Internal grid value for a wall element
PATH_VALUE = 1  # Internal grid value for a path element
WALL, PATH = WALL_VALUE, PATH_VALUE
SOLUTION_VALUE = 2  # Placeholder if needed, but we draw solution separately

DELAULT_COLOR_SCHEME = {
    "color_bg": (255, 255, 255),  # White background (represents path areas)
    "color_wall": (0, 0, 0),  # Black for wall lines
    "color_solution": (255, 0, 0),  # Red for solution path lines
    "color_start_dot": (0, 200, 0),  # Green for start marker area
    "color_end_dot": (0, 0, 200),  # Blue for end marker area
}


class Maze:
    def __init__(self, height, width, color_scheme=None, mask_img=None):
        """
        Initializes the Maze object.

        Args:
            height (int): The number of cells high the maze should be.
            width (int): The number of cells wide the maze should be.
        """
        if color_scheme is None:
            color_scheme = DELAULT_COLOR_SCHEME
        if height < 1 or width < 1:
            raise ValueError("Height and width must be at least 1.")

        self.height = height
        self.width = width

        # The actual grid size is larger to accommodate walls between cells
        self.grid_height = height * 2 + 1
        self.grid_width = width * 2 + 1

        # Initialize grid with all walls (0)
        self.grid = np.zeros(
            (self.grid_height, self.grid_width), dtype=np.uint8
        )  # Use uint8 for memory efficiency

        self.start_node = None
        self.end_node = None
        self.solution_path = None

        self.mask_img = mask_img
        if self.mask_img:
            color_scheme["color_wall"] = (
                0,
                0,
                0,
                0,
            )  # Transparent background for masked areas

        # Define colors for image saving
        self.COLOR_BG = color_scheme["color_bg"]
        self.COLOR_WALL = color_scheme["color_wall"]
        self.COLOR_SOLUTION = color_scheme["color_solution"]
        self.COLOR_START = color_scheme["color_start_dot"]
        self.COLOR_END = color_scheme["color_end_dot"]

    def _is_valid(self, r, c, visited):
        """Checks if a cell (r, c) is valid for maze generation."""
        return 0 <= r < self.height and 0 <= c < self.width and not visited[r, c]

    def generate(self):
        """Generates the maze using Recursive Backtracking."""
        visited = np.zeros((self.height, self.width), dtype=bool)
        stack = []

        # 1. Start at a random cell
        start_r, start_c = (
            random.randint(0, self.height - 1),
            random.randint(0, self.width - 1),
        )
        visited[start_r, start_c] = True
        # Mark the corresponding cell in the main grid as path
        self.grid[start_r * 2 + 1, start_c * 2 + 1] = PATH
        stack.append((start_r, start_c))

        while stack:
            r, c = stack[-1]  # Get current cell from stack top
            grid_r, grid_c = r * 2 + 1, c * 2 + 1

            # 2. Find unvisited neighbors
            neighbors = []
            # Check North, South, East, West
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nr, nc = r + dr, c + dc
                if self._is_valid(nr, nc, visited):
                    neighbors.append((nr, nc, dr, dc))  # Include direction

            if neighbors:
                # 3. Choose a random unvisited neighbor
                nr, nc, dr, dc = random.choice(neighbors)
                n_grid_r, n_grid_c = nr * 2 + 1, nc * 2 + 1

                # 4. Knock down the wall between current and neighbor
                wall_r, wall_c = grid_r + dr, grid_c + dc
                self.grid[wall_r, wall_c] = PATH
                self.grid[n_grid_r, n_grid_c] = PATH  # Mark neighbor cell as path

                # 5. Mark neighbor as visited and push to stack
                visited[nr, nc] = True
                stack.append((nr, nc))
            else:
                # 6. Backtrack if no unvisited neighbors
                stack.pop()

        # 7. Create entrance and exit
        # Ensure entrance and exit are paths
        self.start_node = (1, 0)  # Top-left entrance
        self.end_node = (self.grid_height - 2, self.grid_width - 1)  # Bottom-right exit

        # Carve entrance (make sure cell (1,1) is a path)
        if (
            self.grid[1, 1] == WALL
        ):  # Should usually be path due to generation starting point
            # Find first path cell and connect entrance to it if needed (rare case for 1x1)
            if self.height > 0 and self.width > 0:
                self.grid[1, 1] = PATH  # Ensure start cell is path
        self.grid[self.start_node] = PATH

        # Carve exit (make sure cell (H-2, W-2) is a path)
        if self.grid[self.grid_height - 2, self.grid_width - 2] == WALL:
            # If the natural end cell is a wall, connect the exit to the nearest path
            # This is tricky, let's just force the cell before the exit wall to be path
            self.grid[self.grid_height - 2, self.grid_width - 2] = PATH
        self.grid[self.end_node] = PATH  # Force exit itself to be path

        print("Maze generated.")

    def solve(self):
        """
        Solves the maze using Breadth-First Search (BFS).
        Returns:
            list or None: A list of (row, col) tuples representing the path,
                          or None if no solution is found.
        """
        if self.start_node is None or self.end_node is None:
            print("Error: Maze not generated yet or no start/end points.")
            return None

        q = deque(
            [(self.start_node, [self.start_node])]
        )  # Queue stores (current_node, path_so_far)
        visited = set([self.start_node])

        while q:
            (r, c), path = q.popleft()

            if (r, c) == self.end_node:
                self.solution_path = path
                print(f"Solution found with {len(path)} steps.")
                return path

            # Explore neighbors (North, South, East, West)
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nr, nc = r + dr, c + dc

                # Check bounds
                if 0 <= nr < self.grid_height and 0 <= nc < self.grid_width:
                    # Check if it's a path and not visited
                    if self.grid[nr, nc] != WALL and (nr, nc) not in visited:
                        visited.add((nr, nc))
                        new_path = list(path)  # Create a copy
                        new_path.append((nr, nc))
                        q.append(((nr, nc), new_path))

        print("No solution found.")
        self.solution_path = None
        return None

    def save_image(
        self,
        filename,
        unit_size=5,
        wall_thickness=2,
        show_solution=False,
        solution_width=3,
    ):
        """
        Saves the maze image with thin walls having rounded corners, and a rounded solution path.

        Args:
            filename (str | None): Path to save the image file.
            unit_size (int): Pixels per unit in the detailed grid. Controls overall scaling.
            wall_thickness (int): Thickness (diameter) of the wall elements in pixels.
            show_solution (bool): If True, draws the solution path.
            solution_width (int): Thickness (diameter) of the solution path elements in pixels.
        """
        # Define colors for image saving
        color_bg = self.COLOR_BG
        color_wall = self.COLOR_WALL
        color_solution = self.COLOR_SOLUTION
        color_start = self.COLOR_START
        color_end = self.COLOR_END

        if self.grid is None:
            print("Error: Maze grid not generated.")
            return None
        if unit_size < 1:
            unit_size = 1
        if wall_thickness < 1:
            wall_thickness = 1
        if solution_width < 1:
            solution_width = 1

        wall_radius = wall_thickness / 2
        solution_radius = solution_width / 2

        # Calculate final image dimensions based on the detailed grid
        img_width = self.grid_width * unit_size
        img_height = self.grid_height * unit_size

        # Start with background
        img = Image.new("RGBA", (img_width, img_height), color=color_bg)
        draw = ImageDraw.Draw(img)

        # --- Draw Rounded Wall Elements ---
        for r_grid in range(self.grid_height):
            for c_grid in range(self.grid_width):
                if self.grid[r_grid, c_grid] == WALL_VALUE:
                    # Calculate center coordinates for this wall grid point
                    center_x = int(c_grid * unit_size + unit_size / 2)
                    center_y = int(r_grid * unit_size + unit_size / 2)

                    # Draw a circle at every wall point (handles junctions and ends)
                    # Ellipse bounding box: [x0, y0, x1, y1]
                    wall_box = [
                        center_x - wall_radius,
                        center_y - wall_radius,
                        center_x + wall_radius,
                        center_y + wall_radius,
                    ]
                    # Use ellipse even for radius 0 to draw a point if thickness is 1
                    draw.ellipse(wall_box, fill=color_wall)

                    # Draw connecting rectangles to adjacent wall points (if they exist)
                    # Check EAST neighbor
                    if (
                        c_grid + 1 < self.grid_width
                        and self.grid[r_grid, c_grid + 1] == WALL_VALUE
                    ):
                        center_x_east = int((c_grid + 1) * unit_size + unit_size / 2)
                        # Rectangle height = wall_thickness, spans from center_x to center_x_east
                        rect_box = [
                            center_x,
                            center_y - wall_radius,
                            center_x_east,
                            center_y + wall_radius,
                        ]
                        draw.rectangle(rect_box, fill=color_wall)

                    # Check SOUTH neighbor
                    if (
                        r_grid + 1 < self.grid_height
                        and self.grid[r_grid + 1, c_grid] == WALL_VALUE
                    ):
                        center_y_south = int((r_grid + 1) * unit_size + unit_size / 2)
                        # Rectangle width = wall_thickness, spans from center_y to center_y_south
                        rect_box = [
                            center_x - wall_radius,
                            center_y,
                            center_x + wall_radius,
                            center_y_south,
                        ]
                        draw.rectangle(rect_box, fill=color_wall)

        # --- Draw Rounded Solution Path ---
        if show_solution and self.solution_path:
            # Calculate center coordinates for solution path points
            path_centers = []
            for r_grid, c_grid in self.solution_path:
                center_x = int(c_grid * unit_size + unit_size / 2)
                center_y = int(r_grid * unit_size + unit_size / 2)
                path_centers.append((center_x, center_y))

            # Draw circles at each point for rounded joints/ends
            for cx, cy in path_centers:
                solution_box = [
                    cx - solution_radius,
                    cy - solution_radius,
                    cx + solution_radius,
                    cy + solution_radius,
                ]
                draw.ellipse(solution_box, fill=color_solution)

            # Draw lines connecting the centers (will overlap circles slightly)
            if len(path_centers) > 1:
                draw.line(
                    path_centers,
                    fill=color_solution,
                    width=solution_width + 1,
                    joint="curve",
                )  # Use joint='curve' if available? Check PIL docs. Usually defaults good.

            # Draw start/end markers (larger circles)
            if path_centers:
                marker_radius = solution_radius + max(
                    1, wall_radius
                )  # Slightly larger circle

                # Start Point
                sx_c, sy_c = path_centers[0]
                draw.ellipse(
                    [
                        sx_c - marker_radius,
                        sy_c - marker_radius,
                        sx_c + marker_radius,
                        sy_c + marker_radius,
                    ],
                    fill=color_start,
                    outline=color_wall,
                )  # Green Start

                # End Point
                ex_c, ey_c = path_centers[-1]
                draw.ellipse(
                    [
                        ex_c - marker_radius,
                        ey_c - marker_radius,
                        ex_c + marker_radius,
                        ey_c + marker_radius,
                    ],
                    fill=color_end,
                    outline=color_wall,
                )  # Blue End

        elif show_solution and not self.solution_path:
            print("Warning: Solution path requested for image, but no solution found.")

        # --- Draw Mask Image (if provided) ---
        if self.mask_img:
            mask = Image.open(self.mask_img).convert("RGBA")
            mask = mask.resize((img_width, img_height))
            mask.paste(img, (0, 0), img)  # Paste with mask to keep transparency
            img = mask  # Use the masked image as the final output
        # --- Save Image ---
        if filename:
            output_dir = os.path.dirname(filename)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir)
                print(f"Created directory: {output_dir}")
            try:
                img.thumbnail((1080, 1080))
                img.save(filename)
                print(f"Image saved to {filename}")
            except Exception as e:
                print(f"Error saving image to {filename}: {e}")
        return img


# --- Main Execution ---
if __name__ == "__main__":
    # --- Set Maze Dimensions ---
    MAZE_HEIGHT = 12  # Number of conceptual cells high
    MAZE_WIDTH = MAZE_HEIGHT  # Number of conceptual cells wide

    # --- Set Drawing Parameters ---
    # Pixel size for each unit in the detailed grid (controls spacing/scaling)
    # Larger unit_size = more space between wall elements
    UNIT_SIZE = 500 // MAZE_WIDTH
    # Thickness (diameter) of the wall lines/dots in pixels
    WALL_THICKNESS = 300 // MAZE_WIDTH
    # Thickness (diameter) of the solution path lines/dots in pixels
    SOLUTION_WIDTH = (
        200 // MAZE_WIDTH
    )  # Should generally be <= UNIT_SIZE + WALL_THICKNESS//2 ? Test this. Should be <= UNIT_SIZE to fit in path center.
    # SOLUTION_WIDTH = min(SOLUTION_WIDTH, UNIT_SIZE) # Ensure solution fits

    OUTPUT_DIR = "maze_output_rounded"

    # --- Generate Maze ---
    maze_obj = Maze(MAZE_HEIGHT, MAZE_WIDTH)
    maze_obj.generate()

    # --- Save Generated Maze Image ---
    maze_filename = os.path.join(OUTPUT_DIR, "maze_generated_rounded.png")
    maze_obj.save_image(
        maze_filename,
        unit_size=UNIT_SIZE,
        wall_thickness=WALL_THICKNESS,
        show_solution=False,
        solution_width=SOLUTION_WIDTH,  # Pass solution width even if not shown, for consistency
    )

    # --- Solve Maze ---
    solution = maze_obj.solve()

    # --- Save Solved Maze Image (if solution exists) ---
    if solution:
        solved_filename = os.path.join(OUTPUT_DIR, "maze_solved_rounded.png")
        maze_obj.save_image(
            solved_filename,
            unit_size=UNIT_SIZE,
            wall_thickness=WALL_THICKNESS,
            show_solution=True,
            solution_width=SOLUTION_WIDTH,
        )
    else:
        print("Cannot save solved maze image because no solution was found.")
