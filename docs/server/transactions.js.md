# transactions.js — Transfers and Notifications

- Purpose: Implements account info, transaction history, recipient lookup, sending money, and notifications.
- Auth: All routes require `requireAuth`.

## Routes
- GET `/api/transactions/account`: returns current user account details.
- GET `/api/transactions/history`: paginated history with joined sender/receiver names.
- GET `/api/transactions/lookup?query=...`: search by FundTrace ID, account number, or partial name; prevents self-transfer.
- POST `/api/transactions/send`:
  - Validates amount and channel (IMPS/NEFT/RTGS/UPI), self-transfer guards, and balance.
  - Atomic debit/credit via `db.transaction`.
  - Persists transaction row and emits realtime events:
    - To recipient: `transaction_received`
    - To officers: `new_transaction`
  - Triggers async fraud scoring; updates `fraud_score` and creates alerts if score > 50.
  - Creates notifications for sender/receiver.
- GET `/api/transactions/:txnId`: details for a specific transaction.
- GET `/api/transactions/notifications/all` + POST `/api/transactions/notifications/read`.

## Impact on System
- Central money movement logic with robust validations and atomicity.
- Couples to fraud module for risk analysis and officer visibility.
