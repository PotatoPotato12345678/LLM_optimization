"""Schedule evaluator.

The MILP is solved to exact optimality, so there is a single best schedule for a
given set of inputs — this stage is a thin wrapper around that solve. (The
README's "generate multiple candidates and choose the best" idea would apply if
we introduced tunable trade-offs, e.g. willingness vs. fairness weights; that is
future work.)
"""

from optimizer_engine import solve


def evaluate(employees, dates, shifts, availability, ed, **solve_kwargs):
    """Produce the best schedule for the given inputs."""
    return solve(employees, dates, shifts, availability, ed, **solve_kwargs)
