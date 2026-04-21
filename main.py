"""
main.py
Entry point for Treasure Hunter AI.

Responsibilities:
  - Show the splash / instruction screen
  - Launch the main GameWindow after the player clicks Start
  - Centre the window on screen

Run with:
    python main.py
"""

import tkinter as tk
from constants import BG_COLOR
from ui import GameWindow


# ─────────────────────────────────────────────
#  SPLASH SCREEN
# ─────────────────────────────────────────────

def show_splash(root: tk.Tk, on_start):
    """
    Display a modal intro screen.

    Args:
        root     : The hidden Tk root window
        on_start : Callback invoked when the player clicks START
    """
    splash = tk.Toplevel(root)
    splash.title("")
    splash.configure(bg=BG_COLOR)
    splash.resizable(False, False)
    splash.grab_set()   # block interaction with root until dismissed

    _centre_window(splash, width=500, height=360)

    # Title
    tk.Label(
        splash,
        text="⬡  TREASURE HUNTER GAME  ⬡",
        font=("Courier New", 20, "bold"),
        fg="#f5c400", bg=BG_COLOR,
    ).pack(pady=(40, 4))

    tk.Label(
        splash,
        text="Powered by  A★  Pathfinding",
        font=("Courier New", 12),
        fg="#4455aa", bg=BG_COLOR,
    ).pack(pady=(0, 12))

    # Instructions
    instructions = (
        "  ★   Collect ALL treasures to win\n"
        "  ⚡   Avoid traps — each one costs a life\n"
        "  ◆   The AI enemy hunts you with A*\n"
        "       Trap cells cost ×5 move points\n"
        "  ♥   You start with 3 lives\n"
        "  ⚡   Enemy speeds up at score ≥ 300\n"
        "\n"
        "  Controls:   Arrow Keys   or   W A S D\n"
    )
    tk.Label(
        splash,
        text=instructions,
        font=("Courier New", 11),
        fg="#aabbcc", bg=BG_COLOR,
        justify="left",
    ).pack(padx=30)

    def _start():
        splash.destroy()
        on_start()

    tk.Button(
        splash,
        text="[ START GAME ]",
        command=_start,
        font=("Courier New", 13, "bold"),
        fg="#f5c400", bg="#1a1500",
        activebackground="#2a2500", activeforeground="#f5c400",
        relief="flat", padx=20, pady=8,
        cursor="hand2", bd=0,
    ).pack(pady=20)


def _centre_window(win: tk.Tk, width: int, height: int):
    """Position a Tk window in the centre of the screen."""
    sw = win.winfo_screenwidth()
    sh = win.winfo_screenheight()
    x  = sw // 2 - width  // 2
    y  = sh // 2 - height // 2
    win.geometry(f"{width}x{height}+{x}+{y}")


# ─────────────────────────────────────────────
#  APPLICATION BOOTSTRAP
# ─────────────────────────────────────────────

def main():
    root = tk.Tk()
    root.configure(bg=BG_COLOR)
    root.withdraw()   # hide root until the game window is ready

    def launch_game():
        # Show the root window BEFORE building GameWindow so the canvas
        # has a real surface when the first draw fires after 100ms.
        root.deiconify()
        root.update_idletasks()
        game_win = GameWindow(root)
        root.update_idletasks()
        _centre_window(
            root,
            width=root.winfo_reqwidth(),
            height=root.winfo_reqheight(),
        )

    show_splash(root, on_start=launch_game)
    root.mainloop()


if __name__ == "__main__":
    main()