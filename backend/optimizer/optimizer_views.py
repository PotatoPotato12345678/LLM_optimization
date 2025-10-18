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
        data = json.loads(request.body)
        M_A = extract_A(data)

        M_LLM_ED = extract_ED(data)

        M_LLM_EE = extract_EE(data)


        return JsonResponse({"message": "Successfully created shift requirement"}, status=201)


