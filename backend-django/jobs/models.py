"""
jobs/models.py
---------------
The 3 core tables of the app, defined as Python classes (Django ORM).
Django auto-generates the SQL CREATE TABLE statements for these via
`makemigrations` + `migrate` -> you never hand-write SQL.

Relationships:
  JobPosting  --(1-to-many)-->  belongs to a recruiter (User)
  Resume      --(1-to-many)-->  belongs to a candidate (User)
  MatchResult --(many-to-1)-->  links ONE Resume to ONE JobPosting + AI score
"""
from django.conf import settings
from django.db import models


class JobPosting(models.Model):
    """A job opening created by a recruiter."""
    recruiter = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="job_postings"
    )
    title = models.CharField(max_length=200)
    company = models.CharField(max_length=150)
    description = models.TextField()
    # Comma-separated required skills, e.g. "python,django,postgresql"
    required_skills = models.TextField(help_text="Comma-separated skills")
    location = models.CharField(max_length=120, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]   # newest jobs first, by default

    def __str__(self):
        return f"{self.title} @ {self.company}"


class Resume(models.Model):
    """A resume uploaded/pasted by a candidate."""
    candidate = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="resumes"
    )
    title = models.CharField(max_length=150, help_text="e.g. 'Backend Developer Resume'")
    # For simplicity resumes are stored as plain text (paste or extracted text).
    # A real production version would also store the uploaded PDF file:
    file = models.FileField(upload_to="resumes/", blank=True, null=True)
    raw_text = models.TextField(help_text="Extracted/plain text content of the resume")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} - {self.candidate.username}"


class MatchResult(models.Model):
    """
    Stores the AI-generated match score between one Resume and one
    JobPosting, so we don't need to recompute it every time it's viewed.
    """
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name="matches")
    job = models.ForeignKey(JobPosting, on_delete=models.CASCADE, related_name="matches")
    score = models.FloatField(help_text="0-100 match percentage")
    matched_skills = models.TextField(blank=True)
    missing_skills = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-score"]
        # A candidate shouldn't get two rows for the same resume+job pair
        unique_together = ("resume", "job")

    def __str__(self):
        return f"{self.resume} vs {self.job} = {self.score}%"
