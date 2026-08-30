"""
accounts/serializers.py
------------------------
DRF "Serializers" do two jobs:
  1) VALIDATION - same role Pydantic models play in FastAPI. Incoming JSON
     is checked against field types/rules BEFORE it ever touches the DB.
  2) SERIALIZATION - convert Python/ORM objects -> JSON for API responses,
     and JSON -> Python objects for incoming requests (both directions).
"""
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from .models import User


class SignupSerializer(serializers.ModelSerializer):
    # write_only=True -> password is accepted on input but NEVER sent back out
    password = serializers.CharField(write_only=True, validators=[validate_password])

    class Meta:
        model = User
        fields = ["id", "username", "email", "password", "full_name", "role"]

    def create(self, validated_data):
        # Use create_user() (not create()) so Django hashes the password
        # with PBKDF2 -> raw passwords are NEVER stored in the database.
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data.get("email", ""),
            password=validated_data["password"],
            full_name=validated_data.get("full_name", ""),
            role=validated_data.get("role", User.Role.CANDIDATE),
        )
        return user


class LoginSerializer(serializers.Serializer):
    """A plain Serializer (not tied to a model) since login doesn't create a row."""
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        # `authenticate()` checks the username/password against the hashed
        # password in the DB and returns the User object, or None if invalid.
        user = authenticate(username=attrs["username"], password=attrs["password"])
        if not user:
            raise serializers.ValidationError("Invalid username or password.")
        attrs["user"] = user
        return attrs


class UserSerializer(serializers.ModelSerializer):
    """Safe, read-only view of a user -> used to return `me` profile data."""
    class Meta:
        model = User
        fields = ["id", "username", "email", "full_name", "role", "created_at"]
        read_only_fields = fields
