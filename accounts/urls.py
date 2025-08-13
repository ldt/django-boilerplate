from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from django.contrib.auth import logout
from django.urls import reverse_lazy
from django.views.generic import RedirectView

from .views import (
    LoginView, 
    ProfileView, 
    RegisterView,  # HTML form view
    RegisterAPIView,  # API view
    ValidateUsernameView,
    ValidateEmailView,
    ValidatePasswordView,
)

class LogoutView(RedirectView):
    """
    Handle user logout.
    Supports both HTML form submission and API requests.
    """
    url = reverse_lazy('login')
    
    def get(self, request, *args, **kwargs):
        logout(request)
        if request.accepts('application/json'):
            from rest_framework.response import Response
            from rest_framework import status
            return Response({"detail": "Successfully logged out."}, status=status.HTTP_200_OK)
        return super().get(request, *args, **kwargs)

# API endpoints
api_urlpatterns = [
    path("api/register/", RegisterAPIView.as_view(), name="api_register"),
    path("api/login/", LoginView.as_view(), name="api_login"),
    path("api/logout/", LogoutView.as_view(), name="api_logout"),
    path("api/profile/", ProfileView.as_view(), name="api_profile"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]

# HTML form endpoints
html_urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("profile/", ProfileView.as_view(), name="profile"),
]

# HTMX validation endpoints
htmx_urlpatterns = [
    path("validate-username/", ValidateUsernameView.as_view(), name="validate_username"),
    path("validate-email/", ValidateEmailView.as_view(), name="validate_email"),
    path("validate-password/", ValidatePasswordView.as_view(), name="validate_password"),
]

# Combine all URL patterns
urlpatterns = api_urlpatterns + html_urlpatterns + htmx_urlpatterns
