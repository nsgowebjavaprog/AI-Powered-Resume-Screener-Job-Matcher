"""
main.py
-------
FastAPI microservice: a small, focused service that ONLY does AI resume-vs-
job matching. Django calls this over HTTP (see jobs/views.py `match()`).

Why split it out from Django instead of doing it all in one app?
  - Shows a realistic MICROSERVICE architecture (common interview topic).
  - FastAPI's async speed + native Pydantic validation is a great fit for
    a small, fast, stateless "compute" service, while Django stays focused
    on auth, CRUD and the database (the classic "right tool for the job").

Run directly:      uvicorn main:app --reload --port 8001
Interactive docs:  http://localhost:8001/docs   (FastAPI auto-generates this!)
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from matcher import compute_match_score, extract_skill_gaps

app = FastAPI(
    title="AI Resume Matcher Service",
    description="Scores how well a resume matches a job description using NLP.",
    version="1.0.0",
)

# CORS: allow the Django backend AND the frontend (for direct testing) to call this
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # tighten this to specific origins in production
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# PYDANTIC MODELS = request/response VALIDATION (FastAPI's built-in equivalent
# of DRF serializers). FastAPI reads these type hints and automatically:
#   - rejects malformed requests with a clear 422 error
#   - generates the OpenAPI/Swagger docs at /docs
# ---------------------------------------------------------------------------
class MatchRequest(BaseModel):
    resume_text: str = Field(..., min_length=10, description="Full resume text")
    job_description: str = Field(..., min_length=10, description="Full job description")
    required_skills: str = Field("", description="Comma-separated required skills")


class MatchResponse(BaseModel):
    score: float
    matched_skills: list[str]
    missing_skills: list[str]
    verdict: str


@app.get("/")
def root():
    """Simple health-check route so Docker/monitoring can confirm the service is up."""
    return {"status": "ok", "service": "ai-resume-matcher"}


@app.post("/api/match", response_model=MatchResponse)
def match_resume_to_job(payload: MatchRequest):
    """
    POST /api/match
    Body: { "resume_text": "...", "job_description": "...", "required_skills": "python,sql" }

    Pipeline:
      1. validate input (handled automatically by Pydantic before this line runs)
      2. compute a TF-IDF/cosine similarity score
      3. extract which required skills are present/missing via keyword match
      4. return a friendly verdict string
    """
    try:
        score = compute_match_score(payload.resume_text, payload.job_description)
        matched, missing = extract_skill_gaps(payload.resume_text, payload.required_skills)
    except Exception as e:
        # Any unexpected NLP/library error -> clean 500 instead of a raw traceback
        raise HTTPException(status_code=500, detail=f"Matching failed: {e}")

    if score >= 70:
        verdict = "Strong match - go ahead and apply!"
    elif score >= 40:
        verdict = "Moderate match - consider tailoring your resume."
    else:
        verdict = "Low match - this role may need different skills."

    return MatchResponse(score=score, matched_skills=matched, missing_skills=missing, verdict=verdict)
