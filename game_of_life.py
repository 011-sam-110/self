"""
Conway's Game of Life
Written during free time. Not infrastructure — something to actually run and watch.

Rules:
  1. A live cell with < 2 live neighbors dies (underpopulation)
  2. A live cell with 2 or 3 live neighbors survives
  3. A live cell with > 3 live neighbors dies (overpopulation)
  4. A dead cell with exactly 3 live neighbors becomes alive

Run:  python game_of_life.py
Keys: space=pause, r=randomize, g=glider gun, q=quit, +/-=speed
"""

import time
import sys
import random
import os

try:
    import curses
except ImportError:
    print("This script requires the curses module (standard on Linux/Mac, needs 'windows-curses' on Windows).")
    print("Install with: pip install windows-curses")
    sys.exit(1)

# ── Patterns ────────────────────────────────────────────────────────────────

GLIDER = [
    (0, 1), (1, 2), (2, 0), (2, 1), (2, 2)
]

BLINKER = [(0, 0), (0, 1), (0, 2)]

PULSAR = [
    (0,2),(0,3),(0,4),(0,8),(0,9),(0,10),
    (2,0),(2,5),(2,7),(2,12),
    (3,0),(3,5),(3,7),(3,12),
    (4,0),(4,5),(4,7),(4,12),
    (5,2),(5,3),(5,4),(5,8),(5,9),(5,10),
    (7,2),(7,3),(7,4),(7,8),(7,9),(7,10),
    (8,0),(8,5),(8,7),(8,12),
    (9,0),(9,5),(9,7),(9,12),
    (10,0),(10,5),(10,7),(10,12),
    (12,2),(12,3),(12,4),(12,8),(12,9),(12,10),
]

# Gosper Glider Gun
GLIDER_GUN = [
    (0,24),
    (1,22),(1,24),
    (2,12),(2,13),(2,20),(2,21),(2,34),(2,35),
    (3,11),(3,15),(3,20),(3,21),(3,34),(3,35),
    (4,0),(4,1),(4,10),(4,16),(4,20),(4,21),
    (5,0),(5,1),(5,10),(5,14),(5,16),(5,17),(5,22),(5,24),
    (6,10),(6,16),(6,24),
    (7,11),(7,15),
    (8,12),(8,13),
]

# ── Grid operations ──────────────────────────────────────────────────────────

def empty_grid(rows, cols):
    return set()

def random_grid(rows, cols, density=0.3):
    return {(r, c) for r in range(rows) for c in range(cols) if random.random() < density}

def place_pattern(grid, pattern, offset_r, offset_c):
    for (r, c) in pattern:
        grid.add((r + offset_r, c + offset_c))
    return grid

def step(grid, rows, cols):
    neighbor_counts = {}
    for (r, c) in grid:
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if dr == 0 and dc == 0:
                    continue
                nr, nc = (r + dr) % rows, (c + dc) % cols
                neighbor_counts[(nr, nc)] = neighbor_counts.get((nr, nc), 0) + 1

    new_grid = set()
    for cell, count in neighbor_counts.items():
        if count == 3 or (count == 2 and cell in grid):
            new_grid.add(cell)
    return new_grid

def count_cells(grid):
    return len(grid)

# ── Rendering ────────────────────────────────────────────────────────────────

CELL = "█"
DEAD = " "

def draw(stdscr, grid, rows, cols, generation, population, paused, delay_ms):
    stdscr.erase()
    max_r, max_c = stdscr.getmaxyx()

    for r in range(min(rows, max_r - 2)):
        row_str = ""
        for c in range(min(cols, max_c)):
            row_str += CELL if (r, c) in grid else DEAD
        try:
            stdscr.addstr(r, 0, row_str)
        except curses.error:
            pass

    status = (
        f" Gen: {generation:6d}  "
        f"Pop: {population:5d}  "
        f"Speed: {1000//delay_ms:3d}fps  "
        f"{'[PAUSED]' if paused else '[RUNNING]'}  "
        f"  space=pause  r=random  g=gun  q=quit  +/-=speed"
    )
    try:
        stdscr.addstr(max_r - 1, 0, status[:max_c - 1], curses.A_REVERSE)
    except curses.error:
        pass

    stdscr.refresh()

# ── Main loop ────────────────────────────────────────────────────────────────

def main(stdscr):
    curses.curs_set(0)
    stdscr.nodelay(True)

    max_r, max_c = stdscr.getmaxyx()
    rows = max_r - 2
    cols = max_c

    # Start with glider gun centered
    grid = empty_grid(rows, cols)
    gun_r = max(0, rows // 2 - 20)
    gun_c = max(0, cols // 2 - 20)
    grid = place_pattern(grid, GLIDER_GUN, gun_r, gun_c)

    generation = 0
    paused = False
    delay_ms = 100

    while True:
        key = stdscr.getch()

        if key == ord('q'):
            break
        elif key == ord(' '):
            paused = not paused
        elif key == ord('r'):
            grid = random_grid(rows, cols, density=0.25)
            generation = 0
        elif key == ord('g'):
            grid = empty_grid(rows, cols)
            gun_r = max(0, rows // 2 - 20)
            gun_c = max(0, cols // 2 - 20)
            grid = place_pattern(grid, GLIDER_GUN, gun_r, gun_c)
            generation = 0
        elif key == ord('+') or key == ord('='):
            delay_ms = max(16, delay_ms - 16)
        elif key == ord('-'):
            delay_ms = min(500, delay_ms + 16)

        draw(stdscr, grid, rows, cols, generation, count_cells(grid), paused, delay_ms)

        if not paused:
            grid = step(grid, rows, cols)
            generation += 1

        time.sleep(delay_ms / 1000)


if __name__ == "__main__":
    try:
        curses.wrapper(main)
    except KeyboardInterrupt:
        pass
