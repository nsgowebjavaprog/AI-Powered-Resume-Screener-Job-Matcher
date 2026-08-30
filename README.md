# SkillMatch AI — Resume Screener & Job Matcher

#### Working of application as following:


![alt text](<Screenshot 2026-08-30 125637.png>) 


![alt text](<Screenshot 2026-08-30 125654.png>) 


![alt text](<Screenshot 2026-08-30 125707.png>) 


![alt text](<Screenshot 2026-08-30 125732.png>) 


![alt text](<Screenshot 2026-08-30 125813.png>)


![alt text](<Screenshot 2026-08-30 125828.png>)



#### Prerequisites:

1. Python 3.11+
2. PostgreSQL 14+
3. Docker Desktop
4. Git

#### Run everything with Docker

```
cd resume-screener
```
```
cp .env.example .env
```
```
docker compose up --build
```
```
docker compose exec django python manage.py createsuperuser
```

1. Frontend: localhost:5500
2. Django API root: localhost:8000/api
3. Django admin: localhost:8000/admin
4. FastAPI: localhost:8001/docs

To stop everything: `docker compose down` 
(add `-v` to also wipe the database volume).

---

#### manually
#### Django backend

```
psql -U postgres -c "CREATE DATABASE resume_screener;"
```

```
cd backend-django
```

```
python3 -m venv venv
```
```
venv\Scripts\activate
```
```
pip install -r requirements.txt
```
```
cp ../.env.example ../.env
```
```
python manage.py makemigrations accounts jobs
```
```
python manage.py migrate
```
```
python manage.py createsuperuser
```
```
python manage.py runserver 8000
```
```
See here:  http://127.0.0.1:8000/admin/
```

#### FastAPI AI microservice
```
cd backend-fastapi
```

```
python3 -m venv venv
```
```
venv\Scripts\activate
```
```
pip install -r requirements.txt
```
```
uvicorn main:app --reload --port 8001
```
```
See Here:  http://127.0.0.1:8001/docs
```

#### Frontend

```
cd frontend
```
```
python3 -m http.server 5500
```
```
See Here: http://localhost:5500/
```
---

1. POST --> `/api/auth/signup/` | No | create account, returns JWT tokens
2. POST --> `/api/auth/login/` | No | log in, returns JWT tokens 
3. POST --> `/api/auth/login/refresh/` | No (needs refresh token) | get a new access token 
4. GET -->  `/api/auth/me/` | Yes | current logged-in user's profile 

5. GET/POST -->              `/api/jobs/` | Yes | list all jobs / create a job (recruiter only) 
6. GET/PUT/PATCH/DELETE -->  `/api/jobs/{id}/` | Yes | manage a single job (owner only for writes) 
7. GET/POST -->              `/api/resumes/` | Yes | list your resumes / create a resume 

8. POST  -->  `/api/resumes/{resume_id}/match/{job_id}/` | Yes | run AI match, calls FastAPI internally
9. GET -->    `/api/match-results/` | Yes | your full match history 
10. POST -->  `/api/match` (FastAPI, port 8001) | No (internal) | raw AI scoring endpoint 

---