#!/usr/bin/env python3
"""Single entry point for both tasks. The first argument picks the task,
and with it the agent from solution.py that gets run:

  docking -- solution.DockingAgent (reach the dock despite wheel slips)
  vacuum -- solution.VacuumAgent (find and clean hidden dirt)

Examples of usage:
    python run.py docking --map maps/docking_example.map --visualize

    python run.py docking --map maps/docking_example.map \\
        --slip-prob 0.2 --seed 1 --record trace.txt

    python run.py vacuum --map maps/vacuum_example.map \\
        --clean-success-prob 0.7 --seed 1 --visualize

Run `python run.py <task> --help` for the options of one task.
"""
from __future__ import annotations

import argparse
import os

from roomba_search.grid import Grid
from roomba_search.docking import docking_environment
from roomba_search.docking.docking_environment import DockingEnvironment
from roomba_search.docking.validate_docking import validate_docking_result
from roomba_search.vacuum import vacuum_environment
from roomba_search.vacuum.vacuum_environment import VacuumEnvironment
from roomba_search import viz
from solution import DockingAgent, VacuumAgent


def build_environment(args: argparse.Namespace) -> DockingEnvironment | VacuumEnvironment:
    """Loads the map and creates the environment of the chosen task.
    Raises ValueError if the map or a setting is not valid: the checks live
    in Grid and in the environments, not here."""
    grid = Grid.from_file(args.map)
    if args.task == "docking":
        return DockingEnvironment(
            grid,
            slip_prob=args.slip_prob,
            seed=args.seed,
            max_steps=args.max_steps
        )
    return VacuumEnvironment(
        grid,
        clean_success_prob=args.clean_success_prob,
        seed=args.seed,
        max_steps=args.max_steps
    )


def report(summary: str, violations: list | None = None) -> None:
    """Prints the result to the console. violations=None means the task
    has no validation step."""
    print(summary)
    if violations is None:
        return
    if violations:
        print(f"valid=False ({len(violations)} violation(s)):")
        for v in violations:
            print(f"  - {v}")
    else:
        print("valid=True")


def show(
    args: argparse.Namespace,
    grid: Grid,
    path: list,
    dirt: list | None = None,
    intended_actions: list | None = None,
    slipped: list | None = None
) -> bool:
    """Hands the path the robot took to whichever viewer was requested.
    Returns False if the --record file could not be written."""
    if args.visualize:
        viz.view_interactive(
            grid,
            path,
            dirt,
            intended_actions,
            slipped
        )
    if args.record:
        try:
            viz.record_trace(
                grid,
                path,
                args.record, # path to the file
                dirt,
                intended_actions,
                slipped
            )
        except OSError as e:
            print(f"error: could not write the --record file: {e}")
            return False
    return True


def run_docking(args: argparse.Namespace, env: DockingEnvironment) -> int:
    result = env.run(DockingAgent)
    summary = (f"reached_goal={result.reached_goal} steps_taken={result.steps_taken} "
               f"total_cost={result.total_cost} slips={result.number_of_slips}")
    violations = validate_docking_result(env.grid, result)
    shown = show(
        args,
        env.grid,
        result.path,
        intended_actions=result.intended_actions,
        slipped=result.slipped
    )
    report(summary, violations)
    return 0 if result.reached_goal and not violations and shown else 1


def run_vacuum(args: argparse.Namespace, env: VacuumEnvironment) -> int:
    result = env.run(VacuumAgent)
    summary = (f"cleaned_all={result.cleaned_all} "
               f"dirt_cleaned={result.dirt_cleaned}/{result.dirt_total} "
               f"steps_taken={result.steps_taken} total_cost={result.total_cost}")
    shown = show(args, env.grid, result.path, dirt=result.remaining_dirt_progress)
    report(summary)
    return 0 if result.cleaned_all and shown else 1


def build_parser() -> argparse.ArgumentParser:
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--map", required=True, help="path to a .map file")
    common.add_argument("--seed", type=int, default=None, help="environment random seed")
    common.add_argument(
        "--visualize",
        action="store_true",
        help="view step by step in the terminal (Enter for next step, Ctrl+C to quit) "
             "-- for looking at a solution only, can't be combined with --record"
    )
    common.add_argument(
        "--record",
        metavar="PATH",
        help="write every step (the same frames --visualize shows) "
             "to this plain-text file"
    )

    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    tasks = parser.add_subparsers(dest="task", required=True, metavar="{docking,vacuum}")

    docking = tasks.add_parser("docking", parents=[common], help="solution.DockingAgent")
    docking.add_argument(
        "--slip-prob",
        type=float,
        default=docking_environment.DEFAULT_SLIP_PROB,
        help="probability that a move slips: the robot drifts sideways and ends "
             "diagonally ahead of where it started (default %(default)s)"
    )
    docking.add_argument(
        "--max-steps",
        type=int,
        default=docking_environment.DEFAULT_MAX_STEPS,
        help="maximum number of steps of the run (default %(default)s)"
    )

    vacuum = tasks.add_parser("vacuum", parents=[common], help="solution.VacuumAgent")
    vacuum.add_argument(
        "--clean-success-prob",
        type=float,
        default=vacuum_environment.DEFAULT_CLEAN_SUCCESS_PROB,
        help="probability that arriving on a dirty cell actually cleans it "
             "(default %(default)s; below 1.0 a cell can need more than one visit)"
    )
    vacuum.add_argument(
        "--max-steps",
        type=int,
        default=vacuum_environment.DEFAULT_MAX_STEPS,
        help="maximum number of steps of the run (default %(default)s)"
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if args.visualize and args.record:
        parser.error("--visualize is for interactive viewing only; it can't be combined with --record")
    if not os.path.isfile(args.map):
        parser.error(f"--map: no such file: {args.map}")
    if args.record is not None:
        # checked before the run, so a long run is not lost on a bad path
        if not args.record:
            parser.error("--record: the file name is empty")
        if os.path.isdir(args.record):
            parser.error(f"--record: {args.record} is a directory, not a file")
        if not os.path.isdir(os.path.dirname(args.record) or "."):
            parser.error(f"--record: directory does not exist: {os.path.dirname(args.record)}")

    try:
        env = build_environment(args)
    except ValueError as e:     # a malformed map, a map for the other task, a setting out of range
        parser.error(str(e))

    runner = run_docking if args.task == "docking" else run_vacuum
    try:
        return runner(args, env)
    except NotImplementedError as e:
        print(f"error: {e}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
