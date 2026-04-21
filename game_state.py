"""
game_state.py
Core game logic — completely decoupled from the GUI.

Manages:
  - Grid state (walls, traps, treasures)
  - Player movement and collision
  - Enemy movement via A* pathfinding
  - Score, lives, and win/loss conditions
  - Flash-cell effects (visual hints fed back to renderer)

The GameState class emits events via simple callback hooks
so the GUI layer can react without being tightly coupled.
"""

from constants import (
    BASE_MAP, TREASURE_POSITIONS, PLAYER_START, ENEMY_START,
    EMPTY, WALL, TRAP, TREASURE,
    STARTING_LIVES, TREASURE_SCORE, FAST_THRESHOLD,
    FLASH_TRAP_TICKS, FLASH_TREASURE_TICKS, FLASH_CAPTURE_TICKS,
    TRAP_GLOW, ENEMY_GLOW, TREASURE_GLOW,
)
from pathfinder import astar, heuristic


class GameState:
    """
    Holds and mutates all game state.

    Callbacks (assign a callable to hook into events):
        on_status_message(msg: str)  — short status text for HUD
        on_game_over(won: bool)      — fired when the game ends
        on_hud_update()              — fired whenever score/lives change
    """

    def __init__(self):
        # Callbacks — UI sets these after construction
        self.on_status_message = lambda msg: None
        self.on_game_over      = lambda won: None
        self.on_hud_update     = lambda: None

        self.reset()

    # ─────────────────────────────────────────
    #  PUBLIC API
    # ─────────────────────────────────────────

    def reset(self):
        """Restore everything to initial state."""
        self.paused    = False
        self.game_over = False
        self.score     = 0
        self.lives     = STARTING_LIVES
        self.tick      = 0

        # Visual effect tracking: {(r,c): (color, expiry_tick)}
        self.flash_cells: dict = {}

        # Current A* path for the renderer to draw
        self.path_cells: list = []

        # Deep-copy the base map so we can mutate it
        self.grid = [row[:] for row in BASE_MAP]

        # Stamp treasure positions onto the grid
        for r, c in TREASURE_POSITIONS:
            self.grid[r][c] = TREASURE
        self.treasures_left = len(TREASURE_POSITIONS)

        # Agent positions  (mutable lists for in-place update)
        self.player_pos = list(PLAYER_START)
        self.enemy_pos  = list(ENEMY_START)

    # ── PLAYER ───────────────────────────────

    def move_player(self, dr: int, dc: int) -> bool:
        """
        Attempt to move the player by (dr, dc).

        Returns:
            True  if the move succeeded (cell was walkable)
            False if blocked by a wall or boundary
        """
        if self.game_over or self.paused:
            return False

        r, c = self.player_pos
        nr, nc = r + dr, c + dc

        if not self._in_bounds(nr, nc):
            return False

        cell = self.grid[nr][nc]
        if cell == WALL:
            return False

        self.player_pos = [nr, nc]

        if cell == TRAP:
            self._trigger_trap()
        elif cell == TREASURE:
            self._collect_treasure(nr, nc)

        self._check_capture()
        return True

    # ── ENEMY AI ─────────────────────────────

    def advance_enemy(self):
        """
        Execute one enemy move using A*.
        Called by the GUI's repeating timer.

        Returns:
            dict with keys:
                'path'     : current A* path (list of cells)
                'distance' : Manhattan distance to player
        """
        if self.game_over or self.paused:
            return {'path': [], 'distance': 0}

        self.tick += 1

        pr, pc = self.player_pos
        er, ec = self.enemy_pos

        path = astar(self.grid, (er, ec), (pr, pc))
        self.path_cells = path

        if path:
            nr, nc = path[0]
            self.enemy_pos = [nr, nc]
            self._check_capture()

        return {
            'path':     path,
            'distance': heuristic((er, ec), (pr, pc)),
        }

    # ── TIMING ───────────────────────────────

    @property
    def enemy_delay_ms(self) -> int:
        """Return current enemy move interval — ramps up with score."""
        from constants import (ENEMY_DELAY, MEDIUM_DELAY, FAST_DELAY, FASTEST_DELAY,
                               MEDIUM_THRESHOLD, FAST_THRESHOLD, FASTEST_THRESHOLD)
        if self.score >= FASTEST_THRESHOLD:
            return FASTEST_DELAY
        if self.score >= FAST_THRESHOLD:
            return FAST_DELAY
        if self.score >= MEDIUM_THRESHOLD:
            return MEDIUM_DELAY
        return ENEMY_DELAY

    # ─────────────────────────────────────────
    #  PRIVATE HELPERS
    # ─────────────────────────────────────────

    def _in_bounds(self, r: int, c: int) -> bool:
        from constants import ROWS, COLS
        return 0 <= r < ROWS and 0 <= c < COLS

    def _trigger_trap(self):
        r, c = self.player_pos
        self.flash_cells[(r, c)] = (TRAP_GLOW, self.tick + FLASH_TRAP_TICKS)
        self.lives -= 1
        self.on_hud_update()
        self.on_status_message("⚡ TRAP!  −1 LIFE")
        if self.lives <= 0:
            self._end(won=False)

    def _collect_treasure(self, r: int, c: int):
        self.grid[r][c] = EMPTY
        self.score += TREASURE_SCORE
        self.treasures_left -= 1
        self.flash_cells[(r, c)] = (TREASURE_GLOW, self.tick + FLASH_TREASURE_TICKS)
        self.on_hud_update()
        self.on_status_message(f"★  +{TREASURE_SCORE}")
        if self.treasures_left == 0:
            self._end(won=True)

    def _check_capture(self):
        if self.player_pos == self.enemy_pos:
            self._captured()

    def _captured(self):
        r, c = self.player_pos
        self.flash_cells[(r, c)] = (ENEMY_GLOW, self.tick + FLASH_CAPTURE_TICKS)
        self.lives -= 1
        self.on_hud_update()
        self.on_status_message("💀 CAUGHT!  −1 LIFE")
        # Respawn player at start
        self.player_pos = list(PLAYER_START)
        if self.lives <= 0:
            self._end(won=False)

    def _end(self, won: bool):
        self.game_over = True
        self.on_game_over(won)

    # ─────────────────────────────────────────
    #  READ-ONLY PROPERTIES for the renderer
    # ─────────────────────────────────────────

    @property
    def total_treasures(self) -> int:
        return len(TREASURE_POSITIONS)

    @property
    def treasures_found(self) -> int:
        return self.total_treasures - self.treasures_left