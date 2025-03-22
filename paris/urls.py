from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
import subprocess
import hmac
import hashlib
from decouple import config
import json

def home(request):
    return HttpResponse("Hello, Django is working!")

@csrf_exempt
def webhook(request):
    if request.method == 'POST':
        try:
            # Validate signature
            signature = request.headers.get('X-Hub-Signature-256', '').split('sha256=')[-1].strip()
            body = request.body
            secret_token = config("SSL_SECRET_TOKEN")
            expected_signature = hmac.new(secret_token.encode(), body, hashlib.sha256).hexdigest()

            if not hmac.compare_digest(signature, expected_signature):
                return JsonResponse({'error':f"Received Signature: {signature}", 'error':f" Expected  Signature: {expected_signature}",'error': 'Invalied signature'}, status=403)

            # Execute Git pull and restart services
            repo_dir = config("PROJECT_DIR")
            subprocess.run(['git', '-C', repo_dir, 'pull', 'origin', 'aws-deployment'])
            subprocess.run(['sudo', 'systemctl', 'restart', 'gunicorn'])
            subprocess.run(['sudo', 'systemctl', 'restart','nginx'])

            return JsonResponse({'status': 'success'})

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Invalid request method'}, status=400)


urlpatterns = [
    path("admin/", admin.site.urls),
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/", include("admin_user.urls")),
    path("api/", include("users.urls")),
    path("api/", include("packages.urls")),
    path("api/", include("resorts.urls")),
    path("api/", include("profileapp.urls")),
    path("api/", include("payments.urls")),
    path("api/", include("messege.urls")),
    path("api/", include("visas.urls")),
    path("api/", include("flights.urls")),
    path('', home),
    path('webhook/', webhook, name='webhook'),
]
