# Iteration 16 — Organization Ownership and Private Notes

## Current Project

This is an EXISTING, working University Partnership Management System built with Django REST Framework, Vue 3, Pinia, JWT and Docker.

Do NOT recreate or redesign the application.

The system will be used by two departments, each with one shared user account:

- `international` — International Relations Department
- `local_partnerships` — Local Corporate Partnerships Department

Both accounts belong to the existing `Partnership Editors` group.

The system must allow both departments to access the same organization directory while preventing one department from changing another department's records.

## Objective

Implement organization ownership-based write permissions and private Notes.

Requirements:

1. Both departments can see all organizations and their normal related records.
2. Both departments can create organizations.
3. Only the creator of an organization can edit or delete it.
4. Only the organization's creator can create, modify or delete its related records.
5. Organization Notes must be visible only to the organization creator.
6. Rename "Relationship Notes" to "Notes" in the frontend.
7. Move Notes to the bottom of the Organization Detail page.
8. Preserve superuser administrative access.

## Existing Behavior

The `Organization` model already has `created_by`.

`AuditModelViewSet` automatically sets `created_by` when creating records.

`PartnershipPermission` currently grants CRUD access to every user in the `Partnership Editors` group.

Organization Notes use:

- `OrganizationNote`
- `OrganizationNoteAttachment`

The frontend already has:

- `OrganizationsView.vue`
- `OrganizationDetailView.vue`
- `AgreementDetailView.vue`
- `ActionMenu.vue`
- `ConfirmDialog.vue`
- Pinia auth store
- Axios API client

Inspect their current implementations before changing anything.

## Backend Scope

Relevant files:

- `workspace/backend/partnerships/permissions.py`
- `workspace/backend/partnerships/views.py`
- `workspace/backend/partnerships/serializers.py`

Do not change database models unless absolutely necessary.

### 1. Ownership Rule

Use the existing `Organization.created_by_id`.

A user may modify an organization only when:

- the user is authenticated;
- the user has the existing editor permission;
- `organization.created_by_id == request.user.id`.

Superusers bypass the ownership restriction.

Do not use `updated_by` to determine ownership.

Never allow normal API users to change `created_by` manually.

Keep existing `Partnership Viewers` permissions read-only.

### 2. Organization CRUD

Both department accounts may:

- GET all organizations;
- GET organization details;
- POST new organizations.

Only the owner may:

- PATCH/PUT their organization;
- DELETE their organization.

Reject unauthorized modifications with HTTP 403.

For existing organizations with `created_by=NULL`, allow read access, but permit modifications only to superusers until an owner is assigned.

Do not automatically reassign existing records.

### 3. Related Records

Enforce ownership when creating, editing or deleting:

- Agreements
- AgreementContacts
- Documents
- Activities
- OrganizationMedia
- OrganizationNotes
- OrganizationNoteAttachments

Determine ownership through the parent Organization, not through the individual record's `created_by`.

For example:

`Document -> Agreement -> Organization -> created_by`

Also validate the destination parent during create and update. A user must not bypass ownership by supplying an ID belonging to another department.

Do not allow changing parent relationships to bypass permissions.

For Contacts, preserve the existing normalized Contact/AgreementContact structure. Prevent modification or deletion of contacts linked to another department's organizations, including shared contacts. Do not allow a new contact association to modify another department's relationships.

Reuse centralized ownership-checking logic. Avoid duplicating permission logic across all ViewSets.

### 4. Private Notes

Notes are private to the owner of their Organization.

For ordinary department users:

- GET Notes only for organizations they own.
- POST/PATCH/DELETE Notes only for organizations they own.
- GET attachments only for Notes belonging to owned organizations.
- Upload/delete attachments only for owned organizations.
- Direct retrieval of another department's private Note or attachment must be denied without exposing its contents.

A Note's own `created_by` is not the ownership criterion. Use `note.organization.created_by_id`.

Superusers retain administrative access.

Keep the existing API endpoints and model names unchanged.

Do not expose Notes through the Public API.

### 5. Note Attachment File Security

Existing Nginx configuration serves files under `/media/` directly.

Hiding Notes in Vue or filtering API responses is not sufficient to protect uploaded Note attachments.

Implement a small focused solution:

