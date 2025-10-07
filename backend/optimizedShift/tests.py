from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from .models import OptimizedShift
import json


class OptimizedShiftTests(TestCase):

    def setUp(self):
        User = get_user_model()
        self.employee = User.objects.create_user(username='employee', password='pass', is_manager=False)
        self.manager = User.objects.create_user(username='manager', password='pass', is_manager=True)
        self.client = Client()
        self.employee_url = reverse('optimized_shift_employee')
        self.manager_url = reverse('optimized_shift_manager')

        self.opt = OptimizedShift.objects.create(
            shift=[
                {'employee': 'employee', 'content': 'Mon-Fri 9-5'},
                {'employee': 'other', 'content': 'Tue-Thu 10-4'}
            ],
            year=2025,
            month=11,
            publish_status=False
        )

    def login_as(self, user):
        self.client.force_login(user)

    def test_manager_get_optimized_shift(self):
        self.login_as(self.manager)
        response = self.client.get(f"{self.manager_url}?year=2025&month=11")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['data'], self.opt.shift)

    def test_manager_post_publish(self):
        self.login_as(self.manager)
        response = self.client.post(f"{self.manager_url}?year=2025&month=11")
        self.assertEqual(response.status_code, 200)
        self.opt.refresh_from_db()
        self.assertTrue(self.opt.publish_status)

    def test_employee_get_filtered_shift(self):
        self.login_as(self.employee)
        response = self.client.get(f"{self.employee_url}?year=2025&month=11")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['data'], [{'employee': 'employee', 'content': 'Mon-Fri 9-5'}])
