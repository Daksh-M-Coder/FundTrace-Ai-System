# fraud.js — Rule-Based Fraud Engine and Officer APIs

- Purpose: Scores transactions for suspicious patterns and exposes officer endpoints for alerts, accounts, graphs, and stats.

## Scoring
- `scoreFraud(txn, sender, receiver)`:
  - Layering velocity: many outflows in last hour.
  - Circular flow: overlaps and direct round-trips within 24–72h.
  - Structuring: multiple transactions near ₹9–10L.
  - Dormant activation: high-value from dormant account.
  - Profile mismatch: sudden balance behavior anomalies.
  - Receiver inflow velocity.
  - Caps score at 100 and returns list of triggered patterns.
- `createFraudAlert(...)`:
  - Inserts alert with primary pattern and emits `fraud_alert` to officer room.

## Officer Endpoints (all `requireOfficer`)
- GET `/api/fraud/alerts` and `/alerts/:alertId`: list and detail alerts with joins.
- PATCH `/alerts/:alertId`: update alert status.
- POST `/freeze/:userId` and `/unfreeze/:userId`: account status control + notification.
- GET `/accounts`: list client accounts with filters.
- GET `/graph/:userId`: builds fund-flow graph up to depth via BFS.
- GET `/stats`: aggregates for dashboard (counts, volumes, recent txns, pattern breakdown).

## Impact on System
- Connects transaction monitoring to investigation workflow, powering realtime officer dashboard and case management.
