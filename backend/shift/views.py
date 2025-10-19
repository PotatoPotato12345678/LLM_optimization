from django.http import JsonResponse, Http404
from django.shortcuts import get_object_or_404
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import ShiftRequirement, ManagerRequirement
import json

from optimizer.parse_views import parseViews

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

    @staticmethod
    def get_for_manager(year, month):
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
    

    def get(self, request):
        year = request.GET.get('year')
        month = request.GET.get('month')
        if not (year and month):
            return JsonResponse({"error": "year and month are required"}, status=400)

        if request.user.is_manager:
            return self.get_for_manager(year, month)
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
    - GET: gets the manager's hard rules and the preference 
    - POST: perform shift scheduling optimization and return the optimized shift schedule
    - PUT: updates the working space rules
    Note:
        minimum functionality only
        handle_no_permission is overridden to return 401 when not logged in
        RESTFUL structure is broken
    """

    def handle_no_permission(self):
        return JsonResponse({'error': 'Authentication required'}, status=401)
    
    def manager_only(self, request):
        """Return a JsonResponse if the user is not a manager, otherwise None."""
        if not request.user.is_manager:
            return JsonResponse({'error': 'Only managers can access this endpoint'}, status=403)
        return None
    
    def get(self, request):
        invalid_role = self.manager_only(request)
        if invalid_role:
            return invalid_role

        year = request.GET.get("year")
        month = request.GET.get("month")
        if not (year and month):
            return JsonResponse({"error": "year and month are required"}, status=400)

        try:
            shift = ManagerRequirement.objects.get(manager=request.user, year=year, month=month)
            return JsonResponse({
                "hard_rule": shift.hard_rule,
                "content": shift.content
            }, status=200)
        except ManagerRequirement.DoesNotExist:
            return JsonResponse({"hard_rule": {}, "content": ""}, status=200)

    def post(self, request):
        invalid_role = self.manager_only(request)
        if invalid_role:
            return invalid_role

        year = request.GET.get("year")
        month = request.GET.get("month")
        if not (year and month):
            return JsonResponse({"error": "year and month are required"}, status=400)
        
        employee_data_dic = ShiftEmployee.get_for_manager(year, month)
        if employee_data_dic.status_code != 200:
            return employee_data_dic

        assignment_matrix = parseViews.parseView(employee_data_dic)
        return JsonResponse({"data": assignment_matrix}, status=200)

    def put(self, request):
        invalid_role = self.manager_only(request)
        if invalid_role:
            return invalid_role

        year = request.GET.get("year")
        month = request.GET.get("month")
        if not (year and month):
            return JsonResponse({"error": "year and month are required"}, status=400)

        year = int(year)
        month = int(month)

        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)

        hard_rule = data.get("hardRule")
        content = data.get("content")

        if hard_rule is not None and not isinstance(hard_rule, dict):
            return JsonResponse({"error": "hardRule must be a JSON object"}, status=400)

        shift, created = ManagerRequirement.objects.get_or_create(
            manager=request.user,
            year=year,
            month=month,
            defaults={"hard_rule": hard_rule or {}, "content": content or ""}
        )

        if not created:
            updated = False
            if hard_rule is not None:
                shift.hard_rule = hard_rule
                updated = True
            if content is not None:
                shift.content = content
                updated = True

            if updated:
                shift.save()
                return JsonResponse({"message": "Manager shift requirement updated"}, status=200)
            else:
                return JsonResponse({"message": "No changes provided"}, status=400)

        return JsonResponse({"message": "Manager shift requirement created"}, status=201)
