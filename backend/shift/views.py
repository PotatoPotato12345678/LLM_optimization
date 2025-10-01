from django.http import JsonResponse, Http404
from django.shortcuts import get_object_or_404
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import ShiftRequirement
from LLMoptimizer import shiftOptimizer
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
        try:
            client_shift_req = get_object_or_404(ShiftRequirement, employee=request.user)
            return JsonResponse({
                "content": client_shift_req.content
            }, status=200)
        except Http404:
            return JsonResponse({"error": "Shift requirement not found"}, status=404)

    def post(self, request):
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)

        content = data.get("content")

        if content is None:
            return JsonResponse({'error': 'Content is required'}, status=400)
        else:
            ShiftRequirement.objects.create(content=content, employee=request.user)

        return JsonResponse({"message": "Successfully created shift requirement"}, status=201)

    def put(self, request):
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)

        content = data.get("content")

        if not content:
            return JsonResponse({"error": "Content is required"}, status=400)

        shift_req, created = ShiftRequirement.objects.get_or_create(
            employee=request.user,
            defaults={"content": content}
        )

        if not created:
            shift_req.content = content
            shift_req.save()
            return JsonResponse({"message": "Shift requirement updated"}, status=200)
        else:
            return JsonResponse({"message": "Shift requirement created"}, status=201)
        
    def delete(self, request):
        try:
            shift_req = get_object_or_404(ShiftRequirement, employee=request.user)
        except Http404:
            return JsonResponse({"error": "Shift requirement not found"}, status=404)

        shift_req.delete()
        return JsonResponse({"message": "Shift requirement deleted"}, status=204)

class ShiftManager(LoginRequiredMixin,View):
    """
    Manager manages their employees' shift requirements:
    - GET: gets their employees' shift requirements:
    - POST: start shift scheduling optimization

    Note:
        minimum functionality only
        handle_no_permission is overridden to return 401 when not logged in
    """

    def handle_no_permission(self):
        return JsonResponse({'error': 'Authentication required'}, status=401)
    
    def get(self, request):
        shift_reqs = ShiftRequirement.objects.all()
        data = [
        {
            "employee": s.employee.username,
            "content": s.content
        }
        for s in shift_reqs
        ]
        return JsonResponse({"data": data})

    def post(self, request):
        data = [s.content for s in ShiftRequirement.objects.all()]
        # call the optimization service
        response = shiftOptimizer(data)
        return JsonResponse({"data":response})
