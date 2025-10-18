from django.http import JsonResponse, Http404
from django.shortcuts import get_object_or_404
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.mixins import LoginRequiredMixin

from .data_parse import extract_A, extract_EE, extract_ED
import json

# Create your views here.
@method_decorator(csrf_exempt, name='dispatch')
class optimizerviews(LoginRequiredMixin,View):
    def post(self, request):
        try:
            data = json.loads(request.body)
        except Exception:
            return JsonResponse({"error": "Invalid JSON body"}, status=400)

        try:
            M_A = extract_A(data)
            M_LLM_ED = extract_ED(data)
            M_LLM_EE = extract_EE(data)

            result = {"M_A": M_A, "M_LLM_ED": M_LLM_ED, "M_LLM_EE": M_LLM_EE}
            return JsonResponse({"message": "Successfully created shift requirement", "result": result}, status=201)
        except Exception as exc:
            print("optimizeViews error:", exc)
            return JsonResponse({"error": str(exc)}, status=500)
[new_code]
from django.http import JsonResponse, Http404
from django.shortcuts import get_object_or_404
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.mixins import LoginRequiredMixin

from .data_parse import extract_A, extract_EE, extract_ED
import json

# Create your views here.
@method_decorator(csrf_exempt, name='dispatch')
class optimizerviews(LoginRequiredMixin,View):
    def post(self, request):
        try:
            data = json.loads(request.body)
        except Exception:
            return JsonResponse({"error": "Invalid JSON body"}, status=400)

        try:
            M_A = extract_A(data)
            M_LLM_ED = extract_ED(data)
            M_LLM_EE = extract_EE(data)

            result = {"M_A": M_A, "M_LLM_ED": M_LLM_ED, "M_LLM_EE": M_LLM_EE}
            return JsonResponse({"message": "Successfully created shift requirement", "result": result}, status=201)
        except Exception as exc:
            print("optimizeViews error:", exc)
            return JsonResponse({"error": str(exc)}, status=500)


