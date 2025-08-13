# Django Boilerplate with JWT Authentication - Complete Guide

## Overview

This guide will help you build a production-ready Django boilerplate project with:
- User authentication system
- JWT-based REST API
- Database configuration for both SQLite (development) and PostgreSQL (production)
- Docker setup for production deployment
- Best practices for scalability and maintainability

## Prerequisites

- Python 3.11+
- Docker and Docker Compose
- Basic understanding of Django and REST APIs

## Step 1: Project Setup with UV

### Why UV?
UV is a fast Python package manager that provides:
- Faster dependency resolution than pip
- Better dependency locking
- Virtual environment management
- Improved caching

### Installation and Project Initialization

```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create project directory
mkdir django-boilerplate
cd django-boilerplate

# Initialize Python project with uv
uv init

# Create virtual environment and activate it
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### Install Dependencies

```bash
# Install Django and essential packages
uv add django djangorestframework django-cors-headers python-decouple psycopg2-binary djangorestframework-simplejwt django-extensions drf-spectacular

# Development dependencies
uv add --dev black flake8 isort pytest pytest-django factory-boy
```

**Purpose of each dependency:**
- `django`: Web framework
- `djangorestframework`: REST API toolkit
- `django-cors-headers`: Handle Cross-Origin Resource Sharing
- `python-decouple`: Environment variable management
- `psycopg2-binary`: PostgreSQL adapter
- `djangorestframework-simplejwt`: JWT authentication
- `django-extensions`: Additional Django management commands
- `black`, `flake8`, `isort`: Code formatting and linting
- `pytest`, `pytest-django`, `factory-boy`: Testing tools

## Step 2: Django Project Structure

```bash
# Create Django project
uv run django-admin startproject core .

# Create apps
uv run python manage.py startapp accounts
uv run python manage.py startapp api
```

### Project Structure
```
django-boilerplate/
├── accounts/          # User authentication app
├── api/              # API endpoints
├── core/             # Project settings
├── docker/           # Docker configuration
├── requirements/     # Split requirements files
├── static/           # Static files
├── media/            # Media files
├── .env.example      # Environment variables template
├── .gitignore
├── docker-compose.yml
├── Dockerfile
└── manage.py
```

## Step 3: Settings Configuration

### Create Settings Module

```bash
mkdir core/settings
touch core/settings/__init__.py
touch core/settings/base.py
touch core/settings/development.py
touch core/settings/production.py
```

### Base Settings (`core/settings/base.py`)

```python
import os
from pathlib import Path
from decouple import config
from datetime import timedelta

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY', default='your-secret-key-here')

# Application definition
DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

THIRD_PARTY_APPS = [
    'rest_framework',
    'rest_framework_simplejwt',
    'drf_spectacular',
    'corsheaders',
    'django_extensions',
]

LOCAL_APPS = [
    'accounts',
    'api',
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Custom User Model
AUTH_USER_MODEL = 'accounts.User'

# Django REST Framework Configuration
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_FILTER_BACKENDS': [
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

# DRF Spectacular Configuration
SPECTACULAR_SETTINGS = {
    'TITLE': 'Django Boilerplate API',
    'DESCRIPTION': 'A boilerplate Django REST API with JWT authentication',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'COMPONENT_SPLIT_REQUEST': True,
    'SWAGGER_UI_SETTINGS': {
        'deepLinking': True,
        'persistAuthorization': True,
        'displayOperationId': True,
    },
    'SWAGGER_UI_FAVICON_HREF': '/static/favicon.ico',
    'REDOC_UI_SETTINGS': {
        'hideDownloadButton': True,
    },
}

# JWT Configuration
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUDIENCE': None,
    'ISSUER': None,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
}

# CORS Configuration
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",  # React development server
    "http://127.0.0.1:3000",
]

CORS_ALLOW_CREDENTIALS = True
```

**Purpose of this configuration:**
- **Modular apps**: Separates Django, third-party, and local apps for clarity
- **JWT settings**: Configures token lifetime and security
- **CORS**: Allows frontend applications to access the API
- **Custom user model**: Provides flexibility for user management
- **REST framework**: Sets up API defaults and pagination

### Development Settings (`core/settings/development.py`)

```python
from .base import *

DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# Database - SQLite for development
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
        'ATOMIC_REQUESTS': True,
    }
}

# Email backend for development
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
        },
    },
}
```

### Production Settings (`core/settings/production.py`)

```python
from .base import *

DEBUG = False

ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='').split(',')

# Database - PostgreSQL for production
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default='5432'),
        'ATOMIC_REQUESTS': True,
        'CONN_MAX_AGE': 60,
    }
}

