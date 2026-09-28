# Iteration 10B — Finish Organization CRUD UI

Iteration 10 backend already exists or was attempted.

The current /organizations page is working, but the required CRUD controls are MISSING from the frontend.

Current visible page contains:

- Organizations heading
- search
- type filter
- organization table
- clickable organization name

Missing:

- + Add Organization button
- organization action menu (...)
- Edit organization
- Delete organization
- create/edit form
- delete confirmation

DO NOT redesign the page.
DO NOT rewrite working organization fetching/search/filtering.
DO NOT change models.
DO NOT add unrelated features.

## First

Inspect the CURRENT frontend implementation before changing anything.

Especially inspect:

- src/views/OrganizationsView.vue
- existing ActionMenu component
- existing ConfirmDialog component
- existing modal/form styles
- shared partnership constants
- Axios client

Reuse existing components.

---

# Add Organization

On /organizations add:

+ Add Organization

Place it on the same heading row as:

Organizations

Example:

Organizations                    [+ Add Organization]

Clicking it opens the same simple modal/panel style already used elsewhere.

Fields:

- name
- organization_type
- country
- website
- description
- is_public

Use shared:

ORGANIZATION_TYPE_LABELS

POST:

/api/organizations/

After success:

- close form
- reset form
- reload organization data using the existing load function
- display new organization immediately
- no browser reload

---

# Actions

Add a final narrow Actions column to the organizations table.

Each organization row must have:

⋯

Reuse the EXISTING ActionMenu component.

Menu:

Edit
Delete

Do not display large permanent edit/delete buttons.

---

# Edit

Use the same organization form.

Pre-fill current values.

PATCH:

/api/organizations/:id/

Fields:

- name
- organization_type
- country
- website
- description
- is_public

After successful save:

- close modal
- refresh list
- no browser reload

---

# Delete

Reuse EXISTING ConfirmDialog.

Text:

Delete organization?

This will also remove related agreements and dependent records.

This action cannot be undone.

[Cancel] [Delete]

DELETE:

/api/organizations/:id/

After success:

- close confirmation
- refresh organizations
- no browser reload

Do not use browser confirm().

---

# Permissions

Do not invent new frontend permission architecture.

Backend PartnershipPermission remains authoritative.

If POST/PATCH/DELETE returns 403 show:

"You do not have permission to perform this action."

---

# DRY

Reuse:

- existing loadOrganizations() or equivalent
- Axios client
- ActionMenu
- ConfirmDialog
- existing modal styles
- existing form styles
- shared constants
- existing error handling

Do NOT create duplicate ActionMenu, ConfirmDialog, Axios client, or organization type mappings.

---

# Backend

Do not modify backend unless a required Organization POST/PATCH/DELETE endpoint is actually broken.

Existing OrganizationViewSet should already provide CRUD.

No model changes.
No migrations.

---

# Validation

Frontend:

npm run build

Backend:

python manage.py check
python manage.py test partnerships
python manage.py makemigrations --check --dry-run --noinput

Run separately.

Stop when checks pass.

Final output:

CHANGED FILES
WHAT WAS MISSING
WHAT WAS FIXED
CHECKS RUN
REMAINING BLOCKERS
ITERATION STATUS: COMPLETE or INCOMPLETE