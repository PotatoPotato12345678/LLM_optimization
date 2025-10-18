from django.http import JsonResponse, Http404
from django.shortcuts import get_object_or_404
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import ShiftRequirement, ManagerRequirement
from optimizedShift.models import OptimizedShift
from backend.LLM_optimizer import shiftOptimizer
import json

# Create your views here.
@method_decorator(csrf_exempt, name='dispatch')
class ShiftEmployee(LoginRequiredMixin,View):
    """
    Employee manages their shift requirements:
    - GET: gets their shift requirements
    - POST: post their shift requirements to their manager
    - PUT: updates their shift requirements
    - DELETE: deletes their shift requirements

    Note:
        doesn't keep any history of shift requirements
        Only one shift requirement is stored per employee
        handle_no_permission is overridden to return 401 when not logged in
    """

    def handle_no_permission(self):
        return JsonResponse({'error': 'Authentication required'}, status=401)
    
    def employee_only(self, request):
        """Return a JsonResponse if the user is not an employee, otherwise None."""
        if request.user.is_manager:
            return JsonResponse({'error': 'Only employees can access this endpoint'}, status=403)
        return None
    
    def get(self, request):
        """
        Returns shift requirements differently depending on the requester:
        - Employee: returns only their own shift requirement for the given month/year.
        - Manager: returns all employees' shift requirements for the given month/year.
        """
        year = request.GET.get('year')
        month = request.GET.get('month')
        if not (year and month):
            return JsonResponse({"error": "year and month are required"}, status=400)

        if request.user.is_manager:  # Assuming your User model has is_manager field
            # Manager view: return all employees
            shift_reqs = ShiftRequirement.objects.filter(year=year, month=month)
            if not shift_reqs.exists():
                return JsonResponse({"error": "No shift requirements found"}, status=404)

            result = {}
            for req in shift_reqs:
                result[req.employee.username] = {
                    "content": req.content,
                    "availability_calendar": req.availability_calendar,
                }
            return JsonResponse(result, status=200, safe=False)
        else:
            # Employee view: return only their own
            try:
                shift_req = ShiftRequirement.objects.get(
                    employee=request.user, year=year, month=month
                )
                return JsonResponse({
                    "content": shift_req.content,
                    "availability_calendar": shift_req.availability_calendar
                }, status=200)
            except ShiftRequirement.DoesNotExist:
                return JsonResponse({"error": "Shift requirement not found"}, status=404)



    def post(self, request):
        invalid_role = self.employee_only(request)
        if invalid_role:
            return invalid_role

        year = request.GET.get('year')
        month = request.GET.get('month')
        if not (year and month):
            return JsonResponse({"error": "year and month are required"}, status=400)

        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)

        content = data.get("content")
        availability = data.get("availability_calendar", {})

        if content is None:
            return JsonResponse({'error': 'Content is required'}, status=400)

        ShiftRequirement.objects.create(
            content=content,
            availability_calendar=availability,
            employee=request.user,
            year=year,
            month=month
        )

        return JsonResponse({"message": "Successfully created shift requirement"}, status=201)


    def put(self, request):
        invalid_role = self.employee_only(request)
        if invalid_role:
            return invalid_role

        year = request.GET.get('year')
        month = request.GET.get('month')
        if not (year and month):
            return JsonResponse({"error": "year and month are required"}, status=400)

        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)

        content = data.get("content")
        availability = data.get("availability_calendar")

        shift_req, created = ShiftRequirement.objects.get_or_create(
            employee=request.user,
            year=year,
            month=month,
            defaults={
                "content": content or "",
                "availability_calendar": availability or {},
            }
        )

        if not created:
            updated = False
            if content is not None:
                shift_req.content = content
                updated = True
            if availability is not None:
                shift_req.availability_calendar = availability
                updated = True

            if updated:
                shift_req.save()
                return JsonResponse({"message": "Shift requirement updated"}, status=200)
            else:
                return JsonResponse({"message": "No changes provided"}, status=400)

        return JsonResponse({"message": "Shift requirement created"}, status=201)

        
    def delete(self, request):
        invalid_role = self.employee_only(request)
        if invalid_role:
            return invalid_role
        # Accept year/month only from query params
        year = request.GET.get('year')
        month = request.GET.get('month')
        if not (year and month):
            return JsonResponse({"error": "year and month are required"}, status=400)
        try:
            shift_req = get_object_or_404(ShiftRequirement, employee=request.user, year=year, month=month)
        except Http404:
            return JsonResponse({"error": "Shift requirement not found"}, status=404)

        shift_req.delete()
        return JsonResponse({"message": "Shift requirement deleted"}, status=204)

