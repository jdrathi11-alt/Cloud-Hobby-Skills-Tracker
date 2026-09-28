# Project Report: Online Hobby & Skills Tracker with Community Sharing on Cloud

## Abstract
The Online Hobby & Skills Tracker is a cloud-oriented web application that combines personal learning management with community sharing. Users create accounts and profiles, maintain skills, define measurable goals, record practice sessions, track milestones and publish achievements. The system demonstrates cloud computing concepts through separation of frontend, REST API, managed database, object storage, authentication, analytics, security, deployment and scalability.

## Introduction
People frequently learn multiple skills but lack a structured place to record practice, measure progress and retain evidence of achievement. The proposed system provides a central account accessible from multiple devices and adds optional community interaction.

## Problem Statement
Traditional notes/spreadsheets are often isolated to one device, have limited analytics, do not provide community interaction and are not designed for scalable media storage. A cloud-backed application can centralize these functions.

## Objectives
1. Provide account and profile management.
2. Track hobbies and skills.
3. Measure goals, milestones and practice.
4. Store achievement evidence.
5. Enable controlled community sharing.
6. Provide progress analytics.
7. Demonstrate cloud database, object storage, authentication, APIs, deployment and security.
8. Produce reproducible GitHub proof of work.

## Existing System
Possible existing approaches include notebooks, spreadsheets and generic social platforms. They either lack automated progress calculations or do not model learning goals and practice sessions as first-class entities.

## Proposed System
A React frontend communicates with a Python REST API. Structured records are stored in relational persistence, while images/files are stored separately in object storage. Authentication identifies users and authorization limits resource access. Analytics are generated from practice and engagement records.

## Industry Relevance
The architecture resembles learning, fitness, portfolio, community and employee-learning systems because these products combine user identity, structured activity, user-generated content, media, engagement and analytics.

## Cloud Computing Concepts
Cloud deployment demonstrates managed services, SaaS delivery, PaaS-style hosting, object storage, database services, stateless APIs, CDN, scalability, monitoring, secrets, backups and CI/CD. IaaS and serverless are documented as advanced alternatives.

## Technology Stack
Local: React/Vite, Flask, SQLAlchemy, SQLite, local filesystem, JWT, pytest. Cloud target: React static/CDN host, hosted Python API, managed PostgreSQL, managed Auth and object storage.

## System Architecture
Users -> CDN/static frontend -> REST API -> managed database/object storage/analytics. Advanced design adds API Gateway, cache, queue, background workers and monitoring.

## Database Design
Users own skills, goals and practice sessions. Goals own milestones. Users create posts, comments, likes and files. Follows model directed social relationships. Unique constraints prevent duplicate likes/follows.

## Cloud Storage Design
Object storage contains profile images, achievement images and attachments. Database metadata stores owner, object key, size, MIME type and visibility. Private objects are delivered using signed URLs in production.

## Authentication and Authorization
The local implementation uses password hashing and expiring JWTs. Production can use managed authentication. Every protected endpoint checks identity and ownership.

## Hobby & Skill Tracking
A skill has category, level, status and dates. This supports both personal progress and community discovery.

## Practice Tracking
Practice sessions record duration, activity, notes, skill and timestamp. Sessions update active goals and feed analytics.

## Goal Management
Goals have targets, current values, units and deadlines. Progress is calculated as current/target * 100, capped at 100. Milestones become achieved when the current value reaches their target.

## Community Sharing
Posts contain text and optional skill/media references. The feed supports recent content, search and category filters. Likes are unique per user/post; comments are owned by users and can be removed by the commenter or post owner.

## Analytics
Dashboard metrics include practice hours, streaks, goals, milestones and engagement. Raw events remain available for recomputation.

## API Design
REST endpoints cover authentication, profiles, skills, practice, goals, posts, social interactions, files and analytics. JSON responses and HTTP status codes communicate results.

## Implementation
The project is divided into frontend, backend routes, domain services, data models, tests, cloud deployment files and documentation. This separation makes the application easier to migrate from local services to managed cloud services.

## Testing
Automated tests cover registration, duplicate registration, skill/goal/practice flow, duplicate likes, unauthorized deletion and user-data isolation. The manual test plan expands coverage to uploads, token expiry, failures and analytics.

## Cloud Deployment
The student deployment can use a static frontend host, hosted Python API and managed database/object storage. The advanced AWS architecture uses S3/CloudFront, Cognito, API Gateway, Lambda/App Runner, RDS/DynamoDB, S3, ElastiCache and CloudWatch.

## Security
Security controls include password hashing, TLS, authorization, validation, environment secrets, object permissions, rate limiting and logging. Production must add stronger managed secrets, malware scanning and content moderation.

## Privacy
Only selected profile information is public. Private email and private file objects are not exposed. Account deletion and retention policies should be documented before real users are introduced.

## Scalability
The system starts as a single API but can become stateless and horizontally scalable. Managed databases, object storage, CDN, cache, pagination, queues and feed-specific indexing provide paths toward larger workloads.

## Results
The completed local system demonstrates the end-to-end learning workflow and community workflow. The cloud architecture demonstrates how those same application components map to managed cloud infrastructure.

## Advantages
Centralized access, measurable progress, community engagement, media storage, analytics and modular architecture.

## Limitations
The included local version uses local storage and local JWT authentication. Production cloud authentication, signed URLs, moderation, rate limiting and advanced observability require provider-specific configuration. Free hosting can have cold starts and quota limits.

## Future Scope
Mobile application, notifications, recommendation engine, calendar integration, richer charts, content moderation, media processing, badges, team learning, search indexing, event-driven analytics and multi-region deployment.

## Conclusion
The project demonstrates that cloud computing is not only about hosting a website. The design separates identity, API logic, durable structured data, binary storage, analytics and delivery so the system can evolve from a local student application into a scalable cloud architecture.
