"""
jobs/permissions.py
--------------------
AUTHORIZATION rules (as opposed to accounts/ which is AUTHENTICATION).
Authentication = "who are you?"    Authorization = "are you allowed to do this?"

DRF permission classes are just OOP: each one implements `has_permission`
and/or `has_object_permission`, returning True/False.
"""
from rest_framework import permissions


class IsRecruiter(permissions.BasePermission):
    """Only users with role='recruiter' may create/edit job postings."""
    def has_permission(self, request, view):
        # Read-only requests (GET/HEAD/OPTIONS) are open to any authenticated user
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated and request.user.role == "recruiter"


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Object-level permission: anyone can VIEW a single object, but only the
    user who OWNS it (recruiter of a job, candidate of a resume) can
    update/delete it.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        owner = getattr(obj, "recruiter", None) or getattr(obj, "candidate", None)
        return owner == request.user
