# Online Hobby & Skills Tracker with Community Sharing on Cloud

A cloud-oriented full-stack student project for tracking hobbies/skills, practice sessions, goals, milestones and achievements while demonstrating authentication, REST APIs, managed databases, object storage, analytics, security, scalability and CI/CD concepts.

## Overview
Users create profiles, add skills, set measurable goals, log practice, reach milestones, upload achievement evidence and share posts with a community feed. The local version runs with Flask + SQLite + local object storage. The cloud architecture moves persistence to managed PostgreSQL/object storage and compute to a hosted Python service, with a React frontend on a static/CDN platform.

## Why cloud?
A central cloud data layer lets the same account be accessed from multiple devices. Managed databases provide durable structured storage; object storage handles large binary files; hosted APIs expose business logic; authentication and authorization protect user-specific data; analytics aggregate activity into useful progress indicators.

## Features
- Registration/login/logout token flow
- User profile and public profile
- Skill/hobby CRUD
- Goals and milestones
- Practice-session logging
- Progress percentage and automatic goal updates
- Current/longest streak analytics
- Community posts
- Likes with duplicate prevention
- Comments with ownership checks
- Optional follow/unfollow API
- Search/filterable feed API
- File upload/download/delete with validation
- Dashboard analytics
- Automated API tests
- Docker/local simulation

## Architecture
```text
Browser / Mobile browser
        |
       HTTPS
        v
React static frontend / CDN
        |
        v
REST API (Flask/FastAPI equivalent)
        |
  +-----+---------+----------------+
  |               |                |
  v               v                v
Managed DB    Object Storage    Analytics
(Postgres)    (images/files)   (SQL/service)
  |
  +--> users, skills, goals, practice, posts, likes, comments
```

Advanced target architecture:
```text
Users -> CDN -> React -> API Gateway -> Flask/FastAPI/Lambda
                                  |-> Managed PostgreSQL
                                  |-> Object Storage + signed URLs
                                  |-> Cache (optional)
                                  |-> Queue/worker (optional)
                                  |-> Logs/metrics/alerts
```

## Technology stack
### Local
React + Vite, Flask, SQLAlchemy, SQLite, local filesystem, JWT, pytest.

### Recommended cloud
React on Vercel or another static/CDN host; Flask/FastAPI on Render or equivalent; Supabase PostgreSQL + Auth + Storage, or another managed database/object-storage/auth provider. See `docs/PROJECT_GUIDE.md`.

## Repository layout
- `frontend/` React UI
- `backend/` Flask REST API and domain services
- `tests/` automated tests
- `cloud/` deployment templates and cloud migration notes
- `analytics/` analytics design notes
- `docs/` complete architecture/deployment/project guide
- `reports/` academic project report
- `sample_data/` synthetic examples
- `screenshots/` evidence checklist

## Local installation
### Backend
```bash
cd backend
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
copy .env.example .env  # Windows
# cp .env.example .env # macOS/Linux
python run.py
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```
Open `http://localhost:5173`.

### Tests
```bash
pytest -q
```

### Docker
```bash
docker compose up --build
```

## Environment variables
Never commit secrets. See `backend/.env.example`.

## Cloud deployment
See `docs/PROJECT_GUIDE.md` for the current student-friendly route and AWS/Azure/GCP equivalents.

## API
Main endpoints:
- `POST /api/register`
- `POST /api/login`
- `GET/PUT /api/profile`
- `POST/GET /api/skills`
- `PUT/DELETE /api/skills/{id}`
- `POST/GET /api/practice`
- `POST/GET/PUT /api/goals...`
- `POST /api/posts`
- `GET /api/feed`
- `POST/DELETE /api/posts/{id}/like`
- `POST/GET /api/posts/{id}/comments`
- `POST/DELETE /api/users/{id}/follow`
- `POST/DELETE /api/files/upload...`
- `GET /api/analytics/dashboard`

## Security
Password hashes use Werkzeug; API access uses expiring JWTs; ownership checks prevent cross-user writes; uploads have MIME/type and size validation; secrets come from environment variables. Production should add HTTPS, stronger JWT key management, rate limiting, CSRF strategy where cookie auth is used, malware scanning, content moderation and signed object URLs.

## Scalability
At small scale a single API instance is sufficient. At larger scale, use stateless horizontally scaled API instances, managed PostgreSQL with indexes/read replicas where justified, object storage + CDN, pagination, caching, asynchronous workers and feed fan-out strategies.

## Testing
The included tests cover registration, duplicate registration, skills/goals/practice, likes, unauthorized deletion and user-data isolation. Expand the matrix in `docs/PROJECT_GUIDE.md` before submission.

## Screenshots
See `screenshots/SCREENSHOT_CHECKLIST.md` for professional evidence names and what each proves.

## Academic report
See `reports/project_report.md`.

## Interview preparation
See `docs/INTERVIEW_QA.md`.

## License
For academic/demo use. Add your preferred open-source license before public release.
