# client/js/api.js — Client Utilities

- Purpose: Common client-side helpers for API requests, auth, toasts, formatting, sockets, and form UX.

## HTTP and Auth
- `request(method, url, body)`: fetch wrapper hitting `/api/*` with JSON and `credentials: 'include'` (sends httpOnly cookie).
- `api.get/post/patch/del`: thin wrappers.
- `getUser()`: caches current user via `/auth/me`.
- `requireLogin(expectedRole)`: redirects to login if unauthenticated or wrong role.
- `logout()` / `officerLogout()`: calls `/auth/logout` and redirects.

## UI Helpers
- Toasts: `showToast` with container and styling.
- Formatting: currency, date, time-ago, initials.
- Socket.IO: `initSocket(callbacks)` loads `/socket.io/socket.io.js`, connects, and registers handlers for transaction/friend/fraud events.
- Form helpers: `setLoading`, `showError`, `clearError`.

## Impact
- Standardizes API access, auth flow, realtime wiring, and small UI conveniences across client and officer UIs.
