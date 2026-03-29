---
name: forensic
description: >
  Deep forensic analysis skill for FundTrace AI. Use this whenever an officer
  requests a full investigation, deep dive, or forensic report on a specific
  account or entity. Triggers on: "forensic analysis", "investigate account",
  "deep dive on", "full report on", "audit this account", "analyse entity",
  "run forensics", or when an officer selects an account and clicks the forensic
  endpoint. Routes to POST /api/ai/forensic and renders a structured risk report
  with transaction patterns, fraud indicators, and timeline. Always use this skill
  when the task is a comprehensive single-account investigation rather than a
  free-form agentic chat query.
---

# Forensic Analysis Skill — FundTrace AI

## What This Skill Does

Performs a **deep, structured forensic report** on a single bank account
identified by its `unique_code` (format: `FT-XXXXXX`). It queries the Python
FraudSense agent's `/forensic` endpoint, which in turn uses the agentic loop
to autonomously pull all relevant data for that entity and return a structured
risk report.

This is distinct from the free-form agentic chat: forensic mode is
**account-scoped, deterministic in structure, and always produces a formal
risk report**.

---

## Endpoint

```
POST /api/ai/forensic
Content-Type: application/json
Authorization: Bearer <officer_jwt>

{
  "unique_code": "FT-A4B2C9"
}
```

The Node.js server at `server/ai.js` proxies this to:

```
POST http://localhost:5002/forensic
```

The Python agent (`ai/agent.py`) handles the `/forensic` route.

---

## What the Agent Does Internally

The agent calls `get_entity(unique_code)` first to load the full account
profile, then autonomously runs SQL queries via the agentic loop to gather:

| Data Point | Tool Used |
|------------|-----------|
| Account profile (name, balance, role, branch, status) | `get_entity` |
| Full transaction history (sent + received) | `query_db` |
| All fraud alerts linked to this account | `query_db` |
| Counterparties (who they transact with most) | `query_db` |
| Velocity pattern (txn count per hour/day) | `query_db` |
| Round-trip detection (A→B then B→A within 24h) | `query_db` |
| Structuring detection (txns just below ₹10,000) | `query_db` |
| Dormancy check (gap > 90 days then sudden burst) | `query_db` |
| New account large txn check (< 7 days + > ₹50,000) | `query_db` |
| Unusual hours activity (1am–5am transactions) | `query_db` |

The agent writes all SQL itself — no hardcoded queries in the forensic path.

---

## Report Structure

The forensic endpoint returns a structured markdown report with these sections:

```
## Account Overview
  – Name, unique_code, balance, account_type, branch, status, created_at

## Transaction Summary
  – Total sent, total received, net flow, transaction count, avg amount

## Fraud Pattern Analysis
  – One section per fraud pattern (see Fraud Detection Engine below)
  – Each pattern: DETECTED / NOT DETECTED + supporting evidence

## Risk Score
  – Composite 0–100 score with breakdown per pattern
  – Threshold:  >50 = Alert,  >70 = High Risk

## Timeline
  – Chronological list of significant events (large txns, fraud alerts, dormancy gaps)

## Recommendation
  – CLEAR / MONITOR / FREEZE with brief justification
```

---

## Fraud Detection Patterns (from server/fraud.js)

| Pattern | Trigger Condition | Score Weight |
|---------|-------------------|--------------|
| Velocity spike | >5 transactions in 60 minutes | +25 |
| Round-trip | A→B + B→A within 24 hours | +30 |
| Structuring | Multiple txns just below ₹10,000 in 1 hour | +35 |
| Dormant account burst | No activity 90+ days → suddenly active | +20 |
| New account large txn | Account < 7 days old + amount > ₹50,000 | +25 |
| Unusual hours | Transaction between 1am–5am | +10 |

---

## Database Columns Available to the Agent

The agent can read (but never write) the following:

```sql
users:
  id, unique_code, full_name, email, phone, role,
  balance, account_number, branch, account_type,
  status, last_active, created_at (INTEGER Unix epoch)

transactions:
  id, from_user_id, to_user_id, amount, channel,
  description, status, fraud_score, created_at

fraud_alerts:
  id, user_id, alert_type, risk_score, description,
  status, metadata_json, created_at
```

**Blocked columns**: `password_hash`, `token_hash`
**Blocked tables**: `sessions`, `login_attempts`

---

## UI Integration (officer/dashboard.html)

The forensic report renders in the **AI Analysis tab** of the officer portal:

- Officer searches for an account (live search by name/code)
- Clicks **"Run Forensic Analysis"**
- Results stream via SSE using the same step-log panel as agentic chat
- Final green card shows the full structured report
- Auto-collapse applies: intermediate tool/observation cards collapse when
  the final answer arrives

---

## Error Handling

| Error | Likely Cause | Fix |
|-------|-------------|-----|
| `Agent not reachable` | Python agent not running | `cd ai && python agent.py --http` |
| `Account not found` | Invalid unique_code | Verify format: `FT-XXXXXX` |
| `Max iterations reached` | Very complex account history | Retry — memory improves on repeat |
| `Forbidden column` | AI tried to read password_hash | Agent-side safety block, safe to ignore |

---

## Notes for Claude

- Always validate `unique_code` format (`FT-[A-Z0-9]{6}`) before calling the endpoint.
- The `created_at` column in `users` is a **Unix epoch integer**, not a datetime string.
  When constructing SQL hints, use `datetime(created_at, 'unixepoch')`.
- The agent has **persistent memory** — after the first forensic run on an account,
  subsequent runs will be faster because schema knowledge is cached in
  `ai/memory/long_term.jsonl`.
- If an officer asks "is this account suspicious?", route to forensic, not agentic chat.
