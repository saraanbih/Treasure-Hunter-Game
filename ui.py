"""
ui.py
Tkinter UI layer — window, HUD, canvas, buttons.

Wires together:
  - GameState  (logic)
  - Renderer   (drawing)
  - Keyboard input → GameState.move_player()
  - Enemy timer  → GameState.advance_enemy()

This file is the only one that imports tkinter.
"""

import tkinter as tk
from tkinter import messagebox

from constants import (
    W, H, BG_COLOR,
    TREASURE_POSITIONS,
)
from game_state import GameState
from renderer   import Renderer


class GameWindow:
    """
    Top-level application window.

    Owns the Tk root, all widgets, and the two timers
    (enemy movement + status-message clear).
    """

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Treasure Hunter AI")
        self.root.resizable(False, False)
        self.root.configure(bg=BG_COLOR)

        # Core objects
        self.state    = GameState()
        self.renderer = None   # created after canvas widget exists

        # Timer handles
        self._enemy_timer  = None
        self._msg_timer    = None

        self._build_widgets()
        self._wire_callbacks()
        self._bind_keys()

        # Start first game
        self._start_game()

    # ─────────────────────────────────────────
    #  WIDGET CONSTRUCTION
    # ─────────────────────────────────────────

    def _build_widgets(self):
        self._build_title_bar()
        self._build_hud()
        self._build_canvas()
        self._build_controls()
        self._build_legend()

    def _build_title_bar(self):
        frame = tk.Frame(self.root, bg=BG_COLOR)
        frame.pack(fill="x")

        tk.Label(frame,
                 text="⬡  TREASURE HUNTER AI  ⬡",
                 font=("Courier New", 18, "bold"),
                 fg="#f5c400", bg=BG_COLOR
                 ).pack(side="left", padx=20, pady=8)

        tk.Label(frame,
                 text="A★  Pathfinding Engine",
                 font=("Courier New", 10),
                 fg="#4455aa", bg=BG_COLOR
                 ).pack(side="left", pady=8)

    def _build_hud(self):
        hud = tk.Frame(self.root, bg=BG_COLOR, pady=4)
        hud.pack(fill="x", padx=16)

        self.score_var  = tk.StringVar(value="SCORE      0")
        self.lives_var  = tk.StringVar(value="LIVES  ♥♥♥")
        self.status_var = tk.StringVar(value="")
        self.ai_var     = tk.StringVar(value="AI:  HUNTING")

        hud_items = [
            (self.score_var, "#f5c400", "left"),
            (self.lives_var, "#ff3344", "left"),
            (self.ai_var,    "#ff3344", "right"),
            (self.status_var,"#00d4ff", "right"),
        ]
        for var, color, side in hud_items:
            tk.Label(hud,
                     textvariable=var,
                     font=("Courier New", 12, "bold"),
                     fg=color, bg=BG_COLOR
                     ).pack(side=side, padx=12)

    def _build_canvas(self):
        self.canvas = tk.Canvas(
            self.root, width=W, height=H,
            bg=BG_COLOR, highlightthickness=0
        )
        self.canvas.pack(padx=16, pady=4)
        self.renderer = Renderer(self.canvas)

    def _build_controls(self):
        ctrl = tk.Frame(self.root, bg=BG_COLOR, pady=6)
        ctrl.pack(fill="x", padx=16)

        btn_style = dict(
            font=("Courier New", 10, "bold"),
            bg="#1a1a3a", fg="#00d4ff",
            activebackground="#2a2a5a", activeforeground="#00d4ff",
            relief="flat", padx=14, pady=5, cursor="hand2", bd=0,
        )

        tk.Button(ctrl, text="[ NEW GAME ]",
                  command=self._new_game, **btn_style).pack(side="left", padx=4)
        tk.Button(ctrl, text="[ PAUSE ]",
                  command=self._toggle_pause, **btn_style).pack(side="left", padx=4)

        tk.Label(ctrl,
                 text="Arrow keys / WASD to move",
                 font=("Courier New", 9),
                 fg="#334466", bg=BG_COLOR
                 ).pack(side="right", padx=8)

    def _build_legend(self):
        leg = tk.Frame(self.root, bg=BG_COLOR, pady=4)
        leg.pack(fill="x", padx=16, pady=(0, 8))

        legend_items = [
            ("■  Wall",       "#2a2a5a"),
            ("⚡  Trap",       "#cc2200"),
            ("★  Treasure",   "#f5c400"),
            ("●  Player",     "#00d4ff"),
            ("◆  Enemy",      "#ff3344"),
        ]
        for text, color in legend_items:
            tk.Label(leg, text=text,
                     font=("Courier New", 9),
                     fg=color, bg=BG_COLOR
                     ).pack(side="left", padx=10)

    # ─────────────────────────────────────────
    #  CALLBACK WIRING
    # ─────────────────────────────────────────

    def _wire_callbacks(self):
        """Connect GameState event hooks to UI methods."""
        self.state.on_status_message = self._show_status
        self.state.on_game_over      = self._handle_game_over
        self.state.on_hud_update     = self._update_hud

    # ─────────────────────────────────────────
    #  KEY BINDING
    # ─────────────────────────────────────────

    def _bind_keys(self):
        self.root.bind("<KeyPress>", self._on_key)
        self.root.focus_set()

    _KEY_MAP = {
        "up":    (-1,  0),
        "w":     (-1,  0),
        "down":  ( 1,  0),
        "s":     ( 1,  0),
        "left":  ( 0, -1),
        "a":     ( 0, -1),
        "right": ( 0,  1),
        "d":     ( 0,  1),
    }

    def _on_key(self, event):
        direction = self._KEY_MAP.get(event.keysym.lower())
        if direction:
            moved = self.state.move_player(*direction)
            if moved:
                self._refresh()

    # ─────────────────────────────────────────
    #  GAME LIFECYCLE
    # ─────────────────────────────────────────

    def _start_game(self):
        self._update_hud()
        # Delay the first draw by two frames so the window is fully
        # visible before we paint. Without this the canvas renders
        # while the window is still hidden and the first frame is lost.
        self.root.after(100, self._first_draw)

    def _first_draw(self):
        """Called once after the window is guaranteed to be visible."""
        self.root.update_idletasks()
        self._refresh()
        self._schedule_enemy()

    def _new_game(self):
        self._cancel_timers()
        self.state.reset()
        self.status_var.set("")
        self._update_hud()
        self._refresh()          # immediate redraw is fine here — window is already visible
        self._schedule_enemy()

    def _toggle_pause(self):
        if self.state.game_over:
            return
        self.state.paused = not self.state.paused
        if self.state.paused:
            self.status_var.set("⏸  PAUSED")
            self._cancel_timers()
        else:
            self.status_var.set("")
            self._schedule_enemy()

    # ─────────────────────────────────────────
    #  ENEMY TIMER
    # ─────────────────────────────────────────

    def _schedule_enemy(self):
        delay = self.state.enemy_delay_ms
        self._enemy_timer = self.root.after(delay, self._enemy_tick)

    def _enemy_tick(self):
        if self.state.game_over or self.state.paused:
            return

        result = self.state.advance_enemy()
        self._update_ai_label(result['distance'])
        self._refresh()

        if not self.state.game_over:
            self._schedule_enemy()

    def _update_ai_label(self, distance: int):
        if distance <= 3:
            self.ai_var.set("AI:  🔴  CLOSING IN!")
        elif distance <= 6:
            self.ai_var.set("AI:  🟠  PURSUING")
        else:
            self.ai_var.set("AI:  🟡  TRACKING")

    # ─────────────────────────────────────────
    #  RENDER
    # ─────────────────────────────────────────

    def _refresh(self):
        """Ask the renderer to draw the current state."""
        self.renderer.draw(self.state)

    # ─────────────────────────────────────────
    #  HUD UPDATES
    # ─────────────────────────────────────────

    def _update_hud(self):
        self.score_var.set(f"SCORE   {self.state.score:>5}")
        hearts = "♥" * self.state.lives + "♡" * (3 - self.state.lives)
        self.lives_var.set(
            f"LIVES  {hearts}  │  "
            f"TREASURE  {self.state.treasures_found}/{self.state.total_treasures}"
        )

    def _show_status(self, msg: str):
        self.status_var.set(msg)
        # Auto-clear after 1.3 seconds
        if self._msg_timer:
            self.root.after_cancel(self._msg_timer)
        self._msg_timer = self.root.after(1300, lambda: self.status_var.set(""))

    # ─────────────────────────────────────────
    #  GAME OVER
    # ─────────────────────────────────────────

    def _handle_game_over(self, won: bool):
        self._cancel_timers()
        self._refresh()   # draw final frame

        header = "🏆  VICTORY!" if won else "💀  GAME OVER"
        body   = (
            f"Score:              {self.state.score}\n"
            f"Treasures collected: {self.state.treasures_found}"
            f" / {self.state.total_treasures}\n"
            f"Lives remaining:     {self.state.lives}"
        )
        play_again = messagebox.askyesno(header, body + "\n\nPlay again?")
        if play_again:
            self._new_game()

    # ─────────────────────────────────────────
    #  TIMER CLEANUP
    # ─────────────────────────────────────────

    def _cancel_timers(self):
        for attr in ('_enemy_timer', '_msg_timer'):
            handle = getattr(self, attr, None)
            if handle:
                self.root.after_cancel(handle)
                setattr(self, attr, None)