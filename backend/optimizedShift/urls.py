from django.urls import path
from . import views

urlpatterns = [
    path('employee', views.OptimizedShiftEmployee.as_view(), name='optimized_shift_employee'),
    path('manager', views.OptimizedShiftManager.as_view(), name='optimized_shift_manager'),
]