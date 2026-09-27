# Iteration 06 — Simple Organization Media

The current system is working.

Existing structure:

Organization
  -> Agreements
      -> Overview
      -> Contacts
      -> Documents
      -> Activities

Now add simple photo/media support directly to Organization.

Keep this iteration SMALL and SIMPLE.

Do not redesign existing architecture.
Do not add upload UI yet.
Django Admin remains the temporary place for adding photos.

---

# Goal

Example:

Huawei
  -> Agreements
  -> Photo reports

Photos belong directly to Huawei, not to a specific Agreement.

Public photos must also be available through the public API.

---

# Backend Model

Add one model:

OrganizationMedia

Fields:

- organization: ForeignKey to Organization
- title
- image
- description
- is_public
- uploaded_by
- uploaded_at

Use:

ImageField

Store files in a sensible path such as:

organizations/<organization_id>/media/

Set:

is_public = False by default

Do not create albums or additional media models.

If ImageField requires Pillow, add it to backend requirements.

---

# Admin

Register OrganizationMedia in Django Admin.

Useful fields:

- title
- organization
- is_public
- uploaded_by
- uploaded_at

Allow filtering by:

- organization
- is_public

---

# Internal API

Add:

GET /api/organization-media/

Support optional filter:

GET /api/organization-media/?organization=<organization_id>

Authenticated Partnership permissions must apply.

Editors may CRUD.

Viewers may GET only.

Use existing PartnershipPermission.

Do not duplicate permission logic.

---

# Public API

IMPORTANT:

Existing:

GET /api/public/organizations/

must preserve its CURRENT response fields exactly.

Do not add media to the public organization LIST.

For:

GET /api/public/organizations/<id>/

return:

- id
- name
- organization_type
- country
- website
- media

media must contain ONLY OrganizationMedia where:

is_public=True

Each media item should expose only:

- id
- title
- image
- description
- uploaded_at

Never expose:

- uploaded_by
- private media
- internal audit fields

Only organizations with Organization.is_public=True may be retrieved publicly.

Use a separate detail serializer or equivalent clean DRY approach.

---

# Frontend Organization Detail

Existing route:

/organizations/:id

Add one simple section below Agreements:

Photo reports

Fetch:

GET /api/organization-media/?organization=:id

Display each photo simply:

- image preview
- title
- description if present
- uploaded date
- Public / Private indicator

If there are no photos:

"No photo reports recorded."

Do not build galleries, lightboxes, sliders, albums or animations.

Use a simple responsive grid.

---

# Small Agreement Fix

Current Agreement Detail displays:

Organization: 1

Replace this with the real organization name.

Do this without adding unnecessary API calls.

Prefer extending AgreementSerializer with a read-only:

organization_name

sourced from:

organization.name

Preserve writable organization ID.

Frontend should display:

Organization: Huawei

instead of:

Organization: 1

---

# DRY

Reuse:

- existing serializers
- ViewSet architecture
- PartnershipPermission
- Axios client
- auth store
- AppLayout
- shared constants
- existing styling

Do not duplicate authentication, permissions, API clients or mappings.

Extract shared code only when genuinely reused.

---

# Tests

Add focused tests for:

1. editor can create OrganizationMedia
2. viewer can GET OrganizationMedia
3. viewer cannot POST OrganizationMedia
4. organization filter returns only matching media
5. public organization list response remains unchanged
6. public organization detail includes public media
7. public organization detail excludes private media
8. private organization is not publicly retrievable

Do not remove existing tests.

---

# Scope Guard

DO NOT implement:

- frontend photo upload
- photo delete UI
- albums
- galleries
- agreement CRUD UI
- document upload UI
- contact editing UI
- activity editing UI
- dashboard
- finance
- analytics
- notifications

---

# Validation

Run separately.

Backend:

python manage.py makemigrations
python manage.py migrate
python manage.py check
python manage.py test partnerships
python manage.py makemigrations --check --dry-run --noinput

Frontend:

npm run build

Fix only errors related to this iteration.

Stop when all checks pass.

Final answer:

CHANGED FILES
DATABASE CHANGES
BACKEND CHANGES
FRONTEND CHANGES
TEST COUNT
CHECKS RUN
REMAINING BLOCKERS
ITERATION STATUS: COMPLETE or INCOMPLETE