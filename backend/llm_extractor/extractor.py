"""Callable LLM extractor (ported from the llm_stuff notebooks).

Two public functions:

- :func:`extract_ed` — turn one employee's free-text preferences into a
  willingness score per ``(date, shift)`` (the ED matrix, one employee's slice).
- :func:`extract_ee` — turn one employee's free-text notes into a synergy score
  toward every other employee (the EE matrix, one employee's row).

Both are *offline-safe*: if no ``OPENAI_API_KEY`` is configured, the ``openai``
package is missing, the text is empty, or the API call fails, they return an
empty dict — i.e. neutral (0) willingness everywhere. This lets the optimization
pipeline run end-to-end (driven by the hard availability calendar) without a live
OpenAI key, which is also what the test suite relies on.

The notebooks' coordinate system (``d1..dN`` and shift ``0``/``1``) is mapped to
the canonical contract at this boundary: ``dN`` -> the Nth ISO date of the month,
shift ``0`` -> ``shifts[0]`` ("morning"), shift ``1`` -> ``shifts[1]`` ("evening").
"""

import calendar
import logging
import os
from typing import List

logger = logging.getLogger(__name__)

# Default model id, carried over from the notebooks. Override with OPENAI_MODEL.
DEFAULT_MODEL = os.getenv("OPENAI_MODEL", "gpt-5-mini-2025-08-07")


def _api_key():
    """Read the OpenAI API key from Django settings or the environment."""
    try:
        from django.conf import settings
        key = getattr(settings, "OPENAI_API_KEY", None)
        if key:
            return key
    except Exception:
        pass
    return os.getenv("OPENAI_API_KEY")


def _client():
    """Return an OpenAI client, or ``None`` if unavailable/unconfigured."""
    key = _api_key()
    if not key:
        return None
    try:
        from openai import OpenAI
    except Exception:
        logger.warning("openai package not installed; extractor returns neutral.")
        return None
    return OpenAI(api_key=key)


def month_days_with_weekdays(year: int, month: int):
    """Return ``("1Mon 2Tue ...", num_days)`` for the given month (from notebook)."""
    _, num_days = calendar.monthrange(year, month)
    days_weekdays = "".join(
        f"{day}{calendar.day_abbr[calendar.weekday(year, month, day)]} "
        for day in range(1, num_days + 1)
    ).strip()
    return days_weekdays, num_days


def _ed_system_prompt(year: int, month: int) -> str:
    return f"""
This month has the following weekdays: {month_days_with_weekdays(year, month)[0]}

Task:
- Comprehend the given text input in Japanese and classify willingness to work each shift for every day of the month.

Output Format:
- JSON object with keys "d1" to "dN" (N = number of days in the month).
- Each value is a list of [SHIFT, WILLINGNESS] pairs:
  - SHIFT 0 = Early shift
  - SHIFT 1 = Late shift

Willingness Scale:
- Very unwilling: -1.0 to -0.6 (exclusive)
- Slightly unwilling: -0.6 to -0.2 (exclusive)
- Neutral: -0.2 to 0.2 (exclusive)
- Slightly willing: 0.2 to 0.6 (exclusive)
- Very willing: 0.6 to 1.0 (inclusive)

Japanese Phrase Mapping (with precedence rules):
- If a phrase contains both positive and negative, the negative overrides the positive.
- "入れる" or "働ける" -> slightly willing (0.2-0.6)
- "できれば入りたくない" -> slightly unwilling (-0.6 to -0.2)
- "無理" or "絶対無理" -> very unwilling (-1.0 to -0.6)
- "一番嬉しい" or "大好き" -> very willing (0.6-1.0)

Shift Mapping:
- "早め" -> assign the willingness only to Early shift (shift 0)
- "遅め" -> assign the willingness only to Late shift (shift 1)
- If no time is mentioned, assign the same value to both shifts

Instructions:
1. Never hallucinate information; only use what is explicitly stated.
2. Days not mentioned in the text should default to neutral (0) for both shifts.
3. Every day in the month must have a value for both shifts.
4. Only return the JSON object; do not include any explanations or extra text.
"""


