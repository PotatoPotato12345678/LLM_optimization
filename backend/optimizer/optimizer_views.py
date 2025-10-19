from django.http import JsonResponse, Http404
from django.shortcuts import get_object_or_404
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.mixins import LoginRequiredMixin

from .data_parse import extract_A, extract_EE, extract_ED, generate_data_json
import json
import os
from django.conf import settings
import logging
logger = logging.getLogger(__name__)
# Create your views here.
@method_decorator(csrf_exempt, name='dispatch')
class optimizerviews(LoginRequiredMixin,View):
    def post(self, request):
        data = json.loads(request.body)
        M_A = extract_A(data)

        M_LLM_ED = extract_ED(data)

        M_LLM_EE = extract_EE(data)
        employee_list = [k for k in data.keys()]
        num_shifts = 2
        num_days = 30
        time_open = 9
        time_close = 18
        # Prepare complete data structure
        data = {
            "E": employee_list,
            "n": len(employee_list),
            "S": num_shifts,
            "m": num_days,
            "time_open": time_open,
            "time_close": time_close,
            "M_A": M_A,
            "M_LLM_ED": M_LLM_ED,
            "M_LLM_EE": M_LLM_EE
        }

        output_path = 'data_ext.json'
        
        # Write to JSON file
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Successfully wrote data to {output_path}")
        logger.info(f"Employees: {len(employee_list)}, M_A: {len(M_A)}, "
                    f"M_LLM_ED: {len(M_LLM_ED)}, M_LLM_EE: {len(M_LLM_EE)}")


        return JsonResponse({"message": "Successfully created shift requirement"}, status=201)


