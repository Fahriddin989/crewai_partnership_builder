# Iteration 03 — Vue frontend foundation

The Django REST backend is complete and tested.

Build the FIRST Vue frontend iteration only.

Do NOT redesign the backend models.
Do NOT add finance, analytics, contributions or future features.

## Goal

Create a clean Vue 3 + Vite frontend inside:

workspace/frontend

Use:

- Vue 3
- Vite
- Vue Router
- Axios
- Pinia

Use JavaScript for now unless TypeScript is already naturally configured.

The application is an internal University Partnership Management System.

## Backend

Backend development URL:

http://127.0.0.1:8000

Existing authentication endpoints:

POST /api/auth/token/
POST /api/auth/token/refresh/
GET /api/auth/me/

Existing organizations endpoint:

GET /api/organizations/

Public endpoint:

GET /api/public/organizations/

## Backend CORS

Inspect the Django backend.

If required, add and configure:

django-cors-headers

Allow the Vue development server:

http://localhost:5173
http://127.0.0.1:5173

Do not use CORS_ALLOW_ALL_ORIGINS=True.

Run Django checks after any backend modification.

## Frontend pages

Create only these pages:

### 1. Login

Route:

/login

Fields:

- Username
- Password

Button:

- Sign in

On successful login:

- save JWT access token
- save refresh token
- request /api/auth/me/
- redirect to /

On failed login:

- display a clean error message

Do not expose credentials in logs.

### 2. Main application layout

Authenticated route:

/

Create a clean professional university/admin interface.

Layout:

Left sidebar:
- Dashboard
- Partnerships
- Organizations

For now only Organizations needs real functionality.

Top area:
- application name:
  Partnership Management
- current user's name
- Logout button

The visual style should be:
- modern
- clean
- professional
- not flashy
- suitable for a university internal system

Do not install a large UI framework yet.

Use normal scoped CSS / global CSS.

### 3. Organizations page

Route:

/organizations

Fetch:

GET /api/organizations/

Display partner organizations as a clean list/cards/table.

Each item must show:

- name
- organization_type
- country
- website

Add:

- search field by organization name
- organization type filter

Display types cleanly:

UNIVERSITY -> University
COMPANY -> Company
GOVERNMENT -> Government
NGO -> NGO
OTHER -> Other

Do not build Agreement detail pages yet.

## Authentication architecture

Create an Axios API client.

Automatically attach:

Authorization: Bearer <access token>

Create a Pinia auth store.

Store:

- access token
- refresh token
- current user

Implement:

- login()
- logout()
- loadCurrentUser()

Protect authenticated routes using Vue Router navigation guards.

If user is unauthenticated:
redirect to /login.

Do not overengineer automatic token refresh yet.
It may be added in a later iteration.

## Structure

Prefer a structure similar to:

src/
  api/
    client.js

  stores/
    auth.js

  router/
    index.js

  layouts/
    AppLayout.vue

  views/
    LoginView.vue
    OrganizationsView.vue

  components/

  assets/

## Environment

Do not hardcode API base URL throughout components.

Create:

frontend/.env.example

with:

VITE_API_BASE_URL=http://127.0.0.1:8000

Use:

import.meta.env.VITE_API_BASE_URL

## Validation

Run commands separately.

Backend:

python manage.py check

Frontend:

npm install
npm run build

Do not chain multiple commands with &&.

Fix build errors.

## Scope guard

Do NOT implement:

- Agreement pages
- Activities UI
- Documents UI
- Contact UI
- finance
- contributions
- analytics
- dashboard statistics
- user management
- password reset
- registration
- public website
- elaborate animations

This iteration is only:

LOGIN
+
MAIN LAYOUT
+
ORGANIZATIONS LIST

Stop when these work and frontend build passes.

Final response:

CHANGED FILES
BACKEND CHANGES
FRONTEND STRUCTURE
CHECKS RUN
REMAINING BLOCKERS
ITERATION STATUS: COMPLETE or INCOMPLETE