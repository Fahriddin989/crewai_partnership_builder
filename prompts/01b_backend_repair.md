# Iteration 01B — repair and lock backend foundation

This is an EXISTING Django backend in `workspace/backend`. The server already starts and `python manage.py check` passes. Do not regenerate the project, do not delete `db.sqlite3`, do not delete existing migrations, and do not build Vue.

Make the smallest safe patch needed to match the original schema. Existing harmless extra fields may stay.

Required minimum fields:

- Organization: name, organization_type, country, website, description, is_public, created_by, updated_by, created_at, updated_at.
- Agreement: organization, title, agreement_type, status, description, signed_date, start_date, expiration_date, created_by, updated_by, created_at, updated_at.
- Contact: full_name, organization(nullable), position, email, phone, notes, created_at, updated_at.
- AgreementContact: agreement, contact, side, role, is_primary. Side choices OUR_SIDE and PARTNER_SIDE.
- Document: agreement, title, document_type, file, description, uploaded_by, uploaded_at. The current implementation may be missing document_type/description; add them safely.
- Activity: agreement, title, activity_date, description, created_by, updated_by, created_at, updated_at. The current implementation may be missing title/updated_by/updated_at; add them safely. Existing activity_type may remain.

Organization type choices must include UNIVERSITY, COMPANY, GOVERNMENT, NGO, OTHER. Agreement types must include MOU, MOA, ACADEMY, PARTNERSHIP, EXCHANGE, NDA, OTHER. Agreement statuses must include DRAFT, ACTIVE, INACTIVE, EXPIRED, UNDER_RENEWAL.

Migration safety: make additive/backward-compatible changes where possible; create a NEW migration; do not rewrite/delete applied migrations; avoid interactive migration prompts by using safe defaults or nullable/blank transitional fields where necessary.

Admin and serializers must reference actual fields after repair.

Internal endpoints must remain authenticated: `/api/organizations/`, `/api/agreements/`, `/api/contacts/`, `/api/agreement-contacts/`, `/api/documents/`, `/api/activities/`.

`GET /api/public/organizations/` must allow anonymous access and expose EXACTLY: id, name, organization_type, country, website. Never expose contacts, documents, internal descriptions, or user information publicly.

Run these checks using commands compatible with the detected OS:
`python manage.py makemigrations`
`python manage.py migrate`
`python manage.py check`
`python manage.py makemigrations --check --dry-run`
Run existing tests if present.

Scope: BACKEND REPAIR ONLY. No Vue, JWT, finance, contributions, analytics, notifications, dashboards, or advanced roles. Stop as soon as checks pass.
