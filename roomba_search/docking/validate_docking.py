"""
Validation of an executed docking run (DockingResult).
"""

from __future__ import annotations

from roomba_search.grid import Grid
from roomba_search.actions import action_target
from roomba_search.docking.docking_environment import DockingResult, slip_targets


def validate_docking_result(grid: Grid, exec_result: DockingResult) -> list:
    """
    Validates an executed docking run on `grid` step by step.
    """
    path = exec_result.path
    if not path:
        return ["Path is empty"]

    violations = []
    if path[0] != grid.start:
        violations.append(
            "The path did not start at the robot's starting position "
            f"(path[0]={path[0]!r} != grid.start={grid.start!r})"
        )

    steps = len(path) - 1
    if not len(exec_result.intended_actions) == len(exec_result.slipped) == steps:
        violations.append(
            f"len(intended_actions)={len(exec_result.intended_actions)} and "
            f"len(slipped)={len(exec_result.slipped)} must both equal the number of steps ({steps})"
        )
        return violations

    total_cost = 0.0
    for i in range(steps):
        pos, reported_next = path[i], path[i + 1]
        action, did_slip = exec_result.intended_actions[i], exec_result.slipped[i]
        intended = action_target(grid, pos, action)
        if intended is None:
            violations.append(f"Step {i}: {action} is not a legal action from {pos}")
            continue
        allowed = slip_targets(grid, pos, action) if did_slip else [intended]
        if reported_next not in allowed:
            violations.append(
                f"Step {i}: {reported_next} is not reachable from {pos} via {action} "
                f"({'slipped' if did_slip else 'no slip'}) - produced an impossible transition"
            )
            continue
        total_cost += grid.cost(reported_next)

    if exec_result.reached_goal and path[-1] != grid.goal:
        violations.append(f"reached_goal=True but the final position {path[-1]} is not the dock")

    if abs(total_cost - exec_result.total_cost) > 1e-6:
        violations.append(f"Replayed cost {total_cost} != reported total_cost {exec_result.total_cost}")

    return violations
