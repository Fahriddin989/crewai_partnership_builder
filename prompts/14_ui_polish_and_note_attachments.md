# Iteration 14 — UI Polish + Relationship Note Attachments

The current application is working.

This iteration is primarily UI/UX refinement plus one small backend feature:
file attachments for Organization Relationship Notes.

IMPORTANT:

Inspect the CURRENT repository before making changes.

Preserve all existing working functionality.

Do NOT deploy.
Do NOT add CI/CD.
Do NOT change VPS configuration.
Do NOT split repositories.
Do NOT work on Dashboard, Investments, AI or Reports.

DO NOT create or update automated tests.
DO NOT run `python manage.py test`.

The user will verify behavior manually.

Scope:

1. Remove redundant Partnerships navigation
2. Improve Directions selection UI
3. Fix ActionMenu behavior globally
4. Add file attachments to Relationship Notes
5. Minor visual polish directly related to these changes

---

# 1. Sidebar — Remove redundant Partnerships item

Current sidebar contains items similar to:

Dashboard
Partnerships
Organizations

`Partnerships` is currently redundant and confusing.

Organizations already represents the working list of:

- universities
- companies
- government organizations
- NGOs
- other partners

Organization type and Direction can already be filtered inside the Organizations page.

REMOVE the `Partnerships` item from the sidebar.

Keep:

Dashboard
Organizations

Do NOT add another replacement navigation item.

Do NOT redesign the whole sidebar.

Do NOT change routing unrelated to this item.

---

# 2. Directions selection — replace checkboxes with selectable tiles/chips

Current Add/Edit Organization form displays Directions as normal checkboxes inside a scrollable box.

This UX must be replaced.

Do NOT use traditional visible checkboxes.

Render every available Direction as a clickable selectable tile / chip.

Example:

Directions

[ School of Architecture & Art ]
[ School of Business & Finance ]
[ School of Philology ]
[ School of Education ]
[ School of Engineering ]
[ School of IT & AI ]
[ School of Medicine ]

IMPORTANT:

Direction names are dynamic and come from:

GET /api/academic-units/

DO NOT hard-code any school/direction name.

---

# 3. Direction tile visual states

Unselected Direction:

- light gray / neutral background
- subtle neutral border
- normal dark text

Selected Direction:

- green background or restrained green-tinted background
- green border if appropriate
- visually clear selected state
- include a small check mark if it improves clarity

Example:

unselected:

[ School of Engineering ]

selected:

[ ✓ School of Engineering ]

Clicking again must deselect it.

Multi-select must continue working.

One Organization may have multiple Directions.

Use accessible buttons if practical:

aria-pressed="true/false"

Do not add a UI framework.

---

# 4. Directions layout

REMOVE the current internal scrolling area for Directions.

Do not use:

- fixed-height checkbox container
- internal vertical scrollbar
- cramped 3-column checkbox layout

Instead:

- use flex-wrap or responsive CSS grid
- tiles should wrap naturally
- long names must remain readable
- modal itself may scroll if the whole form is taller than the viewport
- Directions section itself should NOT have its own scrollbar

Use the same Direction selector in BOTH:

- Add Organization
- Edit Organization

Do not duplicate two separate implementations if the current code can share the same markup/styles cleanly.

Preserve the existing active/inactive behavior:

- active Directions are available for new relationships
- already-linked inactive Directions must not silently disappear during unrelated Organization edits

---

# 5. Organizations table — Directions as badges

Current table shows Directions as plain comma-separated text:

School of Engineering, School of IT&AI

Replace this with compact neutral badges/tags.

Example:

[ School of Engineering ] [ School of IT & AI ]

Use the real dynamic Direction names.

Do not hard-code shortened names.

Badges may wrap onto another line when necessary.

Keep the table professional and restrained.

Do not make the row unnecessarily tall.

If an organization has no Directions, continue displaying:

—

Do not redesign the whole Organizations table.

---

# 6. ActionMenu — fix global open/close behavior

Current ActionMenu has two UX bugs:

BUG 1:

Opening an ActionMenu on one row and then opening another ActionMenu leaves the previous menu open.

Required behavior:

ONLY ONE ActionMenu may be open at any time across the page/application.

Opening another ActionMenu must automatically close the previous one.

---

# 7. ActionMenu closing behavior

An open ActionMenu must close when:

- another ActionMenu opens
- user clicks outside the menu
- user chooses Edit
- user chooses Delete
- user presses Escape
- navigation changes if applicable

Implement this behavior in the shared:

ActionMenu.vue

Do NOT fix it separately in every table/view.

Do NOT create duplicate menu components.

