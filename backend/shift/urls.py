from django.urls import path
from . import views

urlpatterns = [
    path('employee', views.ShiftEmployee.as_view(), name='shift_employee'),
    path('manager', views.ShiftManager.as_view(), name='shift_manager'),
]