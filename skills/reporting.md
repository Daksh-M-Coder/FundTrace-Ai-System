---
name: reporting
description: >
  Structured report generation skill for FundTrace AI. Use this whenever an
  officer or analyst wants a summary report, dashboard overview, bulk statistics,
  trend analysis, or exportable findings. Triggers on: "generate report",
  "summary of fraud alerts", "how many accounts are flagged", "weekly overview",
  "statistics on", "trend in transactions", "export findings", "dashboard summary",
  "top risky accounts", "fraud activity this month", "give me an overview".
  Routes to the agentic chat endpoint with a report-framing system prompt, or
  composes multiple API calls to build a structured output. Always use this
  skill when the officer wants AGGREGATED or SUMMARISED data across the whole
  system rather than a deep dive on a single account (use forensic.md for that).
---

# Reporting Skill — FundTrace AI

## What This Skill Does

Generates **structured, aggregated reports** across the entire FundTrace
database. Reports cover fraud trends, account risk summaries, transaction
volumes, and alert status overviews. All data comes from live SQLite queries
via the agentic loop — no cached snapshots.

---

## Report Types

### 1. System Health Dashboard

A top-level snapshot of the current state:

```
Total accounts       | Active | Frozen | New (last 7 days)
Total transactions   | Today  | This week | This month
Open fraud alerts    | Low | Medium | High risk
Real-time alerts fired (Socket.IO pushes today)
```

**Agentic query pattern:**
```sql
-- Account counts
SELECT
  COUNT(*) AS total,
  SUM(CASE WHEN status='active' THEN 1 ELSE 0 END) AS active,
  SUM(CASE WHEN status='frozen' THEN 1 ELSE 0 END) AS frozen,
  SUM(CASE WHEN created_at > strftime('%s','now','-7 days') THEN 1 ELSE 0 END) AS new_7d
FROM users WHERE role = 'client'

-- Transaction volumes
SELECT
  COUNT(*) AS total_txns,
  SUM(amount) AS total_volume,
  COUNT(CASE WHEN created_at > strftime('%s','now','-1 day') THEN 1 END) AS today
FROM transactions

-- Alert status
SELECT status, risk_score,
  COUNT(*) as count
FROM fraud_alerts
GROUP BY status, CASE WHEN risk_score > 70 THEN 'high'
                      WHEN risk_score > 50 THEN 'medium'
                      ELSE 'low' END
```

---

### 2. Top Risky Accounts Report

Ranked list of accounts with highest aggregate fraud risk:

```sql
SELECT u.unique_code, u.full_name, u.balance, u.status,
       MAX(fa.risk_score) AS max_risk,
       COUNT(fa.id) AS alert_count,
       GROUP_CONCAT(fa.alert_type, ', ') AS alert_types
FROM users u
JOIN fraud_alerts fa ON fa.user_id = u.id
GROUP BY u.id
ORDER BY max_risk DESC, alert_count DESC
LIMIT 20
```

Report columns:
- Account code + name
- Current balance
- Account status (active/frozen)
- Highest single risk score
- Number of fraud alerts total
- Alert types triggered (velocity, structuring, round-trip, etc.)

---

### 3. Fraud Alert Status Report

Overview of all open/closed/reviewing alerts:

```sql
SELECT
  fa.id,
  fa.alert_type,
  fa.risk_score,
  fa.status,
  u.full_name AS account_name,
  u.unique_code,
  datetime(fa.created_at,'unixepoch') AS created
FROM fraud_alerts fa
JOIN users u ON fa.user_id = u.id
WHERE fa.status != 'closed'
ORDER BY fa.risk_score DESC, fa.created_at DESC
LIMIT 50
```

**Alert statuses**: `open`, `reviewing`, `closed`, `escalated`

Officers can update alert status via:
```
PATCH /api/fraud/alerts/:id/status
{ "status": "reviewing" }
```

---

### 4. Transaction Trend Report (Time Series)

Aggregates daily transaction volume over a period:

```sql
SELECT
  date(created_at,'unixepoch') AS day,
  COUNT(*) AS txn_count,
  SUM(amount) AS total_volume,
  AVG(amount) AS avg_amount,
  MAX(fraud_score) AS max_fraud_score
FROM transactions
WHERE created_at > strftime('%s','now','-30 days')
GROUP BY day
ORDER BY day
```

