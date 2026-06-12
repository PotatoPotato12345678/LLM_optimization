"""Minimal schedule evaluator.

The README describes generating several candidate schedules and choosing the
best. Without an LLM-in-the-loop (future work), this evaluator runs the optimizer
across a small set of objective weightings ``(Z1, Z2)`` and returns the candidate
with the lowest objective value that actually produced assignments. This keeps the
"generate multiple, pick best" architecture honest and deterministic.
"""

import logging

from optimizer_engine import solve

logger = logging.getLogger(__name__)

# (Z1, Z2) weightings on the ED / EE loss terms to try.
DEFAULT_WEIGHTS = [(1.0, 1.0), (1.0, 0.5), (0.5, 1.0)]


def evaluate(employees, dates, shifts, availability, ed, ee, *,
             weights=None, **solve_kwargs):
    """Run the optimizer over several weightings and return the best candidate.

    Returns the best result dict (the engine's output augmented with the chosen
    ``weights``), or the last attempted result if none produced assignments.
    """
    weights = weights or DEFAULT_WEIGHTS
    best = None
    last = None
    for z1, z2 in weights:
        result = solve(employees, dates, shifts, availability, ed, ee,
                       z1=z1, z2=z2, **solve_kwargs)
        result["weights"] = {"Z1": z1, "Z2": z2}
        last = result
        if not result["assignments"]:
            continue
        if best is None or (
            result["objective"] is not None
            and best["objective"] is not None
            and result["objective"] < best["objective"]
        ):
            best = result
    return best or last
