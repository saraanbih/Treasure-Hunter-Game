"""
constants.py
All game-wide constants: grid settings, cell types,
color palette, map layout, and spawn positions.
"""

# ──────────────────────────────────────────────
#  GRID DIMENSIONS
# ──────────────────────────────────────────────
CELL  = 52          # pixel size of each grid cell
COLS  = 17
ROWS  = 13
W     = COLS * CELL  # canvas width  in pixels
H     = ROWS * CELL  # canvas height in pixels

# ──────────────────────────────────────────────
#  CELL TYPES
# ──────────────────────────────────────────────
EMPTY    = 0
WALL     = 1
TRAP     = 2
TREASURE = 3

# ──────────────────────────────────────────────
#  MOVEMENT COST (used by A* pathfinder)
# ──────────────────────────────────────────────
STEP_COSTS = {
    EMPTY:    1,
    TRAP:     5,   # passable but expensive
    TREASURE: 1,   # treated like empty for movement
    # WALL is impassable - not listed here
}

# ──────────────────────────────────────────────
#  COLOR PALETTE  (dark dungeon theme)
# ──────────────────────────────────────────────
BG_COLOR       = "#0d0d1a"

# Cell colors
EMPTY_COLOR    = "#12122a"
EMPTY_ALT      = "#111128"   # checkerboard second color
WALL_COLOR     = "#1a1a3a"
WALL_BORDER    = "#2a2a5a"
TRAP_COLOR     = "#2a0a0a"
TRAP_GLOW      = "#cc2200"
TREASURE_COLOR = "#1a1500"
TREASURE_GLOW  = "#f5c400"

# Agent colors
PLAYER_COLOR   = "#00d4ff"
PLAYER_GLOW    = "#006688"
ENEMY_COLOR    = "#ff3344"
ENEMY_GLOW     = "#880011"

# A* path overlay - drawn with stipple="gray12" for transparency
PATH_COLOR     = "#ff3344"

# ──────────────────────────────────────────────
#  MAP LAYOUT
#  0 = empty | 1 = wall | 2 = trap | 3 = treasure
# ──────────────────────────────────────────────
BASE_MAP = [
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
    [1,0,0,0,0,0,1,0,0,0,0,0,1,0,0,0,1],
    [1,0,1,1,0,0,1,0,1,1,1,0,1,0,1,0,1],
    [1,0,1,0,0,2,0,0,0,0,1,0,0,0,1,0,1],
    [1,0,0,0,1,1,1,1,0,0,1,1,1,0,0,0,1],
    [1,0,1,0,0,0,0,0,0,2,0,0,0,0,1,0,1],
    [1,0,1,1,1,0,1,0,1,1,1,0,1,1,1,0,1],
    [1,0,0,0,1,0,1,0,0,0,0,0,1,0,0,0,1],
    [1,0,1,0,0,0,1,1,1,0,1,0,0,0,1,0,1],
    [1,0,1,1,0,2,0,0,0,0,1,1,0,2,1,0,1],
    [1,0,0,0,0,0,1,0,1,0,0,0,0,0,0,0,1],
    [1,0,1,0,0,0,0,0,1,0,0,0,1,0,0,0,1],
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
]

TREASURE_POSITIONS = [
    (1, 3), (1, 13), (3,  7), (5, 11), (7, 15),
    (9, 5), (9, 11), (11, 7), (11,15), (3, 13),
]

PLAYER_START = (1,  1)
ENEMY_START  = (11, 15)

# ──────────────────────────────────────────────
#  ENEMY SPEED  (milliseconds between moves)
#  Higher value = slower enemy = easier
#  Speed ramps up gradually as you collect treasures
# ──────────────────────────────────────────────
ENEMY_DELAY       = 700   # 0-2 treasures:  slow, comfortable start
MEDIUM_DELAY      = 500   # 3-5 treasures:  picking up pace
FAST_DELAY        = 350   # 6-8 treasures:  getting tense
FASTEST_DELAY     = 220   # 9 treasures:    final sprint!

MEDIUM_THRESHOLD  = 300   # score when MEDIUM_DELAY kicks in
FAST_THRESHOLD    = 600   # score when FAST_DELAY kicks in
FASTEST_THRESHOLD = 900   # score when FASTEST_DELAY kicks in

# ──────────────────────────────────────────────
#  GAMEPLAY
# ──────────────────────────────────────────────
STARTING_LIVES       = 3
TREASURE_SCORE       = 100
FLASH_TRAP_TICKS     = 6
FLASH_TREASURE_TICKS = 8
FLASH_CAPTURE_TICKS  = 10