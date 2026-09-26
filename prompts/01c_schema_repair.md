# Iteration 01C — Focused schema repair

This is an EXISTING Django REST Framework backend.

Do NOT regenerate the project.
Do NOT rewrite unrelated files.
Do NOT build frontend.
Do NOT redesign the architecture.

The backend is already running successfully with:

python manage.py runserver

and:

python manage.py check

currently passes.

We have already run deterministic verification and found ONLY these schema/migration problems.

## Required fixes

### 1. Document model

The Document model currently lacks:

- document_type
- description

It must contain at least:

- agreement
- title
- document_type
- file
- description
- uploaded_by
- uploaded_at

Add the missing fields safely.

`document_type` may be a CharField.

For now do not overengineer document type choices.

`description` may be blank.

Important:
The current migration state has a problem adding `uploaded_at` with `auto_now_add=True`.

Fix this safely without deleting the database or old migrations.

Prefer an additive/backward-compatible migration.

Do NOT delete db.sqlite3.

Do NOT edit already-applied migration history unless absolutely unavoidable.

### 2. Activity model

The Activity model currently lacks:

- title
- updated_by
- updated_at

It must contain at least:

- agreement
- title
- activity_date
- description
- created_by
- updated_by
- created_at
- updated_at

The existing activity_type field may remain.

Add missing fields safely.

### 3. Admin

Inspect admin.py.

Make sure it references ONLY fields that actually exist after the schema repair.

Do not redesign admin unnecessarily.

### 4. Serializers

Inspect serializers.py.

Update Document and Activity serializers only if required by the repaired model fields.

Preserve existing API behavior.

### 5. Migrations

After model changes:

Run:

python manage.py makemigrations
python manage.py migrate
python manage.py check
python manage.py makemigrations --check --dry-run --noinput

All must complete successfully.

If there is an interactive migration issue, solve it safely using defaults or nullable transitional fields.

Do not wait for interactive input.

### 6. Scope guard

Do NOT implement:

- Vue
- JWT
- finance
- contributions
- analytics
- dashboards
- notifications
- advanced roles
- new architecture

Make only the smallest patch required.

Stop immediately after all requested checks pass.

Final response must include:

CHANGED FILES
CHECKS RUN
REMAINING BLOCKERS
ITERATION STATUS: COMPLETE or INCOMPLETE