# Security Settings
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# Email configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = config('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')

# Static files configuration for production
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'
```

### Update `core/settings/__init__.py`

```python
from decouple import config

environment = config('ENVIRONMENT', default='development')

if environment == 'production':
    from .production import *
elif environment == 'development':
    from .development import *
else:
    from .development import *
```

## Step 4: Custom User Model

### Create User Model (`accounts/models.py`)

```python
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    def __str__(self):
        return self.email
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()
```

**Purpose:** Custom user model using email as the primary identifier, with additional fields for verification and timestamps.

### Create User Admin (`accounts/admin.py`)

```python
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('email', 'username', 'first_name', 'last_name', 'is_verified', 'is_staff')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'is_verified')
    search_fields = ('email', 'username', 'first_name', 'last_name')
    ordering = ('email',)
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('is_verified',)}),
    )
```

## Step 5: Authentication API

### Create Serializers (`accounts/serializers.py`)

```python
from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from drf_spectacular.utils import extend_schema_serializer, OpenApiExample
from .models import User

@extend_schema_serializer(
    examples=[
        OpenApiExample(
            'User Registration Example',
            summary='User registration with email',
            description='Register a new user with email and password',
            value={
                'email': 'user@example.com',
                'username': 'johndoe',
                'first_name': 'John',
                'last_name': 'Doe',
                'password': 'securepassword123',
                'password_confirm': 'securepassword123'
            }
        )
    ]
)
class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True, 
        validators=[validate_password],
        help_text="Password must be at least 8 characters long"
    )
    password_confirm = serializers.CharField(
        write_only=True,
        help_text="Confirm your password"
    )
    
    class Meta:
        model = User
        fields = ('email', 'username', 'first_name', 'last_name', 'password', 'password_confirm')
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords don't match")
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return user

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'first_name', 'last_name', 'is_verified', 'created_at')
        read_only_fields = ('id', 'created_at', 'is_verified')

@extend_schema_serializer(
    examples=[
        OpenApiExample(
            'Login Example',
            summary='User login with email',
            description='Login with email and password to get JWT tokens',
            value={
                'email': 'user@example.com',
                'password': 'securepassword123'
            }
        )
    ]
)
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(help_text="User's email address")
    password = serializers.CharField(help_text="User's password")
    
    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        
        if email and password:
            user = authenticate(username=email, password=password)
            if not user:
                raise serializers.ValidationError('Invalid credentials')
            if not user.is_active:
                raise serializers.ValidationError('User account is disabled')
        
        attrs['user'] = user
        return attrs

class TokenResponseSerializer(serializers.Serializer):
    """Serializer for JWT token response"""
    access = serializers.CharField(help_text="JWT access token")
    refresh = serializers.CharField(help_text="JWT refresh token")
    user = UserSerializer(help_text="User information")
```

### Create Views (`accounts/views.py`)

```python
from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from drf_spectacular.utils import extend_schema, OpenApiResponse
from .serializers import (
    UserRegistrationSerializer, 
    UserSerializer, 
    LoginSerializer,
    TokenResponseSerializer
)
from .models import User

class RegisterView(generics.CreateAPIView):
    """
    Register a new user account
    
    Creates a new user account and returns JWT tokens for immediate authentication.
    """
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]
    
    @extend_schema(
        operation_id='register_user',
        summary='Register new user',
        description='Register a new user account with email and password',
        responses={
            201: OpenApiResponse(
                response=TokenResponseSerializer,
                description='User successfully registered'
            ),
            400: OpenApiResponse(description='Validation error')
        }
    )
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'user': UserSerializer(user).data,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }, status=status.HTTP_201_CREATED)

class LoginView(generics.GenericAPIView):
    """
    User login endpoint
    
    Authenticate user with email and password, returns JWT tokens.
    """
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]
    
    @extend_schema(
        operation_id='login_user',
        summary='User login',
        description='Login with email and password to get JWT tokens',
        responses={
            200: OpenApiResponse(
                response=TokenResponseSerializer,
                description='Login successful'
            ),
            400: OpenApiResponse(description='Invalid credentials')
        }
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = serializer.validated_data['user']
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'user': UserSerializer(user).data,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        })

