# Iteration 17 — Functional Dashboard from Existing Data

## Current Project

This is the EXISTING University Partnership Management System: Django REST Framework backend, Vue 3 frontend, JWT authentication and a local Docker setup. Iteration 16 introduced ownership-based write permissions and private Organization Notes. Preserve all those rules.

First inspect the CURRENT relevant files before modifying them; the repository may have changed since earlier prompts.

## Objective

Replace the placeholder Dashboard navigation item with a useful read-only Dashboard built entirely from existing Organization, Agreement and OrganizationNote data. Show university-wide statistics alongside the logged-in user's organizations and private follow-ups. Do not create new business features.

## Existing Behavior

- Organization has `created_by` and `created_at`.
- Agreement has `organization`, `status`, `expiration_date` and `created_at`.
- OrganizationNote has `organization`, `next_step`, and `follow_up_date`.
- Iteration 16 restricts Notes to the Organization owner and restricts edits to owners.
- The sidebar currently contains a Dashboard placeholder; existing routes include `/organizations`, `/organizations/:id`, and `/agreements/:id`.
- The application already has an Axios API client, Pinia auth store and shared styles.

## Required Changes

### Backend Scope

Inspect and modify only as necessary:
- `workspace/backend/partnerships/views.py`
- `workspace/backend/partnerships/urls.py`
- relevant existing permission helpers, read-only; do not change their behavior.

Add a small authenticated **GET-only** endpoint `/api/dashboard/`, using existing `PartnershipPermission` (or equivalent current authorized read access). Calculate data server-side with efficient Django ORM queries; do not fetch all records and count them in Vue.

Return a consistent JSON response such as:

```json
{
  "summary": {
    "total_organizations": 0,
    "my_organizations": 0,
    "active_agreements": 0,
    "agreements_expiring_30_days": 0
  },
  "my_organizations": [],
  "expiring_agreements": [],
  "my_followups": []
}
```

Definitions:
1. `total_organizations`: count all organizations visible to authenticated partnership users.
2. `my_organizations`: count where `Organization.created_by_id == request.user.id`.
3. `active_agreements`: count all Agreements with status `ACTIVE` (as recorded in the database).
4. `agreements_expiring_30_days`: count Agreements with status `ACTIVE` and `expiration_date` between today's date and 30 days ahead, inclusive. Use Django's timezone-aware local date calculation; exclude null expiration dates.
5. `my_organizations` array: maximum 8 newest organizations created by the current user. Return only `id`, `name`, `organization_type`, `country`, `created_at`.
6. `expiring_agreements` array: maximum 8 of the above expiring agreements, sorted by nearest expiration date. Return `id`, `title`, `organization_id`, `organization_name`, `status`, `expiration_date`.
7. `my_followups` array: maximum 8 OrganizationNotes whose **Organization** has `created_by_id == request.user.id`, whose `follow_up_date` is non-null and not later than 14 days from today, and whose `next_step` is not blank (exclude empty/whitespace-only values where practical). Include overdue follow-ups and sort by ascending follow-up date. Return only `id`, `organization_id`, `organization_name`, `next_step`, `follow_up_date`.

My follow-ups are informational only: the current schema has no completion status. Do not invent statuses or task completion actions. No private Note body, attachments or Note data belonging to other organizations/users may be included in the response. Even superusers should see only their own organization follow-ups in this personalized list. Preserve all existing private Notes APIs and organization ownership logic.

For users without records, return zero counts and empty arrays, not errors or fabricated sample data. Do not expose this API anonymously.

### Frontend Scope

Inspect and modify only as necessary:
- `workspace/frontend/src/router/index.js`
- `workspace/frontend/src/layouts/AppLayout.vue`
- `workspace/frontend/src/views/LoginView.vue`
- `workspace/frontend/src/style.css`
- new `workspace/frontend/src/views/DashboardView.vue`

Implement a clean, responsive Dashboard in the current application's restrained visual style.

The page should contain:
- Title: `Dashboard`, subtitle: `Partnership Management Overview`.
- Four small KPI cards: Total Organizations, My Organizations, Active Agreements, Expiring in 30 Days.
- `My Organizations` section with up to eight linked organization rows; link each to `/organizations/:id`.
- `Agreements Expiring Soon` section with up to eight linked agreement rows; link to `/agreements/:id`, display expiration date and days remaining.
- `My Follow-ups` section with up to eight notes' next steps, linked to their organization; distinguish overdue, today and future due dates in a restrained way.
- Friendly empty states for every section; no fabricated data.
- Loading and readable API error states, with a simple retry action if practical.

Use the existing Axios client with JWT; make one request to `/api/dashboard/` when entering the Dashboard. Do not load full organizations or notes lists just to calculate counts client-side. Reuse existing shared CSS and constants when appropriate. Do not install chart/UI libraries, add complex charts, or create generic abstractions.

Make the sidebar Dashboard item a real `<RouterLink>` to `/dashboard` with appropriate active navigation styling. Add an authenticated `/dashboard` route. Redirect `/` to `/dashboard`. Redirect to Dashboard after successful login and when an already authenticated user visits `/login`. Keep all existing organization and agreement routes working.

## Permissions and Privacy

- Both department accounts can see university-wide aggregated statistics and upcoming Agreement rows; normal existing read permissions apply.
- `My Organizations` must be strictly based on `Organization.created_by_id`, not `updated_by` or the group name.
- `My Follow-ups` must be strictly based on owning the parent Organization, not on the Note's creator alone.
- Do not expose another account's Notes, attachment names or attachment URLs.
- Preserve Iteration 16's backend ownership checks, Note download protection, read/write restrictions, and frontend hiding of unauthorized actions.
- Dashboard is read-only; never grant new editing rights.

## Constraints

- NO DATABASE MODEL CHANGES.
- NO MIGRATIONS.
- NO NEW DEPARTMENT MODEL OR USER MANAGEMENT UI.
- NO NEW FINANCE, AI, NOTIFICATION OR TASK SYSTEM.
- NO CHANGES TO EXISTING PUBLIC API.
- NO NEW THIRD-PARTY PACKAGES.
- NO DOCKER/VPS/DEPLOYMENT CHANGES.
- DO NOT CREATE OR MODIFY AUTOMATED TESTS.
- DO NOT RUN AUTOMATED TEST SUITES (`python manage.py test`).
- Keep changes minimal and preserve existing behavior.

## DRY / Reuse

Reuse existing Django permissions, ORM relationships, Axios client, Pinia authentication, Vue Router, date/label helpers when available, and existing styles. Avoid duplicate access rules and unnecessary API requests.

## Validation

Run only relevant inexpensive checks:
- Backend: `python manage.py check`
- Frontend: `npm run build`

Do not claim manual browser scenarios were executed unless you actually performed them. No deployment or Git push.

## Final Output

Return:

CHANGED FILES

IMPLEMENTATION SUMMARY

DASHBOARD API RESPONSE SHAPE

PERMISSIONS / PRIVACY

CHECKS RUN

REMAINING BLOCKERS

ITERATION STATUS: COMPLETE / INCOMPLETE

Stop once the requested feature is implemented and these checks pass.
