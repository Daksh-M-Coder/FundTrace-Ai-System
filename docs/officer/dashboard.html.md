# officer/dashboard.html — Officer Investigation Console

- Purpose: Multi-tab portal for fraud monitoring: Overview, Graph Explorer, Accounts, Fraud Alerts.
- Uses: `/client/js/api.js` helpers and Socket.IO for live feeds.

## Tabs
- Overview: Metrics, live fraud alert feed (`fraud_alert`), live transaction feed, recent txns table.
- Graph Explorer: loads fund-flow via `/fraud/graph/:userId`, renders canvas graph with risk color-coding; supports trace mode and interactions.
- Accounts: lists client accounts via `/fraud/accounts`, filtering, freeze/unfreeze actions.
- Fraud Alerts: lists alerts via `/fraud/alerts`, status updates, quick actions.

## Impact
- Centralizes fraud ops with realtime visibility and investigative tooling tied to backend analytics.
