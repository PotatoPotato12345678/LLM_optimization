"""Pyomo abstract model for shift scheduling (MILP).

The schedule is a binary assignment problem, so it is solved exactly as a
mixed-integer linear program (CBC) rather than via a continuous relaxation. This
guarantees every constraint holds in the returned 0/1 schedule — no rounding.

Canonical contract: days are ISO date strings of the target month, shifts are
the string labels ``"morning"`` / ``"evening"``, employees are usernames.

- ``M_AVAIL[e, d, s]`` is the binary availability matrix (from each employee's
  O/X calendar), enforced as a hard constraint.
- ``M_LLM_ED[e, d, s]`` is the LLM-extracted willingness in [-1, 1]; the
  objective maximizes the total willingness of the chosen assignments, so
  employees are placed on the shifts they most want subject to the constraints.
- Per-week constraints (>=1 shift/week, <=40h/week) are expressed over ISO-week
  groupings of the month's dates.

Note: the EE (employee-employee synergy) matrix is intentionally not part of the
solve — with the previous formulation it was a decision variable decoupled from
the schedule and never influenced it. Wiring synergy into the schedule (rewarding
willing co-assignments) is future work and requires modeling pairwise
co-assignment.
"""

from pyomo.environ import (
    AbstractModel,
    Set,
    Param,
    Var,
    Binary,
    Reals,
    Constraint,
    Objective,
    minimize,
    value,
)


def build_model():
    """Return a fresh ``AbstractModel`` (new per call, no shared state)."""
    model = AbstractModel()

    # Sets (populated from instance data)
    model.E = Set()                 # Employees (usernames)
    model.D = Set()                 # Days (ISO date strings of the month)
    model.S = Set()                 # Shifts ("morning", "evening")
    model.W = Set()                 # ISO week ids spanned by the month

    # Parameters
    model.n = Param()                                   # No. of employees
    model.m = Param(initialize=2)                       # No. of shifts per day
    model.workers_per_shift = Param(initialize=2)       # required workers per shift
    model.time_open = Param()
    model.time_close = Param()
    model.week_of = Param(model.D, within=Reals)        # date -> week id

    def business_hours_rule(model):
        time_open = model.time_open.value
        time_close = model.time_close.value
        if time_close > time_open:
            return time_close - time_open
        return time_close - time_open + 24
    model.BusinessHours = Param(initialize=business_hours_rule)

    def shift_hours_rule(model):
        return int(model.BusinessHours() / model.m.value)
    model.ShiftHours = Param(initialize=shift_hours_rule)

    # LLM willingness + availability matrices
    model.M_LLM_ED = Param(model.E, model.D, model.S, domain=Reals, default=0)
    model.M_AVAIL = Param(model.E, model.D, model.S, domain=Reals, default=0)

    # Decision variable: who works each (day, shift)
    model.A = Var(model.E, model.D, model.S, domain=Binary)

    # ----------------------------- Constraints -----------------------------
    @model.Constraint(model.E, model.D, model.S)
    def availability_rule(model, e, d, s):
        # Cannot assign an employee to a slot they are not available for.
        return model.A[e, d, s] <= model.M_AVAIL[e, d, s]

    @model.Constraint(model.D, model.S)
    def workers_per_shift_rule(model, d, s):
        # Each shift must be staffed by the required number of workers.
        return sum(model.A[e, d, s] for e in model.E) == model.workers_per_shift

    @model.Constraint(model.E, model.W)
    def minimum_shift_per_week(model, e, w):
        # At least one shift per week — but only for weeks the employee is
        # actually available for (otherwise the requirement is infeasible).
        days = [d for d in model.D if value(model.week_of[d]) == w]
        available = any(
            value(model.M_AVAIL[e, d, s]) > 0 for d in days for s in model.S
        )
        if not available:
            return Constraint.Skip
        return sum(model.A[e, d, s] for d in days for s in model.S) >= 1

    @model.Constraint(model.E, model.W)
    def fourty_hours_per_week(model, e, w):
        # Each worker should work no more than 40 hours per week.
        h_shift = model.ShiftHours.value
        days = [d for d in model.D if value(model.week_of[d]) == w]
        return sum(model.A[e, d, s] * h_shift
                   for d in days for s in model.S) <= 40

    @model.Constraint(model.E, model.D)
    def eight_hours_per_day_rule(model, e, d):
        # Each worker should work no more than 8 hours per day.
        h_shift = model.ShiftHours.value
        return sum(model.A[e, d, s] for s in model.S) * h_shift <= 8

    # ----------------------------- Objective -------------------------------
    # Maximize the total willingness of the chosen assignments (minimize its
    # negative). Linear in A, so the problem is a MILP solvable exactly by CBC.
    @model.Objective(sense=minimize)
    def total_willingness(m):
        return -sum(
            m.M_LLM_ED[e, d, s] * m.A[e, d, s]
            for e in m.E for d in m.D for s in m.S
        )

    return model
