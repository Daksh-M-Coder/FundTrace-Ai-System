# client/login.html — Client Login

- Purpose: Sign-in form for clients with simple validation and redirects.
- Flow:
  - If already authenticated (`getUser()`), redirects to `/client/dashboard.html`.
  - On submit, POST `/auth/login` with email/password.
  - On success, shows toast and redirects to client dashboard (or officer if role is officer).
  - Supports Enter key shortcut and password show/hide.

## Impact
- Entry point into the authenticated experience; interacts with rate-limited auth API.
