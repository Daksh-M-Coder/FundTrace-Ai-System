# FundTrace Knowledge Base

## Regulatory Framework (India)
- **PMLA 2002**: Prevention of Money Laundering Act — primary law governing AML in India
- **FIU-IND**: Financial Intelligence Unit India — receives Suspicious Transaction Reports (STRs)
- **STR Obligation**: Banks must file STR within 7 days of suspicion arising
- **CTR Threshold**: Cash Transaction Reports required for cash transactions ≥ ₹10,00,000
- **STR Threshold**: No minimum — any suspicious pattern must be reported
- **Structuring**: Deliberately splitting transactions below ₹10L threshold is an offence under PMLA
- **RTGS Minimum**: ₹2,00,000 per transfer (transactions below this via RTGS are suspicious)

## FundTrace Bank — Internal Thresholds
| Event | Threshold | Action |
|-------|-----------|--------|
| Single transfer | > ₹9,00,000 | Auto-flag for review |
| Outgoing transfers in 1h | ≥ 5 | Velocity alert |
| Dormant account transfer | > ₹50,000 after 30d | Dormant alert |
| Round-trip time | < 72 hours | Circular alert |
| Balance spike | > 5× previous week avg | Profile alert |
| RTGS below minimum | < ₹2,00,000 | Invalid channel alert |

## Database Schema Summary
- `users`: id, unique_code, full_name, email, role, balance, account_number, branch, status, last_active
- `transactions`: id, txn_id, from_user_id, to_user_id, from_account, to_account, amount, channel, note, status, flagged, fraud_score, created_at
- `fraud_alerts`: id, alert_id, user_id, pattern_type, risk_score, description, status
- `friends`: requester_id, receiver_id, status
- `coupons`: code, name, amount, status, redeemed_by
- `notifications`: user_id, type, title, body, read

## Important Query Patterns
```sql
-- Recent transactions for an account
SELECT t.*, s.full_name AS sender, r.full_name AS receiver
FROM transactions t
LEFT JOIN users s ON t.from_user_id = s.id
LEFT JOIN users r ON t.to_user_id = r.id
WHERE t.from_user_id = X OR t.to_user_id = X
ORDER BY t.created_at DESC LIMIT 50;

-- Velocity check (how many txns in last 1 hour)
SELECT COUNT(*), SUM(amount) FROM transactions
WHERE from_user_id = X
AND created_at > (strftime('%s','now') - 3600)
AND status = 'completed';

-- Circular detection (who sent back to origin)
SELECT DISTINCT from_user_id FROM transactions
WHERE to_user_id = X
AND created_at > (strftime('%s','now') - 259200);

-- Account balance history approximation
SELECT created_at, amount, from_user_id, to_user_id
FROM transactions
WHERE from_user_id = X OR to_user_id = X
ORDER BY created_at ASC;
```

## Channels and Their Risk
- **UPI**: Low risk, retail use, instant
- **IMPS**: Low-medium risk, instant, up to ₹5L standard limit
- **NEFT**: Low risk, batch, used for regular payments
- **RTGS**: Medium risk — large value only (≥ ₹2L). Suspicious if used for small amounts
- **COUPON**: Internal — system credit, not user-originated, no fraud risk
- **SWIFT**: HIGH RISK — cross-border, requires enhanced due diligence

## Red Flag Combinations (highest risk)
1. RTGS + amount just below ₹10L + same-day return = CRITICAL
2. Newly activated account + immediate large transfer = HIGH
3. Savings account + corporate-scale volume = HIGH profile mismatch
4. 5+ sequential transfers with decreasing amounts (2-5% reduction) = LAYERING signature
5. SWIFT transfer after domestic circular pattern = potential integration phase

## Officer Decision Guide
| Risk Score | Recommended Action |
|------------|-------------------|
| 0-40 | Automated monitoring, no human needed |
| 41-60 | Officer review within 48h |
| 61-75 | Freeze linked accounts, immediate review |
| 76-85 | Freeze + prepare STR draft |
| 86-100 | Immediate freeze + file STR + escalate to FIU |
