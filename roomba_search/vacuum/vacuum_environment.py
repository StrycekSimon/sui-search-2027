"""Vacuum task: online search with contact-only sensing.

Dirt locations are hidden from the agent: the robot only learns whether
a cell is dirty by physically standing on it. Walls and terrain are fully
known. The only known fact about the dirt is the total COUNT.

The problem is modeled as a plain interaction loop (same as the docking task):
a) VacuumEnvironment.run calls agent.choose_action(...) once per step
b) your algorithm decides the next step
c) the execution is performed
d) repeat from a)

The robot cleans the spot automatically upon arriving on a cell, but with
a `clean_success_prob` probability it succeeds. Each visit to a still-dirty
cell is an independent trial with this probability of actually succeeding.
Below 1.0, a cell can need more than one visit.

Sensing reports a past fact: `was_dirty_here` says whether the cell WAS
dirty when the robot arrived, before the cleaning attempt. The agent is not
told whether that attempt succeeded, so the cell may or may not be dirty
now -- the only way to find out is to visit it again.

Hint: When grading, there will be cases where cleaning all dirt spots in
the map will not be possible given the number of steps constraint. Your
goal is to clean as many dirt spots as possible.
"""
from __future__ import annotations

import copy
import dataclasses
import random
from dataclasses import dataclass, field
from typing import Any, Callable

from roomba_search.grid import Grid
from roomba_search.actions import action_target_or_raise


DEFAULT_CLEAN_SUCCESS_PROB = 1.0
DEFAULT_MAX_STEPS = 1000


@dataclass
class VacuumResult:
    cleaned_all: bool                               # True if no dirty cell is left
    path: list = field(default_factory=list)        # positions visited, start first
    remaining_dirt_progress: list = field(default_factory=list)  # per path position: snapshot of the dirty cells left after cleaning there
    total_cost: float = 0.0
    dirt_cleaned: int = 0                           # dirty cells actually cleaned (not just found)
    dirt_total: int = 0

    @property
    def steps_taken(self) -> int:
        """How many steps the robot made."""
        return len(self.path) - 1


class VacuumEnvironment:
    """One vacuum run on `grid`. Same shape as DockingEnvironment: the
    settings go to the constructor, `run(agent_factory)` executes the run.

    `seed` controls the cleaning-attempt randomness (see clean_success_prob)
    for reproducibility -- None means nondeterministic."""

    def __init__(
        self,
        grid: Grid,
        clean_success_prob: float = DEFAULT_CLEAN_SUCCESS_PROB,
        seed: int | None = None,
        max_steps: int = DEFAULT_MAX_STEPS
    ):
        if not 0.0 <= clean_success_prob <= 1.0:
            raise ValueError("clean_success_prob must be in <0, 1>")
        if grid.goal is not None:
            raise ValueError("Vacuum map must not contain a goal cell 'G'.")
        self.grid = grid
        self.clean_success_prob = clean_success_prob
        self.rng = random.Random(seed)
        self.max_steps = max_steps

    def run(self, agent_factory: Callable[[Grid, int, int], Any]) -> VacuumResult:
        """Creates the agent as `agent_factory(grid, dirt_total, max_steps)`:
        it gets its own copy of the map without any dirt, the true total
        dirt count -- the only thing told about dirt up front -- and the
        step limit of this run.

        Then the agent's `choose_action(true_pos, was_dirty_here)` is called
        once per step: true_pos is the robot's real current position, and
        was_dirty_here is whether THAT cell was dirty when the robot arrived,
        i.e. before this visit's cleaning attempt (true whether or not that
        attempt succeeded -- the agent is not told). Return an Action to
        keep going, or None to stop early. The run ends once every dirty
        cell has actually been cleaned, or after max_steps.

        Raises ValueError if the agent returns an action that isn't legal
        from its current position (it leads into a wall). Raises
        TypeError if the agent returns something that is neither an Action
        nor None."""
        grid = self.grid
        remaining_dirt = set(grid.dirt)
        dirt_total = len(remaining_dirt)

        # A separate copy of the grid, stripped of all dirt cells: whatever the
        # agent does to it has no effect on the real map
        blind_grid = dataclasses.replace(copy.deepcopy(grid), dirt=set())
        agent = agent_factory(blind_grid, dirt_total, self.max_steps)

        pos = grid.start
        path = [pos]
        total_cost = 0.0

        def clean_here(p: tuple) -> bool:
            was_dirty = p in remaining_dirt
            if was_dirty and self.rng.random() < self.clean_success_prob:
                remaining_dirt.discard(p)
            return was_dirty

        # The start cell 'S' is never dirty
        was_dirty_here = False
        remaining_dirt_progress = [frozenset(remaining_dirt)]
        dirt_cleaned = 0

        for _ in range(self.max_steps):
            if dirt_cleaned >= dirt_total:
                break

            action = agent.choose_action(pos, was_dirty_here)
            if action is None:
                break

            nxt = action_target_or_raise(grid, pos, action)
            total_cost += grid.cost(nxt)
            pos = nxt
            path.append(pos)

            was_dirty_here = clean_here(pos)
            remaining_dirt_progress.append(frozenset(remaining_dirt))
            dirt_cleaned = dirt_total - len(remaining_dirt)

        return VacuumResult(
            cleaned_all=dirt_cleaned >= dirt_total,
            path=path,
            remaining_dirt_progress=remaining_dirt_progress,
            total_cost=total_cost,
            dirt_cleaned=dirt_cleaned,
            dirt_total=dirt_total
        )
