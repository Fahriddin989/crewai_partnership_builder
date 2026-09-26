# Iteration 02 — Authentication and permissions

Existing Django REST backend is working and Step 1 verification is COMPLETE.

Make a SMALL PATCH only.
Do not redesign existing models.
Do not build Vue.
Do not modify public organization response fields.

## Goal

Add JWT authentication and basic staff roles.

Use:

djangorestframework-simplejwt

Add endpoints:

POST /api/auth/token/
POST /api/auth/token/refresh/
GET  /api/auth/me/

`/api/auth/me/` must require authentication and return only:

- id
- username
- first_name
- last_name
- email

## Roles

Use Django built-in Groups.

Required groups:

- Partnership Editors
- Partnership Viewers

Create these groups safely, preferably through a Django data migration.

Do NOT create a custom User model.

## Permissions

Public endpoint:

GET /api/public/organizations/

must remain AllowAny.

All other partnership API endpoints must block anonymous users.

Superuser:
- full access

Partnership Editors:
- GET
- POST
- PUT
- PATCH
- DELETE

Partnership Viewers:
- GET only
- no POST
- no PUT
- no PATCH
- no DELETE

Authenticated users who are not superusers and are in neither partnership group:
- no access to internal partnership API

Create a reusable DRF permission class.
Do not duplicate role logic across every ViewSet.

Apply it to:

- organizations
- agreements
- contacts
- agreement-contacts
- documents
- activities

## Documents

Partnership Viewers may view/download documents.

Only Partnership Editors and superusers may create/update/delete document records.

## Tests

Add focused Django tests using Django's test database.

Test at minimum:

1. public organizations endpoint works anonymously
2. anonymous internal API is blocked
3. anonymous /api/auth/me/ is blocked
4. viewer can GET internal API
5. viewer cannot POST
6. editor can GET
7. editor can POST
8. unrelated authenticated user cannot access internal API
9. superuser has full access
10. JWT token endpoint exists

Run these commands SEPARATELY.

Do not chain them with &&.

Run:

python manage.py check

python manage.py makemigrations --noinput

python manage.py migrate --noinput

python manage.py test

python manage.py makemigrations --check --dry-run --noinput

If any command fails, fix only that issue and rerun it.

## Scope guard

Do NOT implement:

- Vue
- custom User model
- password reset
- email verification
- SSO
- finance
- analytics
- contributions
- notifications
- advanced user management UI

Stop immediately when requested tests pass.

Final answer:

CHANGED FILES
CHECKS RUN
REMAINING BLOCKERS
ITERATION STATUS: COMPLETE or INCOMPLETE