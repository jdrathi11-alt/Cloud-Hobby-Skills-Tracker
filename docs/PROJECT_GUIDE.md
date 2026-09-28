# Complete Project Guide

## 1. Project explanation
### Simple explanation
Online Hobby & Skills Tracker is a personal learning tracker plus a small community. A user records what they are learning, how much they practise, the goals they want to achieve and evidence of achievements. The cloud stores structured records centrally and stores images/files separately in object storage. A community feed lets users publish selected achievements.

### Technical explanation
The browser is the presentation layer. It authenticates the user, calls REST endpoints over HTTPS and renders dashboard/community views. The API validates requests, authenticates the caller, checks resource ownership, applies business rules and writes structured data to a relational database. Binary files are stored in object storage; the database stores object metadata and references. Analytics are calculated from practice, goal and engagement records.

### Workflow
```text
User -> Register/Login -> Auth token -> Create Skill -> Goal -> Practice -> DB
                                              |             |
                                              +-> progress <-+
Practice/Achievement -> upload -> Object Storage -> file metadata in DB
Selected achievement -> Post -> Feed -> Likes/Comments -> Analytics
```

## 2. Industry relevance
The same separation of concerns appears in learning platforms, fitness trackers, LMS/EdTech products, professional learning systems, portfolio applications and community/creator products: identity, user-owned structured data, binary media, APIs, engagement and analytics are separate concerns. Business value comes from centralized data, cross-device access, scalable storage, user-generated content, progress visibility and personalized experiences.

## 3. Cloud concepts mapped to this project
| Concept | Where demonstrated |
|---|---|
| Cloud computing | Hosted frontend/API/database/storage |
| SaaS | End users consume the tracker through a browser |
| PaaS | Managed application hosting/database/storage |
| IaaS | Conceptual AWS EC2/VPC option; not required in student deployment |
| Cloud database | Supabase PostgreSQL / managed PostgreSQL |
| Object storage | Supabase Storage/S3-style bucket |
| Authentication | Local JWT in simulation; managed Auth in cloud target |
| Authorization | Ownership checks and production RLS policies |
| REST API | Flask `/api/*` endpoints |
| Client-server | React client calls Python API |
| Serverless | Optional Lambda/Functions advanced architecture |
| Event-driven | Optional queue for media processing/notifications |
| Scalability | Stateless API, managed DB, object storage, CDN |
| Elasticity | Increase/decrease compute instances or serverless invocations |
| Availability | Managed services, health endpoint, backups; multi-zone is advanced |
| CDN | Static frontend and media distribution |
| Load balancing | Advanced multi-instance deployment |
| API Gateway | Advanced cloud architecture |
| Caching | Optional Redis/managed key-value cache |
| Environment variables | `.env` / cloud environment configuration |
| Secrets management | Production secret store, never Git |
| Logging | Flask/application logs + cloud logs |
| Monitoring | Health checks, request/error metrics, alerts |
| Backup | Managed DB backups/export; object versioning where available |
| CI/CD | GitHub -> host automatic deploy; add GitHub Actions tests |
| Cloud deployment | Render/Vercel/Supabase or AWS/Azure/GCP |

## 4. Implementation options
### A — Beginner local
HTML/CSS/JS + Flask + SQLite + local uploads. Lowest setup complexity. Excellent for understanding APIs, database relationships and local cloud simulation, but it is not persistent cloud infrastructure.

### B — Recommended student cloud
React + Flask/FastAPI + managed PostgreSQL + managed Auth + object storage + static frontend host + hosted API. This provides the clearest cloud-computing proof without requiring a complex Kubernetes/IaaS setup. Current Supabase free usage includes 500 MB database size, 1 GB storage and 50,000 monthly active users; limits can change, so verify the provider dashboard before deployment. citeturn0search8 Vercel's Hobby plan is listed at $0/month and includes automated CDN/CI features for eligible personal projects. citeturn0search3 Render provides free Python web services, but its free web-service filesystem is ephemeral, so uploads/SQLite should not be treated as durable storage there. citeturn0search0

