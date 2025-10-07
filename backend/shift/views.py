from django.http import JsonResponse, Http404
from django.shortcuts import get_object_or_404
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import ShiftRequirement
from optimizedShift.models import OptimizedShift
from backend.LLMoptimizer import shiftOptimizer
import json

# Create your views here.
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
    

    def get(self, request):
        year = request.GET.get('year')
        month = request.GET.get('month')
        if not (year and month):
            return JsonResponse({"error": "year and month are required"}, status=400)
        try:
            client_shift_req = get_object_or_404(ShiftRequirement, employee=request.user, year=year, month=month)
            return JsonResponse({
                "content": client_shift_req.content
            }, status=200)
        except Http404:
            return JsonResponse({"error": "Shift requirement not found"}, status=404)

    def post(self, request):
        # Accept year/month only from query parameters
        year = request.GET.get('year')
        month = request.GET.get('month')
        if not (year and month):
            return JsonResponse({"error": "year and month are required"}, status=400)
        # Require JSON body
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)

        content = data.get("content")

        if content is None:
            return JsonResponse({'error': 'Content is required'}, status=400)
        else:
            ShiftRequirement.objects.create(content=content, employee=request.user, year=year, month=month)

        return JsonResponse({"message": "Successfully created shift requirement"}, status=201)

    def put(self, request):
        # Accept year/month only from query params
        year = request.GET.get('year')
        month = request.GET.get('month')
        if not (year and month):
            return JsonResponse({"error": "year and month are required"}, status=400)
        # Require JSON body for PUT
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)

        content = data.get("content")

        if not content:
            return JsonResponse({"error": "Content is required"}, status=400)

        shift_req, created = ShiftRequirement.objects.get_or_create(
            employee=request.user,
            year=year,
            month=month,
            defaults={"content": content}
        )

        if not created:
            shift_req.content = content
            shift_req.save()
            return JsonResponse({"message": "Shift requirement updated"}, status=200)
        else:
            return JsonResponse({"message": "Shift requirement created"}, status=201)
        
    def delete(self, request):
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
        year = request.GET.get('year')
        month = request.GET.get('month')
        if not (year and month):
            return JsonResponse({"error": "year and month are required"}, status=400)

        try:
            data = self.util_get_shift_reqs(year, month)
        except Http404:
            return JsonResponse({"error": "No shift requirements found"}, status=404)

        return JsonResponse({"data": data})

    def post(self, request):
        year = request.GET.get('year')
        month = request.GET.get('month')
        if not (year and month):
            return JsonResponse({"error": "year and month are required"}, status=400)

        try:
            data = self.util_get_shift_reqs(year, month)
        except Http404:
            return JsonResponse({"error": "No shift requirements found"}, status=404)

        response = shiftOptimizer(data)
        # save it to optimizedShift table in DB
        OptimizedShift.objects.create(shift=response, year=year, month=month)

        return JsonResponse({"data": response})
