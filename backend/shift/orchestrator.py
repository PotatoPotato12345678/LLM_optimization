"""Orchestration glue: the missing bridge between the components.

``run_optimization`` is what ``ShiftManager.post`` calls. It:

1. Loads every employee's ``ShiftRequirement`` for the target month.
2. Builds the canonical contract (employees, ISO dates, morning/evening shifts).
3. Turns each O/X availability calendar into the hard availability matrix.
4. Calls the LLM extractor on each employee's free text for ED/EE willingness.
5. Runs the evaluator (optimizer over several weightings, best candidate).
6. Persists the result on an ``OptimizedShift`` row and returns it.
"""

import calendar
import logging

from .models import ShiftRequirement, ManagerRequirement
from .evaluator import evaluate
from llm_extractor import extract_ed
from optimizedShift.models import OptimizedShift

logger = logging.getLogger(__name__)

SHIFTS = ["morning", "evening"]


def _month_dates(year, month):
    _, num_days = calendar.monthrange(year, month)
    return [f"{year:04d}-{month:02d}-{day:02d}" for day in range(1, num_days + 1)]


def _build_availability(requirements, dates):
    """O/X calendars -> ``{(emp, date, shift): 0|1}``.

    A slot is available (1) unless the employee explicitly marked it "X". An
    employee who left a day/shift blank is treated as available so an unfilled
    calendar does not silently make the problem infeasible.
    """
    availability = {}
    for req in requirements:
        cal = req.availability_calendar or {}
        username = req.employee.username
        for d in dates:
            day_cal = cal.get(d, {}) or {}
            for s in SHIFTS:
                availability[(username, d, s)] = 0 if day_cal.get(s) == "X" else 1
    return availability


def run_optimization(year, month):
    """Run the full pipeline for ``(year, month)`` and persist the result.

    Returns the optimizer result dict (also stored on ``OptimizedShift.shift``).

    Raises:
        ValueError: if no shift requirements exist for the month.
    """
    year = int(year)
    month = int(month)

    requirements = list(
        ShiftRequirement.objects.filter(year=year, month=month).select_related("employee")
    )
    if not requirements:
        raise ValueError(f"No shift requirements found for {year}-{month}.")

    employees = sorted(req.employee.username for req in requirements)
    dates = _month_dates(year, month)

    availability = _build_availability(requirements, dates)

    # LLM extraction (offline-safe: returns neutral when no API key configured).
    ed = {}
    for req in requirements:
        username = req.employee.username
        text = req.content or ""
        for (d, s), willingness in extract_ed(text, year, month, dates, SHIFTS).items():
            ed[(username, d, s)] = willingness

    # Manager hard rules (workers per shift, business hours) for this month.
    manager_req = ManagerRequirement.objects.filter(year=year, month=month).first()
    hard_rule = (manager_req.hard_rule if manager_req else {}) or {}
    workers_per_shift = int(hard_rule.get("workers_per_shift", 2))
    time_open = int(hard_rule.get("time_open", 9))
    time_close = int(hard_rule.get("time_close", 17))

    result = evaluate(
        employees, dates, SHIFTS, availability, ed,
        workers_per_shift=workers_per_shift,
        time_open=time_open,
        time_close=time_close,
    )

    OptimizedShift.objects.update_or_create(
        year=year,
        month=month,
        defaults={"shift": result, "publish_status": False},
    )
    return result
