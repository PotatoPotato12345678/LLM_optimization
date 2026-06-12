"""Callable solver entry point for the shift-scheduling model.

Refactored from the former standalone ``optimizer/solver.py``: instead of reading
``data.json`` from disk and printing to stdout, :func:`solve` takes the problem
data as arguments and returns a structured result dict that the Django
orchestrator can persist on an ``OptimizedShift`` row.
"""

import os
from datetime import date

import pyomo.environ as pyo

from .model import build_model

# Default solver. ``ipopt`` solves the (continuous relaxation of the) nonlinear
# objective; the binary assignment variables are rounded afterwards. Override
# with the OPTIMIZER_SOLVER env var (e.g. "bonmin" for a true MINLP solve).
DEFAULT_SOLVER = os.getenv("OPTIMIZER_SOLVER", "ipopt")


def _week_index(dates):
    """Map each ISO date string to a small integer week id (grouping for the
    per-week constraints). Weeks are identified by their (iso-year, iso-week)
    pair so a month spanning a year boundary still groups correctly."""
    seen = {}
    week_of = {}
    for d in dates:
        iso = date.fromisoformat(d).isocalendar()
        key = (iso[0], iso[1])
        if key not in seen:
            seen[key] = len(seen)
        week_of[d] = seen[key]
    return week_of, sorted(set(week_of.values()))


def solve(
    employees,
    dates,
    shifts,
    availability,
    ed,
    ee,
    *,
    workers_per_shift=2,
    time_open=9,
    time_close=17,
    z1=1.0,
    z2=1.0,
    solver=None,
    tee=False,
):
    """Solve one shift-scheduling instance.

    Args:
        employees: list of employee usernames (the ``E`` set).
        dates: list of ISO date strings for the month (the ``D`` set).
        shifts: list of shift labels, e.g. ``["morning", "evening"]`` (``S``).
        availability: dict ``{(emp, date, shift): 0|1}`` — hard availability.
        ed: dict ``{(emp, date, shift): willingness}`` — sparse, default 0.
        ee: dict ``{(emp, other_emp): synergy}`` — sparse, default 0.
        workers_per_shift: required number of workers per shift.
        time_open/time_close: business hours (drive per-shift hour length).
        z1/z2: objective weights on the ED / EE loss terms.
        solver: solver name; falls back to ``OPTIMIZER_SOLVER`` / ipopt.
        tee: stream solver logs to stdout when True.

    Returns:
        dict with keys ``assignments`` (list of {employee, date, shift}),
        ``objective`` (float), ``status`` (solver termination), ``solver``.

    Raises:
        RuntimeError: if the configured solver is not available.
    """
    solver_name = solver or DEFAULT_SOLVER
    opt = pyo.SolverFactory(solver_name)
    if opt is None or not opt.available(exception_flag=False):
        raise RuntimeError(
            f"Optimization solver '{solver_name}' is not available. Install it "
            f"or set the OPTIMIZER_SOLVER environment variable to an installed "
            f"solver."
        )

    week_of, weeks = _week_index(dates)

    pyomo_data = {None: {
        "E": {None: list(employees)},
        "D": {None: list(dates)},
        "S": {None: list(shifts)},
        "W": {None: list(weeks)},
        "n": {None: len(employees)},
        "m": {None: len(shifts)},
        "workers_per_shift": {None: workers_per_shift},
        "time_open": {None: time_open},
        "time_close": {None: time_close},
        "week_of": dict(week_of),
        "Z1": {None: z1},
        "Z2": {None: z2},
        "M_AVAIL": {k: v for k, v in availability.items() if v},
        "M_LLM_ED": {k: v for k, v in ed.items() if v},
        "M_LLM_EE": {k: v for k, v in ee.items() if v},
    }}

    model = build_model()
    instance = model.create_instance(pyomo_data)
    results = opt.solve(instance, tee=tee)

    status = str(results.solver.termination_condition)

    # Round the (possibly relaxed) binary assignment variables.
    assignments = []
    for (e, d, s), var in instance.A.items():
        if pyo.value(var) > 0.5:
            assignments.append({"employee": e, "date": d, "shift": s})
    assignments.sort(key=lambda a: (a["date"], a["shift"], a["employee"]))

    try:
        objective = float(pyo.value(instance.minimize_oss))
    except Exception:
        objective = None

    return {
        "assignments": assignments,
        "objective": objective,
        "status": status,
        "solver": solver_name,
    }
