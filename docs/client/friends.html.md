# client/friends.html — Connections

- Purpose: Manage connections (friends) to streamline money transfers.
- Logic:
  - Requires client auth; loads accepted friends via `/social/list`.
  - Shows incoming/outgoing requests via `/social/requests`.
  - Sends requests `/social/request`, responds `/social/respond`, removes `/social/remove/:id`.
  - Realtime notifications on friend requests/acceptances via Socket.IO.
- Impact: Social layer enabling quick targeting for transfers and network visibility.
