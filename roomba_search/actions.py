"""
Shared movement definitions: the actions the robot can take and where they
lead on a map. Both tasks and the engine itself use them.
"""

from __future__ import annotations

from enum import Enum

from roomba_search.grid import Grid


# Possible map actions
class Action(Enum):
    UP = "UP"
    DOWN = "DOWN"
    LEFT = "LEFT"
    RIGHT = "RIGHT"


# The order legal_actions() lists moves in BY DEFAULT.
# The order is not a constraint, just a default value.
ACTION_ORDER = [Action.UP, Action.DOWN, Action.LEFT, Action.RIGHT]
_ACTION_DELTAS = {
    Action.UP: (-1, 0),
    Action.DOWN: (1, 0),
    Action.LEFT: (0, -1),
    Action.RIGHT: (0, 1),
}


def action_target(grid: Grid, pos: tuple, action: Action) -> tuple | None:
    """The cell an `action` from `pos` leads to, or None if that cell is a
    wall. No slipping involved."""
    delta_row, delta_col = _ACTION_DELTAS[action]
    nxt = (pos[0] + delta_row, pos[1] + delta_col)
    return nxt if grid.is_walkable(nxt) else None


def action_target_or_raise(grid: Grid, pos: tuple, action: Action) -> tuple:
    """The cell `action` from `pos` leads to, for an action that must be
    valid (the engine uses it on what an agent returned).
    Raises TypeError if `action` is not an Action, and ValueError if it is
    illegal (leads into a wall)."""
    if not isinstance(action, Action):
        raise TypeError(f"choose_action must return an Action or None, got {action!r}")
    target = action_target(grid, pos, action)
    if target is None:
        raise ValueError(f"Illegal action {action} from {pos}.")
    return target


def legal_actions(grid: Grid, pos: tuple) -> list:
    """The actions that can be taken from `pos` (those not leading into a
    wall), in `ACTION_ORDER`. Your own code may use any order."""
    return [a for a in ACTION_ORDER if action_target(grid, pos, a) is not None]
