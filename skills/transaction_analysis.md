---
name: transaction_analysis
description: >
  Transaction investigation and fund-flow analysis skill for FundTrace AI.
  Use this whenever an officer wants to explore transactions, trace money flows,
  examine fund paths between accounts, investigate suspicious transfers, or
  visualise the network graph of an account's connections. Triggers on:
  "show transactions", "trace funds", "fund flow", "follow the money",
  "graph of account", "BFS from account", "transaction history for",
  "who sent money to", "money trail", "network of", or when rendering the
  Transactions tab graph. Routes to GET /api/transactions/all,
  GET /api/social/graph/:code, and the D3.js force-directed graph in the
  officer portal. Always use this skill when the question is about tracing
  WHERE money moved rather than WHAT fraud patterns exist on an account
  (use forensic.md for that).
---

# Transaction Analysis Skill — FundTrace AI

## What This Skill Does

Investigates **how money moves** through the FundTrace network. This covers:

1. **Transaction history lookup** — all transfers by account, date, amount, channel
2. **Fund-flow graph traversal** — BFS (breadth-first search) from a source account,
   revealing multi-hop money paths
3. **D3.js graph visualisation** — interactive force-directed graph in the officer portal
4. **Counterparty analysis** — who transacts with whom and at what volumes

---

## API Endpoints

### 1. All Transactions (Officer View)

```
GET /api/transactions/all
Authorization: Bearer <officer_jwt>
```

Returns every transaction in the system. Supports query params:

| Param | Type | Description |
|-------|------|-------------|
| `from` | ISO date | Filter from this date |
| `to` | ISO date | Filter to this date |
| `min_amount` | number | Minimum transaction amount (₹) |
| `max_amount` | number | Maximum transaction amount (₹) |
| `account` | string | Filter by unique_code (sender or receiver) |

Response shape:
```json
{
  "transactions": [
    {
      "id": 42,
      "from_user_id": 7,
      "from_code": "FT-A4B2C9",
      "from_name": "Ravi Kumar",
      "to_user_id": 12,
      "to_code": "FT-X9Z1Q3",
      "to_name": "Priya Shah",
      "amount": 9500,
      "channel": "NEFT",
      "description": "rent",
      "status": "completed",
      "fraud_score": 35,
      "created_at": 1718000000
    }
  ]
}
```

> `created_at` is a Unix epoch integer. Convert with `new Date(ts * 1000)` in JS.

---

### 2. Fund-Flow Graph (BFS Traversal)

```
GET /api/social/graph/:code
Authorization: Bearer <officer_jwt>
```

Where `:code` is a `unique_code` like `FT-A4B2C9`.

The server-side BFS in `server/social.js` walks outgoing and incoming
transactions up to N hops deep and returns a graph structure:

```json
{
  "nodes": [
    { "id": "FT-A4B2C9", "name": "Ravi Kumar", "balance": 45000, "risk_score": 60 },
    { "id": "FT-X9Z1Q3", "name": "Priya Shah", "balance": 12000, "risk_score": 10 }
  ],
  "edges": [
    { "from": "FT-A4B2C9", "to": "FT-X9Z1Q3", "amount": 9500, "count": 3 }
  ]
}
```

`risk_score` is the max fraud_alert risk_score linked to that account.

---

### 3. Transaction History (Client View — own history only)

```
GET /api/transactions/history
Authorization: Bearer <client_jwt>
```

Returns only the authenticated user's own transactions.

---

## D3.js Fund-Flow Graph (officer/dashboard.html)

The **Transactions tab** renders a force-directed graph using D3.js:

| Feature | Detail |
|---------|--------|
| Node labels | Human-readable `full_name` (not raw codes) |
| Node colour | 🔴 Red = high risk (>70), 🟡 Yellow = medium (>50), 🟢 Green = low |
| Edge thickness | Proportional to total amount transferred |
| Zoom/pan | D3 zoom behaviour, mouse wheel + drag |
| Node drag | Reposition nodes manually |
| Tooltip on hover | Shows: name, code, balance, risk_score |
| Click on node | Loads that account's forensic analysis |

