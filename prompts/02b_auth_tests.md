# Iteration 02B — Authentication and permissions verification

The authentication and permissions implementation already exists.

DO NOT redesign authentication.
DO NOT modify partnership models.
DO NOT build Vue.
DO NOT add new features.

Your primary task is to ADD TESTS and verify the existing implementation.

Use the existing backend in:

workspace/backend

## Existing expected behavior

JWT endpoints:

POST /api/auth/token/
POST /api/auth/token/refresh/
GET /api/auth/me/

Groups:

- Partnership Editors
- Partnership Viewers

Permissions:

### Public
GET /api/public/organizations/
- anonymous access allowed

### Anonymous
All internal partnership APIs:
- denied

/api/auth/me/:
- denied

### Partnership Viewer
- GET internal partnership API: allowed
- POST: denied
- PUT/PATCH/DELETE: denied

### Partnership Editor
- GET: allowed
- POST: allowed
- PUT/PATCH/DELETE: allowed

### Authenticated user with neither group
- internal partnership API: denied

### Superuser
- full access

## Tests

Create real Django automated tests.

Prefer:

partnerships/tests/
    __init__.py
    test_auth_permissions.py

Do not create fake/manual tests.

Test at minimum:

1. public organizations works anonymously
2. anonymous internal organizations is denied
3. anonymous /api/auth/me/ is denied
4. JWT token endpoint returns access and refresh tokens for valid credentials
5. authenticated /api/auth/me/ returns only:
   - id
   - username
   - first_name
   - last_name
   - email
6. Partnership Viewer can GET organizations
7. Partnership Viewer cannot POST organizations
8. Partnership Editor can GET organizations
9. Partnership Editor can POST organizations
10. unrelated authenticated user cannot GET internal organizations
11. superuser can GET and POST
12. public endpoint does not expose internal/private organization fields

Use Django's isolated test database.

Do not depend on existing development database records.

Create users/groups/organizations needed for tests inside setUp / setUpTestData.

## Run separately

python manage.py check

python manage.py test partnerships

python manage.py makemigrations --check --dry-run --noinput

If a test exposes a SMALL implementation bug, fix only that bug and rerun tests.

Do not alter architecture.

Stop once tests pass.

Final output:

CHANGED FILES
TEST COUNT
CHECKS RUN
FIXES MADE
REMAINING BLOCKERS
ITERATION STATUS: COMPLETE or INCOMPLETE