from django.http import JsonResponse, Http404
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

import json

from .ED_generate import ED_generate

# Create your views here.
@method_decorator(csrf_exempt, name='dispatch')
class ED(View):
    @staticmethod
    def post(request):
        data = json.loads(request.body)
        ED_matrix = {}
        for k in data: # iterate through each employee
            text_input = data[k]["content"]
            ED_matrix[k] = ED_generate(text_input)

        return JsonResponse(ED_matrix)