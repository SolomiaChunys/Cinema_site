from datetime import datetime, timezone, timedelta
from django.contrib.auth import logout
from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import reverse
from rest_framework import status


class LastActivityMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        user = request.user

        if user.is_authenticated and not user.is_staff:
            last_activity = user.last_activity
            user.last_activity = datetime.now(timezone.utc)
            user.save()
            if last_activity:
                if datetime.now(timezone.utc) - last_activity > timedelta(minutes=1):
                    if hasattr(request, 'auth'):
                        request.auth.delete()
                        logout(request)
                        return HttpResponse(status=status.HTTP_401_UNAUTHORIZED)

                    logout(request)
                    return redirect(reverse('login_page'))

        return response