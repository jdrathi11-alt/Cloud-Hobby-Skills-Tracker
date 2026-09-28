# Interview Preparation — 10 Questions and Strong Answers

## 1. Explain your project.
I built an Online Hobby & Skills Tracker with Community Sharing on Cloud. Users register, maintain profiles, add skills, set measurable goals, log practice sessions, reach milestones and optionally publish achievements to a community feed. I separated the React frontend from a Python REST API, relational data from binary file storage, and analytics from the transactional records. I first implemented a local SQLite/filesystem mode for repeatable testing, then designed the cloud version around managed PostgreSQL, object storage, hosted compute and static/CDN frontend hosting. I also added authorization checks, duplicate-like prevention, upload validation and automated API tests.

## 2. Why did you use a cloud database instead of storing everything in the frontend?
The frontend is not a trusted or durable system of record. A cloud database centralizes structured data, supports concurrent users, enforces relationships and constraints, and lets the same account access data from multiple devices. The API controls what each user is allowed to read or modify.

## 3. Why object storage for images instead of the database?
Images and other binary files are better suited to object storage because it is designed for large blobs, high durability and scalable delivery. The relational database stores metadata such as owner, content type and object key. This keeps transactional queries small and allows CDN/signed-URL delivery later.

## 4. How does authentication differ from authorization?
Authentication answers “who are you?” Authorization answers “what are you allowed to do?” A valid JWT authenticates a user. Before updating a skill, deleting a post or reading a private file, the API checks that the authenticated user's ID owns that resource or has an appropriate role.

## 5. How do your REST APIs work?
The React client sends HTTP requests such as POST for creating a practice session, GET for reading skills/feed, PUT for updates and DELETE for deletion. The API validates input, authenticates the caller, performs business logic, commits database changes and returns JSON plus an appropriate status code. Errors use a consistent JSON error shape.

## 6. How would you scale the community feed?
I would add cursor pagination and indexes first. At higher traffic I would avoid scanning all posts and use a feed strategy. Fan-out on read queries posts when the feed is opened and is simpler for normal users. Fan-out on write prepares feed entries when a post is created and makes reads faster but can create expensive writes for users with huge follower counts. A hybrid approach can handle both cases, with queues/workers for asynchronous fan-out.

## 7. How are analytics calculated?
Raw practice sessions are the source of truth. Total, weekly and monthly hours are sums of durations. Most-practiced skill is the maximum aggregated duration by skill. Streaks use unique practice dates and consecutive calendar-day comparisons. Goal progress is current divided by target and capped at 100%. For larger scale I would pre-aggregate daily summaries or use background jobs.

## 8. What security controls did you implement?
Passwords are hashed; secrets are environment variables; API endpoints require authentication where appropriate; user-owned resources are checked by user ID; likes have a database uniqueness constraint; uploads validate type and size; private files require ownership; and community content is treated as untrusted input. Production deployment should add HTTPS, managed secrets, rate limiting, malware scanning, stronger token/session management, audit logs and RLS where supported.

## 9. What happens when an image upload succeeds but the database write fails?
That creates an orphan object. I would design the production upload flow so object creation and metadata creation have an explicit state, or perform cleanup after a failed transaction. A background reconciliation job can detect orphaned objects. Conversely, if the database record exists but the object upload fails, the record should remain in a failed/pending state or be rolled back, depending on the operation.

## 10. Why did you build a local version before cloud deployment?
It made the application reproducible and reduced cloud debugging variables. I could demonstrate the complete business workflow without paid services, run automated tests locally, and then replace infrastructure adapters with managed services. That also helped me understand which parts are application logic and which parts are cloud infrastructure.
