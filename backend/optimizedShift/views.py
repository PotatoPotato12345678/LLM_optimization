from django.http import JsonResponse, Http404
from django.shortcuts import get_object_or_404
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import OptimizedShift
import json

class Utils:
    @staticmethod
    def util_get_optimized_shift(year, month):
        # Return the OptimizedShift instance or raise Http404 so callers can handle it
        return get_object_or_404(OptimizedShift, year=year, month=month)
    
    @staticmethod
    def employee_only(request):
        if request.user.is_manager:
            return JsonResponse({'error': 'Only employees can access this endpoint'}, status=403)
        return None
    
    @staticmethod
    def manager_only(request):
        if not request.user.is_manager:
            return JsonResponse({'error': 'Only managers can access this endpoint'}, status=403)
        return None

@method_decorator(csrf_exempt, name='dispatch')
class OptimizedShiftEmployee(LoginRequiredMixin,View):
    """
    Employee
    - GET: Retrieve the employee's assigned optimized shifts.
    """ 

    def handle_no_permission(self):
        return JsonResponse({'error': 'Authentication required'}, status=401)

    def get(self, request):
        invalid_role = Utils.employee_only(request)
        if invalid_role:
            return invalid_role
        year = request.GET.get('year')
        month = request.GET.get('month')
        if not (year and month):    
            return JsonResponse({"error": "year and month are required"}, status=400)
        if request.user.is_manager:
            return JsonResponse({'error': 'Only employees can access this endpoint'}, status=403)
        else:
            optimized_shift = Utils.util_get_optimized_shift(
                year=request.GET.get('year'),
                month=request.GET.get('month')
            )

            optimized_shift.shift = [s for s in optimized_shift.shift if s['employee'] == request.user.username]
            return JsonResponse({"data": optimized_shift.shift}, status=200)


@method_decorator(csrf_exempt, name='dispatch')
class OptimizedShiftManager(LoginRequiredMixin,View):
    """
    Manager
    - GET: get the optimized shift schedule.
    - POST: publish the optimized shift schedule to employee by changing the publish_status field after running the optimizer.
    """
    def handle_no_permission(self):
        return JsonResponse({'error': 'Authentication required'}, status=401)

    def get(self, request):
        invalid_role = Utils.manager_only(request)
        if invalid_role:
            return invalid_role
        
        year = request.GET.get('year')
        month = request.GET.get('month')
        if not (year and month):
            return JsonResponse({"error": "year and month are required"}, status=400)
        
        if request.user.is_manager:
            optimized_shift = Utils.util_get_optimized_shift(
                year=year,
                month=month
            )
            return JsonResponse({"data": optimized_shift.shift}, status=200)
        else:
            return JsonResponse({'error': 'Only managers can access this endpoint'}, status=403)

    def post(self, request):
        invalid_role = Utils.manager_only(request)
        if invalid_role:
            return invalid_role
        
        year = request.GET.get('year')
        month = request.GET.get('month')
        if not (year and month):
            return JsonResponse({"error": "year and month are required"}, status=400)
        
        if not request.user.is_manager:
            return JsonResponse({'error': 'Only managers can access this endpoint'}, status=403)
        optimized_shift = Utils.util_get_optimized_shift(
            year=year,
            month=month
        )
        optimized_shift.publish_status = True
        optimized_shift.save()
        return JsonResponse({"message": f"Optimized shift in {year}-{month} is published successfully"}, status=200)