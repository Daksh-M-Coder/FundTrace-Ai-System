# social.js — Connections and Requests

- Purpose: Manages friend requests, acceptance/rejection, listing, pending requests, removal, and search.
- Auth: All routes require `requireAuth`.

## Routes
- POST `/api/social/request`: send a connection request to a FundTrace ID; prevents self and officer targets; dedups existing relations.
- POST `/api/social/respond`: accept or reject a pending request; notifies requester; emits realtime event.
- GET `/api/social/list`: lists accepted connections with profile info.
- GET `/api/social/requests`: lists incoming and outgoing pending requests.
- DELETE `/api/social/remove/:friendId`: removes an accepted connection.
- GET `/api/social/search?q=...`: searches client users by name/ID/account.

## Impact on System
- Adds social layer and cross-user discovery to improve ease of transfers and notifications.