### C — Advanced enterprise-style
React/Next.js + API Gateway + Lambda/App Runner/containers + managed relational/NoSQL database + S3 + CloudFront + Cognito + cache + CloudWatch. Highest learning value for architecture, but more setup and more opportunities for billing/configuration mistakes.

### Recommendation
For a student, build A completely, then deploy B. Document C as the scale-out architecture. This creates evidence of both implementation and architectural understanding.

## 5. Data model
```text
USERS 1----N SKILLS 1----N GOALS 1----N MILESTONES
  |             |
  |             +----N PRACTICE_SESSIONS
  |
  +----N POSTS 1----N COMMENTS
  |          |
  |          +----N LIKES
  |
  +----N FILES
  |
  +----N FOLLOWS (follower_id -> followed_id)
```
Primary keys are numeric locally; production can use UUIDs. Foreign keys enforce relationships. Important indexes: user_id, skill_id, post created_at, username/email, category, follow pairs and unique `(post_id,user_id)` for likes. Query patterns should drive indexes rather than indexing every field.

### Relational vs NoSQL
Relational PostgreSQL is a natural fit because goals, sessions, skills, likes and comments have clear relationships and require constraints. Firestore/DynamoDB can work when access patterns are known and denormalization is acceptable. A community feed often requires deliberate indexing/denormalization either way.

## 6. Goals, milestones and progress
`progress = min(100, current_value / target_value * 100)`. For a 30-hour goal with 18 hours completed, the display is 60%.

Every practice session for a skill adds `duration_minutes / 60` to active goals for that skill. A milestone becomes achieved when the goal's current value reaches its target; record `achieved_at` once. In production, put this update in a transaction so practice and goal update succeed/fail together.

## 7. Practice streak algorithm
Convert practice timestamps to calendar dates. Remove duplicates so multiple sessions on one day count as one active day. Sort dates descending. The current streak counts consecutive calendar days ending today. A product can alternatively define “active through yesterday” as valid; document the rule. The longest streak scans consecutive date pairs. Time zones should be normalized carefully in production; this demo uses UTC timestamps and UTC calendar days.

## 8. Object storage
Database: file ID, owner, original filename, content type, size, visibility, object key. Object store: bytes. Suggested keys:
```text
users/{user_id}/profile/{uuid}.jpg
users/{user_id}/skills/{skill_id}/{uuid}.jpg
users/{user_id}/posts/{post_id}/{uuid}.jpg
```
Private objects should be served through short-lived signed URLs. Public assets can use a CDN URL. Never expose a bucket's service-role/admin key to the browser.

## 9. Community sharing
A post references an author and optionally a skill. Likes use a unique composite constraint to prevent duplicate rows. Comments reference both post and author. Deletion checks owner/admin permissions. Feed APIs use pagination rather than returning every post. Search filters content/username/skill; at larger scale use database full-text search or a search service.

### Follow feed scaling
Fan-out on read: store one post and query followed users when a user opens the feed. Simple and storage-efficient, but expensive for users following many accounts.

Fan-out on write: when a user publishes, copy/queue references into followers' feed indexes. Read becomes fast, but writes can become expensive for celebrity-scale accounts. A hybrid strategy is common.

## 10. REST API contract
| Method | Endpoint | Purpose | Auth | Common status |
|---|---|---|---|---|
| POST | `/api/register` | Create account | No | 201, 400, 409 |
| POST | `/api/login` | Issue token | No | 200, 401 |
| POST | `/api/logout` | Client token discard | Token optional | 200 |
| GET/PUT | `/api/profile` | Own profile | Yes | 200, 401 |
| POST/GET | `/api/skills` | Create/list own skills | Yes | 201/200 |
| GET/PUT/DELETE | `/api/skills/{id}` | Own skill | Yes | 200/404 |
| POST/GET | `/api/practice` | Practice log/list | Yes | 201/200 |
| GET | `/api/skills/{id}/practice` | Skill practice | Yes | 200/404 |
| POST/GET | `/api/goals` | Goal create/list | Yes | 201/200 |
| PUT | `/api/goals/{id}` | Update goal | Yes | 200/404 |
| POST | `/api/posts` | Publish | Yes | 201 |
| GET | `/api/feed` | Community feed | No | 200 |
| DELETE | `/api/posts/{id}` | Delete own post | Yes | 200/404 |
| POST/DELETE | `/api/posts/{id}/like` | Like/unlike | Yes | 200 |
| GET/POST | `/api/posts/{id}/comments` | Read/add comments | GET no, POST yes | 200/201 |
| DELETE | `/api/comments/{id}` | Owner/post-owner delete | Yes | 200/403 |
| POST/DELETE | `/api/users/{id}/follow` | Follow/unfollow | Yes | 200 |
| POST | `/api/files/upload` | Upload | Yes | 201/400 |
| GET/DELETE | `/api/files/{id}` | Retrieve/delete | Yes | 200/403 |
| GET | `/api/analytics/dashboard` | Dashboard metrics | Yes | 200 |

