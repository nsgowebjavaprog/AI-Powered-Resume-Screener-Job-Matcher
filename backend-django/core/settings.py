"""
core/settings.py
-----------------
Central configuration file for the whole Django project.
Everything (database, installed apps, auth rules, middleware, CORS, JWT)
is configured here. Values that change between environments (dev/prod)
are pulled from environment variables using python-decouple, so secrets
never get hard-coded or committed to git.
"""
from pathlib import Path
from datetime import timedelta
from decouple import config

# BASE_DIR = the backend-django/ folder itself. Used to build absolute paths.
BASE_DIR = Path(__file__).resolve().parent.parent

# ---------------------------------------------------------------------------
# SECURITY
# ---------------------------------------------------------------------------
# SECRET_KEY is used by Django to sign sessions, tokens, etc. NEVER hardcode
# this in real projects -> it is read from the .env file (see .env.example).
SECRET_KEY = config("DJANGO_SECRET_KEY", default="dev-insecure-secret-key")

# DEBUG=True shows detailed error pages -> turn OFF in production.
DEBUG = config("DEBUG", default=True, cast=bool)

# Which hostnames are allowed to serve this app. "*" is fine for local dev.
ALLOWED_HOSTS = config("ALLOWED_HOSTS", default="*").split(",")

# ---------------------------------------------------------------------------
# INSTALLED APPS
# ---------------------------------------------------------------------------
INSTALLED_APPS = [
    "django.contrib.admin",          # built-in admin panel (CRUD UI for free)
    "django.contrib.auth",           # Django's built-in authentication system
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # 3rd party
    "rest_framework",                # Django REST Framework -> turns models into JSON APIs
    "rest_framework_simplejwt",      # JWT (JSON Web Token) authentication
    "corsheaders",                   # allows the frontend (different origin) to call this API
    "django_filters",                # lets API endpoints be filtered via query params

    # our own apps
    "accounts",                      # custom User model + login/signup/JWT
    "jobs",                          # JobPosting, Resume, MatchResult models + CRUD API
]

# ---------------------------------------------------------------------------
# MIDDLEWARE
# ---------------------------------------------------------------------------
# Middleware = code that runs on EVERY request/response, in order, like a
# pipeline. Order matters (e.g. CORS must run before CommonMiddleware).
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",       # 1) handle cross-origin headers first
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "core.urls"  # points to core/urls.py -> the master URL router

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "core.wsgi.application"
ASGI_APPLICATION = "core.asgi.application"

# ---------------------------------------------------------------------------
# DATABASE  (PostgreSQL)
# ---------------------------------------------------------------------------
# All values come from environment variables (see .env.example / docker-compose.yml)
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": config("POSTGRES_DB", default="resume_screener"),
        "USER": config("POSTGRES_USER", default="postgres"),
        "PASSWORD": config("POSTGRES_PASSWORD", default="postgres"),
        "HOST": config("POSTGRES_HOST", default="localhost"),   # "db" inside docker-compose
        "PORT": config("POSTGRES_PORT", default="5432"),
    }
}

# ---------------------------------------------------------------------------
# CUSTOM USER MODEL
# ---------------------------------------------------------------------------
# We use our own User model (accounts.User) instead of Django's default so we
# can add fields like `role` (candidate / recruiter) and `full_name`.
AUTH_USER_MODEL = "accounts.User"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "Asia/Kolkata"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
MEDIA_URL = "/media/"                       # for uploaded resume files (PDF/DOCX)
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ---------------------------------------------------------------------------
# DJANGO REST FRAMEWORK
# ---------------------------------------------------------------------------
REST_FRAMEWORK = {
    # Every request must present a valid JWT access token EXCEPT views that
    # explicitly opt out (login/signup use AllowAny).
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
    ),
    "DEFAULT_FILTER_BACKENDS": (
        "django_filters.rest_framework.DjangoFilterBackend",
    ),
    # Built-in pagination -> API list endpoints return 10 items per page
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 10,
    # Consistent error format for the whole API
    "EXCEPTION_HANDLER": "core.exceptions.custom_exception_handler",
}

# ---------------------------------------------------------------------------
# SIMPLE JWT (Authentication tokens)
# ---------------------------------------------------------------------------
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=60),   # short-lived token used on every request
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),      # used to get a new access token
    "ROTATE_REFRESH_TOKENS": True,
    "AUTH_HEADER_TYPES": ("Bearer",),                 # frontend sends: Authorization: Bearer <token>
}

# ---------------------------------------------------------------------------
# CORS  (allow the plain HTML/JS frontend, served on a different port, to
# call this API from the browser)
# ---------------------------------------------------------------------------
CORS_ALLOWED_ORIGINS = config(
    "CORS_ALLOWED_ORIGINS",
    default="http://localhost:5500,http://127.0.0.1:5500,http://localhost:3000",
).split(",")
CORS_ALLOW_CREDENTIALS = True

# ---------------------------------------------------------------------------
# CUSTOM PROJECT SETTINGS
# ---------------------------------------------------------------------------
# URL of the FastAPI microservice that does the AI resume-vs-job matching.
# Django calls this internally (server-to-server) when a match is requested.
FASTAPI_MATCH_SERVICE_URL = config(
    "FASTAPI_MATCH_SERVICE_URL", default="http://localhost:8001"
)
