"""
jobs/views.py
-------------
This is where CRUD (Create, Read, Update, Delete) actually happens.

DRF's `ModelViewSet` is an OOP base class that, by inheritance, already
implements list/create/retrieve/update/destroy for a model. We just point
it at a queryset + serializer and add our own hooks (perform_create,
get_queryset) to bolt on business rules -> this is "Don't Repeat Yourself"
in action: a handful of lines gives us 5 REST endpoints per model:

    GET    /api/jobs/          -> list
    POST   /api/jobs/          -> create
    GET    /api/jobs/{id}/     -> retrieve
    PUT    /api/jobs/{id}/     -> update
    PATCH  /api/jobs/{id}/     -> partial update
    DELETE /api/jobs/{id}/     -> delete
"""
import requests
from django.conf import settings
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import JobPosting, Resume, MatchResult
from .serializers import JobPostingSerializer, ResumeSerializer, MatchResultSerializer
from .permissions import IsRecruiter, IsOwnerOrReadOnly


class JobPostingViewSet(viewsets.ModelViewSet):
    """Full CRUD for job postings. Recruiters create/edit; everyone can browse."""
    serializer_class = JobPostingSerializer
    permission_classes = [permissions.IsAuthenticated, IsRecruiter, IsOwnerOrReadOnly]
    # Lets the frontend do: GET /api/jobs/?location=Bangalore
    filterset_fields = ["location", "company"]
    search_fields = ["title", "company", "required_skills"]

    def get_queryset(self):
        # All jobs are visible to everyone who is logged in (candidates browse them)
        return JobPosting.objects.all()

    def perform_create(self, serializer):
        # Force the recruiter field to be the CURRENTLY LOGGED IN user.
        # (never trust the client to say who they are for this field)
        serializer.save(recruiter=self.request.user)


class ResumeViewSet(viewsets.ModelViewSet):
    """Full CRUD for resumes. A candidate can only see/edit THEIR OWN resumes."""
    serializer_class = ResumeSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]

    def get_queryset(self):
        # Row-level security: filter the queryset itself so a user can never
        # even list another candidate's resumes, let alone edit them.
        return Resume.objects.filter(candidate=self.request.user)

    def perform_create(self, serializer):
        serializer.save(candidate=self.request.user)

    @action(detail=True, methods=["post"], url_path="match/(?P<job_id>[^/.]+)")
    def match(self, request, pk=None, job_id=None):
        """
        POST /api/resumes/{resume_id}/match/{job_id}/
        Custom endpoint (not part of default CRUD) that:
          1. loads the Resume + JobPosting from Postgres
          2. calls the FastAPI AI microservice to score them
          3. stores the result in MatchResult (upsert) and returns it
        This shows Django and FastAPI working TOGETHER: Django owns auth +
        data, FastAPI owns the AI computation.
        """
        resume = self.get_object()
        try:
            job = JobPosting.objects.get(pk=job_id)
        except JobPosting.DoesNotExist:
            return Response({"detail": "Job not found."}, status=status.HTTP_404_NOT_FOUND)

        # --- call the FastAPI microservice over HTTP (server-to-server) ---
        try:
            resp = requests.post(
                f"{settings.FASTAPI_MATCH_SERVICE_URL}/api/match",
                json={
                    "resume_text": resume.raw_text,
                    "job_description": job.description,
                    "required_skills": job.required_skills,
                },
                timeout=10,
            )
            resp.raise_for_status()
            ai_result = resp.json()
        except requests.RequestException as e:
            return Response(
                {"detail": f"AI matching service unavailable: {e}"},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        # update_or_create = upsert: avoids duplicate rows for the same pair
        match_obj, _ = MatchResult.objects.update_or_create(
            resume=resume, job=job,
            defaults={
                "score": ai_result["score"],
                "matched_skills": ",".join(ai_result["matched_skills"]),
                "missing_skills": ",".join(ai_result["missing_skills"]),
            },
        )
        return Response(MatchResultSerializer(match_obj).data, status=status.HTTP_200_OK)


class MatchResultViewSet(viewsets.ReadOnlyModelViewSet):
    """Read-only history of all match results for the logged-in candidate."""
    serializer_class = MatchResultSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return MatchResult.objects.filter(resume__candidate=self.request.user)
