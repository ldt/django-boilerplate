from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from drf_spectacular.utils import OpenApiExample, extend_schema_serializer
from rest_framework import serializers

from .models import User


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            "User Registration Example",
            summary="User registration with email",
            description="Register a new user with email and password",
            value={
                "email": "user@example.com",
                "username": "johndoe",
                "first_name": "John",
                "last_name": "Doe",
                "password": "securepassword123",
                "password_confirm": "securepassword123",
            },
        )
    ]
)
class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        validators=[validate_password],
        help_text="Password must be at least 8 characters long",
    )
    password_confirm = serializers.CharField(
        write_only=True, help_text="Confirm your password"
    )

    class Meta:
        model = User
        fields = (
            "email",
            "username",
            "first_name",
            "last_name",
            "password",
            "password_confirm",
        )

    def validate(self, attrs):
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError("Passwords don't match")
        return attrs

    def create(self, validated_data):
        validated_data.pop("password_confirm")
        user = User.objects.create_user(**validated_data)
        return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "username",
            "first_name",
            "last_name",
            "is_verified",
            "created_at",
        )
        read_only_fields = ("id", "created_at", "is_verified")


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            "Login Example",
            summary="User login with email",
            description="Login with email and password to get JWT tokens",
            value={"email": "user@example.com", "password": "securepassword123"},
        )
    ]
)
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(help_text="User's email address")
    password = serializers.CharField(help_text="User's password")

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        if email and password:
            user = authenticate(username=email, password=password)
            if not user:
                raise serializers.ValidationError("Invalid credentials")
            if not user.is_active:
                raise serializers.ValidationError("User account is disabled")

        attrs["user"] = user
        return attrs


class TokenResponseSerializer(serializers.Serializer):
    """Serializer for JWT token response"""

    access = serializers.CharField(help_text="JWT access token")
    refresh = serializers.CharField(help_text="JWT refresh token")
    user = UserSerializer(help_text="User information")
