# SkillMatch AI — Resume Screener & Job Matcher

An end-to-end, portfolio-ready project: a **Django REST API** (auth + CRUD),
a **FastAPI microservice** (AI resume-vs-job matching using NLP), a
**PostgreSQL** database, and a plain **HTML/CSS/JS + Three.js** frontend —
all wired together and runnable with **Docker**.

```
resume-screener/
├── backend-django/        # Auth, CRUD, database (Django + DRF)
│   ├── core/               # settings, urls, wsgi/asgi, custom exception handler
│   ├── accounts/            # custom User model, signup/login, JWT
│   ├── jobs/                 # JobPosting, Resume, MatchResult models + API
│   ├── manage.py
│   ├── requirements.txt
│   └── Dockerfile
├── backend-fastapi/        # AI matching microservice
│   ├── main.py               # FastAPI app + pydantic models + endpoints
│   ├── matcher.py            # TF-IDF / cosine-similarity NLP logic
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/               # Plain HTML/CSS/JS, no build step needed
│   ├── index.html            # landing page with Three.js hero
│   ├── login.html / signup.html
│   ├── dashboard.html
│   ├── css/style.css
│   └── js/ (three-bg.js, api.js, auth.js, dashboard.js)
├── docker-compose.yml
├── .env.example
└── .gitignore
```

---

## 1. What this project does (2-minute explanation)

SkillMatch AI is a **two-sided marketplace**: recruiters post jobs, candidates
submit resumes, and an AI service scores how well each resume matches each
job. Concretely:

1. A user **signs up** as either a `candidate` or a `recruiter` and gets a
   **JWT access + refresh token** back (Django + `djangorestframework-simplejwt`).
2. **Recruiters** create job postings (title, company, description, required
   skills) — full **CRUD** via a Django REST Framework `ModelViewSet`, stored
   in **PostgreSQL**.
