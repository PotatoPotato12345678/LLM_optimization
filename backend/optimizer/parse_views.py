from django.http import JsonResponse, Http404
from django.shortcuts import get_object_or_404
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
import json

from .data_parse import extract_A, extract_EE, extract_ED
from llmModule.ED_views import ED_generate
from llmModule.EE_views import EE_generate


# Create your views here.
@method_decorator(csrf_exempt, name='dispatch')
class parseViews(View):
    @staticmethod
    def post(request):
        data = json.loads(request.body)
        E = [k for k in data.keys()]
        M_A = extract_A(data)
        M_LLM_ED = extract_ED(ED_generate(data))
        M_LLM_EE = extract_EE(EE_generate(data))

        with open('data_test.json', 'w') as f:
            json.dump({
                "E": E,
                "n": len(E),
                "S": 2,
                "m": 2,
                "M_A": M_A,
                "M_LLM_ED": M_LLM_ED,
                "M_LLM_EE": M_LLM_EE
            }, f, indent=4)

        return JsonResponse({"message": "Successfully created shift requirement"}, status=201)


