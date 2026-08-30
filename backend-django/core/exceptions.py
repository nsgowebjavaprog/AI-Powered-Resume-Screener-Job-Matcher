"""
core/exceptions.py
-------------------
A custom DRF exception handler so EVERY error the API ever returns has the
same predictable JSON shape:

    {
        "success": false,
        "error": {
            "message": "...",
            "details": {...}
        }
    }

Without this, DRF's default errors are inconsistent (sometimes a list,
sometimes a dict), which makes frontend error-handling messy.
"""
from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    # Let DRF build its normal response first
    response = exception_handler(exc, context)

    if response is not None:
        response.data = {
            "success": False,
            "error": {
                "message": str(exc),
                "details": response.data,
            },
        }
    return response
