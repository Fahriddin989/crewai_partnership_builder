# Iteration 04 — Organization detail and agreements

The existing Django REST + Vue application is working.

Current working functionality includes:

- JWT authentication
- Partnership Editors / Partnership Viewers permissions
- Organizations API
- Agreements API
- Vue login
- authenticated layout
- organizations list
- organization search and filtering

Huawei is already visible in the Organizations page.

Make a SMALL incremental patch.

Do NOT redesign existing architecture.
Do NOT rebuild existing working pages.
Do NOT modify unrelated models.

## Goal

Implement:

ORGANIZATIONS
    ->
ORGANIZATION DETAIL
    ->
AGREEMENTS BELONGING TO THAT ORGANIZATION

Example:

Huawei
  - MoU 2024
  - Huawei ICT Academy
  - Cooperation Agreement 2026

Do NOT implement Agreement detail tabs yet.

---

# Backend

Existing endpoints:

GET /api/organizations/
GET /api/organizations/{id}/

GET /api/agreements/
GET /api/agreements/{id}/

## Agreement filtering

Add optional server-side filtering:

GET /api/agreements/?organization=<organization_id>

When the query parameter is supplied, return only agreements belonging to that organization.

When it is absent, preserve current behavior and return all agreements allowed to the user.

Implement this with a small get_queryset() change in AgreementViewSet.

Do NOT install django-filter for this one simple filter.

Keep existing PartnershipPermission behavior.

## Backend tests

Add focused tests for:

1. viewer can retrieve an organization
2. viewer can retrieve agreements
3. agreements can be filtered by organization
4. filtering does not return agreements belonging to another organization
5. anonymous organization detail is denied
6. anonymous agreements are denied

Do not remove existing tests.

---

# Frontend

## Organizations page

Existing route:

/organizations

Make each organization name clickable.

Clicking Huawei must navigate to:

/organizations/:id

Do NOT make the website column trigger organization navigation.

---

# Organization Detail page

Create:

src/views/OrganizationDetailView.vue

Route:

/organizations/:id

Protected route.

Fetch:

GET /api/organizations/:id/

and:

GET /api/agreements/?organization=:id

## Header

Show:

- organization name
- organization type
- country
- website
- description if available

Add a clear:

Back to Organizations

link/button.

---

# Agreements section

Below organization details show:

Agreements

Display agreements belonging ONLY to this organization.

Each agreement should show:

- title
- agreement_type
- status
- signed_date
- start_date
- expiration_date

Readable agreement type labels:

MOU -> Memorandum of Understanding
MOA -> Memorandum of Agreement
ACADEMY -> Academy
PARTNERSHIP -> Partnership
EXCHANGE -> Exchange
NDA -> Non-Disclosure Agreement
OTHER -> Other

Readable statuses:

DRAFT -> Draft
ACTIVE -> Active
INACTIVE -> Inactive
EXPIRED -> Expired
UNDER_RENEWAL -> Under renewal

Use restrained status badges.

Examples:

ACTIVE
EXPIRED
DRAFT

Do not use flashy colors.

## Empty state

If the organization has no agreements:

"No agreements have been recorded for this organization."

## Loading/error

Handle:

- organization loading
- agreement loading
- organization not found
- API error

---

# Routing

Update Vue Router.

Required routes:

/login
/organizations
/organizations/:id

Existing authentication guards must continue working.

Do not break login/logout.

---

# Important scope guard

DO NOT implement:

- Agreement detail page
- create agreement form
- edit agreement form
- delete agreement
- contacts UI
- documents UI
- activities UI
- contributions
- finance
- analytics
- dashboard
- notifications
- user management
- automatic JWT refresh

This iteration is READ-ONLY frontend navigation from:

Organizations -> Organization -> Agreements

Existing Django Admin remains the temporary place for creating test organizations and agreements.

---
# DRY / engineering rules

Before creating new code, inspect existing helpers,
components, constants and API utilities.

Do not duplicate mappings or business constants.

Create one shared frontend constants module:

src/constants/partnerships.js

It should be the single source of truth for frontend display labels:

- ORGANIZATION_TYPE_LABELS
- AGREEMENT_TYPE_LABELS
- AGREEMENT_STATUS_LABELS

Update the existing Organizations page to use
ORGANIZATION_TYPE_LABELS from this module.

The new Organization Detail page must use the same shared constants.

Reuse the existing:
- Axios client
- auth store
- AppLayout
- permission system
- serializers
- ViewSet architecture

Do not duplicate API/auth/permission logic.

Extract shared logic only when it is genuinely reused.
Do not over-engineer one-off behavior.

# Validation

Run separately.

Backend:

python manage.py check

python manage.py test partnerships

python manage.py makemigrations --check --dry-run --noinput

Frontend:

npm run build

Do not chain commands with &&.

If something fails, make only the smallest required fix and rerun that command.

Stop when all checks pass.

Final response:

CHANGED FILES
BACKEND CHANGES
FRONTEND CHANGES
TEST COUNT
CHECKS RUN
REMAINING BLOCKERS
ITERATION STATUS: COMPLETE or INCOMPLETE