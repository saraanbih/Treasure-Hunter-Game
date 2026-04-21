"""
pathfinder.py
Pure A* (A-Star) pathfinding algorithm.
No GUI dependencies — fully testable in isolation.

The algorithm finds the lowest-cost path between two
cells on a 2D grid, treating walls as impassable and
trap cells as high-cost nodes (defined in STEP_COSTS).
"""

import heapq
from constants import WALL, STEP_COSTS


def heuristic(a: tuple, b: tuple) -> int:
    """
    Manhattan distance heuristic.
    Admissible for 4-directional grid movement.

    Args:
        a: (row, col) of current node
        b: (row, col) of goal node

    Returns:
        Integer Manhattan distance
    """
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def astar(grid: list, start: tuple, goal: tuple) -> list:
    """
    A* pathfinding on a 2D grid.

    Finds the optimal (lowest-cost) path from start to goal
    while avoiding walls and penalising traps.

    Args:
        grid  : 2D list of cell types (int)
        start : (row, col) starting position
        goal  : (row, col) target position

    Returns:
        List of (row, col) tuples from start (exclusive)
        to goal (inclusive), or [] if no path exists.
    """
    rows = len(grid)
    cols = len(grid[0])

    # Min-heap: (f_score, node)
    open_set = []
    heapq.heappush(open_set, (0, start))

    came_from: dict = {}
    g_score: dict   = {start: 0}

    while open_set:
        _, current = heapq.heappop(open_set)

        if current == goal:
            return _reconstruct_path(came_from, current)

        r, c = current
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = r + dr, c + dc

            if not (0 <= nr < rows and 0 <= nc < cols):
                continue                         # out of bounds

            cell_type = grid[nr][nc]
            if cell_type == WALL:
                continue                         # impassable

            move_cost   = STEP_COSTS.get(cell_type, 1)
            tentative_g = g_score[current] + move_cost
            neighbor    = (nr, nc)

            if tentative_g < g_score.get(neighbor, float('inf')):
                came_from[neighbor] = current
                g_score[neighbor]   = tentative_g
                f_score             = tentative_g + heuristic(neighbor, goal)
                heapq.heappush(open_set, (f_score, neighbor))

    return []   # no path found


def _reconstruct_path(came_from: dict, current: tuple) -> list:
    """
    Walk the came_from chain backwards to build the path.

    Returns:
        Path as a list of nodes from the step after start
        up to and including goal.
    """
    path = []
    while current in came_from:
        path.append(current)
        current = came_from[current]
    path.reverse()
    return path