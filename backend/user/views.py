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
    def get(self, request):
        # Return a clean 401 for unauthenticated callers instead of redirecting
        # to LOGIN_URL (which 404s and is just noise for the SPA's auth check).
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Authentication required'}, status=401)
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

    def delete(self, request):
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Authentication required'}, status=401)
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
