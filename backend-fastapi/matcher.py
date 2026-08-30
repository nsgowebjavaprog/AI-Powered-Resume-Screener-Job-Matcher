"""
matcher.py
----------
This is the "AI" brain of the project.

APPROACH: TF-IDF vectorization + cosine similarity (classic NLP technique,
100% FREE and runs OFFLINE - no paid API key / rate limits / internet
needed, which makes the whole project easy to demo in an interview).

  1. TF-IDF (Term Frequency - Inverse Document Frequency) turns text into
     a vector of numbers, where words that are common across ALL documents
     (like "the", "and") get a LOW weight, and words that are distinctive
     to a specific document (like "kubernetes", "postgresql") get a HIGH
     weight.
  2. Cosine similarity then measures the ANGLE between the resume vector
     and the job-description vector: 1.0 = identical direction (great
     match), 0.0 = completely unrelated.

OPTIONAL UPGRADE (mentioned for the interview): this function could be
swapped to call a free-tier LLM API (e.g. Hugging Face Inference API,
Groq free tier, or Google Gemini free tier) for smarter semantic
similarity instead of TF-IDF -> same interface, easy to plug in later.
"""
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def compute_match_score(resume_text: str, job_description: str) -> float:
    """
    Returns a 0-100 similarity score between a resume and a job description.
    """
    documents = [resume_text, job_description]

    # stop_words="english" removes filler words ("the","is","and"...) before scoring
    vectorizer = TfidfVectorizer(stop_words="english")
    tfidf_matrix = vectorizer.fit_transform(documents)

    # cosine_similarity returns a 2x2 matrix; [0][1] = similarity between doc0 and doc1
    similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]

    # Convert 0.0-1.0 similarity into a friendlier 0-100 percentage
    return round(float(similarity) * 100, 2)


def extract_skill_gaps(resume_text: str, required_skills: str):
    """
    Simple keyword-matching to tell the candidate exactly WHICH required
    skills were found in their resume, and which are missing.
    `required_skills` is a comma-separated string, e.g. "python,django,sql"
    """
    resume_lower = resume_text.lower()
    skills = [s.strip().lower() for s in required_skills.split(",") if s.strip()]

    matched = [s for s in skills if s in resume_lower]
    missing = [s for s in skills if s not in resume_lower]
    return matched, missing
