# Iteration 12 — Dynamic Academic Units + Organization Relationship Notes

The application is already working.

This iteration improves Organization from a simple directory record into a practical workspace for staff who manage university/company partnerships.

IMPORTANT:

Inspect the CURRENT repository before changing anything.

Preserve all working behavior.

Do NOT implement Dashboard, Investments, AI, analytics, notifications, or unrelated future features.

Do NOT add another Responsible Person field in this iteration.
Existing contact/responsibility behavior must remain unchanged.

The scope is ONLY:

1. Dynamic Academic Units
2. Organization ↔ Academic Unit relationships
3. Organization Relationship Notes
4. Organization filtering by Academic Unit
5. Minimal UI required to manage these features

---

# 1. Dynamic Academic Units

Academic units MUST NOT be hard-coded in Vue or Python.

Users must be able to create and modify them through the application.

Examples:

IT & AI Faculty
Artificial Intelligence
Software Engineering
Tourism
Architecture
Business Management

The structure must support future changes without redesigning Organization.

Create model:

AcademicUnit

Fields:

- id
- name
- category
- parent
- is_active
- created_at
- updated_at

## name

Required.

Example:

Tourism

Artificial Intelligence

IT & AI Faculty

## category

Use a normal editable CharField.

DO NOT use hard-coded Django choices.

This is intentionally dynamic.

Examples users may enter:

Faculty
Department
Program
Center
Laboratory
Other

New categories must be possible without source-code changes.

## parent

Nullable self ForeignKey:

AcademicUnit -> AcademicUnit

Use:

on_delete=SET_NULL

related_name="children"

This allows:

IT & AI Faculty
  -> Artificial Intelligence
  -> Software Engineering

or:

Business Faculty
  -> Tourism

or any future structure.

Do NOT assume a fixed:

Faculty -> Department -> Program

hierarchy.

## is_active

Boolean.

Default:

True

Inactive units remain in historical relationships but should not normally be offered when creating new relationships.

## Validation

Prevent:

- AcademicUnit being its own parent
- circular parent structures

Example invalid:

A -> B -> C -> A

Keep validation small and understandable.

---

# 2. Organization Academic Units

One Organization may belong to MANY Academic Units.

One Academic Unit may have MANY Organizations.

Do NOT add:

department = CharField(...)

to Organization.

Do NOT hard-code department/program names.

Create explicit relationship model:

OrganizationAcademicUnit

Fields:

- organization
- academic_unit
- created_at

Add unique constraint:

organization + academic_unit

Also add on Organization:

academic_units = ManyToManyField(
    AcademicUnit,
    through="OrganizationAcademicUnit",
    related_name="organizations"
)

The explicit through-model is intentional so the relationship can be extended later without redesigning the main models.

Do not add unnecessary extra relationship fields yet.

---

# 3. Internal API — Academic Units

Add authenticated endpoint:

/api/academic-units/

Use existing PartnershipPermission.

Editors:
CRUD

Viewers:
GET only

Superusers:
full access

Support:

GET /api/academic-units/

GET /api/academic-units/:id/

POST

PATCH

DELETE may technically remain available through ModelViewSet,
but DO NOT create destructive Delete UI in this iteration.

The UI should use Active / Inactive instead.

Ordering:

active first,
then name.

Use select_related("parent") where appropriate.

---

# 4. Organization Serializer

Extend the INTERNAL Organization API.

Do NOT change the existing PUBLIC organization API response.

Internal Organization responses should expose related Academic Units.

Example:

{
  "id": 1,
  "name": "Huawei",
  ...
  "academic_units": [
    {
      "id": 4,
      "name": "Artificial Intelligence",
      "category": "Program",
      "parent": 1,
      "is_active": true
    }
  ]
}

Also provide a simple writable field:

academic_unit_ids

that accepts a list of AcademicUnit IDs.

Example:

{
  "name": "Huawei",
  ...
  "academic_unit_ids": [4, 5, 6]
}

On create/update:

synchronize OrganizationAcademicUnit relationships.

Use transaction.atomic() so an Organization update and its Academic Unit relationship update do not partially succeed.

When editing:

- retained relationships remain
- removed IDs remove the relationship
- new IDs create the relationship

Do not duplicate relationships.

Do not remove an existing relationship merely because the AcademicUnit later became inactive.

Inactive units may remain historically linked.

---

# 5. Organization filtering

Extend existing:

GET /api/organizations/

with optional:

?academic_unit=<id>

Example:

GET /api/organizations/?academic_unit=8

returns only organizations related to that AcademicUnit.

Do not install django-filter.

Use a small get_queryset() change.

Use distinct() if necessary.

Preserve current behavior when the parameter is absent.