- Block direct public Nginx access to `/media/organization_notes/`.
- Provide an authenticated download endpoint for Note attachments.
- Verify ownership before serving file bytes.
- Use the existing Django storage API.
- Update frontend Note attachment downloads to use the authenticated Axios client and Blob response.
- Preserve original filenames.
- Do not change unrelated Agreement Documents or Photo Reports storage.

Do not build a new storage framework.

## Frontend Scope

Relevant files:

- `workspace/frontend/src/views/OrganizationsView.vue`
- `workspace/frontend/src/views/OrganizationDetailView.vue`
- `workspace/frontend/src/views/AgreementDetailView.vue`
- `workspace/frontend/src/stores/auth.js`
- `workspace/frontend/src/api/client.js` if needed

### 1. Current User

Use the existing Pinia auth store and `/api/auth/me/`.

Make sure current user information is loaded after page refresh.

Do not rely on a nonexistent `localStorage.user` value.

Use the current user's ID and the organization's existing `created_by` field.

For Agreement Detail, obtain the parent organization's owner through a small read-only serializer field or reuse existing available data. Avoid unnecessary additional requests.

### 2. Organizations List

Keep all organizations visible.

Keep the "+ Add Organization" button available to both editor accounts.

Display the existing Edit/Delete ActionMenu only when the current user owns that organization or is a superuser.

For other organizations, display the row without edit actions.

Do not change search, filtering, Directions, or navigation.

### 3. Organization Detail

Keep the following order:

1. Organization Information
2. Agreements
3. Photo reports
4. Notes

Rename the heading:

`Relationship Notes` -> `Notes`

Move the complete Notes section to the bottom of the page, including Notes forms, attachments and related actions.

Do not recreate the Notes implementation.

For another department's organization:

- Display Organization Information.
- Display Agreements in read-only mode.
- Display Photo Reports in read-only mode.
- Hide all create/edit/delete controls.
- Do not render the Notes section.
- Do not request private Notes or attachments.

For the owner:

- Preserve all existing create/edit/delete functionality.
- Display Notes and their attachments.

### 4. Agreement Detail

When viewing an agreement belonging to another department:

- Display Overview.
- Display Contacts.
- Display Documents.
- Display Activities.
- Hide editing and deletion controls.
- Hide Add Contact, Upload Document and Add Activity.

When viewing an owned agreement, preserve existing editing functionality.

### 5. UI Reliability

Reuse:

- ActionMenu
- ConfirmDialog
- existing forms
- existing Axios client
- existing auth store
- existing error handling

Handle HTTP 403 correctly.

Do not create another authorization store or permissions framework.

## Department Accounts

Do not hardcode passwords.

Do not create users inside migrations or source code.

The administrator will manually create these Django users:

- `international`
- `local_partnerships`

Both should be assigned to the existing `Partnership Editors` group.

Do not grant superuser or Django staff status to these accounts.

## Constraints

- DO NOT redesign the architecture.
- DO NOT introduce a new Department model.
- DO NOT introduce an additional owner field.
- DO NOT change existing database relationships.
- DO NOT delete existing records.
- DO NOT modify old migrations.
- DO NOT change the Public API response structure.
- DO NOT implement unrelated features.
- DO NOT deploy to VPS.
- DO NOT push to Git.
- DO NOT create automated tests.
- DO NOT modify existing tests.
- DO NOT run automated test suites.
- DO NOT run `python manage.py test`.

All current data is test data, so no historical ownership migration is required.

Keep this iteration focused on access control, private Notes and related frontend visibility.

## Validation

Run only:

Backend:

`python manage.py check`

Frontend:

`npm run build`

If Django models remain unchanged, do not generate migrations.

Review the implementation against these scenarios without creating automated tests:

1. International creates an organization and can edit it.
2. Local Partnerships can view that organization but cannot modify it.
3. Local Partnerships cannot create or modify related records under the International organization.
4. Local Partnerships cannot see International Notes or attachment contents.
5. The reverse scenario works identically.
6. Superuser retains full access.
7. Existing organizations without owners remain visible but read-only to normal users.
8. JWT login/refresh and existing organization navigation still work.

Do not claim these scenarios were executed unless they were actually verified.

## Final Output

Return:

CHANGED FILES

IMPLEMENTATION SUMMARY

OWNERSHIP PERMISSIONS

PRIVATE NOTES BEHAVIOR

FRONTEND CHANGES

CHECKS RUN

REMAINING BLOCKERS

ITERATION STATUS: COMPLETE / INCOMPLETE

Stop after completing this iteration.