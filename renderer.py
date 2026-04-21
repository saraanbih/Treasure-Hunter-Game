"""
renderer.py
Handles all Tkinter canvas drawing.
Receives a GameState snapshot each frame and paints it.

Responsible for:
  - Grid tiles  (walls, traps, treasures, empty cells)
  - A* path overlay
  - Flash-cell effects
  - Player and enemy sprites
"""

import math
import tkinter as tk

from constants import (
    CELL, ROWS, COLS,
    EMPTY, WALL, TRAP, TREASURE,
    BG_COLOR,
    EMPTY_COLOR, EMPTY_ALT,
    WALL_COLOR, WALL_BORDER,
    TRAP_COLOR, TRAP_GLOW,
    TREASURE_COLOR, TREASURE_GLOW,
    PLAYER_COLOR, PLAYER_GLOW,
    ENEMY_COLOR, ENEMY_GLOW,
)


class Renderer:
    """
    Draws one full frame onto a Tkinter Canvas.

    Usage:
        renderer = Renderer(canvas)
        renderer.draw(game_state)   # call each frame
    """

    def __init__(self, canvas: tk.Canvas):
        self.canvas = canvas

    # ─────────────────────────────────────────
    #  PUBLIC
    # ─────────────────────────────────────────

    def draw(self, state) -> None:
        """
        Render a complete frame from the given GameState.

        Args:
            state: GameState instance (read-only access)
        """
        c = self.canvas
        c.delete("all")

        self._draw_grid(state.grid)
        self._draw_path(state.path_cells, state.enemy_pos, state.player_pos)
        self._draw_flash_cells(state.flash_cells, state.tick)
        self._draw_player(state.player_pos)
        self._draw_enemy(state.enemy_pos, state.tick)

    # ─────────────────────────────────────────
    #  PRIVATE DRAWING METHODS
    # ─────────────────────────────────────────

    def _draw_grid(self, grid: list) -> None:
        c = self.canvas
        for r in range(ROWS):
            for col in range(COLS):
                x1, y1 = col * CELL, r * CELL
                x2, y2 = x1 + CELL, y1 + CELL
                cell_type = grid[r][col]

                if cell_type == WALL:
                    self._draw_wall(x1, y1, x2, y2)

                elif cell_type == TRAP:
                    self._draw_trap(x1, y1, x2, y2)

                elif cell_type == TREASURE:
                    self._draw_treasure(x1, y1, x2, y2)

                else:
                    # Alternating checkerboard for empty cells
                    fill = EMPTY_COLOR if (r + col) % 2 == 0 else EMPTY_ALT
                    c.create_rectangle(x1, y1, x2, y2, fill=fill, outline="")

    def _draw_wall(self, x1, y1, x2, y2) -> None:
        c = self.canvas
        c.create_rectangle(x1, y1, x2, y2,
                            fill=WALL_COLOR, outline=WALL_BORDER, width=1)
        # Inner bevel lines for a 3-D stone effect
        c.create_line(x1 + 2, y1 + 2, x2 - 2, y1 + 2, fill="#252550", width=1)
        c.create_line(x1 + 2, y1 + 2, x1 + 2, y2 - 2, fill="#252550", width=1)

    def _draw_trap(self, x1, y1, x2, y2) -> None:
        c = self.canvas
        c.create_rectangle(x1, y1, x2, y2,
                            fill=TRAP_COLOR, outline=TRAP_GLOW, width=1)
        mx, my = x1 + CELL // 2, y1 + CELL // 2
        c.create_text(mx, my, text="⚡", font=("Arial", 16), fill=TRAP_GLOW)

    def _draw_treasure(self, x1, y1, x2, y2) -> None:
        c = self.canvas
        c.create_rectangle(x1, y1, x2, y2,
                            fill=TREASURE_COLOR, outline=TREASURE_GLOW, width=1)
        mx, my = x1 + CELL // 2, y1 + CELL // 2
        c.create_text(mx, my, text="★", font=("Arial", 20, "bold"),
                      fill=TREASURE_GLOW)
        # Glow halo ring
        c.create_oval(mx - 14, my - 14, mx + 14, my + 14,
                      outline=TREASURE_GLOW, width=1, fill="")

    def _draw_path(self, path_cells: list,
                   enemy_pos: list, player_pos: list) -> None:
        """Draw the A* path as a semi-transparent red overlay.
        Tkinter only supports 6-digit #RRGGBB hex — transparency is
        achieved with stipple patterns instead of an alpha channel.
        """
        c = self.canvas
        for pr, pc in path_cells:
            if [pr, pc] == enemy_pos or [pr, pc] == player_pos:
                continue
            x1 = pc * CELL + 4
            y1 = pr * CELL + 4
            x2 = x1 + CELL - 8
            y2 = y1 + CELL - 8
            c.create_rectangle(x1, y1, x2, y2,
                                fill="#ff3344", outline="#ff3344",
                                stipple="gray12", width=1)

    def _draw_flash_cells(self, flash_cells: dict, tick: int) -> None:
        """Draw temporary colour flashes (trap hit, capture, treasure)."""
        c = self.canvas
        expired = []
        for (fr, fc), (color, expiry) in flash_cells.items():
            if tick <= expiry:
                x1, y1 = fc * CELL, fr * CELL
                c.create_rectangle(x1, y1, x1 + CELL, y1 + CELL,
                                   fill=color, outline="", stipple="gray25")
            else:
                expired.append((fr, fc))
        # Clean up expired entries
        for key in expired:
            del flash_cells[key]

    def _draw_player(self, player_pos: list) -> None:
        c  = self.canvas
        pr, pc = player_pos
        px = pc * CELL + CELL // 2
        py = pr * CELL + CELL // 2
        R  = CELL // 2 - 5

        # Soft glow behind the body
        c.create_oval(px - R - 5, py - R - 5, px + R + 5, py + R + 5,
                      fill=PLAYER_GLOW, outline="", stipple="gray12")
        # Body circle
        c.create_oval(px - R, py - R, px + R, py + R,
                      fill=PLAYER_COLOR, outline="#aaeeff", width=2)
        # Eyes
        c.create_oval(px - 7, py - 6, px - 2, py - 1, fill="white", outline="")
        c.create_oval(px + 2, py - 6, px + 7, py - 1, fill="white", outline="")
        c.create_oval(px - 6, py - 5, px - 3, py - 2, fill="#001a22", outline="")
        c.create_oval(px + 3, py - 5, px + 6, py - 2, fill="#001a22", outline="")

    def _draw_enemy(self, enemy_pos: list, tick: int) -> None:
        c  = self.canvas
        er, ec = enemy_pos
        ex = ec * CELL + CELL // 2
        ey = er * CELL + CELL // 2
        R  = CELL // 2 - 5

        # Pulsing glow ring (sine-wave radius)
        pulse = int(4 + 3 * math.sin(tick * 0.4))
        c.create_oval(ex - R - pulse, ey - R - pulse,
                      ex + R + pulse, ey + R + pulse,
                      fill=ENEMY_GLOW, outline="", stipple="gray12")
        # Diamond-shaped body
        pts = [ex, ey - R, ex + R, ey, ex, ey + R, ex - R, ey]
        c.create_polygon(pts, fill=ENEMY_COLOR, outline="#ff8888", width=2)
        # Skull eyes
        c.create_oval(ex - 8, ey - 8, ex - 2, ey - 2, fill="#330000", outline="")
        c.create_oval(ex + 2, ey - 8, ex + 8, ey - 2, fill="#330000", outline="")
        c.create_text(ex, ey + 4, text="✕", font=("Arial", 6, "bold"),
                      fill="#660000")