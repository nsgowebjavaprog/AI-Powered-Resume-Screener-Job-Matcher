"""
accounts/urls.py
-----------------
Routes owned by the "accounts" app. Included into core/urls.py under the
prefix /api/auth/, so the full paths are:
    POST /api/auth/signup/
    POST /api/auth/login/
    POST /api/auth/login/refresh/   (built-in simplejwt view: exchange refresh->access)
    GET  /api/auth/me/
"""
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import SignupView, LoginView, MeView

urlpatterns = [
    path("signup/", SignupView.as_view(), name="signup"),
    path("login/", LoginView.as_view(), name="login"),
    path("login/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("me/", MeView.as_view(), name="me"),
]
