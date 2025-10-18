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
        try:
            data = json.loads(request.body)
        except Exception:
            return JsonResponse({"error": "Invalid JSON body"}, status=400)

        try:
            # E: list of employees (keys at top-level)
            E = [k for k in data.keys()]

            # The extract_* helpers accept either a dict or JSON string. Try to be permissive.
            M_A = extract_A(data)

            # ED/EE generation may call external services. Guard against errors.
            try:
                ed_source = ED_generate(data)
            except Exception:
                ed_source = None
            try:
                ee_source = EE_generate(data)
            except Exception:
                ee_source = None

            M_LLM_ED = extract_ED(ed_source if ed_source is not None else data)
            M_LLM_EE = extract_EE(ee_source if ee_source is not None else data)

            out = {
                "E": E,
                "n": len(E),
                "S": 2,
                "m": 2,
                "M_A": M_A,
                "M_LLM_ED": M_LLM_ED,
                "M_LLM_EE": M_LLM_EE,
            }

            with open('data_test.json', 'w') as f:
                json.dump(out, f, indent=4)

            return JsonResponse({"message": "Successfully created shift requirement", "result": out}, status=201)
        except Exception as exc:
            # Log and return the error without exposing internal traceback
            print("parseViews error:", exc)
            return JsonResponse({"error": str(exc)}, status=500)


