# Iteration 04B — Automatic JWT access token refresh

The existing Django REST + Vue application works.

JWT authentication already exists:

POST /api/auth/token/
POST /api/auth/token/refresh/
GET /api/auth/me/

The frontend already stores:

- access_token
- refresh_token

in localStorage.

Current problem:

When the access token expires, authenticated API requests return 401.
The frontend still considers the user authenticated because the expired access token remains in localStorage.

Implement a SMALL focused authentication reliability patch.

Do NOT redesign authentication.
Do NOT change backend models.
Do NOT add unrelated features.

## Goal

When an authenticated API request receives HTTP 401 because the access token expired:

1. Use the stored refresh_token.
2. POST it to:

   /api/auth/token/refresh/

3. Save the returned new access token.
4. Retry the original failed request exactly once.
5. The user should remain logged in without manual intervention.

If refresh fails:

1. clear access_token
2. clear refresh_token
3. clear current user state
4. redirect user to /login

## DRY

Use the existing Axios client.

Do NOT create a second Axios client.

Keep token logic centralized.

Do not duplicate refresh logic across Vue components.

Use a single response interceptor in the existing API client.

## Infinite loop protection

The retry logic MUST prevent infinite retry loops.

Mark the failed request with something such as:

_originalRequest._retry = true

or an equivalent mechanism.

Do not attempt refresh repeatedly for the same request.

Do not try to refresh if:

- there is no refresh token
- the failing request itself is /api/auth/token/
- the failing request itself is /api/auth/token/refresh/

## Concurrent requests

Keep implementation simple.

Do not build a large authentication framework.

If several requests fail simultaneously, avoid obviously unnecessary repeated refresh calls if this can be done with a small implementation.

Do not over-engineer.

## Auth store

Reuse the existing Pinia auth store.

Ensure logout clears:

- access token
- refresh token
- current user

Existing login behavior must continue working.

## Router

Existing protected routes must continue working.

After an unrecoverable authentication failure, user must end up on:

/login

Do not create new routes.

## Backend

Do not change Django authentication behavior unless required.

Do not increase access token lifetime merely to hide the issue.

Existing SimpleJWT refresh endpoint should be used.

## Validation

Run separately:

Backend:

python manage.py check
python manage.py test partnerships

Frontend:

npm run build

Do not chain commands.

Fix only errors caused by this iteration.

Stop once checks pass.

Final answer:

CHANGED FILES
AUTH FLOW
CHECKS RUN
REMAINING BLOCKERS
ITERATION STATUS: COMPLETE or INCOMPLETE