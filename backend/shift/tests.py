import os
import calendar
import unittest

from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
import json

from .models import ShiftRequirement, ManagerRequirement
from optimizedShift.models import OptimizedShift
from llm_extractor import extract_ed, extract_ee
from shift.orchestrator import run_optimization, _build_availability, _month_dates


def _solver_available():
    """True if the configured Pyomo solver is installed (tests that actually
    solve are skipped otherwise so the suite is green without a solver)."""
    try:
        import pyomo.environ as pyo
        opt = pyo.SolverFactory(os.getenv("OPTIMIZER_SOLVER", "cbc"))
        return opt is not None and opt.available(exception_flag=False)
    except Exception:
        return False


def _full_availability(year, month, blocked=None):
    """All-O availability calendar for a month, optionally blocking some
    ``(date, shift)`` slots with "X". ``blocked`` is a set of (date, shift)."""
    blocked = blocked or set()
    _, num_days = calendar.monthrange(year, month)
    cal = {}
    for day in range(1, num_days + 1):
        d = f"{year:04d}-{month:02d}-{day:02d}"
        cal[d] = {
            "morning": "X" if (d, "morning") in blocked else "O",
            "evening": "X" if (d, "evening") in blocked else "O",
        }
    return cal


class ShiftTests(TestCase):
    def setUp(self):
        UserModel = get_user_model()
        self.employee = UserModel.objects.create_user(username='employee', password='pass', is_manager=False)
        self.manager = UserModel.objects.create_user(username='manager', password='pass', is_manager=True)

        self.client = Client()
        self.employee_url = reverse('shift_employee')
        self.manager_url = reverse('shift_manager')

    def login_as(self, user):
        self.client.force_login(user)

    # ----------------- ShiftEmployee Tests -----------------

    def test_employee_get_no_shift(self):
        self.login_as(self.employee)
        response = self.client.get(f"{self.employee_url}?year=2025&month=11")
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()['error'], "Shift requirement not found")

    def test_employee_post_create_shift(self):
        self.login_as(self.employee)
        response = self.client.post(
            f"{self.employee_url}?year=2025&month=11",
            data=json.dumps({'content': 'Mon-Fri 9-5'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()['message'], "Successfully created shift requirement")
        self.assertTrue(ShiftRequirement.objects.filter(employee=self.employee).exists())

    def test_employee_put_update_shift(self):
        self.login_as(self.employee)
        ShiftRequirement.objects.create(content='Mon-Fri 9-5', employee=self.employee, year=2025, month=11)
        response = self.client.put(
            f"{self.employee_url}?year=2025&month=11",
            data=json.dumps({'content': 'Tue-Thu 10-4'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['message'], "Shift requirement updated")
        self.assertEqual(ShiftRequirement.objects.get(employee=self.employee).content, 'Tue-Thu 10-4')

    def test_employee_delete_shift(self):
        self.login_as(self.employee)
        ShiftRequirement.objects.create(content='Mon-Fri 9-5', employee=self.employee, year=2025, month=11)
        response = self.client.delete(f"{self.employee_url}?year=2025&month=11")
        self.assertEqual(response.status_code, 204)
        self.assertFalse(ShiftRequirement.objects.filter(employee=self.employee).exists())

    # ----------------- ShiftManager Tests -----------------

    def test_manager_get_returns_requirements(self):
        """GET returns the manager's own stored hard_rule / content."""
        self.login_as(self.manager)
        ManagerRequirement.objects.create(
            manager=self.manager, year=2025, month=11,
            hard_rule={"workers_per_shift": 1}, content="notes",
        )
        response = self.client.get(f"{self.manager_url}?year=2025&month=11")
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body['hard_rule'], {"workers_per_shift": 1})
        self.assertEqual(body['content'], "notes")

    @unittest.skipUnless(_solver_available(), "no NLP solver available")
    def test_manager_post_runs_optimization(self):
        """POST triggers the pipeline, persists an OptimizedShift, returns data."""
        self.login_as(self.manager)
        UserModel = get_user_model()
        e2 = UserModel.objects.create_user(username='e2', password='pass', is_manager=False)
        e3 = UserModel.objects.create_user(username='e3', password='pass', is_manager=False)
        for emp in (self.employee, e2, e3):
            ShiftRequirement.objects.create(
                content='', employee=emp, year=2025, month=11,
                availability_calendar=_full_availability(2025, 11),
            )
        ManagerRequirement.objects.create(
            manager=self.manager, year=2025, month=11,
            hard_rule={"workers_per_shift": 1},
        )

        response = self.client.post(f"{self.manager_url}?year=2025&month=11")
        self.assertEqual(response.status_code, 200)
        result = response.json()['data']
        self.assertIn('assignments', result)
        self.assertTrue(len(result['assignments']) > 0)
        self.assertTrue(OptimizedShift.objects.filter(year=2025, month=11).exists())

    def test_manager_post_no_requirements_404(self):
        self.login_as(self.manager)
        response = self.client.post(f"{self.manager_url}?year=2025&month=11")
        self.assertEqual(response.status_code, 404)


class ExtractorTests(TestCase):
    """The extractor must degrade to neutral (empty dict) when offline."""

    def setUp(self):
        # Ensure no API key is configured for these tests.
        self._saved = os.environ.pop("OPENAI_API_KEY", None)
        from django.test import override_settings
        self._override = override_settings(OPENAI_API_KEY="")
        self._override.enable()

    def tearDown(self):
        self._override.disable()
        if self._saved is not None:
            os.environ["OPENAI_API_KEY"] = self._saved

    def test_extract_ed_offline_neutral(self):
        dates = _month_dates(2025, 11)
        result = extract_ed("月曜は無理です", 2025, 11, dates, ["morning", "evening"])
        self.assertEqual(result, {})

    def test_extract_ee_offline_neutral(self):
        result = extract_ee("e2さんと働きたい", ["a", "b", "c"], "a")
        self.assertEqual(result, {})


class OrchestratorTests(TestCase):
    def setUp(self):
        UserModel = get_user_model()
        self.emps = [
            UserModel.objects.create_user(username=f"emp{i}", password='pass', is_manager=False)
            for i in range(3)
        ]

    def test_build_availability_respects_X(self):
        dates = _month_dates(2025, 11)
        req = ShiftRequirement.objects.create(
            content='', employee=self.emps[0], year=2025, month=11,
            availability_calendar=_full_availability(2025, 11, blocked={("2025-11-10", "morning")}),
        )
        avail = _build_availability([req], dates)
        self.assertEqual(avail[("emp0", "2025-11-10", "morning")], 0)
        self.assertEqual(avail[("emp0", "2025-11-10", "evening")], 1)
        self.assertEqual(avail[("emp0", "2025-11-01", "morning")], 1)

    @unittest.skipUnless(_solver_available(), "no NLP solver available")
    def test_run_optimization_respects_availability(self):
        blocked = {("2025-11-10", "morning")}
        for emp in self.emps:
            ShiftRequirement.objects.create(
                content='', employee=emp, year=2025, month=11,
                availability_calendar=_full_availability(2025, 11, blocked=blocked if emp is self.emps[0] else None),
            )
        ManagerRequirement.objects.create(
            manager=self.emps[0], year=2025, month=11, hard_rule={"workers_per_shift": 1},
        )
        result = run_optimization(2025, 11)
        # No assignment should violate the blocked availability slot.
        self.assertNotIn(
            {"employee": "emp0", "date": "2025-11-10", "shift": "morning"},
            result["assignments"],
        )
        self.assertTrue(len(result["assignments"]) > 0)