---

# 8. ActionMenu — prevent clipping at bottom of tables/cards

Current problem:

For rows near the bottom of a table, the ActionMenu dropdown may be clipped by:

- table container
- card overflow
- bottom edge
- viewport

Fix this globally in ActionMenu.vue.

Preferred robust approach:

- render dropdown using Vue Teleport to `body`
- position it using the trigger button's bounding rectangle
- use fixed positioning
- calculate whether there is enough space below
- if there is not enough space below, open upward
- keep dropdown horizontally inside viewport bounds
- use appropriate z-index

The dropdown must remain fully visible.

It must NOT be clipped by:

overflow: hidden
overflow-x: auto

on a parent table/card.

Recalculate position when opening.

If necessary, close on window scroll/resize rather than implementing complex live repositioning.

Do not install Popper, Floating UI, Bootstrap or another UI library.

Keep this small.

---

# 9. Preserve current ActionMenu API

Inspect how ActionMenu is currently used.

Preserve existing events such as:

@edit
@delete

unless a very small internal adjustment is necessary.

Existing Organization and Agreement actions must continue working.

Do not redesign business actions.

---

# 10. Relationship Notes — add multiple file attachments

Relationship Notes currently work correctly.

KEEP the existing OrganizationNote model and behavior:

- organization
- body
- next_step
- follow_up_date
- created_by
- updated_by
- created_at
- updated_at

Do NOT replace OrganizationNote.

Add a separate model:

OrganizationNoteAttachment

Fields:

- note
- file
- original_name
- uploaded_by
- uploaded_at

---

# 11. OrganizationNoteAttachment model

`note`

ForeignKey to OrganizationNote

on_delete=CASCADE

related_name="attachments"

---

`file`

FileField

Use a sensible upload path such as:

organization_notes/<organization_id>/<note_id>/<filename>

or another equivalent clean path.

Do not store file bytes directly in the database.

---

`original_name`

CharField

Store the original uploaded filename automatically.

Do not ask frontend users to enter it manually.

---

`uploaded_by`

Reuse the existing user reference pattern where practical.

Server assigns authenticated user.

Client must not control uploaded_by.

---

`uploaded_at`

DateTimeField(auto_now_add=True)

---

# 12. Attachment API

Add internal authenticated endpoint:

/api/organization-note-attachments/

Use existing PartnershipPermission.

Editors:
CRUD

Viewers:
GET only

Superusers:
full access

Support optional filtering:

GET /api/organization-note-attachments/?note=<note_id>

Use multipart parsers.

Serializer should expose:

- id
- note
- file
- original_name
- uploaded_by
- uploaded_at

uploaded_by and original_name are server-managed/read-only.

Do not expose these attachments in the public API.

---

# 13. Attachment upload behavior

Frontend should allow MULTIPLE files for one Relationship Note.

Do not restrict a note to one file.

The form should support:

<input type="file" multiple>

or a visually improved equivalent without adding a UI framework.

Typical create flow:

1. POST OrganizationNote
2. receive note ID
3. upload selected attachments using the new attachment API
4. refresh notes / attachments

Keep implementation simple.

If a note already exists, user must also be able to add another attachment later.

Do not require editing/recreating the note simply to add a file.

---

# 14. Relationship Note form UI

Existing note form fields remain:

Note
Next step
Follow-up date

Add:

Attachments

The user should be able to choose multiple files.

Show selected filenames before save when practical.

Do not build:

- drag/drop uploader
- file preview framework
- document editor
- upload progress system

Keep it simple.

---

# 15. Existing attachments display

Each Relationship Note should display its files clearly.

Example:

13 Oct 2026 · admin

Discussed student exchange cooperation.

Next step:
Send curriculum

Follow-up:
20 Oct 2026

Attachments
📎 meeting-notes.pdf
📎 proposal.docx

Files must be clickable/openable/downloadable using their media URL.

Use a clean text/file icon presentation.

Do not use large cards for each attachment.

---

# 16. Add files to an existing note

Each existing note with edit permissions should have a small action:

+ Add file

or:

Add attachment

Use whichever matches current UI best.

It must allow adding one or more files without changing the note text.

After upload:

refresh that note's attachments without a full page reload.

---

# 17. Delete an attachment

Allow an editor to remove an attachment.

Use the existing confirmation pattern if appropriate.

Do NOT use browser:

confirm()

Deleting an attachment record should also delete the physical uploaded file from storage if the existing project already has a safe shared file-cleanup approach.

If no file-cleanup mechanism currently exists, implement the smallest safe cleanup specifically for OrganizationNoteAttachment.

