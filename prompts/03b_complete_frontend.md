# Iteration 03B — Complete the existing Vue frontend

The Vue frontend was partially created in the previous iteration.

DO NOT recreate the project.
DO NOT rewrite working files unnecessarily.
DO NOT change backend models.
DO NOT add new product features.

Existing working files include:

frontend/package.json
frontend/index.html
frontend/vite.config.js
frontend/.env.example
frontend/src/main.js
frontend/src/api/client.js
frontend/src/stores/auth.js

Current frontend build fails because required files are missing.

## Current build errors

Missing:

- src/App.vue
- src/router
- src/style.css

The previous iteration also did not finish:

- Login page
- authenticated app layout
- organizations page
- router guards
- organization search
- organization type filter

Complete ONLY these missing pieces.

## Required files

Create:

frontend/src/App.vue

frontend/src/router/index.js

frontend/src/layouts/AppLayout.vue

frontend/src/views/LoginView.vue

frontend/src/views/OrganizationsView.vue

frontend/src/style.css

Do not replace existing api/client.js or stores/auth.js unless a small compatibility fix is necessary.

## Router

Routes:

/login
/organizations
/

Behavior:

- unauthenticated user -> /login
- authenticated user -> protected pages
- / should redirect to /organizations for now
- authenticated user visiting /login should redirect to /organizations

Use Pinia auth store.

## Login page

Fields:

- username
- password

Use existing auth store login().

On successful login:
redirect to /organizations

On failure:
show clean error message.

## Application layout

Professional internal university style.

Left sidebar:

- Dashboard
- Partnerships
- Organizations

Only Organizations must be active/functional now.

Top area:

- Partnership Management
- current user's name or username
- Logout button

Logout:
clear auth state
redirect to /login

## Organizations page

Fetch:

GET /api/organizations/

Use existing Axios client.

Display:

- name
- organization_type
- country
- website

Add:

- search by name
- organization type filter

Type labels:

UNIVERSITY -> University
COMPANY -> Company
GOVERNMENT -> Government
NGO -> NGO
OTHER -> Other

Handle:

- loading
- empty result
- API error

Do not build create/edit/delete UI yet.

## Styling

Create a clean, restrained, professional admin UI.

No large UI framework.

Use responsive CSS.

## Vite warning

Fix the Vite ESM warning cleanly.

Preferred:
add `"type": "module"` to frontend/package.json

Do not introduce unrelated config.

## Validation

Run commands separately:

npm run build

Then:

cd ../backend

python manage.py check

If build fails, fix only the reported frontend errors and rerun.

Stop once both pass.

Final output:

CHANGED FILES
BUILD RESULT
BACKEND CHECK
REMAINING BLOCKERS
ITERATION STATUS: COMPLETE or INCOMPLETE