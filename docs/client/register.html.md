# client/register.html — Client Registration

- Purpose: Account creation UI for new clients.
- Flow:
  - Collects name/email/phone/password (+ optional branch/account type).
  - Enforces password strength and basic input validation client-side.
  - Submits to POST `/auth/register`; displays success and redirects after token issuance.
- Impact: Onboards users into the system; triggers welcome notification server-side.