All API errors should return JSON such as `{"error":"message"}`. Production should add request IDs, structured logs and consistent error schemas.

## 11. Local simulation — exact flow
```bash
# Terminal 1
cd backend
python -m venv .venv
# activate it
pip install -r requirements.txt
cp .env.example .env
python run.py

# Terminal 2
cd frontend
npm install
npm run dev

# Terminal 3
pytest -q
```
Expected health response: `{"service":"cloud-hobby-skills-tracker","status":"ok"}` from `GET http://localhost:5000/health`.

Manual scenario:
1. Create User A.
2. Add Photography.
3. Create a 20-hour goal with milestones 5/10/20.
4. Log 60 minutes.
5. Dashboard should show 1.0 total practice hour and 5% goal progress.
6. Publish an achievement post.
7. Create User B in a second browser/private window.
8. User B opens feed, likes the post and comments.
9. User A refreshes community and analytics.
10. Confirm User B cannot see User A's private skills through `/api/skills` and cannot delete User A's post.

For a real file upload, use the UI extension or API `multipart/form-data` request to `/api/files/upload`; allowed demo types are JPEG/PNG/WebP/PDF and the configured max is 5 MB.

## 12. Cloud deployment — recommended student route
### Frontend
Build React with `npm run build`. Deploy `frontend/dist` to Vercel or a static host. Set `VITE_API_URL` to the deployed API URL.

### Backend
Deploy the `backend` service to a Python host such as Render. Set `DATABASE_URL`, `SECRET_KEY`, `JWT_SECRET` and `FRONTEND_ORIGIN` as environment variables. Render's free web services can be used for testing/academic prototypes, but they spin down after inactivity and their local filesystem is ephemeral. citeturn0search0

### Database/storage/auth
Use a managed PostgreSQL provider and managed object storage. Supabase's current free plan lists 500 MB database, 1 GB storage and 50,000 MAU; confirm current quotas before submission. citeturn0search8 For the strongest cloud-auth story, use Supabase Auth in production and either validate its JWTs in the API or use the database's row-level security for direct client data access. Keep local JWT mode for offline demonstration.

### Cloud object storage
Create a private bucket for achievements. Store only the object key in PostgreSQL. Generate signed URLs on the server. Add bucket policies so a user can read/delete only their own private objects.

## 13. AWS/Azure/GCP mapping
| Capability | AWS | Azure | GCP |
|---|---|---|---|
| Frontend/CDN | S3 + CloudFront | Blob Storage + CDN | Cloud Storage + Cloud CDN |
| Auth | Cognito | Entra External ID/B2C-style customer identity | Identity Platform/Firebase Auth |
| API | API Gateway | API Management | API Gateway |
| Compute | Lambda/ECS/App Runner | Functions/App Service/Container Apps | Cloud Run/Cloud Functions |
| SQL | RDS/Aurora | Azure Database for PostgreSQL | Cloud SQL |
| NoSQL | DynamoDB | Cosmos DB | Firestore |
| Object storage | S3 | Blob Storage | Cloud Storage |
| Cache | ElastiCache | Azure Cache for Redis | Memorystore |
| Logs | CloudWatch | Azure Monitor | Cloud Logging |

