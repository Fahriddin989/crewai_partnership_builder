# Iteration 05 — Simple Agreement Workspace

The existing system is working.

Current structure:

Organizations
  -> Organization Detail
      -> Agreements

Now make each agreement clickable and open a simple read-only agreement page.

Keep this iteration SMALL and SIMPLE.

Do not redesign existing architecture.
Do not add create/edit/delete UI.
Do not add large components or frameworks.

## Goal

Example:

Huawei
  -> MoU

Page:

MoU
Status: Active
Type: Memorandum of Understanding

Overview
Contacts
Documents
Activities

All sections must appear vertically on ONE page.

No tabs yet.

---

# Backend

Existing models already include:

- Agreement
- AgreementContact
- Contact
- Document
- Activity

Do not change models in this iteration.

## Agreement filtering

Add optional query filtering:

GET /api/documents/?agreement=<agreement_id>

GET /api/agreement-contacts/?agreement=<agreement_id>

GET /api/activities/?agreement=<agreement_id>

When the parameter is absent, preserve existing behavior.

Use small get_queryset() implementations.

Do not install django-filter.

## Agreement contacts

The frontend should not need a separate API request for every Contact.

Extend AgreementContactSerializer with read-only contact information:

- contact_name
- contact_position
- contact_email
- contact_phone

Use the existing Contact relationship.

Preserve existing writable `contact` ID field.

Do not create a new serializer unless genuinely needed.

---

# Frontend

## Organization Detail

Existing agreement rows must become clickable by agreement title.

Example:

MoU

click ->

/agreements/:id

---

# Agreement Detail

Create:

src/views/AgreementDetailView.vue

Protected route:

/agreements/:id

Fetch:

GET /api/agreements/:id/

GET /api/agreement-contacts/?agreement=:id

GET /api/documents/?agreement=:id

GET /api/activities/?agreement=:id

Reuse the existing Axios client.

## Header

Show:

- agreement title
- agreement type
- status
- organization
- signed date
- start date
- expiration date

Add:

Back to Organization

The back link should use the agreement's organization ID.

Use existing shared constants for agreement type/status labels.

Do not duplicate mappings.

---

# Overview

Show description if it exists.

If no description:

"No description recorded."

---

# Contacts

Display simple rows/cards.

Show:

- name
- position
- email
- phone
- side
- role
- primary contact indicator

Group visually into:

Our side

Partner side

If empty:

"No contacts recorded."

---

# Documents

Display:

- title
- document type
- uploaded date
- file link

Clicking the file link should open/download the existing uploaded file.

Do not implement uploads yet.

If empty:

"No documents recorded."

---

# Activities

Display newest activities first.

Show:

- activity date
- activity type
- title
- description

If empty:

"No activities recorded."

---

# Styling

Reuse existing styles.

Keep the page simple and professional.

Do not add a large UI framework.

Do not create complex tabs, accordions, dashboards, or animations.

---

# DRY

Reuse:

- existing Axios client
- auth store
- AppLayout
- shared partnership constants
- existing permissions
- existing ViewSet architecture

Do not duplicate:
- API logic
- auth logic
- label mappings
- status mappings

Extract shared code only when genuinely reused.

---

# Scope Guard

DO NOT implement:

- create agreement
- edit agreement
- delete agreement
- upload document UI
- add contact UI
- add activity UI
- organization photo reports
- finance
- contributions
- analytics
- dashboard statistics
- notifications
- public website

This iteration is READ-ONLY.

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
CHECKS RUN
REMAINING BLOCKERS
ITERATION STATUS: COMPLETE or INCOMPLETE