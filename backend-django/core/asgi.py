"""
core/asgi.py
------------
ASGI entrypoint used by async servers (uvicorn/daphne) if you ever need
websockets or async views.
"""
import os
from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
application = get_asgi_application()