---

# 6. Organization Relationship Notes

Do NOT add one large TextField called "note" directly to Organization.

Create a separate model:

OrganizationNote

Purpose:

A lightweight chronological work log for staff managing the relationship with an organization.

Fields:

- organization
- body
- next_step
- follow_up_date
- created_by
- updated_by
- created_at
- updated_at

## organization

ForeignKey Organization

on_delete=CASCADE

related_name="notes"

## body

TextField

Required.

Example:

"Had an online meeting with the university. They are interested in Tourism student exchange."

## next_step

TextField(blank=True)

Example:

"Send the curriculum and wait for confirmation."

## follow_up_date

DateField(null=True, blank=True)

Example:

2026-10-20

This is intentionally included now because later Dashboard and AI can identify relationships that require attention.

## audit fields

Reuse existing:

user_foreign_key()

TimeStampedModel

and existing AuditModelViewSet behavior where possible.

Do not duplicate audit logic.

---

# 7. Organization Notes API

Add:

/api/organization-notes/

Use existing PartnershipPermission.

Editors:
CRUD

Viewers:
GET only

Superusers:
full access

Support filtering:

GET /api/organization-notes/?organization=<id>

When organization is provided:

return notes only for that organization.

Sort:

newest created note first.

Serializer should expose:

- id
- organization
- body
- next_step
- follow_up_date
- created_by
- created_by_name
- updated_by
- created_at
- updated_at

created_by_name is read-only.

A reasonable display may use:

first_name + last_name

falling back to username.

Do not accept created_by/updated_by from client input.

---

# 8. Public API Privacy

VERY IMPORTANT:

Do NOT expose any of the following through the existing public API:

- OrganizationNote
- next_step
- follow_up_date
- created_by
- internal Academic Unit relationships

Preserve the current public organization list/detail behavior unless absolutely necessary.

This iteration is internal staff functionality.

Public API tests must continue passing.

---

# 9. Django Admin

Register:

AcademicUnit
OrganizationAcademicUnit
OrganizationNote

AcademicUnit admin should show:

- name
- category
- parent
- is_active
- updated_at

Useful filters:

- category
- is_active

Search:

- name
- category
- parent__name

OrganizationNote admin should show:

- organization
- short body or body
- follow_up_date
- created_by
- created_at

Filter/search appropriately.

Keep admin implementation simple.

---

# 10. Frontend — Academic Units Management

Create protected route:

/academic-units

Create:

src/views/AcademicUnitsView.vue

Add sidebar navigation:

Academic Units

Do NOT redesign the sidebar.

Page title:

Academic Units

Button:

+ Add Academic Unit

Table:

Name
Category
Parent
Status
Actions

Actions:

Edit
Activate / Deactivate

Use existing:

ActionMenu.vue
ConfirmDialog.vue if genuinely needed
Axios client
modal styles
form styles
permission/error patterns

Do NOT create another action menu or modal system.

## Add/Edit form

Fields:

Name
Category
Parent
Active

Category is FREE TEXT.

Do not use hard-coded options.

Parent should be loaded dynamically from /api/academic-units/.

Prevent selecting itself as parent when editing.

Backend remains authoritative for cycle validation.

After save:

- close/reset modal
- refresh list
- no browser reload

Prevent duplicate submits using the existing safe submitting pattern.

---

# 11. Organization Create/Edit UI

Extend the existing Organization create/edit form.

Add:

Related Academic Units

The choices must come dynamically from:

GET /api/academic-units/

Do NOT hard-code unit names.

Only active units should normally be available for new selection.

If an Organization already has an inactive Academic Unit linked,
do not silently remove it.

Use a simple multi-select or compact checkbox list.

Do NOT install a UI framework.

On Organization save, send:

academic_unit_ids

through the existing Organization POST/PATCH request.

Do not create a second parallel Organization save workflow.

---

# 12. Organizations List

Add a dynamic filter:

Academic Unit: [All ▼]

Populate it from:

/api/academic-units/

When selected, request:

/api/organizations/?academic_unit=<id>

Do not perform all filtering only in the browser.

Existing:

search
organization type filter

must continue working.

Do not break current Organization CRUD.

If practical without making the table cluttered, show a restrained:

Academic Units

column with unit names.

Keep it compact.

Do not redesign the entire table.

---

# 13. Organization Detail

On:

/organizations/:id

show related Academic Units near organization metadata.

Example:

Related Academic Units

[ Tourism ]
[ International Relations ]

If none:

No academic units assigned.

Below organization details add:

Relationship Notes

Button:

+ Add Note

Each note should show:

- created date/time
- created by
- body
- next step if present
- follow-up date if present

Newest first.

Example:

