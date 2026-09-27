# Iteration 08 — Simple Agreement Actions

The current application is working.

Current flow:

Organizations
  -> Organization Detail
      -> Agreements
          -> Agreement Detail

Agreement Detail already shows:

- Overview
- Contacts
- Documents
- Activities

Now add ONLY three simple write actions:

1. Add Contact
2. Upload Document
3. Add Activity

Keep this iteration SMALL and SIMPLE.

Do not redesign the page.
Do not add edit/delete yet.
Do not create a general admin system.

---

# Goal

Agreement page should look conceptually like:

MoU

Overview

Contacts
[+ Add Contact]

Documents
[+ Upload Document]

Activities
[+ Add Activity]

All existing content remains on one page.

---

# Permissions

Reuse existing PartnershipPermission.

Editors:
- may create

Viewers:
- read only

Superusers:
- full access

Backend remains the source of truth.

If a write request returns 403, show:

"You do not have permission to perform this action."

Do not duplicate permission rules in frontend.

---

# Add Contact

On Agreement Detail add:

+ Add Contact

Keep the form simple.

Fields:

- side
- full_name
- position
- email
- phone
- role
- is_primary

Supported side values:

OUR_SIDE
PARTNER_SIDE

## Required backend flow

A contact consists of:

Contact
+
AgreementContact

Do not change this normalized model structure.

Frontend should perform the smallest clean workflow:

1. POST /api/contacts/
2. receive contact id
3. POST /api/agreement-contacts/

with:

- agreement = current agreement id
- contact = created contact id
- side
- role
- is_primary

If creating AgreementContact fails after Contact was created,
show a clear error.

Do not redesign backend models to avoid these two calls.

After success:

- reset/close form
- refresh agreement contacts
- show new contact immediately

---

# Upload Document

Add:

+ Upload Document

Fields:

- title
- document_type
- file
- description

Agreement must automatically be the current agreement.

POST multipart/form-data:

/api/documents/

Include:

agreement=<current agreement id>

Use the existing Axios client.

Do not create another Axios instance.

After success:

- reset/close form
- refresh documents
- display document immediately

---

# Add Activity

Add:

+ Add Activity

Fields:

- activity_type
- title
- activity_date
- description

Agreement automatically equals current agreement.

POST:

/api/activities/

Supported activity types come from existing backend model:

NOTE
MEETING
EMAIL
CALL
STATUS_CHANGE
OTHER

Do not duplicate labels if shared constants already exist.

If needed, add activity type labels to the existing shared partnerships constants file.

After success:

- reset/close form
- refresh activities
- newest activity remains first

---

# Frontend UX

Forms may be:

- small inline panels
OR
- simple modal

Choose the smallest solution consistent with existing UI.

Do not add a UI framework.

Buttons:

+ Add Contact
+ Upload Document
+ Add Activity

Reuse existing button/form styles.

---

# Contacts

Existing grouping remains:

Our side
Partner side

After creation, contact must immediately appear under correct section.

---

# Documents

Existing document list remains.

Uploaded files must remain clickable/openable.

---

# Activities

Existing activities remain sorted newest first.

---

# DRY

Reuse:

- existing Axios client
- auth store
- AppLayout
- shared constants
- existing form styles
- existing API refresh functions where possible
- existing ViewSets
- PartnershipPermission

Do not duplicate:

- auth logic
- API clients
- mappings
- form error formatting
- permission logic

If the Agreement Detail page already has functions such as:

loadContacts()
loadDocuments()
loadActivities()

reuse them after successful creation.

Do not reload the whole browser page.

---

# Backend

Do not change models unless a real bug prevents this iteration.

Existing endpoints should already support:

POST /api/contacts/
POST /api/agreement-contacts/
POST /api/documents/
POST /api/activities/

Preserve filtering by agreement.

---

# Tests

Add focused tests only if missing:

1. editor can create Contact
2. editor can create AgreementContact
3. editor can upload/create Document
4. editor can create Activity
5. viewer cannot create Contact
6. viewer cannot create AgreementContact
7. viewer cannot create Document
8. viewer cannot create Activity

Do not remove existing tests.

---

# Scope Guard

DO NOT implement:

- edit contact
- delete contact
- edit document
- delete document
- edit activity
- delete activity
- edit agreement
- delete agreement
- organization editing
- dashboard
- finance
- analytics
- notifications

This iteration is CREATE + READ only.

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

Stop when checks pass.

Final answer:

CHANGED FILES
BACKEND CHANGES
FRONTEND CHANGES
TEST COUNT
CHECKS RUN
REMAINING BLOCKERS
ITERATION STATUS: COMPLETE or INCOMPLETE