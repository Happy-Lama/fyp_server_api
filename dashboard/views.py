from django.middleware.csrf import get_token
from django.http import JsonResponse
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from .serializers import UserSerializer, NotificationSerializer
from .models import Notifications

def index(request):
    return JsonResponse({"message": "Hello"})


def get_csrf_token(request):
    csrf_token = get_token(request)
    return JsonResponse({ 'csrfToken': csrf_token})

def login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        # print(request.POST)
    
        user_exists = User.objects.get(email=email)
        # print(user_exists)

        # Authenticate user
        user = authenticate(request, username=user_exists, password=password)
        # print(user)        
        if user is not None:
            # Log in the user
            auth_login(request, user)

            # Return a success response
            return JsonResponse({'success': True, 'message': 'Login successful', 'user': UserSerializer(user).data})
        else:
            # Return an error response
            return JsonResponse({'message': 'Invalid credentials'}, status=400)

    # Return an error response for non-POST requests
    return JsonResponse({'success': False, 'message': 'Invalid request method'}, status=400)

@csrf_exempt
def logout(request):
    if request.method == 'POST':
        # Logout the currently authenticated user
        print(request.POST)
        username = request.POST.get('username')
        if username is not None:
            user = User.objects.get(username=username)
            request.user = user

            print(request.user)
            auth_logout(request)

            # Return a success response
            return JsonResponse({'success': True, 'message': 'Logout successful'})

    # Return an error response for non-POST requests
    return JsonResponse({'success': False, 'message': 'Invalid request'})


def get_notifications(request, filter):
    if filter == 'all':
        notifications = Notifications.objects.all()
        return JsonResponse({'notifications': NotificationSerializer(notifications, many=True).data})
    if filter == 'latest':
        notifications = Notifications.objects.order_by('-timestamp')[:100]
        return JsonResponse({'notifications': NotificationSerializer(notifications, many=True).data})