**Search to start**: Officer types a name/code into the live search box, selects
an account, and the graph renders BFS from that root.

---

## Fraud Score on Transactions

Every transaction in `transactions` table has a `fraud_score` (0–100) computed
at time of transfer by `server/fraud.js`. This score reflects the **transaction-level**
risk, separate from the **account-level** risk in `fraud_alerts`.

| Score Range | Interpretation |
|-------------|----------------|
| 0–30 | Normal |
| 31–50 | Low suspicion |
| 51–70 | Alert created |
| 71–100 | High risk — real-time Socket.IO push to officer portal |

---

## Common Investigation Queries

When an officer asks a transaction question, the agentic loop can run these
patterns directly via `query_db`:

### All transactions from a specific account
```sql
SELECT t.*, u1.full_name AS sender, u2.full_name AS receiver
FROM transactions t
JOIN users u1 ON t.from_user_id = u1.id
JOIN users u2 ON t.to_user_id = u2.id
WHERE u1.unique_code = 'FT-A4B2C9'
ORDER BY t.created_at DESC
LIMIT 50
```

### Round-trip detection
```sql
SELECT a.id, a.from_user_id, a.to_user_id, a.amount AS amount_ab,
       b.amount AS amount_ba,
       datetime(a.created_at,'unixepoch') AS time_a,
       datetime(b.created_at,'unixepoch') AS time_b
FROM transactions a
JOIN transactions b
  ON a.from_user_id = b.to_user_id
 AND a.to_user_id   = b.from_user_id
 AND b.created_at BETWEEN a.created_at AND a.created_at + 86400
WHERE a.from_user_id != a.to_user_id
LIMIT 30
```

### Structuring detection (txns just below ₹10,000 in 1 hour)
```sql
SELECT from_user_id, COUNT(*) as cnt, SUM(amount) as total,
       datetime(MIN(created_at),'unixepoch') as window_start
FROM transactions
WHERE amount BETWEEN 8000 AND 9999
GROUP BY from_user_id, (created_at / 3600)
HAVING cnt >= 2
LIMIT 20
```

### Largest single transfers today
```sql
SELECT t.amount, u1.full_name AS sender, u2.full_name AS receiver,
       datetime(t.created_at,'unixepoch') AS time
FROM transactions t
JOIN users u1 ON t.from_user_id = u1.id
JOIN users u2 ON t.to_user_id = u2.id
WHERE t.created_at > strftime('%s','now','-1 day')
ORDER BY t.amount DESC
LIMIT 20
```

---

## Transaction Channels

The `channel` field in transactions can be:

| Channel | Description |
|---------|-------------|
| `NEFT` | National Electronic Funds Transfer |
| `IMPS` | Immediate Payment Service |
| `UPI` | Unified Payments Interface |
| `RTGS` | Real Time Gross Settlement (large amounts) |
| `internal` | Internal ledger transfer |

---

## Notes for Claude

- Always convert `created_at` (Unix epoch integer) when displaying times:
  `datetime(created_at, 'unixepoch')` in SQLite,  `new Date(ts * 1000)` in JS.
- The graph endpoint is BFS from a **root account** — it does not accept a
  pair of accounts. To trace A→B, start BFS from A and look for B in the
  resulting nodes/edges.
- `fraud_score` on a transaction != `risk_score` on a fraud_alert.
  Transaction score is per-transfer; alert risk is per-account aggregate.
- If asked "show me all suspicious transactions", filter by `fraud_score > 50`.
- If asked "show the network around FT-XXXXX", call the graph BFS endpoint —
  don't try to replicate BFS manually with recursive SQL.
- The agent's `query_db` tool enforces `LIMIT 200`. For pagination hints,
  tell the officer to narrow the date range.
