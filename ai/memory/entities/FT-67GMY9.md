# Entity Profile: FT-67GMY9

## Identity
- Name: Unknown
- Account Number: Unknown
- Account Type: Unknown
- Branch: Unknown
- First Flagged: 2026-03-21 16:09 UTC
- Profile Created: 2026-03-21 16:09 UTC

## Risk Escalation
- **2026-03-21 16:09 UTC**: First analysis — risk 50/100 — recommendation: review

## Known Linked Accounts
_(will be updated as network is mapped)_

## Watch Flags
_(patterns to watch for in future transactions)_


## AI Analysis History

### Analysis: 2026-03-21 16:09 UTC
- **Risk Score**: 50/100 (medium)
- **Patterns**: none
- **Recommendation**: review
- **Reasoning**: Agent reached iteration limit without conclusive finding. Manual review recommended.
- **Evidence Cited**: 0 items

- **Open Questions**:   - Inconclusive after maximum iterations

### Analysis: 2026-03-22 19:27 UTC
- **Risk Score**: 65/100 (high)
- **Patterns**: structuring, channel_misuse
- **Recommendation**: review
- **Reasoning**: Large single transaction over internal threshold, suspicious use of COUPON channel for high-value transfer, and transaction velocity suggest potential structuring. No clear circular patterns yet.
- **Evidence Cited**: 3 items
  - TXN-11935: ₹100,000 sent via IMPS (exceeds ₹90,000 auto-flag threshold)
  - TXN-31112: ₹50,000 received via COUPON channel (unusual for this value)
  - 3+ transactions within 120 seconds (1774034465 to 1774035646)
- **Open Questions**:   - Is the COUPON transaction (TXN-31112) related to legitimate promotional activity?
  - Does the account have a history of high-value coupon redemptions?
