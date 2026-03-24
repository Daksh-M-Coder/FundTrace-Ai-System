# officer/login.html — Officer Login

- Purpose: Sign-in UI for bank officers to access investigation tools.
- Flow:
  - If authenticated (`getUser()`), redirects to `/officer/dashboard.html`.
  - Posts to `/auth/login`; requires role `officer` to access officer pages.
- Impact: Gateway to protected officer features (alerts, accounts, graph).
