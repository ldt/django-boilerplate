"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.http import HttpResponse
from django.urls import include, path
from django.views.generic import RedirectView


def home_view(request):
    """Simple home view for testing"""
    return HttpResponse("Welcome to the home page!")

# Regular URL patterns
urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/", include("api.urls")),
    path("accounts/", include("accounts.urls")),  # Include accounts URLs
    path("", home_view, name='home'),  # Home page
    path("", include("accounts.urls")),  # Include root URLs for login/register
]

# Catch-all pattern - must be the last pattern
# This will match any URL that hasn't been matched by previous patterns
urlpatterns += [
    path('<path:path>', RedirectView.as_view(url='/register/', permanent=False)),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