13 Oct 2026 · Akmal Karimov

Had an online meeting with the partner.
They are interested in Tourism cooperation.

Next step:
Send curriculum.

Follow-up:
20 Oct 2026

Each note should use the existing ActionMenu:

Edit
Delete

Delete must use existing ConfirmDialog.

Do not use browser confirm().

---

# 14. Add/Edit Note UI

Fields:

Note
Next step
Follow-up date

Note is required.

POST:

/api/organization-notes/

Payload includes current organization automatically.

Do NOT ask the user to choose Organization again.

Edit:

PATCH /api/organization-notes/:id/

Delete:

DELETE /api/organization-notes/:id/

After create/edit/delete:

refresh only the notes list.

No full browser reload.

Prevent duplicate submissions.

Readable 403 message:

"You do not have permission to perform this action."

---

# 15. Existing Agreement Contacts

DO NOT redesign:

Contact
AgreementContact
OUR_SIDE
PARTNER_SIDE
is_primary

Do NOT create another Responsible Person field.

Do NOT move Agreement contacts to Organization.

Existing Agreement behavior must remain working.

This iteration is about:

Organization Academic Units
+
Organization Relationship Notes

only.

---

# 16. DRY / Architecture

Before writing code inspect existing:

- Organization model
- TimeStampedModel
- user_foreign_key()
- AuditModelViewSet
- PartnershipPermission
- OrganizationSerializer
- OrganizationViewSet
- router
- ActionMenu
- ConfirmDialog
- OrganizationsView
- OrganizationDetailView
- AppLayout
- shared constants
- form styles
- error handling

Reuse existing implementations.

Do NOT create:

- another Axios client
- another permission system
- another auth store
- another action-menu implementation
- another confirmation implementation
- duplicate Organization forms
- static Academic Unit constants

Keep the implementation understandable.

Do not create a generic CMS or settings framework.

---

# 17. Migrations

Schema changes ARE expected in this iteration.

Create only the migration required for:

AcademicUnit
OrganizationAcademicUnit
Organization.academic_units
OrganizationNote

Run:

python manage.py makemigrations partnerships

Inspect the generated migration.

Then:

python manage.py migrate

Do not modify old migrations.

Do not delete db.sqlite3.

Do not delete existing data.

---

# 18. Backend Tests

Add focused tests.

At minimum:

Academic Units:

1. editor can create AcademicUnit
2. viewer cannot create AcademicUnit
3. viewer can GET AcademicUnit
4. editor can PATCH AcademicUnit
5. AcademicUnit cannot parent itself
6. circular hierarchy is rejected

Organization relationships:

7. editor can create/update Organization with academic_unit_ids
8. multiple Academic Units can belong to one Organization
9. same Academic Unit can belong to multiple Organizations
10. duplicate relationship is prevented
11. organizations can be filtered by academic_unit
12. filtering excludes unrelated organizations

Notes:

13. editor can create OrganizationNote
14. created_by is assigned from authenticated user
15. viewer cannot create OrganizationNote
16. viewer can GET notes
17. notes can be filtered by organization
18. notes are returned newest first
19. editor can PATCH note
20. editor can DELETE note

Privacy:

21. public Organization API still does not expose OrganizationNote
22. public Organization API still does not expose internal academic-unit relationship data

Do not duplicate equivalent existing tests.

---

# 19. Frontend Reliability

Every new async form must:

- return immediately if already submitting
- set submitting=true before request
- disable submit button
- close/reset correctly on success
- restore submitting=false in finally
- never allow one click to create duplicate records

Do NOT repeat the previous modal-close bug where close() refuses because submitting=true.

---

# 20. Scope Guard

DO NOT implement:

- Dashboard
- Investments
- AI Report Generator
- AI Analyst
- notifications
- email sending
- calendar integration
- reminder automation
- task completion workflow
- Organization-level Responsible Person
- advanced workflow statuses
- Academic Unit drag-and-drop tree
- permissions per Academic Unit
- public Academic Unit pages
- bulk import
- Excel import
- CSV import
- soft delete framework

Finish only this iteration.

---

# 21. Validation

Run separately.

Backend:

python manage.py check

python manage.py test partnerships

python manage.py makemigrations --check --dry-run --noinput

Frontend:

npm run build

Fix only problems caused by this iteration.

Do not claim completion if checks fail.

Final answer must contain:

CHANGED FILES

MODELS ADDED

API ENDPOINTS

ACADEMIC UNIT BEHAVIOR

ORGANIZATION NOTES BEHAVIOR

FRONTEND CHANGES

TEST COUNT

CHECKS RUN

REMAINING BLOCKERS

ITERATION STATUS: COMPLETE or INCOMPLETE