from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User
from .serializers import LoginSerializer, TokenResponseSerializer, UserRegistrationSerializer, UserSerializer


class RegisterView(generics.CreateAPIView):
    """
    Register a new user account

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
                response=TokenResponseSerializer, description="User successfully registered"
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


class LoginView(generics.GenericAPIView):
    """
    User login endpoint

    Authenticate user with email and password, returns JWT tokens.
    """

    serializer_class = LoginSerializer
    permission_classes = [AllowAny]

    @extend_schema(
        operation_id="login_user",
        summary="User login",
        description="Login with email and password to get JWT tokens",
        responses={
            200: OpenApiResponse(response=TokenResponseSerializer, description="Login successful"),
            400: OpenApiResponse(description="Invalid credentials"),
        },
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["user"]
        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "user": UserSerializer(user).data,
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            }
        )


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
            200: OpenApiResponse(response=UserSerializer, description="User profile retrieved successfully"),
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
            200: OpenApiResponse(response=UserSerializer, description="User profile updated successfully"),
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
            200: OpenApiResponse(response=UserSerializer, description="User profile updated successfully"),
            401: OpenApiResponse(description="Authentication required"),
        },
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)

    def get_object(self):
        return self.request.user
