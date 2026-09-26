# Iteration 01 — Backend foundation

We are building a scalable University Partnership Management System.

For this iteration work ONLY on the Django REST Framework backend.
Do NOT build the Vue frontend yet.

The platform will eventually become a large system used by university staff, international relations, deans, finance, rectorate and other departments. Keep the first iteration small, but design the data model so future features can be added without redesigning Organization and Agreement.

## Goal
Create a working Django REST Framework backend for managing partner organizations, agreements, contacts, documents and activities.

Use SQLite for this development iteration.
Create the Django project inside `workspace/backend` and create a Django app named `partnerships`.

## Models

### Organization
Fields:
- name
- organization_type: UNIVERSITY, COMPANY, GOVERNMENT, NGO, OTHER
- country
- website
- description
- is_public
- created_by
- updated_by
- created_at
- updated_at

One organization can have many agreements.
Example: Huawei -> MoU 2024, Huawei ICT Academy, Cooperation Agreement 2026.

### Agreement
Fields:
- organization: ForeignKey to Organization
- title
- agreement_type: MOU, MOA, ACADEMY, PARTNERSHIP, EXCHANGE, NDA, OTHER
- status: DRAFT, ACTIVE, INACTIVE, EXPIRED, UNDER_RENEWAL
- description
- signed_date
- start_date
- expiration_date
- created_by
- updated_by
- created_at
- updated_at

Do not assume only one agreement per organization.

### Contact
Fields:
- full_name
- organization: nullable ForeignKey to Organization
- position
- email
- phone
- notes
- created_at
- updated_at

A Contact can represent a partner employee or an internal university employee. Internal contacts may have organization = null.

### AgreementContact
Fields:
- agreement: ForeignKey
- contact: ForeignKey
- side: OUR_SIDE or PARTNER_SIDE
- role
- is_primary

Use this model so an agreement can have multiple contacts on both sides.

### Document
Fields:
- agreement: ForeignKey
- title
- document_type
- file
- description
- uploaded_by
- uploaded_at

An Agreement can have unlimited documents. Do not store one document directly on Agreement.

### Activity
Fields:
- agreement: ForeignKey
- title
- activity_date
- description
- created_by
- updated_by
- created_at
- updated_at

An Agreement can have unlimited activities.

## Django Admin
Register all models with useful `list_display`, `search_fields`, and `list_filter`.

## REST API
Install and configure Django REST Framework.
Create serializers and ModelViewSets.
Create authenticated internal endpoints:
- /api/organizations/
- /api/agreements/
- /api/contacts/
- /api/agreement-contacts/
- /api/documents/
- /api/activities/

For this iteration, Django session authentication and DRF default authentication are sufficient. Do not implement JWT yet.

## Public API
Create `GET /api/public/organizations/`.
This endpoint must allow unauthenticated access, be read-only, and expose only:
- id
- name
- organization_type
- country
- website

Do not expose contacts, documents, descriptions, users, created_by or updated_by.

## Media uploads
Configure MEDIA_ROOT and MEDIA_URL correctly for local development. Documents must upload into a sensible folder structure.

## Audit-ready foundation
Keep created_by, updated_by, created_at and updated_at on core models where requested. We will add full audit history later.

Do NOT implement Contribution, finance, analytics, notifications or audit history yet. The architecture must allow them later without redesigning Organization and Agreement.

## Validation
Create and run migrations. Run `python manage.py check`. Fix all errors that can be fixed.

## Documentation
Create `workspace/backend/README.md` with exact local commands to create a virtual environment, install dependencies, migrate, create a superuser and runserver. Also document the public and internal endpoints.

## Scope guard
BACKEND ONLY. Do not create Vue, frontend, dashboards, JWT, finance, analytics, notifications or advanced roles. Finish only this backend foundation and leave it clean and runnable.
