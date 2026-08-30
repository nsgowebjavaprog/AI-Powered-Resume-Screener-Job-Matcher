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
    """
    Handles resumes uploaded as a PDF/DOCX file. `raw_text` is extracted
    server-side (see jobs/utils.py + jobs/views.py perform_create) and is
    NEVER accepted directly from the client -> it's read_only here.
    `file` is required on create so every resume has a source document.
    """
    candidate_username = serializers.ReadOnlyField(source="candidate.username")

    class Meta:
        model = Resume
        fields = [
            "id", "title", "file", "raw_text", "candidate",
            "candidate_username", "created_at",
        ]
        # raw_text is set automatically by the view from the uploaded file,
        # never sent by the client directly -> read-only.
        read_only_fields = ["candidate", "raw_text", "created_at"]
        extra_kwargs = {
            "file": {"required": True},
        }

    def validate_file(self, value):
        # Restrict uploads to PDF/DOCX only, and cap the size (5 MB) so a
        # huge file can't be used to overload the text-extraction step.
        allowed_extensions = (".pdf", ".docx")
        filename = value.name.lower()
        if not filename.endswith(allowed_extensions):
            raise serializers.ValidationError("Only .pdf or .docx files are allowed.")
        max_size_mb = 5
        if value.size > max_size_mb * 1024 * 1024:
            raise serializers.ValidationError(f"File too large — max {max_size_mb}MB.")
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