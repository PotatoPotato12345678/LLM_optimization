from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from .models import ShiftRequirement
from django.urls import reverse
import json


class ShiftTests(TestCase):
    def setUp(self):
        # Create an employee and a manager (use create_user to set hashed password)
        UserModel = get_user_model()
        self.employee = UserModel.objects.create_user(username='employee', password='pass', is_manager=False)
        self.manager = UserModel.objects.create_user(username='manager', password='pass', is_manager=True)

        self.client = Client()
        # URLs
        self.employee_url = reverse('shift_employee')
        self.manager_url = reverse('shift_manager')

    def login_as(self, user):
        """Helper to login"""
        self.client.force_login(user)

    # ----------------- ShiftEmployee Tests -----------------

    def test_employee_get_no_shift(self):
        self.login_as(self.employee)
        response = self.client.get(f"{self.employee_url}?year=2025&month=11")
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()['error'], "Shift requirement not found")

    def test_employee_post_create_shift(self):
        self.login_as(self.employee)
        # Provide year/month in querystring; content in JSON body
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
        # First create
        ShiftRequirement.objects.create(content='Mon-Fri 9-5', employee=self.employee, year=2025, month=11)
        # Then update using PUT with JSON body and query params
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

    def test_manager_get_shifts(self):
        self.login_as(self.manager)
        # Create shifts for multiple employees
        ShiftRequirement.objects.create(content='Mon-Fri 9-5', employee=self.employee, year=2025, month=11)
        ShiftRequirement.objects.create(content='Tue-Thu 10-4', employee=self.manager, year=2025, month=11)
        response = self.client.get(f"{self.manager_url}?year=2025&month=11")
        self.assertEqual(response.status_code, 200)
        data = response.json()['data']
        self.assertEqual(len(data), 2)
        self.assertIn({'employee': self.employee.username, 'content': 'Mon-Fri 9-5'}, data)

    def test_manager_post_optimization(self):
        self.login_as(self.manager)
        ShiftRequirement.objects.create(content='Mon-Fri 9-5', employee=self.employee, year=2025, month=11)
        # Manager POST expects year/month in query params
        response = self.client.post(f"{self.manager_url}?year=2025&month=11")
        self.assertEqual(response.status_code, 200)
        # response.data is a list of dicts; compare contents
        returned = response.json()['data']
        self.assertEqual([d['content'] for d in returned], ['Mon-Fri 9-5'])