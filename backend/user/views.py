from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import View
from django.contrib.auth import authenticate, login, logout
import json


@method_decorator(csrf_exempt, name='dispatch')
class User(View):
    """
    Employee and Manager manages their own authentication:
    - GET: gets their own information
    - POST: login
    - DELETE: logout

    Note:
        minimum functionality only
        Registration and deletion are done by the system admin
    """
    @method_decorator(login_required(login_url=None))
    def get(self, request):
        return JsonResponse({
            "username": request.user.username,
            "is_manager": request.user.is_manager
        }, status=200)
    
    def post(self, request):
        try:
            data = json.loads(request.body)
            username = data['username']
            password = data['password']
        except (KeyError, json.JSONDecodeError):
            return JsonResponse({'error': 'Invalid data'}, status=400)
        
        user = authenticate(request, username=username, password=password)
        if user is None:
            return JsonResponse({'error': 'Not Found'}, status=404)
        else:
            try:
                login(request, user)
                return JsonResponse({'message': 'Login successful'}, status=200)
            except Exception as e:
                return JsonResponse({'error': str(e)}, status=500)

    @method_decorator(login_required(login_url=None))
    def delete(self, request):
        try:
            logout(request)
            return JsonResponse({'message': 'Logout successful'}, status=200)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
        

@login_required
@csrf_exempt  # or use proper CSRF token handling
def updateProfile(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            user = request.user

            # Update fields (only if present)
            if "username" in data:
                user.username = data["username"]
            if "email" in data:
                user.email = data["email"]
            if "first_name" in data:
                user.first_name = data["first_name"]
            if "last_name" in data:
                user.last_name = data["last_name"]

            user.save()
            return JsonResponse({
                "username": user.username,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name
            })
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    return JsonResponse({"error": "Invalid method"}, status=405)
