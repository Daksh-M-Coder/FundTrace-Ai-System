# client/transactions.html — Transaction History

- Purpose: Dedicated page for viewing and filtering full transaction history.
- Logic:
  - Requires client auth; loads paginated `/transactions/history`.
  - Displays direction (sent/received), channel, note, timestamps, amounts.
  - May include basic filters and navigation to specific txn details.
- Impact: Complements dashboard recent list with broader visibility.
