# SUI 2026/27 -- search project (robot vacuum)

The full assignment is the PDF published in the course. This file is only a
short guide to the repository.

## In one paragraph

You implement two agents in `solution.py`: `DockingAgent` drives the robot to
the dock as cheaply as possible although its wheels sometimes slip, and
`VacuumAgent` finds and cleans dirt it cannot see in advance. A plain textbook
search is only the starting point; the project is about improving it with
ideas about how a real robot in a real flat behaves, and explaining those
ideas in `QUESTIONNAIRE.md`.

## Running

Python 3.12 is recommended. The repository itself needs no extra packages.

```
python run.py docking --map maps/docking_example.map --slip-prob 0.2 --seed 1
python run.py vacuum  --map maps/vacuum_example.map  --clean-success-prob 0.7 --seed 1
```

- `--visualize` steps through the run in the terminal (Enter = next step, Ctrl+C = quit).
- `--record FILE` writes every step of the run to a text file.
- `--seed N` makes a run repeatable; `--max-steps N` sets the step limit.
- `python run.py docking --help` / `python run.py vacuum --help` list everything.

Until you implement an agent, `run.py` prints the `TODO` message of its stub.

## What is where

| path | content |
|---|---|
| `solution.py` | **your file**: the two agents |
| `QUESTIONNAIRE.md` | **your file**: methods, improvements and their justification |
| `run.py` | runs one task on one map |
| `roomba_search/grid.py` | the map: format, walls, costs, start, dock |
| `roomba_search/actions.py` | `Action`, `legal_actions`, `action_target` |
| `roomba_search/docking/` | docking run (slips) and its checker |
| `roomba_search/vacuum/` | vacuum run (hidden dirt, cleaning that can fail) |
| `roomba_search/viz.py` | the terminal viewer and the recorder |
| `maps/` | small example maps |
| `AGENTS.md` | instructions for AI coding assistants |

Map symbols: `#` wall, `.` floor (cost 1), `~` carpet (cost 2), `S` start,
`G` dock (docking maps), `*` dirt (vacuum maps). A position is `(row, col)`
with `(0, 0)` in the top-left corner. You can write your own maps in the same
format; the outer frame must be walls.

## Keep in mind

- Change only `solution.py` and `QUESTIONNAIRE.md`. Grading uses its own copy
  of everything else.
- Keep the names and signatures of `DockingAgent` and `VacuumAgent`.
- A move into a wall, or returning anything other than an `Action` or `None`,
  ends the run with an error.
- The agent must not read hidden information (dirt positions, the engine's
  random numbers) or change the map it is given.
- The example maps are only examples; graded maps are different.
- Submit `solution.py`, `QUESTIONNAIRE.md` and, if you used extra packages,
  `requirements-student.txt` listing them.
