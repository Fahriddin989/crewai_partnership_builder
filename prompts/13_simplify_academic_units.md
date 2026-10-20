# Iteration 13 — Simplify Academic Units into Admin-Managed Directions

The application is working.

The previous Academic Units implementation became more complex than required.

IMPORTANT:

This is a CORRECTION / SIMPLIFICATION iteration.

Do not redesign the application.
Do not recreate working features.
Do not touch Organization Relationship Notes except where absolutely required to keep the application working.

DO NOT create or update automated tests.
DO NOT run `python manage.py test`.

The required concept is simple:

- University administration creates the available directions manually through Django Admin.
- Normal frontend users DO NOT create/edit/delete directions.
- An Organization may be related to one or MANY directions.
- Frontend users only select existing directions when creating/editing an Organization.
- Directions must remain dynamic: no direction names may be hard-coded in Vue or Python.

Example:

UZUM
- Digital Technologies & AI
- Business & Finance

Huawei
- Digital Technologies & AI
- Engineering

A university may belong to:
- Tourism
- Business & Finance

etc.

The number of directions is NOT technically limited to 7.
Initially the administrator may create 7 directions through Django Admin.
More may be added later without code changes.

---

# 1. Simplify AcademicUnit model

KEEP the existing `AcademicUnit` model and existing database records.

Do NOT rename the Django model because that would create unnecessary migration complexity.

Simplify AcademicUnit to only:

- id
- name
- is_active
- created_at
- updated_at

REMOVE:

- category
- parent

REMOVE all hierarchy/circular-parent validation because hierarchy is no longer required.

Do NOT delete existing AcademicUnit records.

Create a new migration that safely removes only:

- category
- parent

Existing:
- names
- active status
- OrganizationAcademicUnit relationships

must remain.

If useful, set Django model Meta:

verbose_name = "Direction"
verbose_name_plural = "Directions"

so Django Admin displays the business terminology clearly.

---

# 2. Keep Organization ↔ AcademicUnit many-to-many

KEEP:

OrganizationAcademicUnit

KEEP:

Organization.academic_units

This relationship is correct and must continue allowing:

one Organization -> many directions

and:

one Direction -> many Organizations

Example:

UZUM
  -> Digital Technologies & AI
  -> Business & Finance

Do not replace this with a CharField.

Do not limit Organization to one direction.

Do not hard-code direction names.

---

# 3. Django Admin is the ONLY management UI for Directions

Directions are managed through Django Admin.

Update AcademicUnit admin so it is simple.

Display:

- name
- is_active
- updated_at

Filters:

- is_active

Search:

- name

Administrator must be able to:

- create direction
- rename direction
- activate/deactivate direction

No category.
No parent.
No hierarchy.

Existing OrganizationAcademicUnit admin may remain if useful.

---

# 4. Academic Units frontend page must be REMOVED

Remove the frontend management page:

AcademicUnitsView.vue

Remove route:

/academic-units

Remove:

Academic Units

from the sidebar navigation.

Normal frontend users must NOT see:

- + Add Academic Unit
- Category
- Parent
- Active/Inactive management screen
- Academic Unit edit actions

Do not leave dead navigation.

If AcademicUnitsView.vue becomes completely unused, delete the file.

Do not redesign the rest of the sidebar.

---

# 5. Keep a read-only internal Directions API for frontend selection

Frontend still needs to retrieve directions dynamically.

Keep:

GET /api/academic-units/

GET /api/academic-units/:id/

The frontend uses this endpoint to populate Organization forms and filters.

Normal application API users should not need POST/PATCH/DELETE for directions.

Prefer making AcademicUnit API read-only using an appropriate DRF read-only viewset.

Django Admin remains the place for managing directions.

Authentication and existing read permissions remain required.

Do not create a second API endpoint such as `/api/directions/`.

Keep the existing endpoint to avoid unnecessary frontend changes.

---

# 6. Simplify AcademicUnit serializer

AcademicUnitSerializer should expose only:

- id
- name
- is_active
- created_at
- updated_at

Remove:

- category
- parent

Remove hierarchy validation.

---

# 7. Organization Create/Edit

Keep dynamic direction selection in existing Organization Create/Edit forms.

Rename the frontend label from:

Related Academic Units

to:

Related Directions

or:

Directions

Use whichever fits the existing UI best.

