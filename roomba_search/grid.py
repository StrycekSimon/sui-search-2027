"""Grid loading and representation.

Map file format (plain ASCII, one line per row):
    #   wall
    .   tile floor   (cost 1 to enter)
    ~   carpet       (cost 2 to enter)
    S   start cell (exactly one required)
    G   goal / dock cell (docking only; at most one per map)
    *   dirt (vacuum only)

All non-wall symbols are walkable. S, G and * cells behave like tile floor
(cost 1) once the robot is standing on them.

Layout rules checked for every map: all rows have the same length, there
are no blank lines between rows and the outer frame is all walls.
Which of 'G' / '*' a map may contain is checked by each task.
"""
from __future__ import annotations

from dataclasses import dataclass, field

TERRAIN_COST = {".": 1, "~": 2}
WALL = "#"
START = "S"
GOAL = "G"
DIRT = "*"
DEFAULT_COST = TERRAIN_COST["."]  # S, G and * cells cost the same as tile floor


class MapError(ValueError):
    """Raised when a map file/string is malformed."""


@dataclass
class Grid:
    height: int
    width: int
    walls: set
    terrain: dict
    start: tuple
    goal: tuple | None
    dirt: set = field(default_factory=set)

    @classmethod
    def from_lines(cls, lines: list[str]) -> Grid:
        """Builds the grid from map rows: one string per row, without line endings."""
        if not lines:
            raise MapError("map is empty")
        width = len(lines[0])
        for i, line in enumerate(lines):
            if len(line) != width:
                raise MapError(
                    f"row {i} has length {len(line)}, expected {width} "
                    "(all rows must be the same length; pad with '#')"
                )
        height = len(lines)

        walls: set = set()
        terrain: dict = {}
        dirt: set = set()
        start = None
        goal = None

        for r, line in enumerate(lines):
            for c, ch in enumerate(line):
                pos = (r, c)
                if ch == WALL:
                    walls.add(pos)
                elif ch == START:
                    if start is not None:
                        raise MapError("map has more than one start cell 'S'")
                    start = pos
                    terrain[pos] = DEFAULT_COST
                elif ch == GOAL:
                    if goal is not None:
                        raise MapError("map has more than one goal cell 'G'")
                    goal = pos
                    terrain[pos] = DEFAULT_COST
                elif ch == DIRT:
                    dirt.add(pos)
                    terrain[pos] = DEFAULT_COST
                elif ch in TERRAIN_COST:
                    terrain[pos] = TERRAIN_COST[ch]
                else:
                    raise MapError(f"unknown map symbol {ch!r} at row {r}, col {c}")

        if start is None:
            raise MapError("map has no start cell 'S'")

        # Map should not be open
        for r, line in enumerate(lines):
            border_cols = range(width) if r in (0, height - 1) else (0, width - 1)
            for c in border_cols:
                if line[c] != WALL:
                    raise MapError(f"map border must be walls, found a walkable cell at row {r}, col {c}")

        return cls(
            height=height,
            width=width,
            walls=walls,
            terrain=terrain,
            start=start,
            goal=goal,
            dirt=dirt
        )

    @classmethod
    def from_string(cls, text: str) -> Grid:
        """Splits map text into rows."""
        return cls.from_lines(text.strip("\r\n").splitlines())

    @classmethod
    def from_file(cls, path: str) -> Grid:
        with open(path, "r") as f:
            return cls.from_string(f.read())

    def in_bounds(self, pos: tuple) -> bool:
        r, c = pos
        return 0 <= r < self.height and 0 <= c < self.width

    def is_wall(self, pos: tuple) -> bool:
        return pos in self.walls

    def is_walkable(self, pos: tuple) -> bool:
        return self.in_bounds(pos) and not self.is_wall(pos)

    def cost(self, pos: tuple) -> float:
        """Cost to enter `pos` (assumes walkable)."""
        return self.terrain.get(pos, DEFAULT_COST)