@method_decorator(csrf_exempt, name='dispatch')
class ShiftManager(LoginRequiredMixin,View):
    """
    Manager manages their employees' shift requirements:
    - GET: gets their employees' shift requirements
    - POST: perform shift scheduling optimization and return the optimized shift schedule
    Note:
        minimum functionality only
        handle_no_permission is overridden to return 401 when not logged in
    """

    def handle_no_permission(self):
        return JsonResponse({'error': 'Authentication required'}, status=401)
    
    def manager_only(self, request):
        """Return a JsonResponse if the user is not a manager, otherwise None."""
        if not request.user.is_manager:
            return JsonResponse({'error': 'Only managers can access this endpoint'}, status=403)
        return None
    
    def util_get_shift_reqs(self, year, month):
        shift_reqs = ShiftRequirement.objects.filter(year=year, month=month)

        if not shift_reqs.exists():
            raise Http404(f"No shift requirements found for year: {year}, month: {month}")

        data = [
            {"employee": s.employee.username, "content": s.content}
            for s in shift_reqs
        ]
        return data
    
    def get(self, request):
        invalid_role = self.manager_only(request)
        if invalid_role:
            return invalid_role

        year = request.GET.get('year')
        month = request.GET.get('month')
        if not (year and month):
            return JsonResponse({"error": "year and month are required"}, status=400)

        # Try to get the manager requirement for this month
        manager_req = ManagerRequirement.objects.filter(
            manager=request.user, year=year, month=month
        ).first()

        if not manager_req:
            return JsonResponse({"error": "Manager requirement not found"}, status=404)

        return JsonResponse(
            {
                "hard_rule": manager_req.hard_rule,
                "content": manager_req.content,
            },
            status=200,
        )

    def post(self, request):
        invalid_role = self.manager_only(request)
        if invalid_role:
            return invalid_role

        year = request.GET.get('year')
        month = request.GET.get('month')
        if not (year and month):
            return JsonResponse({"error": "year and month are required"}, status=400)

        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)

        content = data.get("content")
        hard_rule = data.get("hardRule")

        if content is None or hard_rule is None:
            return JsonResponse({'error': 'Both content and hardRule are required'}, status=400)

        ManagerRequirement.objects.create(
            content=content,
            hard_rule=hard_rule,
            year=year,
            month=month,
            manager=request.user
        )

        return JsonResponse({"message": "Manager shift requirement created"}, status=201)


    def put(self, request):
        invalid_role = self.manager_only(request)
        if invalid_role:
            return invalid_role

        year = request.GET.get('year')
        month = request.GET.get('month')
        if not (year and month):
            return JsonResponse({"error": "year and month are required"}, status=400)

        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)

        content = data.get("content")
        hard_rule = data.get("hardRule")

        manager_req, created = ManagerRequirement.objects.get_or_create(
            year=year,
            month=month,
            manager=request.user,
            defaults={
                "content": content or "",
                "hard_rule": hard_rule or ""
            }
        )

        if not created:
            updated = False
            if content is not None:
                manager_req.content = content
                updated = True
            if hard_rule is not None:
                manager_req.hard_rule = hard_rule
                updated = True

            if updated:
                manager_req.save()
                return JsonResponse({"message": "Manager shift requirement updated"}, status=200)
            else:
                return JsonResponse({"message": "No changes provided"}, status=400)

        return JsonResponse({"message": "Manager shift requirement created"}, status=201)
