# Iteration 15 — Local Production-Like Docker Setup

The current Django + Vue application is working locally.

Containerize the CURRENT application for local development/testing in a production-like Docker setup.

IMPORTANT:

This iteration is LOCAL DOCKER ONLY.

DO NOT deploy to VPS.
DO NOT configure GitHub Actions.
DO NOT configure CI/CD.
DO NOT modify server Nginx.
DO NOT create automated tests.
DO NOT run `python manage.py test`.

Inspect the current repository before changing anything.

Preserve all current functionality:
- authentication
- Organizations
- Directions
- Agreements
- Contacts
- Documents
- Activities
- Photo Reports
- Relationship Notes
- Note attachments
- Django Admin

---

# Goal

After this iteration the whole application must start locally with:

docker compose up --build

The browser should open:

http://localhost:8081

Architecture:

Browser
  |
  v
Frontend Nginx container :8081
  |
  +-- /              -> Vue static build
  +-- /api/          -> backend:8000
  +-- /admin/        -> backend:8000
  +-- /static/       -> shared Django static volume
  +-- /media/        -> shared Django media volume
                         |
                         v
                    Django/Gunicorn
                         |
                         v
                    PostgreSQL

Services:

- frontend
- backend
- db

Use Docker Compose.

---

# 1. Backend Dockerfile

Create:

workspace/backend/Dockerfile

Use a stable lightweight Python image compatible with the existing project.

Example family:

python:3.12-slim

Do not use Django runserver inside Docker.

Run Django with Gunicorn.

Use working directory:

/app

Install requirements.

Copy backend source.

Container should expose:

8000

Gunicorn should bind:

0.0.0.0:8000

Use the existing Django WSGI application.

Do not add Celery, Redis or unrelated services.

---

# 2. Backend requirements

Inspect the CURRENT requirements.txt.

Add only production dependencies actually required.

At minimum ensure support for:

- gunicorn
- PostgreSQL driver

Prefer modern psycopg 3 binary package if compatible with the current Django version.

Do not remove current dependencies.

Do not introduce a large settings/configuration framework.

---

# 3. Django settings — environment driven

Update current Django settings minimally so Docker production-like configuration comes from environment variables.

IMPORTANT:

Normal local non-Docker development must remain possible.

Support environment variables for:

DEBUG
SECRET_KEY
ALLOWED_HOSTS

Database:

DB_ENGINE
DB_NAME
DB_USER
DB_PASSWORD
DB_HOST
DB_PORT

When DB_ENGINE indicates PostgreSQL, use PostgreSQL.

Otherwise preserve the existing SQLite behavior for normal local development.

Example logic conceptually:

if DB_ENGINE == "postgres":
    use PostgreSQL
else:
    use existing SQLite

Do not hard-code passwords.

---

# 4. Django static/media

Configure:

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

Keep:

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

The Docker setup must persist media between container rebuilds.

Django uploaded files must NOT disappear after:

docker compose down
docker compose up

Use Docker volumes for:

- media
- staticfiles

Frontend Nginx will serve these shared volumes.

---

# 5. Backend startup

Create a small backend entrypoint script if useful.

On container start it should perform:

python manage.py migrate
python manage.py collectstatic --noinput

Then start Gunicorn.

Keep the script simple and fail on errors.

Do NOT automatically create a superuser.

Do NOT load demo data.

---

# 6. Frontend Dockerfile

Create:

workspace/frontend/Dockerfile

Use a multi-stage build.

Stage 1:
Node image
npm install / npm ci
npm run build

Stage 2:
nginx:alpine

Copy built Vue dist into Nginx HTML directory.

Do NOT run Vite development server in the final container.

Frontend final container should listen on:

80

---

# 7. Frontend production API behavior

The browser must NOT contain URLs such as:

http://127.0.0.1:8000
http://localhost:8000
http://backend:8000

Browser API requests must use same-origin paths:

/api/...

Use the existing Axios client.

Do not create another Axios client.

If the current Axios base URL supports VITE_API_BASE_URL, configure the Docker frontend build so the browser uses same-origin requests.

Preserve normal local Vite development behavior where practical.

---

# 8. Frontend Nginx

Create:

workspace/frontend/nginx.conf

Requirements:

Vue SPA:

location / {
    try_files $uri $uri/ /index.html;
}

Proxy API requests to:

http://backend:8000

Support:

/api/
/admin/

Serve shared Django static:

/static/

Serve shared user uploads:

/media/

Static/media configuration must match the Docker shared volumes.

IMPORTANT:

Large enough upload limit for documents/photo reports/note attachments.

Set a reasonable:

client_max_body_size

For example:

