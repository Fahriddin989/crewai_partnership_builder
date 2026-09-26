# Iteration 02 — authentication and basic staff permissions

Run ONLY after Iteration 01B verification reports STATUS: COMPLETE.

Add SimpleJWT for the future Vue SPA. Endpoints: POST `/api/auth/token/`, POST `/api/auth/token/refresh/`, GET `/api/auth/me/`.

Use Django Groups, not a complex custom role model:
- Partnership Editors: full CRUD for partnership data/documents/activities/contacts.
- Partnership Viewers: authenticated read-only internal access, including document viewing/downloading.
- Superusers: full access.

Use a reusable DRF permission class. Do not hard-code usernames.

Public `GET /api/public/organizations/` remains anonymous and unchanged. Anonymous users remain blocked from internal APIs.

Manage users/groups initially through Django Admin; no custom user-management UI yet.

Add focused tests for anonymous/public/viewer/editor permissions. Run `python manage.py check`, `python manage.py test`, and `python manage.py makemigrations --check --dry-run`.

No Vue or unrelated features in this iteration.