## 14. Security
Authentication proves identity; authorization proves whether that identity may access a resource. Passwords are hashed, not encrypted for reversible recovery. Use HTTPS/TLS in deployment. Encrypt databases and object storage at rest. Validate file MIME/type, extension and size; ideally scan uploads for malware. Escape/encode rendered user content to reduce XSS risk. Parameterized SQL/ORM protects against injection. Add rate limiting to login, comments, uploads and post creation. Use environment variables and cloud secret managers. Do not log passwords, raw tokens or private URLs. Use backups and test restoration.

Community content creates extra risk: spam, malicious files, abusive text, impersonation, privacy leakage and denial-of-service attempts. Add reporting, blocking, moderation, quotas, file scanning and audit logs before calling the system production-ready.

## 15. Privacy/moderation
Public profile: username, display name, bio and selected interests. Private profile: email and private settings. Users choose whether an achievement is shared. Account deletion should remove or anonymize owned data according to the product's retention policy. Public APIs should never return password hashes, private email, private object keys or internal tokens.

## 16. Scalability
### 10 users
Single API, managed DB, object storage, simple feed query.

### 1,000 users
Add pagination, indexes, rate limits, CDN/static hosting and better observability. Keep API stateless so a second instance can be added.

### 100,000 users
Use managed DB sizing/read replicas as required, cache hot data, background jobs for analytics/media, object storage + CDN, stronger search, connection pooling and queue-based asynchronous work.

### 1,000,000 posts
Never scan all posts. Use indexed `created_at`, category/skill indexes, cursor pagination and feed-specific storage/indexes. Consider fan-out on write/hybrid feeds and asynchronous counters.

## 17. Failure handling
- DB failure: timeout, return friendly 503, log correlation ID, retry only safe/idempotent operations.
- Upload failure: do not create the DB metadata row until upload succeeds; if DB fails after upload, delete the orphan object asynchronously.
- DB succeeds but upload fails: transactionally keep post without media or mark media state as failed.
- Token expiry: return 401; frontend prompts re-authentication/refreshes managed token.
- Network drop: show retryable UI and avoid blindly duplicating writes.
- Duplicate requests: idempotency keys for critical operations; unique constraints for likes/follows.
- Backend unavailable: health checks, retry with backoff, static frontend remains accessible.

## 18. Analytics
Metrics: total/weekly/monthly hours, most-practiced skill, current/longest streak, completed/active goals, milestones, posts, likes and comments. For production, pre-aggregate expensive metrics with scheduled/background jobs and store daily summaries if raw-session queries become costly.

## 19. Testing matrix
| ID | Scenario | Input | Expected |
|---|---|---|---|
| T01 | Registration | Valid unique user | 201 + token |
| T02 | Duplicate registration | Same email | 409 |
| T03 | Login | Correct password | 200 + token |
| T04 | Invalid login | Wrong password | 401 |
| T05 | Profile update | New bio | 200 |
| T06 | Add skill | Valid skill | 201 |
| T07 | Update skill | Valid owner | 200 |
| T08 | Delete skill | Valid owner | 200 |
| T09 | Create goal | Existing owned skill | 201 |
| T10 | Practice | 60 min | Goal increments by 1 hour |
| T11 | Progress | 18/30 hours | 60% |
| T12 | Milestone | Reach target | achieved=true |
| T13 | File upload | PNG under limit | 201 |
| T14 | Invalid file | unsupported type | 400 |
| T15 | Post | Text | 201 |
| T16 | Feed | GET | Post visible |
| T17 | Like | First like | 200 |
| T18 | Duplicate like | Same user again | no duplicate row |
| T19 | Unlike | Existing like | removed |
| T20 | Comment | Valid text | 201 |
| T21 | Unauthorized delete | Other user | 403/404 |
| T22 | Analytics | Sessions | Correct aggregates |
| T23 | Isolation | User B requests skills | User A data absent |
| T24 | Storage failure | Simulated exception | No misleading success |
| T25 | DB failure | Simulated outage | Friendly 5xx |
| T26 | Token expiry | Expired JWT | 401 |
| T27 | Logout | Client discard | Token no longer sent |

