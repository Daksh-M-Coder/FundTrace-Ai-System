# client/dashboard.html — Client Dashboard

- Purpose: Authenticated landing for clients showing balance, quick actions, send money form, recent transactions, and notifications.
- Uses: `/client/js/api.js` helpers and Socket.IO for realtime updates.

## Key UI/Logic
- Balance card: shows available balance, account number, and unique FundTrace ID.
- Stats: totals for sent/received and transaction count.
- Send Money form:
  - Recipient lookup via `/transactions/lookup` (ID/account/name).
  - Amount/channel validation (RTGS minimum ₹2L).
  - POST `/transactions/send`, updates balance, shows success modal.
- Recent transactions list with direction, channel, time-ago.
- Notifications panel: loads `/transactions/notifications/all`, marks all read via `/transactions/notifications/read`.
- Realtime: on `transaction_received`, refresh transactions and balance.

## Impact
- Central user workflow page integrating transfer, history, and notifications.
