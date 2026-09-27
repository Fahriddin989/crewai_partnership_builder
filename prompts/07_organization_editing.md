# Iteration 07 — Simple Organization Editing

The current system is working.

Current structure:

Organizations
  -> Organization Detail
      -> Agreements
      -> Photo reports

Agreement pages already show:

- Overview
- Contacts
- Documents
- Activities

Now add ONLY two simple write actions to Organization Detail:

1. Add Agreement
2. Add Photo Report

Keep the UI SMALL and SIMPLE.

Do not build a general admin panel.
Do not redesign the application.

---

# Permissions

Existing backend permissions already define:

- Partnership Editors: CRUD
- Partnership Viewers: read only
- Superusers: full access

Keep using PartnershipPermission.

Backend permissions remain the source of truth.

If a frontend write request returns 403, display:

"You do not have permission to perform this action."

Do not duplicate permission logic in Vue.

---

# Add Agreement

On:

/organizations/:id

Add button:

+ Add Agreement

Show a small inline form or simple modal.

Fields:

- title
- agreement_type
- status
- description
- signed_date
- start_date
- expiration_date

Organization must automatically be the current organization.

Do NOT ask user to choose organization again.

POST:

/api/agreements/

Example payload:

{
  "organization": 1,
  "title": "Huawei ICT Academy",
  "agreement_type": "ACADEMY",
  "status": "ACTIVE",
  "description": "",
  "signed_date": null,
  "start_date": null,
  "expiration_date": null
}

Use existing shared constants for:

- agreement type labels
- agreement status labels

Do not duplicate mappings.

After successful creation:

- close/reset form
- refresh agreement list
- show the new agreement immediately

Do not reload the entire browser page.

---

# Agreement date validation

Preserve existing backend validation.

Expiration date must not be earlier than start date.

If backend returns field validation errors,
show a simple readable error in the form.

Do not duplicate complex validation in frontend.

---

# Add Photo Report

On the same Organization Detail page add:

+ Add Photo Report

Fields:

- title
- image
- description
- is_public

Organization must automatically be current organization.

POST multipart/form-data to:

/api/organization-media/

Use existing Axios client.

Do not create another Axios instance.

After upload:

- close/reset form
- refresh media list
- display the uploaded image immediately

---

# Media UI

Keep it simple.

Current photo cards remain.

No:
- albums
- drag/drop
- cropper
- image editor
- lightbox
- slider

---

# Editing

Do NOT implement editing or deleting yet.

This iteration is CREATE ONLY.

---

# Agreement Detail

Do not change Contacts/Documents/Activities in this iteration.

They remain read-only.

---

# DRY

Reuse:

- Axios client
- auth store
- AppLayout
- shared constants
- existing form/button styles
- existing ViewSets
- PartnershipPermission

Do not duplicate:
- API clients
- auth logic
- agreement labels
- organization labels
- permission logic

If a small reusable form-error helper is genuinely useful,
extract it.

Do not create abstractions for one-off code.

---

# Tests

Add focused backend tests if current test coverage does not already verify:

1. editor can create agreement
2. viewer cannot create agreement
3. editor can create OrganizationMedia
4. viewer cannot create OrganizationMedia
5. created agreement belongs to requested organization
6. created media belongs to requested organization

Do not remove existing tests.

---

# Scope Guard

DO NOT implement:

- edit agreement
- delete agreement
- edit organization
- delete organization
- delete media
- contact creation
- document upload to Agreement
- activity creation
- dashboard
- finance
- analytics
- notifications

---

# Validation

Backend:

python manage.py check

python manage.py test partnerships

python manage.py makemigrations --check --dry-run --noinput

Frontend:

npm run build

Run commands separately.

Fix only problems caused by this iteration.

Stop when checks pass.

Final answer:

CHANGED FILES
BACKEND CHANGES
FRONTEND CHANGES
TEST COUNT
CHECKS RUN
REMAINING BLOCKERS
ITERATION STATUS: COMPLETE or INCOMPLETE