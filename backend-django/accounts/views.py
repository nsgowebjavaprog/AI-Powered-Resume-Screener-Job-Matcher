"""
accounts/views.py
------------------
API "views" = the actual functions/classes that run when a request hits a
URL. Each one: (1) validates input via a serializer, (2) does the work,
(3) returns a Response. This is the Authentication + Authorization layer.
"""
from rest_framework import status, generics, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User
from .serializers import SignupSerializer, LoginSerializer, UserSerializer


def get_tokens_for_user(user):
    """
    Helper: manually issue a JWT pair for a user.
    - refresh token: long-lived (7 days), used only to fetch new access tokens
    - access token: short-lived (60 min), sent on every API request in the
      header:  Authorization: Bearer <access_token>
    """
    refresh = RefreshToken.for_user(user)
    return {"refresh": str(refresh), "access": str(refresh.access_token)}


class SignupView(generics.CreateAPIView):
    """
    POST /api/auth/signup/
    AllowAny -> the ONE endpoint that must be reachable without already
    being logged in (chicken-and-egg problem of authentication).
    """
    queryset = User.objects.all()
    serializer_class = SignupSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)   # <- validation happens here
        user = serializer.save()                     # <- calls SignupSerializer.create()
        tokens = get_tokens_for_user(user)
        return Response(
            {"user": UserSerializer(user).data, "tokens": tokens},
            status=status.HTTP_201_CREATED,
        )


class LoginView(APIView):
    """
    POST /api/auth/login/  { "username": "...", "password": "..." }
    Returns JWT access + refresh tokens on success.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        tokens = get_tokens_for_user(user)
        return Response({"user": UserSerializer(user).data, "tokens": tokens})


class MeView(APIView):
    """
    GET /api/auth/me/
    Requires a valid access token (default permission = IsAuthenticated,
    inherited from settings.REST_FRAMEWORK). Used by the frontend to check
    "who is currently logged in" / restore session on page refresh.
    """
    def get(self, request):
        return Response(UserSerializer(request.user).data)
