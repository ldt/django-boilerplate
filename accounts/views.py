import re
from django.contrib import messages
from django.contrib.auth import login
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .forms import UserRegistrationForm
from .models import User
from .serializers import (
    LoginSerializer,
    TokenResponseSerializer,
    UserRegistrationSerializer,
    UserSerializer,
)


class RegisterAPIView(generics.CreateAPIView):
    """
    API: Register a new user account

    Creates a new user account and returns JWT tokens for immediate authentication.
    """

    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]

    @extend_schema(
        operation_id="register_user",
        summary="Register new user",
        description="Register a new user account with email and password",
        responses={
            201: OpenApiResponse(
                response=TokenResponseSerializer,
                description="User successfully registered",
            ),
            400: OpenApiResponse(description="Validation error"),
        },
    )
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "user": UserSerializer(user).data,
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            },
            status=status.HTTP_201_CREATED,
        )


class RegisterView(CreateView):
    """
    HTML form for user registration
    """
    model = User
    form_class = UserRegistrationForm
    template_name = 'registration/register.html'
    success_url = reverse_lazy('home')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = self.get_form()
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        messages.success(self.request, 'Registration successful! Welcome to our site.')
        return response

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))



class LoginView(generics.GenericAPIView):
    """
    Unified login view that handles both HTML form and JWT API authentication.
    
    - For HTML form submissions: Authenticates and logs in the user with session
    - For API requests: Returns JWT tokens
    """
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]
    template_name = 'registration/login.html'
    redirect_authenticated_user = True
    success_url = reverse_lazy('home')

    def get_serializer_context(self):
        """Extra context provided to the serializer class."""
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def get(self, request, *args, **kwargs):
        """Handle GET requests: display the login form."""
        if request.user.is_authenticated:
            return redirect(self.get_success_url())
            
        # For API requests, return 405 Method Not Allowed
        if not request.accepts('text/html'):
            return Response(
                {'detail': 'Method "GET" not allowed.'},
                status=status.HTTP_405_METHOD_NOT_ALLOWED
            )
            
        return render(request, self.template_name, {'form': self.serializer_class()})

    @extend_schema(
        operation_id="login_user",
        summary="User login",
        description="Authenticate user and return JWT tokens or session cookie",
        responses={
            200: OpenApiResponse(
                response=TokenResponseSerializer,
                description="Authentication successful"
            ),
            302: OpenApiResponse(
                description="HTML form authentication successful - redirects to success URL"
            ),
            400: OpenApiResponse(description="Invalid credentials"),
        },
    )
    def post(self, request, *args, **kwargs):
        """Handle POST requests: authenticate the user."""
        serializer = self.get_serializer(data=request.data)
        
        if not serializer.is_valid():
            # Check if this is an API request (JSON content-type or explicit JSON format)
            is_api_request = (
                request.content_type == 'application/json' or
                request.META.get('HTTP_ACCEPT', '').startswith('application/json') or
                not request.accepts('text/html')
            )
            
            if not is_api_request:
                # For HTML forms, re-render the form with errors
                return render(
                    request, 
                    self.template_name, 
                    {'form': serializer}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            # For API, return validation errors
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        user = serializer.validated_data["user"]
        
        # Check if this is an API request (JSON content-type or explicit JSON format)
        is_api_request = (
            request.content_type == 'application/json' or
            request.META.get('HTTP_ACCEPT', '').startswith('application/json') or
            not request.accepts('text/html')
        )
        
        if not is_api_request:
            # For HTML form submissions, use session-based auth
            login(request, user)
            next_url = request.POST.get('next') or self.get_success_url()
            return redirect(next_url)
        
        # For API requests, return JWT tokens
        refresh = RefreshToken.for_user(user)
        return Response({
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "user": {
                "id": user.id,
                "email": user.email,
                "username": user.username
            }
        })
    
    def get_success_url(self):
        """
        Returns the default redirect URL.
        Override this method to customize the redirect URL.
        """
        return self.success_url


class ProfileView(generics.RetrieveUpdateAPIView):
    """
    User profile endpoint

    Retrieve and update the authenticated user's profile information.
    """

    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(
        operation_id="get_user_profile",
        summary="Get user profile",
        description="Retrieve the authenticated user profile",
        responses={
            200: OpenApiResponse(
                response=UserSerializer,
                description="User profile retrieved successfully",
            ),
            401: OpenApiResponse(description="Authentication required"),
        },
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        operation_id="update_user_profile",
        summary="Update user profile",
        description="Update the authenticated user profile",
        responses={
            200: OpenApiResponse(
                response=UserSerializer, description="User profile updated successfully"
            ),
            401: OpenApiResponse(description="Authentication required"),
        },
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @extend_schema(
        operation_id="partial_update_user_profile",
        summary="Partially update user profile",
        description="Partially update the authenticated user profile",
        responses={
            200: OpenApiResponse(
                response=UserSerializer, description="User profile updated successfully"
            ),
            401: OpenApiResponse(description="Authentication required"),
        },
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)

    def get_object(self):
        return self.request.user
