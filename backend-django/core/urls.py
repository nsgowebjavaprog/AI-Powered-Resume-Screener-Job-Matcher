"""
core/urls.py
------------
The MASTER router. Every incoming request first lands here, and Django
walks down this list top-to-bottom looking for a matching pattern.
Each app (accounts, jobs) owns its own urls.py -> we just "include" them,
which keeps routing modular (Separation of Concerns / OOP-style design).
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),                 # Django's built-in admin CRUD UI
    path("api/auth/", include("accounts.urls")),      # /api/auth/signup, /api/auth/login, ...
    path("api/", include("jobs.urls")),                # /api/jobs/, /api/resumes/, ...
]

# In development, let Django serve uploaded resume files directly.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
