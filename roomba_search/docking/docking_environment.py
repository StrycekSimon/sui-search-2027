"""Stochastic execution layer for the docking task.

`DockingEnvironment(grid, ...).run(agent_factory)` creates the agent and runs
a closed loop: before every step, ask the agent for the next action from the
robot's current true position, execute it (it may slip, see `slip_prob`),
and repeat from wherever the robot actually ended up.

A slip is directional: the robot still moves forward but drifts one cell
sideways, ending diagonally ahead of where it started (see
`slip_targets`).
"""
from __future__ import annotations

import copy
import random
from dataclasses import dataclass, field
from typing import Any, Callable

from roomba_search.grid import Grid
from roomba_search.actions import Action, action_target, action_target_or_raise

# For each action: the two directions it can drift towards when it slips
# (perpendicular to the movement). Example, moving RIGHT from @:
#
#     . s        > = intended cell (no slip)
#     @ >        s = where a slip can land (only if not a wall)
#     . s
#
_SLIP_DIRECTIONS = {
    Action.UP: (Action.LEFT, Action.RIGHT),
    Action.DOWN: (Action.LEFT, Action.RIGHT),
    Action.LEFT: (Action.UP, Action.DOWN),
    Action.RIGHT: (Action.UP, Action.DOWN),
}


DEFAULT_SLIP_PROB = 0.0
DEFAULT_MAX_STEPS = 500


def slip_targets(grid: Grid, pos: tuple, action: Action) -> list:
    """Cells the robot can end up in if `action` from `pos` slips"""
    intended = action_target_or_raise(grid, pos, action)
    targets = [action_target(grid, intended, side) for side in _SLIP_DIRECTIONS[action]]
    return [t for t in targets if t is not None]


@dataclass
class DockingResult:
    reached_goal: bool
    path: list = field(default_factory=list)   # positions actually visited, start first
    intended_actions: list = field(default_factory=list)  # per step: the action the agent chose
    slipped: list = field(default_factory=list)     # per step: True if that action landed somewhere unintended
    total_cost: float = 0.0

    @property
    def steps_taken(self) -> int:
        """How many steps the robot made."""
        return len(self.path) - 1

    @property
    def number_of_slips(self) -> int:
        """How many steps slipped."""
        return sum(self.slipped)


class DockingEnvironment:
    """One docking run on `grid`. Same shape as VacuumEnvironment: the
    settings go to the constructor, `run(agent_factory)` executes the run."""

    def __init__(
        self,
        grid: Grid,
        slip_prob: float = DEFAULT_SLIP_PROB,
        seed: int | None = None,
        max_steps: int = DEFAULT_MAX_STEPS
    ):
        if not 0.0 <= slip_prob <= 1.0:
            raise ValueError("slip_prob must be in <0, 1>")
        if grid.goal is None:
            raise ValueError("Docking map has no goal cell 'G'.")
        if grid.dirt:
            raise ValueError("Docking map must not contain dirt '*'.")
        self.grid = grid
        self.slip_prob = slip_prob
        self.rng = random.Random(seed)
        self.max_steps = max_steps

    def _move_with_slip(self, pos: tuple, action: Action) -> tuple[tuple, bool]:
        """Executes `action` from `pos` the way the real robot does: with
        probability slip_prob the robot drifts sideways and ends up in one
        of `slip_targets` (chosen at random) instead of the intended cell.

        Returns (actual_next_pos, slipped: bool)."""
        intended = action_target_or_raise(self.grid, pos, action)
        if self.rng.random() >= self.slip_prob:
            return intended, False
        targets = slip_targets(self.grid, pos, action)
        if not targets:
            return intended, False
        return self.rng.choice(targets), True

    def run(self, agent_factory: Callable[[Grid, int], Any]) -> DockingResult:
        """Creates the agent as `agent_factory(grid, max_steps)`: it gets its
        own copy of the map and the step limit of this run.
        Then runs the closed loop: before every step,
        call `agent.choose_action(true_pos)` with the robot's current
        true position, and execute the returned action.
        Stops at the goal, when the agent returns None,
        or after `max_steps` actions. An illegal action
        raises ValueError; returning something that is neither an
        Action nor None raises TypeError."""
        grid = self.grid
        # A separate copy of the grid: whatever the agent does to it has
        # no effect on the real map
        agent = agent_factory(copy.deepcopy(grid), self.max_steps)

        pos = grid.start
        path = [pos]
        intended_actions = []
        slipped = []
        total_cost = 0.0

        while len(path) - 1 < self.max_steps and pos != grid.goal:
            action = agent.choose_action(pos)
            if action is None:
                break

            actual, did_slip = self._move_with_slip(pos, action)
            total_cost += grid.cost(actual)  # the cell actually entered
            intended_actions.append(action)
            slipped.append(did_slip)
            pos = actual
            path.append(pos)

        return DockingResult(
            reached_goal=pos == grid.goal,
            path=path,
            intended_actions=intended_actions,
            slipped=slipped,
            total_cost=total_cost
        )
