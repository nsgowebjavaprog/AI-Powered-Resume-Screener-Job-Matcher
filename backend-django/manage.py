#!/usr/bin/env python
"""
manage.py
----------
Django's command-line utility. This is the file you run for EVERYTHING:
    python manage.py runserver        -> starts the dev server
    python manage.py makemigrations   -> creates migration files from models.py changes
    python manage.py migrate          -> applies migrations to the database
    python manage.py createsuperuser  -> creates an admin login
You normally never need to edit this file.
"""
import os
import sys


def main():
    # Tell Django which settings module to use (core/settings.py)
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    # Hand off control to whatever command was typed after "manage.py"
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
