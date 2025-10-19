from django.http import JsonResponse, Http404
from django.shortcuts import get_object_or_404
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
import json

from .data_parse import extract_A, extract_EE, extract_ED
from llmModule.ED_views import ED_generate
from llmModule.EE_views import EE_generate

import logging
logger = logging.getLogger(__name__)


# Create your views here.
@method_decorator(csrf_exempt, name='dispatch')
class parseViews(View):
    @staticmethod
    def parseView(request):
        data = json.loads(request.content)

        logger.info(data)
        logger.info(type(data))
        logger.info(data.keys())

        
        E = [k for k in data.keys()]
        M_A = extract_A(data)
        logger.info(M_A)
        M_LLM_ED = extract_ED(data)
        logger.info("cappy")
        M_LLM_EE = extract_EE(data)

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


