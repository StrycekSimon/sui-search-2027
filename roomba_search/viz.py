"""Terminal visualization: no external dependencies required."""
from __future__ import annotations

import sys
from typing import Iterator

from roomba_search.grid import DIRT, GOAL, START, TERRAIN_COST, WALL, Grid

# The map symbol of each terrain cost, taken from the map format itself
# (cost 1 -> ".", cost 2 -> "~")
_TERRAIN_CHARS = {cost: symbol for symbol, cost in TERRAIN_COST.items()}
ROBOT = "@"
WALKED = "+"


def render_single_state(
    grid: Grid,
    path: list | None = None,
    current: tuple | None = None,
    dirt: set | None = None
) -> str:
    """Generates a string containing a single state."""
    dirt = grid.dirt if dirt is None else dirt
    path_set = set(path or [])
    lines = []
    for r in range(grid.height):
        row = []
        for c in range(grid.width):
            pos = (r, c)
            if grid.is_wall(pos):
                ch = WALL
            elif pos == current:
                ch = ROBOT
            elif pos == grid.start:
                ch = START
            elif pos == grid.goal:
                ch = GOAL
            elif pos in dirt:
                ch = DIRT
            elif pos in path_set:
                ch = WALKED
            else:
                ch = _TERRAIN_CHARS[grid.cost(pos)]
            row.append(ch)
        lines.append("".join(row))
    return "\n".join(lines)


def _frames(
    grid: Grid,
    path: list,
    dirt: list | None = None,
    intended_actions: list | None = None,
    slipped: list | None = None
) -> Iterator[tuple[str, str]]:
    """Yields one (title, map) frame per state in `path`."""
    last = len(path) - 1
    for i, pos in enumerate(path):
        title = f"=== step {i}/{last} ==="
        if slipped and i > 0:
            title += f" slipped=True intended={intended_actions[i - 1].name}" if slipped[i - 1] else " slipped=False"
        yield title, render_single_state(
            grid,
            path=path[: i + 1],
            current=pos,
            dirt=dirt[i] if dirt else None
        )


def view_interactive(
    grid: Grid,
    path: list,
    dirt: list | None = None,
    intended_actions: list | None = None,
    slipped: list | None = None
) -> None:
    """
    Step-by-step terminal viewer: shows one frame of `path` at a time,
    Enter advances to the next frame, Ctrl+C quits.
    """
    if not path:
        return
    if not sys.stdin.isatty():
        print("(not an interactive terminal -- skipping; use --record for file output instead)")
        return

    for i, (title, frame) in enumerate(_frames(grid, path, dirt, intended_actions, slipped)):
        print(f"\n{title}")
        print(frame)
        if i == len(path) - 1:
            break
        try:
            input("(Enter = next step, Ctrl+C = quit) ")
        except (EOFError, KeyboardInterrupt):
            print()
            break


def record_trace(
    grid: Grid,
    path: list,
    file_path: str,
    dirt: list | None = None,
    intended_actions: list | None = None,
    slipped: list | None = None
) -> None:
    """
    Writes the same frames view_interactive shows, all at once, to a
    plain-text file.
    """
    frames = [
        f"{title}\n{frame}"
        for title, frame in _frames(grid, path, dirt, intended_actions, slipped)
    ]
    with open(file_path, "w") as f:
        f.write("\n\n".join(frames) + "\n")
