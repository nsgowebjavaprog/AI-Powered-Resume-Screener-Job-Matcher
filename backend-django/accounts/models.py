"""
accounts/models.py
-------------------
Defines our custom User table.

OOP CONCEPT: `User` INHERITS from Django's `AbstractUser`. That means it
automatically gets username, email, password, is_active, is_staff, etc.
"for free" via inheritance, and we just ADD the extra fields we need
(role, full_name). This is the standard Django way of extending auth
instead of writing a whole new auth system from scratch.

Each model class = one database table (this is Django's ORM: Object
Relational Mapper -> Python classes map directly to SQL tables, each
field maps to a column, no raw SQL needed).
"""
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    # Two kinds of accounts: a job-seeker uploading resumes, or a recruiter
    # posting jobs. `choices` restricts the value at the database level.
    class Role(models.TextChoices):
        CANDIDATE = "candidate", "Candidate"
        RECRUITER = "recruiter", "Recruiter"

    full_name = models.CharField(max_length=150, blank=True)
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.CANDIDATE)
    created_at = models.DateTimeField(auto_now_add=True)  # set once, on creation

    def __str__(self):
        # Controls how a User prints (e.g. in Django admin dropdowns)
        return f"{self.username} ({self.role})"