25M

Do not use an unnecessarily huge limit.

Forward standard proxy headers:

Host
X-Real-IP
X-Forwarded-For
X-Forwarded-Proto

---

# 9. Docker Compose

Create at repository root:

docker-compose.yml

Services:

db
backend
frontend

---

## db

Use:

postgres:16-alpine

Environment values must come from `.env.docker`.

Use persistent named volume:

partnership_postgres_data

Do NOT publish PostgreSQL port to the host.

PostgreSQL should be accessible only inside the Docker network.

Add a healthcheck using pg_isready.

---

## backend

Build:

./workspace/backend

Depends on healthy db.

Use `.env.docker`.

Expose internally:

8000

For debugging/local direct access also publish:

127.0.0.1:8001:8000

Do NOT bind backend to 0.0.0.0 on the host.

Mount persistent/shared volumes for:

- media
- staticfiles

Backend must connect to database using:

DB_HOST=db
DB_PORT=5432

---

## frontend

Build:

./workspace/frontend

Publish:

127.0.0.1:8081:80

Depends on backend.

Mount shared volumes read-only where appropriate:

- media
- staticfiles

The application must be reachable at:

http://localhost:8081

---

# 10. Environment file

Create:

.env.docker.example

Include placeholders only.

Example variables:

DEBUG=False
SECRET_KEY=change-me
ALLOWED_HOSTS=localhost,127.0.0.1

DB_ENGINE=postgres
DB_NAME=partnership
DB_USER=partnership
DB_PASSWORD=change-me
DB_HOST=db
DB_PORT=5432

POSTGRES_DB=partnership
POSTGRES_USER=partnership
POSTGRES_PASSWORD=change-me

Do NOT commit real secrets.

Ensure:

.env.docker

is ignored by Git.

If the root .gitignore already exists, extend it instead of creating duplicate ignore logic.

---

# 11. Docker ignore files

Create appropriate `.dockerignore` files.

Backend should exclude things such as:

.venv
__pycache__
*.pyc
db.sqlite3
media
.git

Frontend should exclude:

node_modules
dist
.git

Do not accidentally exclude required source files.

---

# 12. Preserve uploads

Uploaded data must survive container rebuilds.

Use named volumes:

partnership_media
partnership_static
partnership_postgres_data

Do not store important runtime data only inside disposable container layers.

---

# 13. Existing SQLite data

DO NOT delete:

db.sqlite3

DO NOT automatically import SQLite data into PostgreSQL in this iteration.

The Docker PostgreSQL database may initially be empty.

SQLite-to-PostgreSQL data migration will be handled separately after Docker functionality is confirmed.

---

# 14. Django Admin

Django Admin must work through:

http://localhost:8081/admin/

Static admin CSS/JS must load correctly.

Do not require direct access to port 8001 for normal use.

---

# 15. Media

The following must work through frontend Nginx:

organization photos
agreement documents
relationship note attachments

URLs beginning with:

/media/

must load correctly.

---

# 16. Health/restart behavior

Use sensible Compose restart policies:

unless-stopped

for:

db
backend
frontend

Do not add complex orchestration.

---

# 17. Do not add unnecessary infrastructure

DO NOT add:

Redis
Celery
RabbitMQ
Traefik
Caddy
Prometheus
Grafana
Kubernetes
Docker Swarm

The application does not need these currently.

---

# 18. No automated tests

DO NOT:

create tests
modify tests
run tests

Do NOT run:

python manage.py test

---

# 19. Validation

Run only inexpensive checks.

Backend:

python manage.py check

Frontend:

npm run build

Docker:

docker compose config

docker compose build

If Docker is available in the current environment, start the stack:

docker compose up -d

Then inspect:

docker compose ps

If Docker is unavailable to the agent environment, do not claim containers were run.

---

# 20. Existing development workflow

Do not break current normal development commands:

Backend:
python manage.py runserver

Frontend:
npm run dev

Docker is an additional deployment/local-production mode.

---

# 21. Scope guard

DO NOT:

deploy to VPS
change DNS
configure SSL
configure server Nginx
configure CI/CD
create GitHub Actions
push Git
change business functionality
redesign UI
modify Relationship Notes behavior
modify Directions behavior

Only containerize the existing application.

---

# Final response

Return only:

CHANGED FILES

DOCKER ARCHITECTURE

BACKEND DOCKER CHANGES

FRONTEND DOCKER CHANGES

DATABASE CONFIGURATION

PERSISTENT VOLUMES

ENVIRONMENT VARIABLES

COMMANDS RUN

REMAINING BLOCKERS

ITERATION STATUS: COMPLETE or INCOMPLETE