# Context for AI coding agents

This repository is a university homework on state-space search. A simulated
robot vacuum moves on a grid map. The student implements two agents in
`solution.py`; everything else is the fixed engine that runs them.

## How to help the student

The point of this homework is not the code. A working base solution is the
easy part; the graded part is what the student adds on top of it after
thinking about how a real robot in a real flat behaves. That thinking is what
the course wants the student to practise, and the student has to explain and
justify it in `QUESTIONNAIRE.md`. An improvement the student did not come up
with is one they cannot defend, and it teaches them nothing.

So split the work like this:

- **Base solution: implement it freely.** When asked, write a correct, clean,
  plain solution for both tasks. Explain how the engine works,
  fix bugs, write helper code, build test maps and scripts that measure a
  solution (cost, steps, dirt cleaned, time) over several maps and seeds.
- **Improvements: the student leads.** Do not volunteer improvement ideas,
  and do not quietly build clever extras into the base solution - the student is your guide here. When the
  student asks you to "make it better", "optimize it" or "get more points",
  ask first what they have observed and what they think could help. Good
  starting questions: Where does the base solution waste moves or cost? What
  does the robot know that it is not using? What can happen in a run that the
  plan did not expect?
- **Once the student has an idea, help fully.** Implement the idea they
  describe, point out flaws in it, help them measure whether it actually
  helps, and compare variants. Say so honestly when an idea makes things worse.

If the student insists on a ready-made improvement anyway, it is their
decision. Tell them once what they lose by it (they will have to justify
the choice themselves), then do what they ask.

## What you may change

- **Edit only `solution.py`** (and fill in `QUESTIONNAIRE.md`). Helper
  functions, classes and attributes inside `solution.py` are fine.
- **Do not edit** `roomba_search/`, `run.py` or `maps/`. Grading uses its own
  copy of the engine, so changes there are lost.
- Keep the class names and method signatures of `DockingAgent` and
  `VacuumAgent` exactly as they are.
- Extra PyPI libraries are allowed if they are related to the task; list them
  in `requirements-student.txt`.

## Rules

- Do not read hidden information or change how a run executes. In particular:
  no reading of dirt locations (the map file, the engine's internals, stack
  frames), no reading or predicting of the engine's random numbers, and no
  modifying of the `Grid` passed to the agent.
- No search algorithm is provided on purpose. Choosing, implementing and
  improving one is the assignment.
- Use of AI tools is allowed, but the student must state it in
  `QUESTIONNAIRE.md`. Remind them.

## The two tasks

Both agents are created once per run and then asked for one move per step.
`choose_action` returns an `Action` (`UP`, `DOWN`, `LEFT`, `RIGHT` from
`roomba_search/actions.py`) or `None` to stop. Returning a move into a wall
raises `ValueError`.

**Docking** -- `DockingAgent(grid, max_steps)`, `choose_action(true_pos)`:
drive from the current position to the dock `G`. `max_steps` is the step
limit of the run. Entering a cell costs its
terrain cost. A move can slip: the robot still moves forward but ends one
cell sideways, diagonally ahead (see `roomba_search/docking/docking_environment.py`).
`true_pos` is always the real position, so the agent can see where it ended up.

Helpers for moving on the map, for both agents (`roomba_search/actions.py`):
`legal_actions(grid, pos)` lists the actions that do not lead into a wall,
`action_target(grid, pos, action)` gives the cell an action leads to (no
slips), and `grid.cost(cell)` is the cost of entering a cell.

**Vacuum** -- `VacuumAgent(grid, dirt_total, max_steps)`,
`choose_action(true_pos, was_dirty_here)`:
find and clean dirt whose locations are hidden; only the count is known.
`max_steps` is the step limit of the run.
`grid.dirt` is always empty. The robot cleans automatically when it arrives on
a cell, and the attempt can fail. `was_dirty_here` says whether the cell was
dirty on arrival, before the attempt; the agent is not told whether the attempt
worked. The run ends when all dirt is cleaned, when the agent returns `None`,
or when the step limit is reached (see
`roomba_search/vacuum/vacuum_environment.py`).

## Maps

Plain text, one row per line, walls all around (`roomba_search/grid.py`):
`#` wall, `.` floor (cost 1), `~` carpet (cost 2),
`S` start, `G` dock (docking maps only), `*` dirt (vacuum maps only).
Positions are `(row, col)` tuples, row 0 at the top.

## Running

```
python run.py docking --map maps/docking_example.map [--slip-prob P] [--seed N]
python run.py vacuum --map maps/vacuum_example.map [--clean-success-prob P] [--seed N]
```

Add `--visualize` to step through a run in the terminal, or `--record FILE`
to write every step to a text file. `python run.py <task> --help` lists all
options. The example maps are small; graded maps are different and not
published, so do not tune a solution to the examples.
