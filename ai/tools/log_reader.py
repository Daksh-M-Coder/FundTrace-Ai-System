#!/usr/bin/env python3
"""
log_reader.py — Event Log Reader for FraudSense AI Agent
=========================================================
Reads structured JSONL event logs written by logger.js,
filters by account, time window, and event type,
and returns clean formatted context for the LLM.
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime, timezone, timedelta

LOGS_DIR = Path(__file__).parent.parent / "logs"
MAX_EVENTS = 100  # Max events to return in one call

def read_logs(
    account_code: str = None,
    hours: int = 48,
    event_types: list = None,
    limit: int = 50
) -> dict:
    """
    Read and filter event logs.

    Args:
        account_code: FT-XXXXXX code to filter by (optional)
        hours: How many hours back to look (default 48)
        event_types: List of event types to include (optional, all if None)
        limit: Max events to return

    Returns:
        dict with 'events' list and 'summary' string
    """
    limit = min(limit, MAX_EVENTS)
    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
    events = []

    log_file = LOGS_DIR / "events.jsonl"
    if not log_file.exists():
        return {
            "success": True,
            "count": 0,
            "events": [],
            "summary": f"No event log file found at {log_file}. Logger may not have started yet.",
            "filter": {"account_code": account_code, "hours": hours}
        }

    try:
        with open(log_file, "r", encoding="utf-8") as f:
            lines = f.readlines()

        # Read newest first
        for line in reversed(lines):
            line = line.strip()
            if not line:
                continue
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue

            # Time filter
            ts_str = event.get("ts", "")
            if ts_str:
                try:
                    ts = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
                    if ts < cutoff:
                        continue
                except Exception:
                    pass

            # Account filter
            if account_code:
                code = account_code.upper()
                event_str = json.dumps(event)
                if code not in event_str:
                    continue

            # Event type filter
            if event_types:
                if event.get("event") not in event_types:
                    continue

            events.append(event)
            if len(events) >= limit:
                break

    except Exception as e:
        return {"success": False, "error": str(e), "events": [], "count": 0}

    # Generate a readable summary for LLM context
    summary = _summarize_events(events, account_code)

    return {
        "success": True,
        "count": len(events),
        "events": events,
        "summary": summary,
        "filter": {
            "account_code": account_code,
            "hours": hours,
            "event_types": event_types
        }
    }

def _summarize_events(events: list, account_code: str = None) -> str:
    """Create a human-readable summary of events for LLM context."""
    if not events:
        return "No events found matching the filter criteria."

    lines = [f"Event log summary ({len(events)} events):"]
    for e in events[:30]:  # Only summarize first 30
        ts = e.get("ts", "?")[:19].replace("T", " ")
        event_type = e.get("event", "unknown")
        entity = e.get("entity_id", "")
        data = e.get("data", {})

        if event_type == "transaction":
            amt = data.get("amount", "?")
            channel = data.get("channel", "?")
            from_c = data.get("from_code", "?")
            to_c = data.get("to_code", "?")
            lines.append(f"  [{ts}] TXN: {from_c} → {to_c} ₹{amt:,} via {channel}" if isinstance(amt, (int, float)) else f"  [{ts}] TXN: {from_c} → {to_c} ₹{amt} via {channel}")

        elif event_type == "fraud_alert":
            score = data.get("risk_score", "?")
            pattern = data.get("pattern", "?")
            alert_id = data.get("alert_id", "?")
            lines.append(f"  [{ts}] FRAUD ALERT {alert_id}: {pattern} (score: {score})")

        elif event_type == "login":
            status = data.get("status", "?")
            lines.append(f"  [{ts}] LOGIN: {entity} — {status}")

        elif event_type == "account_freeze":
            reason = data.get("reason", "?")
            lines.append(f"  [{ts}] FREEZE: {entity} — {reason}")

        elif event_type == "coupon_redeem":
            code = data.get("coupon_code", "?")
            amt = data.get("amount", "?")
            lines.append(f"  [{ts}] COUPON: {entity} redeemed {code} for ₹{amt}")

        elif event_type == "officer_action":
            action = data.get("action", "?")
            target = data.get("target", "?")
            lines.append(f"  [{ts}] OFFICER: {action} on {target}")

        else:
            lines.append(f"  [{ts}] {event_type.upper()}: {entity}")

    return "\n".join(lines)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--account", help="Account code to filter (e.g. FT-X7K2P9)")
    parser.add_argument("--hours", type=int, default=48, help="Hours back to look")
    parser.add_argument("--type", help="Event type filter")
    parser.add_argument("--limit", type=int, default=50, help="Max events")
    args = parser.parse_args()

    result = read_logs(
        account_code=args.account,
        hours=args.hours,
        event_types=[args.type] if args.type else None,
        limit=args.limit
    )
    print(json.dumps(result, indent=2, default=str))
