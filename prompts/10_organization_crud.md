# Iteration 10 — Organization Create, Edit and Delete

The application is working.

Current organization page:

/organizations

already supports:

- organization list
- search
- organization type filtering
- organization detail navigation

Now add simple Organization CRUD.

Keep the UI CLEAN and SIMPLE.

Reuse the modern interaction patterns already introduced in Agreement Workspace.

Do not redesign the page.
Do not install a UI framework.

---

# Goal

Organizations page should become:

Organizations                         [+ Add Organization]

Search by name...   [All types]

Huawei                                  ⋯
ZTE                                     ⋯
University of Debrecen                  ⋯

---

# Add Organization

Add:

+ Add Organization

on:

/organizations

Use a small modal or panel consistent with existing UI.

Fields:

- name
- organization_type
- country
- website
- description
- is_public

Organization type values:

UNIVERSITY
COMPANY
GOVERNMENT
NGO
OTHER

Use existing:

ORGANIZATION_TYPE_LABELS

from shared frontend constants.

Do not duplicate organization type mappings.

POST:

/api/organizations/

After successful creation:

- close/reset form
- refresh organization list
- show new organization immediately
- do not reload browser

If backend validation fails:

- keep entered form values
- show readable validation errors

---

# Organization actions

Each organization row gets the existing modern:

⋯

action menu.

Actions:

Edit
Delete

Reuse the existing ActionMenu component if it exists.

Do not create another implementation.

---

# Edit Organization

Edit fields:

- name
- organization_type
- country
- website
- description
- is_public

Use:

PATCH /api/organizations/:id/

After successful edit:

- close form
- refresh organization list
- no page reload

If editing Organization Detail from the list is simpler,
keep this iteration focused on the Organizations list.

Do not duplicate an edit implementation on multiple pages.

---

# Delete Organization

Use:

DELETE /api/organizations/:id/

Before deleting show the existing ConfirmDialog.

Do NOT use browser confirm().

Dialog example:

Delete organization?

Deleting this organization will also remove its related agreements and
other dependent records according to the existing database relationships.

This action cannot be undone.

[Cancel] [Delete]

IMPORTANT:

Organization currently owns Agreements through a cascading relationship.

Do not change database relationships in this iteration.

Do not add soft-delete yet.

Do not silently delete without confirmation.

After deletion:

- close dialog
- refresh organization list
- no browser reload

---

# Permissions

Reuse existing PartnershipPermission.

Editors:
- create
- edit
- delete

Viewers:
- read only

Superusers:
- full access

Backend remains authoritative.

If a write request returns 403:

"You do not have permission to perform this action."

Do not duplicate permission rules in multiple frontend components.

---

# Public visibility

is_public controls whether the organization may appear through public APIs.

Default behavior must remain compatible with the existing backend model.

Do not redesign the public API.

Do not expose private organizations publicly.

---

# Frontend

Reuse existing:

- Axios client
- auth store
- AppLayout
- ActionMenu
- ConfirmDialog
- existing modal/form styling
- shared partnership constants
- existing organization load function

Do not create:

- another Axios client
- another confirmation component
- another action-menu implementation
- duplicate label maps

---

# DRY

Inspect current components before adding code.

Reuse existing:

ActionMenu.vue
ConfirmDialog.vue

or their current equivalents.

If an existing reusable modal shell exists, use it.

Do not create a generic form framework.

Keep organization form logic specific and simple.

---

# Backend

Existing OrganizationViewSet should already provide:

POST
PATCH
DELETE

Do not add custom endpoints unless necessary.

Do not change Organization model.

Do not create migrations.

Do not change database schema.

---

# Tests

Add only missing focused tests:

1. editor can POST organization
2. viewer cannot POST organization
3. editor can PATCH organization
4. viewer cannot PATCH organization
5. editor can DELETE organization
6. viewer cannot DELETE organization
7. public API does not expose organization after it is deleted

Reuse existing test helpers/setup.

Do not duplicate test setup unnecessarily.

---

# Scope Guard

DO NOT implement:

- bulk organization actions
- soft delete
- archive system
- organization merge
- CSV import
- Excel import
- photo report editing
- dashboard
- finance
- analytics
- notifications

This iteration is only Organization CRUD.

---

# Validation

Backend:

python manage.py check

python manage.py test partnerships

python manage.py makemigrations --check --dry-run --noinput

Frontend:

npm run build

Run separately.

Fix only problems caused by this iteration.

Stop when all checks pass.

Final answer:

CHANGED FILES
FRONTEND CHANGES
BACKEND CHANGES
TEST COUNT
CHECKS RUN
REMAINING BLOCKERS
ITERATION STATUS: COMPLETE or INCOMPLETE