class ProfileView(generics.RetrieveUpdateAPIView):
    """
    User profile endpoint
    
    Retrieve and update the authenticated user's profile information.
    """
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        operation_id='get_user_profile',
        summary='Get user profile',
        description='Retrieve the authenticated user profile',
        responses={
            200: OpenApiResponse(
                response=UserSerializer,
                description='User profile retrieved successfully'
            ),
            401: OpenApiResponse(description='Authentication required')
        }
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @extend_schema(
        operation_id='update_user_profile',
        summary='Update user profile',
        description='Update the authenticated user profile',
        responses={
            200: OpenApiResponse(
                response=UserSerializer,
                description='User profile updated successfully'
            ),
            401: OpenApiResponse(description='Authentication required')
        }
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)
    
    @extend_schema(
        operation_id='partial_update_user_profile',
        summary='Partially update user profile',
        description='Partially update the authenticated user profile',
        responses={
            200: OpenApiResponse(
                response=UserSerializer,
                description='User profile updated successfully'
            ),
            401: OpenApiResponse(description='Authentication required')
        }
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)
    
    def get_object(self):
        return self.request.user
```

### Create URLs (`accounts/urls.py`)

```python
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import RegisterView, LoginView, ProfileView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
```

## Step 6: API Structure

### Create API URLs (`api/urls.py`)

```python
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

router = DefaultRouter()

