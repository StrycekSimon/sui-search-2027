"""YOUR SOLUTION GOES IN THIS FILE.

There are two tasks, each with its own entry point below:

  1. Docking -- `DockingAgent`: get the robot to the dock, deciding one
     step at a time while wheel slips push it off course.
  2. Vacuum -- `VacuumAgent`: find and clean dirt whose locations are
     hidden from you, deciding one step at a time.

Both are agents: the script creates a dedicated agent for a specified
task and calls its `choose_action(...)` once per step; you return the next Action.

Let this file be your playground - you can define your own helper functions,
define your own state variables, etc. The only requirement is that you
ensure the pre-defined interface is kept intact (`DockingAgent` and `VacuumAgent`).
You are not allowed to override the pre-defined codebase in a way to either
expose hidden variables (like dirt location) or change the behavior of the
execution loop.

In this project, primarily the performance of your solution will be graded.
"""
from __future__ import annotations

from roomba_search.grid import Grid
# Helpers for moving on the map, usable in both tasks:
#   legal_actions(grid, pos)         -> the actions that do not lead into a wall
#   action_target(grid, pos, action) -> the cell an action leads to (None for a wall)
#   grid.cost(cell)                  -> the cost of entering a cell
from roomba_search.actions import Action, action_target, legal_actions


###################
# Task 1: Docking #
###################

class DockingAgent:
    """Gets the robot to the dock. roomba_search/docking/docking_environment.py
    constructs this agent once per run and calls choose_action(...) per
    step, executing the action you return -- which may slip (the robot
    ends up somewhere other than intended - see `docking_environment.py`).

    __init__ gets the Grid, representing the whole map, and the step limit
    of the run (`max_steps`): the run is cut off after that many moves.
    You are free to keep whatever state you need between steps as
    attributes of this class.

    choose_action(true_pos) gets the robot's true current position.
    Return the next Action, or None if the dock can't be reached."""

    def __init__(self, grid: Grid, max_steps: int):
        raise NotImplementedError("TODO: set up whatever state you need")

    def choose_action(self, true_pos: tuple) -> Action | None:
        raise NotImplementedError("TODO: decide where to go next")


##################
# Task 2: Vacuum #
##################

class VacuumAgent:
    """Cleans the map from all dirt places. Dirt locations are hidden.
    The execution logic stays the same as for the Docking task.

    __init__ gets a Grid -- but its .dirt is always empty; you SHOULD
    NOT rely on it or try to extract it. Consider dirt locations
    as strictly unknown for your solution. It also gets the total
    number of dirty cells (`dirt_total`) and the step limit of the
    run (`max_steps`): the run is cut off after that many moves.

    You can keep any planning-related values stored as attributes of
    this class.

    choose_action(true_pos, was_dirty_here) is called once per step:
    true_pos is the robot's real current position, and was_dirty_here
    says whether THAT cell was dirty when the robot arrived.
    The robot cleans the cell automatically upon arrival, but the
    cleaning might not be successful (see `clean_success_prob` in
    roomba_search/vacuum/vacuum_environment.py).
    `was_dirty_here` is a fact about the past: it does not guarantee
    a successful cleaning, so the cell may or may not be dirty now.
    """

    def __init__(self, grid: Grid, dirt_total: int, max_steps: int):
        raise NotImplementedError("TODO: set up whatever state you need")

    def choose_action(self, true_pos: tuple, was_dirty_here: bool) -> Action | None:
        raise NotImplementedError("TODO: decide where to go next")