Use this to identify:
- Sudden volume spikes (potential coordinated fraud)
- Days with elevated fraud scores
- Weekday vs weekend patterns

---

### 5. Fraud Pattern Frequency Report

Which fraud patterns are being triggered most:

```sql
SELECT
  alert_type,
  COUNT(*) AS frequency,
  AVG(risk_score) AS avg_risk,
  MAX(risk_score) AS max_risk,
  SUM(CASE WHEN status='open' THEN 1 ELSE 0 END) AS open_count
FROM fraud_alerts
GROUP BY alert_type
ORDER BY frequency DESC
```

Pattern types from `server/fraud.js`:
| Pattern Key | Description |
|-------------|-------------|
| `velocity_spike` | >5 txns in 60 min |
| `round_trip` | A→B + B→A in 24h |
| `structuring` | Multiple txns just below ₹10,000 |
| `dormant_burst` | 90+ day dormancy then sudden activity |
| `new_account_large` | Account < 7 days + txn > ₹50,000 |
| `unusual_hours` | Txn between 1am–5am |

---

### 6. New Accounts Report

Recently registered accounts for KYC review:

```sql
SELECT
  unique_code, full_name, email, phone,
  branch, account_type, status, balance,
  datetime(created_at,'unixepoch') AS registered_at
FROM users
WHERE role = 'client'
  AND created_at > strftime('%s','now','-30 days')
ORDER BY created_at DESC
LIMIT 50
```

Cross-referenced with fraud alerts to flag new accounts already under scrutiny.

---

## Report Output Format

All reports are structured as markdown with:

```
# Report Title
Generated: <timestamp>
Period: <date range>

## Executive Summary
  3–5 bullet points of key findings

## Detailed Findings
  Tables, sorted by risk/relevance

## Flagged Items Requiring Action
  Specific accounts/alerts needing officer attention

## Recommended Next Steps
  Prioritised action list
```

---

## Routing to Agentic Chat

All reports are generated by sending a report-framing prompt to `POST /api/ai/agentic-chat`:

```json
{
  "message": "Generate a [report type] report. Structure it with an executive summary, detailed data tables, and recommended actions. Cover the period [date range].",
  "session_id": "report-<timestamp>"
}
```

The agent autonomously decides which tables to query and how to aggregate.
SSE stream delivers the report progressively.

---

## Officer Portal — Reports Tab

The **AI Analysis tab** quick-query chips include preset report prompts:

| Chip Label | Underlying Query |
|------------|-----------------|
| "Top risky accounts" | Runs top-risky-accounts SQL |
| "Recent fraud alerts" | Lists open alerts sorted by risk |
| "New accounts last 30 days" | New account registration report |
| "Velocity spike victims" | Filters alerts by type=velocity_spike |
| "Round-trip suspects" | Filters alerts by type=round_trip |
| "High-value transfers today" | Top transfers in last 24h |
| "Dormant accounts that woke up" | dormant_burst alert type |
| "Structuring suspects" | structuring alert type |
| "After-hours activity" | unusual_hours alert type |
| "New accounts, large txns" | new_account_large alert type |

---

## API Endpoints Relevant to Reporting

| Method | Path | Auth | Use |
|--------|------|------|-----|
| GET | `/api/fraud/alerts` | Officer | All fraud alerts |
| GET | `/api/fraud/accounts` | Officer | All accounts with risk scores |
| GET | `/api/transactions/all` | Officer | Full transaction history |
| GET | `/api/ai/health` | Public | Agent health check |
| POST | `/api/ai/agentic-chat` | Officer | Generate custom report |

---

## Notes for Claude

- Reports use **live data** — always route through agentic chat so the LLM
  queries the database in real time. Never use stale cached data.
- `created_at` throughout is a Unix epoch integer. Always wrap with
  `datetime(created_at,'unixepoch')` or `date(created_at,'unixepoch')`.
- For time-period reports, use `strftime('%s','now','-N days')` as the
  lower bound — this is SQLite-compatible.
- If asked for a "weekly report" without a specific date, default to the
  last 7 days from today.
- Reports should always end with a **Recommended Next Steps** section —
  officers need actionable guidance, not just data dumps.
- For very large result sets the agent applies `LIMIT 200` automatically.
  If an officer needs more, suggest they narrow the date range or export
  to CSV from the UI.
- Socket.IO real-time alerts only fire for `risk_score > 70`. Lower-risk
  alerts are only visible by querying `fraud_alerts` directly.
