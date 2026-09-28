# Iteration 09 — Modern Edit and Delete for Agreement Workspace

The current application is working.

Agreement Detail currently supports:

- Overview
- Contacts
- Documents
- Activities
- Add Contact
- Upload Document
- Add Activity

Now add EDIT and DELETE operations.

Keep the interface CLEAN, MODERN and SIMPLE.

Do not turn the application into a dense admin panel.
Do not install a large UI framework.

---

# UX STANDARD

Use modern contextual actions.

Do NOT place permanent large Edit/Delete buttons beside every row.

For individual records use a small overflow action button:

⋯

Menu:

Edit
Delete

Delete should be visually destructive only inside the menu/dialog.

Use existing application styling.

---

# Shared UI

If useful, create small reusable components:

src/components/ActionMenu.vue

src/components/ConfirmDialog.vue

Do not create a component framework.

Use shared components only because the same behavior is reused across Contacts, Documents and Activities.

## Confirm Dialog

Delete must NEVER happen immediately after one click.

Show a confirmation dialog.

Example:

Delete activity?

This action cannot be undone.

[Cancel] [Delete]

Requirements:

- Cancel is default/non-destructive
- Delete button uses destructive styling
- disable Delete while request is running
- Escape may close the dialog when safe
- do not use browser confirm()

---

# Agreement Edit

At the top of Agreement Detail add a small:

⋯

menu near the agreement title.

Actions:

Edit agreement

Do NOT implement agreement deletion in this iteration.

Edit fields:

- title
- agreement_type
- status
- description
- signed_date
- start_date
- expiration_date

Do not allow organization to be changed here.

Use:

PATCH /api/agreements/:id/

Use existing shared agreement type/status constants.

After save:

- close edit form
- update displayed agreement
- no full page reload

Backend validation remains authoritative.

Show readable validation errors.

---

# Contacts

Each contact row/card gets:

⋯

Actions:

Edit
Remove from agreement

IMPORTANT:

Contacts are normalized:

Contact
+
AgreementContact

A Contact may potentially be used by more than one agreement.

Therefore "Remove from agreement" must DELETE the AgreementContact relation only.

DO NOT automatically delete the underlying Contact record.

## Edit Contact

Allow editing:

Contact fields:

- full_name
- position
- email
- phone

AgreementContact fields:

- side
- role
- is_primary

Use:

PATCH /api/contacts/:contact_id/

and when needed:

PATCH /api/agreement-contacts/:agreement_contact_id/

Do not recreate records unnecessarily.

After save:

- refresh contacts
- keep correct Our side / Partner side grouping
- no browser reload

---

# Documents

Each document gets:

⋯

Actions:

Edit details
Delete

## Edit Document

Allow editing metadata only:

- title
- document_type
- description

Do NOT replace the uploaded file in this iteration.

Use:

PATCH /api/documents/:id/

## Delete Document

Use:

DELETE /api/documents/:id/

Before deletion show ConfirmDialog.

After successful deletion:

- remove/refresh document list
- no full browser reload

IMPORTANT:

Deleting the database record should also handle the actual uploaded file safely if the existing architecture already does this.

If Django currently leaves orphaned uploaded files, do NOT introduce a large storage subsystem.
Report it as a remaining blocker instead of over-engineering.

---

# Activities

Each activity gets:

⋯

Actions:

Edit
Delete

Edit fields:

- activity_type
- title
- activity_date
- description

Use:

PATCH /api/activities/:id/

Delete:

DELETE /api/activities/:id/

After edit/delete:

- refresh activity list
- newest remains first
- no browser reload

---

# Forms / Modal UX

Reuse one consistent visual language.

A simple modal/panel should have:

Title

fields

[Cancel] [Save]

Requirements:

- disable Save while submitting
- prevent duplicate submission
- show backend validation errors near the form
- preserve entered values when API returns validation error
- close only after successful save
- do not use browser alert()

Keep forms compact.

---

# Permissions

Backend PartnershipPermission remains authoritative.

Editors:
- may edit/delete

Viewers:
- read only

Superusers:
- full access

Do not reproduce permission rules in multiple frontend components.

If backend returns 403 show:

"You do not have permission to perform this action."

Do not fake success.

---

# API

Reuse the existing Axios client.

Do not create another Axios client.

Use PATCH for partial updates.

Use DELETE for deletion.

Reuse existing JWT refresh behavior.

---

# DRY

Before adding code inspect existing:

- AgreementDetailView
- form styles
- API helpers
- error formatting
- shared constants
- auth logic

Reuse existing load functions:

- loadAgreement()
- loadContacts()
- loadDocuments()
- loadActivities()

or their current equivalents.

Do not duplicate fetch logic.

If several edit forms need the same small modal shell, extract one reusable modal component.

Do not over-engineer field-specific forms into a generic form framework.

---

# Backend

Existing ModelViewSets should already provide:

PATCH
DELETE

Do not add custom endpoints unless genuinely necessary.

Do not change models.

Do not change database schema.

---

# Tests

Add only missing focused tests:

1. editor can PATCH agreement
2. viewer cannot PATCH agreement

3. editor can PATCH Contact
4. editor can PATCH AgreementContact
5. viewer cannot PATCH Contact

6. editor can PATCH Document
7. editor can DELETE Document
8. viewer cannot DELETE Document

9. editor can PATCH Activity
10. editor can DELETE Activity
11. viewer cannot DELETE Activity

12. deleting AgreementContact does not delete underlying Contact

Reuse existing setup/helpers.

Do not duplicate test setup unnecessarily.

---

# Scope Guard

DO NOT implement:

- delete Agreement
- delete Organization
- edit Organization
- Photo Report edit/delete
- replace document file
- bulk operations
- undo system
- activity comments
- notifications
- finance
- analytics
- dashboard work

This iteration is only modern edit/delete behavior inside Agreement Workspace.

---

# Validation

Run separately.

Backend:

python manage.py check

python manage.py test partnerships

python manage.py makemigrations --check --dry-run --noinput

Frontend:

npm run build

Do not chain commands.

Fix only issues caused by this iteration.

Stop when all checks pass.

Final answer:

CHANGED FILES
UX CHANGES
BACKEND CHANGES
FRONTEND CHANGES
TEST COUNT
CHECKS RUN
REMAINING BLOCKERS
ITERATION STATUS: COMPLETE or INCOMPLETE