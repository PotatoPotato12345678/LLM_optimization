from django.http import JsonResponse, Http404
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.mixins import LoginRequiredMixin

import json

from .EE_generate import EE_generate
import logging
logger = logging.getLogger(__name__)

@method_decorator(csrf_exempt, name='dispatch')
class EE(View):
    @staticmethod
    def post(request):
        data = json.loads(request.body)
        EE_matrix = {}

        employee_list = [k for k in data.keys()]
        employee_flat = ", ".join([f"e{i+1}:{name}" for i, name in enumerate(employee_list)])
        
        for k in data: # iterate through each employee
            text_input = data[k]["content"]
            logger.info(f"--------------------------------------------------------------------")
            logger.info(f"-----------------{text_input}-----------------")
            logger.info(f"--------------------------------------------------------------------")
            EE_matrix[k] = EE_generate(text_input, employee_list, employee_flat)
        
        return JsonResponse(EE_matrix)
