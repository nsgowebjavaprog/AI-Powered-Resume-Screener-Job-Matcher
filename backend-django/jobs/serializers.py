"""
jobs/serializers.py
--------------------
Validation + JSON conversion for JobPosting, Resume, MatchResult.
"""
from rest_framework import serializers
from .models import JobPosting, Resume, MatchResult


class JobPostingSerializer(serializers.ModelSerializer):
    # Show the recruiter's username in output instead of just their ID (read-only)
    recruiter_username = serializers.ReadOnlyField(source="recruiter.username")

    class Meta:
        model = JobPosting
        fields = [
            "id", "title", "company", "description", "required_skills",
            "location", "recruiter", "recruiter_username", "created_at", "updated_at",
        ]
        # recruiter is set automatically from the logged-in user (see views.py),
        # never trust a client-supplied recruiter id.
        read_only_fields = ["recruiter", "created_at", "updated_at"]

    def validate_required_skills(self, value):
        # Custom field-level validation, same idea as a Pydantic @validator
        if not value.strip():
            raise serializers.ValidationError("required_skills cannot be empty.")
        return value


class ResumeSerializer(serializers.ModelSerializer):
    candidate_username = serializers.ReadOnlyField(source="candidate.username")

    class Meta:
        model = Resume
        fields = [
            "id", "title", "file", "raw_text", "candidate",
            "candidate_username", "created_at",
        ]
        read_only_fields = ["candidate", "created_at"]

    def validate_raw_text(self, value):
        if len(value.strip()) < 30:
            raise serializers.ValidationError(
                "Resume text looks too short — paste the full resume content."
            )
        return value


class MatchResultSerializer(serializers.ModelSerializer):
    job_title = serializers.ReadOnlyField(source="job.title")
    resume_title = serializers.ReadOnlyField(source="resume.title")

    class Meta:
        model = MatchResult
        fields = [
            "id", "resume", "job", "resume_title", "job_title",
            "score", "matched_skills", "missing_skills", "created_at",
        ]
        read_only_fields = fields  # match results are only ever created by the system