Do not build a generic storage framework.

Deleting a note should naturally delete its attachment records through CASCADE and should not leave attachment files orphaned.

Keep implementation focused.

---

# 18. Note edit behavior

Editing an existing Relationship Note must NOT require re-uploading existing files.

Existing attachments remain unless explicitly deleted.

New files may be added separately.

Do not include existing file URLs inside a file input.

---

# 19. Public API privacy

Do NOT expose:

OrganizationNote
OrganizationNoteAttachment
file URLs
uploaded_by
follow_up_date
next_step

through the public Organization API.

Relationship Notes remain internal staff data.

---

# 20. Permissions

Reuse existing:

PartnershipPermission

Do not create another permission system.

Backend remains the source of truth.

If frontend receives HTTP 403, use the existing readable permission-error behavior.

---

# 21. Do not touch working Directions backend logic

Current dynamic Directions behavior works.

Do NOT redesign:

AcademicUnit
OrganizationAcademicUnit
academic_unit_ids
organization filtering by academic_unit

Directions continue to be managed through Django Admin.

Normal frontend users only SELECT existing Directions.

This iteration only changes their presentation in the UI.

---

# 22. Do not touch working Notes logic unnecessarily

Current Relationship Notes work.

Preserve:

create
edit
delete
next step
follow-up date
audit fields
ordering

Only extend Notes with attachments.

---

# 23. General design direction

The application should look like a professional internal university management system.

Use the existing design language:

- restrained blue navigation
- light page background
- white cards/modals
- subtle borders
- moderate border radius
- consistent spacing
- no flashy gradients
- no excessive animations

Do not perform a complete visual redesign in this iteration.

This is targeted polish.

---

# 24. DRY

Before changing anything inspect:

frontend:
- AppLayout.vue
- OrganizationsView.vue
- OrganizationDetailView.vue
- ActionMenu.vue
- ConfirmDialog.vue
- style.css
- router
- existing organization modal logic
- existing note UI

backend:
- models.py
- serializers.py
- views.py
- urls.py
- admin.py
- upload path helpers
- PartnershipPermission
- existing file models

Reuse existing:

- Axios client
- auth store
- ActionMenu
- ConfirmDialog
- modal styles
- button styles
- error handling
- audit helpers
- permissions

Do not duplicate working logic.

---

# 25. Migration

A schema migration is expected ONLY for:

OrganizationNoteAttachment

Do not modify old migrations.

Do not delete db.sqlite3.

Do not delete existing OrganizationNotes.

Do not recreate tables.

Run:

python manage.py makemigrations partnerships

Inspect the migration.

Then:

python manage.py migrate

---

# 26. No automated tests

DO NOT:

- create tests
- modify tests
- run tests
- repair old test expectations

Do NOT run:

python manage.py test

The user will manually inspect functionality.

---

# 27. Minimal validation only

Run only:

Backend:

python manage.py migrate

python manage.py check

Frontend:

npm run build

Do not run automated tests.

Fix only errors caused by this iteration.

---

# 28. Explicit non-goals

DO NOT implement:

- deployment
- VPS configuration
- Docker deployment
- Nginx
- Gunicorn
- PostgreSQL migration
- GitHub Actions
- GitLab CI
- CI/CD
- repository splitting
- frontend/backend server separation
- Dashboard functionality
- Investments
- AI Analyst
- AI Report Generator
- notification system
- email
- calendar
- task management
- new Organization statuses
- Academic Unit management frontend

Deployment and CI/CD will be handled in a later iteration.

---

# 29. Final manual behavior expected

After implementation:

Sidebar:

Dashboard
Organizations

No Partnerships item.

---

Add/Edit Organization:

Directions appear as wrapping selectable tiles.

Unselected:
neutral gray

Selected:
green

Multiple Directions may be selected.

No internal Directions scrollbar.

---

Organizations list:

Directions appear as small badges.

---

Actions:

Only one menu may be open.

Opening another closes the first.

Click outside closes it.

Escape closes it.

Bottom-row menus remain fully visible and are never clipped.

---

Relationship Note:

Note text
Next step
Follow-up date
Attachments

Multiple files can belong to one note.

Existing notes can receive additional files later.

Existing attachments remain during note editing.

---

# Final output

Return only:

CHANGED FILES

SIDEBAR CHANGES

DIRECTIONS UI CHANGES

ACTION MENU FIX

ATTACHMENT MODEL/API

RELATIONSHIP NOTES UI

MIGRATION

CHECKS RUN

REMAINING BLOCKERS

ITERATION STATUS: COMPLETE or INCOMPLETE