Run automated tests with `pytest -q`.

## 20. GitHub strategy
```bash
git init
git add .
git commit -m "Initialize cloud hobby and skills tracker"
git branch -M main
git remote add origin <repository-url>
git push -u origin main
```
Recommended sequence:
```text
Create cloud application architecture
Implement user authentication
Add user profile management
Implement hobby and skill tracking
Add practice session tracking
Implement goals and milestones
Integrate cloud database
Add cloud object storage
Build community sharing module
Implement likes and comments
Add progress analytics dashboard
Add cloud security controls
Add automated tests
Deploy application to cloud
Complete README and documentation
```

## 21. 14-day proof-of-work plan
| Day | Deliverable | Suggested commit | Screenshot proof |
|---|---|---|---|
| 1 | Architecture + repo | Create cloud application architecture | architecture diagram |
| 2 | Auth | Implement user authentication | registration/login |
| 3 | Profile | Add user profile management | profile page |
| 4 | Skills | Implement hobby and skill tracking | skill dashboard |
| 5 | Practice | Add practice session tracking | practice form |
| 6 | Goals | Implement goals and milestones | progress/milestone |
| 7 | DB | Integrate cloud database | DB tables/console |
| 8 | Storage | Add cloud object storage | bucket/object |
| 9 | Posts | Build community sharing module | post composer |
| 10 | Engagement | Implement likes and comments | interaction |
| 11 | Analytics | Add progress analytics dashboard | charts |
| 12 | Security/tests | Add cloud security controls + automated tests | pytest + security config |
| 13 | Deploy | Deploy application to cloud | live URL/dashboard |
| 14 | Docs | Complete README and documentation | README + architecture |

## 22. Screenshot checklist
Use these filenames:
1. `01-repository-structure.png`
2. `02-cloud-architecture.png`
3. `03-registration.png`
4. `04-login.png`
5. `05-profile.png`
6. `06-add-skill.png`
7. `07-skills-dashboard.png`
8. `08-goal-creation.png`
9. `09-practice-entry.png`
10. `10-progress-calculation.png`
11. `11-milestone-achieved.png`
12. `12-analytics-dashboard.png`
13. `13-cloud-database.png`
14. `14-storage-console.png`
15. `15-achievement-image.png`
16. `16-create-post.png`
17. `17-community-feed.png`
18. `18-like-interaction.png`
19. `19-comment-interaction.png`
20. `20-second-user.png`
21. `21-data-isolation.png`
22. `22-rest-api-response.png`
23. `23-automated-tests.png`
24. `24-cloud-deployment.png`
25. `25-live-application.png`
26. `26-github-history.png`
27. `27-github-repository.png`
28. `28-readme-preview.png`

Each screenshot should show one concrete feature and, where possible, the URL/environment or test result that proves the cloud concept.

## 23. Resume/LinkedIn proof
Resume bullets:
- Built and deployed a cloud-oriented full-stack hobby/skills tracker using React, Python Flask, REST APIs, relational data modeling, JWT authentication, object-storage integration and progress analytics.
- Designed user-isolated skill, goal, practice, milestone and community entities with ownership authorization, duplicate-like prevention, pagination and automated API tests.
- Documented a scalable cloud architecture using managed PostgreSQL, object storage, CDN/static hosting, stateless APIs, logging, secrets and CI/CD concepts.

Two-line description:
`Cloud-based hobby and skills tracker with goals, practice analytics, milestones and community sharing. Demonstrates REST APIs, authentication/authorization, relational cloud data, object storage, deployment, security, testing and scalability.`

LinkedIn description:
`Developed an industry-oriented cloud computing project that combines personal skill tracking with community sharing. The system separates frontend, REST API, relational persistence, object storage and analytics, with a local simulation and a managed-cloud deployment path. Key engineering work includes authentication, authorization, progress/streak calculations, user-generated content, file validation, scalable feed design and automated tests.`

Technical skills: Python, Flask/FastAPI concepts, React, REST, SQL, PostgreSQL, SQLite, JWT, object storage, cloud deployment, Git/GitHub, Docker, pytest, API security, analytics, scalability.