urlpatterns = [
    path('auth/', include('accounts.urls')),
    path('', include(router.urls)),
    
    # OpenAPI Documentation URLs
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]
```

### Update Main URLs (`core/urls.py`)

```python
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include('api.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

## Step 7: Environment Configuration

### Create `.env.example`

```bash
# Environment
ENVIRONMENT=development

# Security
SECRET_KEY=your-super-secret-key-here

# Database (Production)
DB_NAME=your_database_name
DB_USER=your_database_user
DB_PASSWORD=your_database_password
DB_HOST=localhost
DB_PORT=5432

# Email Configuration
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=your_app_password

# Allowed Hosts (Production)
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
```

### Create `.env` for development

```bash
cp .env.example .env
# Edit .env with your local values
```

## Step 8: Docker Configuration

### Create `Dockerfile`

```dockerfile
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install UV
RUN pip install uv

# Copy pyproject.toml and uv.lock
COPY pyproject.toml uv.lock* ./

# Install dependencies
RUN uv sync --no-dev

# Copy project
COPY . .

# Collect static files
RUN python manage.py collectstatic --noinput

# Expose port
EXPOSE 8000

# Run the application
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
```

### Create `docker-compose.yml`

```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - .:/app
    depends_on:
      - db
    environment:
      - ENVIRONMENT=production
      - DB_HOST=db
      - DB_NAME=postgres
      - DB_USER=postgres
      - DB_PASSWORD=postgres
    command: >
      sh -c "python manage.py migrate &&
             python manage.py runserver 0.0.0.0:8000"

  db:
    image: postgres:15
    volumes:
      - postgres_data:/var/lib/postgresql/data/
    environment:
      - POSTGRES_DB=postgres
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres

volumes:
  postgres_data:
```

## Step 9: Testing Setup

### Create `conftest.py` in the project root

```python
import pytest
import os
import django
from django.conf import settings
from django.test.utils import get_runner

def pytest_configure():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings.development')
    django.setup()

@pytest.fixture(scope='session')
def django_db_setup():
    settings.DATABASES['default'] = {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
        'ATOMIC_REQUESTS': True,
    }
```

### Create `pytest.ini`

```ini
[tool:pytest]
DJANGO_SETTINGS_MODULE = core.settings.development
python_files = tests.py test_*.py *_tests.py
addopts = -v --tb=short --reuse-db
testpaths = .
```

### Create Test Factory (`accounts/tests/factories.py`)

First, create the test directory structure:

```bash
mkdir -p accounts/tests
touch accounts/tests/__init__.py
touch accounts/tests/factories.py
touch accounts/tests/test_authentication.py
```

```python
import factory
from django.contrib.auth import get_user_model

User = get_user_model()

class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
    
    email = factory.Sequence(lambda n: f"user{n}@example.com")
    username = factory.Sequence(lambda n: f"user{n}")
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    is_active = True
```

### Create Tests (`accounts/tests/test_authentication.py`)

```python
import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from .factories import UserFactory

User = get_user_model()

@pytest.mark.django_db
class TestAuthentication:
    def setup_method(self):
        self.client = APIClient()
    
    def test_user_registration(self):
        url = reverse('register')
        data = {
            'email': 'test@example.com',
            'username': 'testuser',
            'first_name': 'Test',
            'last_name': 'User',
            'password': 'testpassword123',
            'password_confirm': 'testpassword123'
        }
        response = self.client.post(url, data)
        
        assert response.status_code == status.HTTP_201_CREATED
        assert 'access' in response.data
        assert 'refresh' in response.data
        assert User.objects.filter(email='test@example.com').exists()
    
    def test_user_login(self):
        user = UserFactory(email='test@example.com')
        user.set_password('testpassword123')
        user.save()
        
        url = reverse('login')
        data = {
            'email': 'test@example.com',
            'password': 'testpassword123'
        }
        response = self.client.post(url, data)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data
        assert 'refresh' in response.data
    
    def test_user_login_invalid_credentials(self):
        url = reverse('login')
        data = {
            'email': 'nonexistent@example.com',
            'password': 'wrongpassword'
        }
        response = self.client.post(url, data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_profile_access_authenticated(self):
        user = UserFactory()
        self.client.force_authenticate(user=user)
        
        url = reverse('profile')
        response = self.client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['email'] == user.email
    
    def test_profile_access_unauthenticated(self):
        url = reverse('profile')
        response = self.client.get(url)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
```

## Step 10: Database Migrations and Setup

```bash
# Create and run migrations
uv run python manage.py makemigrations
uv run python manage.py migrate

# Create superuser
uv run python manage.py createsuperuser

# Run tests to make sure everything works
uv run pytest

# Run development server
uv run python manage.py runserver
```

### If you get import errors with tests, make sure you have the correct directory structure:

```bash
# Ensure proper test directory structure
mkdir -p accounts/tests
touch accounts/tests/__init__.py

# Also create __init__.py in the accounts app if it doesn't exist
touch accounts/__init__.py
```

## Step 11: Production Deployment

### For Docker deployment:

```bash
# Build and run with Docker Compose
docker-compose up --build

# Run migrations in production
docker-compose exec web python manage.py migrate

# Create superuser in production
docker-compose exec web python manage.py createsuperuser
```

### Environment Variables for Production:

```bash
# Set these in your production environment
export ENVIRONMENT=production
export SECRET_KEY=your-production-secret-key
export DB_NAME=your_production_db
export DB_USER=your_production_user
export DB_PASSWORD=your_production_password
export DB_HOST=your_production_host
export ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
```

## Step 12: API Documentation

Your API documentation is now automatically generated and available at:

- **Swagger UI**: `http://localhost:8000/api/v1/docs/` - Interactive API documentation
- **ReDoc**: `http://localhost:8000/api/v1/redoc/` - Alternative documentation format
- **OpenAPI Schema**: `http://localhost:8000/api/v1/schema/` - Raw OpenAPI 3.0 schema

### Features of the API Documentation:

1. **Interactive Testing**: Use the "Try it out" button in Swagger UI to test endpoints
2. **JWT Authentication**: Use the "Authorize" button to add your JWT token
3. **Example Requests/Responses**: Each endpoint includes example data
4. **Schema Validation**: Automatic validation based on serializers
5. **Error Responses**: Documented error codes and messages

### Testing the Documentation:

```bash
# Start the development server
uv run python manage.py runserver

# Visit the documentation URLs:
# - Swagger UI: http://localhost:8000/api/v1/docs/
# - ReDoc: http://localhost:8000/api/v1/redoc/
```

### Using JWT Authentication in Swagger UI:

1. Register a new user or login to get an access token
2. Click the "Authorize" button in Swagger UI
3. Enter: `Bearer <your-access-token>`
4. Now you can test protected endpoints

## Step 13: Additional Tools and Commands

### Create `Makefile` for common commands:

```makefile
.PHONY: install migrate test run docker-build docker-run

install:
	uv sync

migrate:
	uv run python manage.py makemigrations
	uv run python manage.py migrate

test:
	uv run pytest

run:
	uv run python manage.py runserver

docker-build:
	docker-compose build

docker-run:
	docker-compose up

format:
	uv run black .
	uv run isort .

lint:
	uv run flake8 .
```

## API Usage Examples

### Register a new user:
```bash
curl -X POST http://localhost:8000/api/v1/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "username": "newuser",
    "first_name": "John",
    "last_name": "Doe",
    "password": "securepassword123",
    "password_confirm": "securepassword123"
  }'
```

### Login:
```bash
curl -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepassword123"
  }'
```

### Access protected endpoint:
```bash
curl -X GET http://localhost:8000/api/v1/auth/profile/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## Best Practices Summary

1. **Environment Management**: Use separate settings for development and production
2. **Security**: Implement proper JWT configuration and security headers
3. **Database**: SQLite for development, PostgreSQL for production
4. **Testing**: Comprehensive test coverage with pytest and factories
5. **Code Quality**: Use black, isort, and flake8 for code formatting
6. **Documentation**: Clear API documentation and setup instructions
7. **Scalability**: Modular app structure for easy extension
8. **Deployment**: Docker-ready configuration for consistent deployments

This boilerplate provides a solid foundation for Django REST API projects with modern best practices and can be easily extended for various use cases.