3. **Candidates** paste in their resume text, which is also saved via CRUD.
4. When a candidate clicks **"Check my match"**, the Django backend calls a
   separate **FastAPI microservice** over HTTP, passing the resume text and
   job description. FastAPI vectorizes both texts with **TF-IDF** and
   computes their **cosine similarity** — a classic, free, offline NLP
   technique — producing a 0–100% match score plus a list of matched/missing
   skills (via keyword comparison against the job's required-skills list).
5. Django stores that result (`MatchResult`) and returns it to the frontend,
   which renders a colored score badge (green/amber/red) and the skill gaps.
6. The whole thing is **containerized** with Docker Compose: one command
   (`docker compose up --build`) starts Postgres, Django, FastAPI, and an
   nginx container serving the static frontend — showing a realistic,
   interview-ready **microservice architecture** (auth/CRUD service +
   compute service + database + reverse-proxied static frontend).

This project intentionally demonstrates a *breadth* of real-world backend
concepts in one place: REST API design, CRUD, ORM models, request
validation, JWT auth, role-based authorization, middleware, custom exception
handling, inter-service HTTP calls, and containerized deployment — all things
interviewers commonly probe for.

---

## 2. Prerequisites (what to install)

Install these BEFORE you start:

| Tool | Why | Check install |
|---|---|---|
| **Python 3.11+** | runs Django & FastAPI | `python3 --version` |
| **PostgreSQL 14+** (or use Docker instead — see below) | the database | `psql --version` |
| **Docker Desktop** (recommended — includes Docker Compose) | run everything with one command | `docker --version` |
| **Git** | version control | `git --version` |
| **A modern browser** | run the frontend (no Node.js needed — it's plain HTML/CSS/JS) | — |
| **VS Code** (optional but recommended) | editing | — |

> You do **not** need to install Node.js — the frontend has zero build step;
> Three.js is loaded straight from a CDN in the browser.

---

## 3. Option A — Run everything with Docker (recommended, easiest)

This is the fastest path and matches exactly how you'd demo it in an interview.

```bash
# 1. Clone / unzip the project, then move into it
cd resume-screener

# 2. Copy the environment template and (optionally) edit values
cp .env.example .env

# 3. Build and start ALL 4 services (Postgres, Django, FastAPI, frontend)
docker compose up --build

# 4. Once you see "Starting development server at http://0.0.0.0:8000/"
#    in the logs, in a NEW terminal, create a Django admin superuser:
docker compose exec django python manage.py createsuperuser
```

Now open:
- **Frontend**: http://localhost:5500
- **Django API root**: http://localhost:8000/api/
- **Django admin**: http://localhost:8000/admin/
- **FastAPI interactive docs (Swagger)**: http://localhost:8001/docs

To stop everything: `docker compose down` (add `-v` to also wipe the database volume).

---

## 4. Option B — Run each service manually (no Docker), step by step

Useful to understand exactly what's happening under the hood, or if you
don't have Docker installed.

### Step 1 — Set up PostgreSQL
```bash
# Using psql, create the database and confirm it exists
psql -U postgres -c "CREATE DATABASE resume_screener;"
```

### Step 2 — Django backend
```bash
cd backend-django

# Create & activate a virtual environment (keeps dependencies isolated)
python3 -m venv venv
venv\Scripts\activate

# Install all Python dependencies listed in requirements.txt
pip install -r requirements.txt

# Copy the env template up one level and edit DB credentials to match
# your local Postgres install (username/password/port)
cp ../.env.example ../.env

# Create the database tables from our models.py files
python manage.py makemigrations accounts jobs
python manage.py migrate

# Create an admin login for the /admin/ panel
python manage.py createsuperuser

# Start the Django dev server on port 8000
python manage.py runserver 8000


See here:  http://127.0.0.1:8000/admin/
```

### Step 3 — FastAPI AI microservice (in a second terminal)
```bash
cd backend-fastapi
python3 -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

# --reload auto-restarts the server whenever you edit the code (dev only)
uvicorn main:app --reload --port 8001

See Here:  http://127.0.0.1:8001/docs
```

### Step 4 — Frontend (in a third terminal)
No install needed — it's static files. Any of these work:
```bash
cd frontend
python3 -m http.server 5500

See Here: http://localhost:5500/
```
Or just double-click `frontend/index.html` to open it directly (note:
some browsers restrict `fetch()` from `file://` pages — the Python
http.server method above is more reliable).

---

## 5. Environment variables (`.env`)

| Variable | Purpose |
|---|---|
| `DJANGO_SECRET_KEY` | signs sessions/tokens — use a long random string in production |
| `DEBUG` | `True` locally, always `False` in production |
| `POSTGRES_DB/USER/PASSWORD/HOST/PORT` | database connection |
| `CORS_ALLOWED_ORIGINS` | which frontend origins may call the API |
| `FASTAPI_MATCH_SERVICE_URL` | where Django finds the AI microservice |

---

## 6. API endpoint reference

| Method | Endpoint | Auth? | Purpose |
|---|---|---|---|
| POST | `/api/auth/signup/` | No | create account, returns JWT tokens |
| POST | `/api/auth/login/` | No | log in, returns JWT tokens |
| POST | `/api/auth/login/refresh/` | No (needs refresh token) | get a new access token |
| GET | `/api/auth/me/` | Yes | current logged-in user's profile |
| GET/POST | `/api/jobs/` | Yes | list all jobs / create a job (recruiter only) |
| GET/PUT/PATCH/DELETE | `/api/jobs/{id}/` | Yes | manage a single job (owner only for writes) |
| GET/POST | `/api/resumes/` | Yes | list your resumes / create a resume |
| POST | `/api/resumes/{resume_id}/match/{job_id}/` | Yes | run AI match, calls FastAPI internally |
| GET | `/api/match-results/` | Yes | your full match history |
| POST | `/api/match` (FastAPI, port 8001) | No (internal) | raw AI scoring endpoint |

---

## 7. Why this stack (interview talking points)

- **Django** — chosen for auth, CRUD, and the admin panel: batteries-included,
  fast to build a secure, well-structured REST API with an ORM instead of
  hand-writing SQL.
- **FastAPI** — chosen for the AI microservice specifically because of its
  native Pydantic validation, automatic OpenAPI docs, and async performance
  for a small, focused compute endpoint — demonstrating you can pick the
  right tool for each job instead of forcing one framework to do everything.
- **PostgreSQL** — a production-grade relational database with strong support
  for structured data and foreign-key relationships (User → JobPosting →
  Resume → MatchResult).
- **TF-IDF/cosine similarity** — a genuinely free, offline, well-understood
  NLP technique (no API keys, no rate limits, no cost) that's easy to explain
  and defend in an interview, with a clear upgrade path to a real LLM API later.
- **Docker Compose** — shows you can containerize a multi-service system,
  a core DevOps skill interviewers look for.
