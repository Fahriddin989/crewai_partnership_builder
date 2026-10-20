# Iteration 11 — Finish CRUD and Reliability

The application is already working.

This iteration is a SMALL cleanup/finalization step.

Do NOT redesign the application.
Do NOT add dashboard, analytics, finance, notifications or other future features.

First inspect the CURRENT repository because some edit/delete functionality may already exist.

Preserve anything that already works.

## Goals

Finish only these items:

1. Agreement delete
2. Organization Photo Report edit/delete
3. Prevent duplicate form submissions
4. Delete physical uploaded files when their database records are deleted

---

# 1. Agreement Delete

On Agreement Detail:

/agreements/:id

Use the existing modern overflow menu if it exists.

If agreement edit already exists, preserve it.

Menu should include:

Edit
Delete

Delete must show confirmation:

Delete agreement?

This will also remove related:
- agreement contacts
- documents
- activities

This action cannot be undone.

[Cancel] [Delete]

DELETE:

/api/agreements/:id/

After successful deletion:

navigate back to:

/organizations/<organization_id>

Do not reload the browser.

Do not change database relationships.

---

# 2. Photo Report Edit/Delete

On Organization Detail:

/organizations/:id

Each Photo Report card should have a small:

⋯

menu.

Actions:

Edit
Delete

## Edit Photo Report

Allow editing ONLY:

- title
- description
- is_public

Do NOT replace the image in this iteration.

Use:

PATCH /api/organization-media/:id/

After save:

- close modal
- refresh media list
- no browser reload

## Delete Photo Report

Use confirmation:

Delete photo report?

This action cannot be undone.

DELETE:

/api/organization-media/:id/

After success:

- refresh media
- no browser reload

Reuse existing modal/action/confirmation styles if they already exist.

Do not create parallel UI implementations.

---

# 3. Duplicate Submission Protection

Audit ALL current create/edit/upload forms:

- Add Organization
- Edit Organization
- Add Agreement
- Edit Agreement
- Add Contact
- Edit Contact
- Upload Document
- Edit Document
- Add Activity
- Edit Activity
- Add Photo Report
- Edit Photo Report

For every async write action:

1. Return immediately if already submitting.
2. Set submitting=true BEFORE request.
3. Disable Save/Create/Upload while submitting.
4. On success, close/reset the form correctly.
5. In finally, restore submitting=false.
6. A single user action must never create duplicate records.

IMPORTANT:

Do not introduce the previous bug where a close/reset function refuses to close because submitting=true.

If a shared helper already exists, reuse it.

Do not build a large generic form framework.

---

# 4. Physical File Cleanup

Current models include uploaded files:

Document.file

OrganizationMedia.image

When a Document or OrganizationMedia database record is deleted,
the actual stored file must also be deleted.

This must also work when deletion happens indirectly through CASCADE, for example:

Organization deleted
  -> Agreement deleted
  -> Document deleted

Use a small DRY Django solution based on post_delete signals or an equivalent safe mechanism.

Do NOT build a storage subsystem.

Do NOT delete files during ordinary update unless the file itself is intentionally replaced.

Since file replacement is not implemented, focus only on deletion.

Use the FileField/ImageField storage API rather than manually assuming filesystem paths.

---

# Backend Tests

Add focused tests for missing behavior:

1. editor can DELETE Agreement
2. viewer cannot DELETE Agreement

3. editor can PATCH OrganizationMedia metadata
4. viewer cannot PATCH OrganizationMedia
5. editor can DELETE OrganizationMedia
6. viewer cannot DELETE OrganizationMedia

7. deleting Document removes its stored file
8. deleting OrganizationMedia removes its stored image

9. deleting Agreement cascades and removes its document file

Do not duplicate existing tests if equivalent coverage already exists.

Use temporary media storage / temporary MEDIA_ROOT in tests when appropriate.

---

# Permissions

Continue using existing PartnershipPermission.

Do not create another permission system.

Editors:
CRUD

Viewers:
read only

Superusers:
full access

403 message:

"You do not have permission to perform this action."

---

# DRY

Before writing code inspect existing:

- modals
- action menus
- confirmation dialogs
- form error handling
- load functions
- submitting flags
- API client
- serializers
- ViewSets

Reuse existing working implementations.

Do not create:
- another Axios client
- duplicate constants
- duplicate auth logic
- parallel modal systems
- parallel confirmation systems

Keep code simple.

---

# Scope Guard

DO NOT implement:

- document file replacement
- photo image replacement
- bulk delete
- undo
- archive
- soft delete
- dashboard
- partnerships global page
- analytics
- finance
- notifications
- role management

---

# Validation

Run separately.

Backend:

python manage.py check

python manage.py test partnerships

python manage.py makemigrations --check --dry-run --noinput

Frontend:

npm run build

No schema change should be necessary.

If makemigrations reports model changes, STOP and report why instead of creating an unrelated migration.

Fix only problems related to this iteration.

Final answer:

CHANGED FILES
CRUD COMPLETED
DUPLICATE-SUBMIT CHECK
FILE CLEANUP
TEST COUNT
CHECKS RUN
REMAINING BLOCKERS
ITERATION STATUS: COMPLETE or INCOMPLETE