def _build_ed_schema(num_days: int):
    """Dynamically build the per-month Pydantic response schema (d1..dN)."""
    from pydantic import BaseModel, create_model

    class ShiftItem(BaseModel):
        shift: int
        willingness: float

    fields = {f"d{i}": (List[ShiftItem], ...) for i in range(1, num_days + 1)}
    return create_model("ShiftWillingness", **fields)


def extract_ed(content_text, year, month, dates, shifts, model=None):
    """Extract a willingness score per ``(date, shift)`` for one employee.

    Returns ``{(date, shift): willingness}`` (sparse; missing entries are 0).
    """
    if not content_text or not content_text.strip():
        return {}
    client = _client()
    if client is None:
        return {}

    num_days = len(dates)
    schema = _build_ed_schema(num_days)
    try:
        response = client.responses.parse(
            model=model or DEFAULT_MODEL,
            input=[
                {"role": "system", "content": _ed_system_prompt(year, month)},
                {"role": "user", "content": content_text},
            ],
            text_format=schema,
        )
        parsed = response.output_parsed.model_dump()
    except Exception as exc:  # network/key/parse errors -> neutral
        logger.warning("extract_ed failed, returning neutral: %s", exc)
        return {}

    result = {}
    for day_idx in range(1, num_days + 1):
        items = parsed.get(f"d{day_idx}") or []
        iso_date = dates[day_idx - 1]
        for item in items:
            shift_id = item.get("shift")
            if shift_id is None or shift_id >= len(shifts):
                continue
            shift_label = shifts[shift_id]
            result[(iso_date, shift_label)] = float(item.get("willingness", 0.0))
    return result


def _ee_system_prompt(employees: List[str]) -> str:
    employee_flat = ", ".join(f"e{i + 1}:{name}" for i, name in enumerate(employees))
    return f"""
The available employees are: {employee_flat}. Total employees are {len(employees)}.
Task:
- Comprehend the given text input in Japanese and classify willingness to work with a given employee.

Output Format:
- JSON object with keys "e1" to "eN" (N = {len(employees)}).
- The value indicates willingness to work with that employee.
- Employees not mentioned in the text MUST default to neutral (0).

Willingness Scale:
- Very unwilling: -1.0 to -0.6 (exclusive)
- Slightly unwilling: -0.6 to -0.2 (exclusive)
- Neutral: -0.2 to 0.2 (exclusive)
- Slightly willing: 0.2 to 0.6 (exclusive)
- Very willing: 0.6 to 1.0 (inclusive)

Instructions:
1. Never hallucinate information; only use what is explicitly stated.
2. Only return the JSON object; do not include any explanations or extra text.
"""


def extract_ee(content_text, employees, target_username, model=None):
    """Extract synergy scores from ``target_username`` toward every other employee.

    Returns ``{other_username: synergy}`` (sparse; missing entries are 0). The
    target's own entry and unmentioned employees are omitted (treated as 0).
    """
    if not content_text or not content_text.strip():
        return {}
    client = _client()
    if client is None:
        return {}

    from pydantic import BaseModel

    class Employee(BaseModel):
        id: str
        willingness: float

    class EmployeeWillingness(BaseModel):
        employees: List[Employee]

    try:
        response = client.beta.chat.completions.parse(
            model=model or DEFAULT_MODEL,
            messages=[
                {"role": "system", "content": _ee_system_prompt(employees)},
                {"role": "user", "content": content_text},
            ],
            response_format=EmployeeWillingness,
        )
        parsed = response.choices[0].message.parsed
    except Exception as exc:
        logger.warning("extract_ee failed, returning neutral: %s", exc)
        return {}

    # Map "e1".."eN" ids back to usernames by position.
    result = {}
    for emp in parsed.employees:
        eid = emp.id.lstrip("e")
        if not eid.isdigit():
            continue
        pos = int(eid) - 1
        if pos < 0 or pos >= len(employees):
            continue
        other = employees[pos]
        if other == target_username:
            continue
        if emp.willingness:
            result[other] = float(emp.willingness)
    return result