Load choices dynamically from:

GET /api/academic-units/

DO NOT hard-code names.

Example:

Directions

[x] Digital Technologies & AI
[x] Business & Finance
[ ] Engineering
[ ] Medicine

One Organization may have multiple selected directions.

Keep existing `academic_unit_ids` save behavior.

Do not create another save workflow.

---

# 8. Active / inactive behavior

For creating NEW relationships:

show only active directions.

However:

If an Organization is already linked to a direction that later becomes inactive,
the relationship must NOT silently disappear when editing unrelated Organization fields.

Existing inactive linked directions should remain visible when editing that Organization.

Do not automatically delete historical relationships.

---

# 9. Organization Detail

Keep displaying the related directions on:

/organizations/:id

Change wording from:

Related Academic Units

to:

Directions

Example:

Directions

[ Digital Technologies & AI ]
[ Business & Finance ]

If none:

No directions assigned.

Do not change Agreements.
Do not change Photo Reports.
Do not change Relationship Notes.

---

# 10. Organizations list/filter

Keep the dynamic direction filter.

Rename label from:

Academic Unit

to:

Direction

Example:

Direction: [ All Directions ▼ ]

Options come dynamically from the backend.

Selecting:

Digital Technologies & AI

must return organizations associated with that direction.

Keep server-side filtering:

GET /api/organizations/?academic_unit=<id>

Do not rename this query parameter in this iteration.
The internal API name may remain `academic_unit` to avoid unnecessary changes.

If Organizations table currently shows:

Academic Units

rename the column to:

Directions

Keep display compact.

---

# 11. Relationship Notes

IMPORTANT:

Organization Notes are working correctly.

DO NOT redesign or remove:

OrganizationNote
body
next_step
follow_up_date
created_by
updated_by
created_at
updated_at

Do not alter Notes UI behavior.

Do not alter Notes API behavior.

Only make a change there if required to prevent an actual regression caused by this iteration.

---

# 12. Existing Agreement logic

Do not change:

Agreement
Contact
AgreementContact
Document
Activity
OrganizationMedia

Do not add Responsible Person.

Do not change OUR_SIDE / PARTNER_SIDE behavior.

Do not change existing agreement pages.

---

# 13. Public API

Do not expose Directions through the public API.

Preserve current public Organization API response exactly.

Do not expose Organization Notes publicly.

---

# 14. Remove obsolete hierarchy code

Search the current repository for logic related to the removed AcademicUnit hierarchy.

Remove only obsolete references to:

category
parent
parent selection
hierarchy validation
circular validation
Academic Units management frontend

Do not remove unrelated code.

Do not leave frontend code trying to access:

unit.category
unit.parent

after those fields are removed.

---

# 15. Migration safety

Create a NEW migration.

Do NOT modify migration 0006.

Do NOT delete db.sqlite3.

Do NOT recreate AcademicUnit.

Do NOT recreate OrganizationAcademicUnit.

Do NOT lose existing Organization ↔ AcademicUnit relationships.

The new migration should only perform the schema simplification required by this iteration.

Run:

python manage.py makemigrations partnerships

Then:

python manage.py migrate

---

# 16. No automated tests

Do NOT:

- create tests
- update tests
- run tests
- spend time repairing old test expectations

Do not run:

python manage.py test

The user will verify application behavior manually.

Existing tests.py may remain untouched.

---

# 17. Minimal validation only

Run only:

Backend:

python manage.py migrate

python manage.py check

Frontend:

npm run build

Do NOT run automated tests.

Fix only errors caused by this iteration.

---

# 18. Scope Guard

DO NOT implement:

- Dashboard
- Investments
- AI
- reports
- notifications
- reminders
- new permissions
- Faculty hierarchy
- Department hierarchy
- Program hierarchy
- Direction management frontend
- drag/drop
- additional Organization statuses
- Responsible Person
- new Note features

This iteration ONLY simplifies Academic Units into admin-managed Directions.

---

# Final output

Return only:

CHANGED FILES

WHAT WAS REMOVED

WHAT WAS PRESERVED

DIRECTIONS BEHAVIOR

DJANGO ADMIN CHANGES

FRONTEND CHANGES

MIGRATION

CHECKS RUN

REMAINING BLOCKERS

ITERATION STATUS: COMPLETE or INCOMPLETE