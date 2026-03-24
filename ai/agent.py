#!/usr/bin/env python3
"""
agent.py — FraudSense AI Agent Orchestrator
============================================
Main entry point. Implements the ReAct (Reason + Act) loop:

  1. Build context from memory + live data
  2. Call LLM
  3. If LLM wants a tool → run tool → add result → call LLM again
  4. Repeat up to MAX_ITERATIONS
  5. Save final analysis to memory
  6. Return result to caller (Node.js server or CLI)

Usage:
  python agent.py --alert-id ALT-0892 --user-id 42
  python agent.py --http   (starts HTTP server on port 5002)
"""

import json
import sys
import os
import argparse
import time
from pathlib import Path
from datetime import datetime, timezone

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.context_builder import build_prompt
from core.llm_client import call_llm, extract_json_from_response
from core.memory_writer import write_episode, update_entity_profile
from tools.db_tool import run_query
from tools.log_reader import read_logs

MAX_ITERATIONS = 5  # Max tool-use cycles before forcing conclusion
DB_PATH = Path(__file__).parent.parent / "server" / "fundtrace.db"

# ─── TOOL RUNNER ─────────────────────────────────────────────────────────────

def run_tool(tool_name: str, tool_input: str) -> str:
    """Execute a tool and return result as string."""
    if tool_name == "query_db":
        result = run_query(tool_input)
        if result["success"]:
            rows = result["rows"]
            return f"Query returned {result['count']} rows:\n{json.dumps(rows[:15], indent=2, default=str)}"
        else:
            return f"Query error: {result['error']}"

    elif tool_name == "read_logs":
        # Parse params: "account_code=FT-X7K2P9|hours=48"
        params = {}
        for part in tool_input.split("|"):
            if "=" in part:
                k, v = part.split("=", 1)
                params[k.strip()] = v.strip()
        result = read_logs(
            account_code=params.get("account_code"),
            hours=int(params.get("hours", 48)),
            limit=int(params.get("limit", 30))
        )
        return result.get("summary", "No events found")

    elif tool_name == "read_entity_profile":
        safe = tool_input.strip().upper().replace("FT-", "FT-")
        profile_path = Path(__file__).parent / "memory" / "entities" / f"{safe}.md"
        if profile_path.exists():
            return profile_path.read_text(encoding="utf-8")[:2000]
        return f"No entity profile found for {safe}"

    return f"Unknown tool: {tool_name}"

# ─── PRE-LOAD DB DATA ─────────────────────────────────────────────────────────

def preload_alert_data(alert_id: str = None, user_id: int = None) -> dict:
    """Pre-load key data before starting the agent loop."""
    preload = {}

    if alert_id:
        result = run_query(f"""
            SELECT fa.*, u.full_name, u.unique_code, u.account_number, u.branch, u.balance,
                   u.status as account_status, t.txn_id, t.amount, t.channel
            FROM fraud_alerts fa
            LEFT JOIN users u ON fa.user_id = u.id
            LEFT JOIN transactions t ON fa.transaction_id = t.id
            WHERE fa.alert_id = '{alert_id}'
        """)
        if result["success"] and result["rows"]:
            preload["alert"] = result["rows"][0]

    if user_id:
        result = run_query(f"""
            SELECT t.*, s.full_name AS sender_name, s.unique_code AS sender_code,
                   r.full_name AS receiver_name, r.unique_code AS receiver_code
            FROM transactions t
            LEFT JOIN users s ON t.from_user_id = s.id
            LEFT JOIN users r ON t.to_user_id = r.id
            WHERE t.from_user_id = {user_id} OR t.to_user_id = {user_id}
            ORDER BY t.created_at DESC LIMIT 30
        """)
        if result["success"]:
            preload["recent_transactions"] = result["rows"]

    return preload

# ─── MAIN AGENT LOOP ──────────────────────────────────────────────────────────

def analyze(
    task: str,
    entity_code: str = None,
    pattern: str = None,
    alert_id: str = None,
    user_id: int = None,
    verbose: bool = False,
    backend: str = None,
    model: str = None
) -> dict:
    """
    Run the FraudSense analysis agent.
    Returns the final analysis dict.
    """
    start_time = time.time()
    tool_history = []
    iteration = 0
    final_answer = None
    preload = preload_alert_data(alert_id, user_id)

    print(f"\n🤖 FraudSense Agent starting...")
    print(f"   Task: {task[:80]}")
    print(f"   Entity: {entity_code} | Pattern: {pattern}")

    # Initial context build with preloaded data
    db_preload = {"success": True, "rows": list(preload.values())[:1]} if preload else None

    while iteration < MAX_ITERATIONS and final_answer is None:
        iteration += 1
        print(f"\n   Iteration {iteration}/{MAX_ITERATIONS}...")

        # Build prompt with accumulated tool history
        prompt = build_prompt(
            task=task,
            entity_code=entity_code,
            pattern=pattern,
            tool_history=tool_history if tool_history else None,
            db_results=db_preload if iteration == 1 else None,
        )

        if verbose:
            print(f"   Prompt length: {len(prompt)} chars")

        # Call LLM
        llm_result = call_llm(prompt, None, backend=backend, model=model)

        if not llm_result.get("success"):
            error = llm_result.get("error", "Unknown LLM error")
            print(f"   ❌ LLM error: {error}")
            return {
                "success": False,
                "error": error,
                "iterations": iteration,
                "elapsed_s": round(time.time() - start_time, 2)
            }

        raw_text = llm_result.get("text", "")
        if verbose:
            print(f"   LLM response ({len(raw_text)} chars):\n{raw_text[:500]}")

        # Parse LLM response
        parsed = extract_json_from_response(raw_text)

        if not parsed:
            print(f"   ⚠️  Could not parse JSON from LLM response")
            # Try one more time with a simpler prompt
            if iteration < MAX_ITERATIONS:
                tool_history.append({
                    "tool": "system",
                    "input": "parse_error",
                    "output": "Previous response was not valid JSON. Please respond with ONLY valid JSON."
                })
                continue
            break

        thought = parsed.get("thought", "")
        tool_needed = parsed.get("tool_needed", False)
        tool_name = parsed.get("tool", "none")
        tool_input = parsed.get("tool_input", "")
        final_answer = parsed.get("final_answer")

        if verbose:
            print(f"   Thought: {thought[:200]}")
            print(f"   Tool needed: {tool_needed} ({tool_name})")

        # If LLM wants a tool, run it
        if tool_needed and tool_name and tool_name != "none" and final_answer is None:
            print(f"   🔧 Running tool: {tool_name}")
            tool_output = run_tool(tool_name, str(tool_input or ""))
            tool_history.append({
                "tool": tool_name,
                "input": str(tool_input or "")[:200],
                "output": tool_output[:800]
            })
            print(f"   Tool returned {len(tool_output)} chars")

        elif final_answer:
            print(f"   ✅ Final answer: risk={final_answer.get('risk_score')}/100")
            break

    # Fallback if no final answer after all iterations
    if final_answer is None:
        final_answer = {
            "risk_score": 50,
            "risk_level": "medium",
            "patterns_detected": [pattern] if pattern else [],
            "evidence": [],
            "reasoning": "Agent reached iteration limit without conclusive finding. Manual review recommended.",
            "recommendation": "review",
            "confidence": 20,
            "open_questions": ["Inconclusive after maximum iterations"]
        }

    elapsed = round(time.time() - start_time, 2)

    # Save to memory
    try:
        ep_id = write_episode(
            entity_code=entity_code,
            task="fraud_analysis",
            trigger="fraud_alert",
            input_summary=f"Alert {alert_id or 'unknown'} | pattern={pattern} | {task[:200]}",
            output_summary=f"Risk {final_answer.get('risk_score')}/100 | {final_answer.get('recommendation')} | {', '.join(final_answer.get('patterns_detected', []))}",
            risk_score=final_answer.get("risk_score"),
            recommendation=final_answer.get("recommendation"),
            patterns=final_answer.get("patterns_detected"),
            evidence=final_answer.get("evidence"),
            open_questions=final_answer.get("open_questions")
        )

        # Update entity profile if we have account info
        if entity_code:
            update_entity_profile(entity_code, final_answer)

    except Exception as e:
        ep_id = None
        print(f"   ⚠️  Memory write error: {e}")

    return {
        "success": True,
        "episode_id": ep_id,
        "final_answer": final_answer,
        "iterations": iteration,
        "tool_calls": len(tool_history),
        "elapsed_s": elapsed,
        "model": llm_result.get("model"),
        "backend": llm_result.get("backend")
    }

# ─── FORENSIC DEEP ANALYSIS ───────────────────────────────────────────────────

FORENSIC_SYSTEM_PROMPT = """You are FraudSense, a financial forensics AI at FundTrace Bank — like a cyber-crime analyst and AML investigator combined.

Your task: perform a DEEP FORENSIC INVESTIGATION of an account's transaction history.

WRITE A COMPREHENSIVE INVESTIGATION REPORT in this exact structure:

## 🕵️ Investigation Report: [Account Code]

### 📊 Account Overview
[Who is this person, their balance, current status, first/last seen]

### 💸 Transaction Flow Summary
[Summarize: total received vs sent, number of counterparties, timespan of transactions, avg transaction size]

### 🔍 Counterparty Analysis
[For each major counterparty: who they are, how much sent/received, direction, any suspicious timing]

### ⚠️ Suspicious Patterns Detected
[List each pattern found: circular flows, rapid-fire transactions, structuring, dormancy exploitation, etc.]
[If a cycle is detected: "CYCLE DETECTED: FT-XXX → FT-YYY → FT-XXX — funds returned within X hours"]

### 📈 Risk Assessment
[Overall risk level: LOW / MEDIUM / HIGH / CRITICAL]
[Risk score: 0-100]
[Top 3 red flags]

### 🎯 Recommended Actions
[Specific actionable steps for the investigating officer]

Use ALL the data provided. Be specific — cite actual account codes, names, amounts, dates. This is a REAL investigation."""


def forensic_analyze(entity_code: str, backend: str = None, model: str = None) -> dict:
    """
    Full forensic deep-dive on an account:
    1. Extract all transactions (sent + received) from DB
    2. Build flow table + counterparty aggregation
    3. Detect cycles using graph analysis
    4. Generate comprehensive NLP forensic report via LLM
    """
    from core.llm_client import call_llm as _call_llm

    result = {"success": False, "entity_code": entity_code}

    # ── Step 1: Fetch account info ───────────────────────────────────────────
    # Use UPPER() for case-insensitive match; use last_active (correct column name)
    acct_q = f"SELECT id, full_name, email, balance, status, account_number, created_at, last_active FROM users WHERE UPPER(unique_code) = UPPER('{entity_code}') LIMIT 1"
    acct_res = run_query(acct_q)
    if not acct_res["success"] or not acct_res["rows"]:
        return {"success": False, "error": f"Account {entity_code} not found"}
    account = acct_res["rows"][0]
    user_id = account.get("id")

    # ── Step 2: Fetch ALL transactions (sent + received) ─────────────────────
    txn_q = f"""
        SELECT t.txn_id, t.id AS tx_db_id, t.from_user_id, t.to_user_id,
               t.amount, t.channel, t.status, t.created_at, t.fraud_score,
               s.unique_code AS from_code, s.full_name AS from_name,
               r.unique_code AS to_code, r.full_name AS to_name,
               datetime(t.created_at, 'unixepoch') AS txn_date
        FROM transactions t
        LEFT JOIN users s ON t.from_user_id = s.id
        LEFT JOIN users r ON t.to_user_id = r.id
        WHERE t.from_user_id = {user_id} OR t.to_user_id = {user_id}
        ORDER BY t.created_at ASC
    """
    txn_res = run_query(txn_q)
    transactions = txn_res.get("rows", []) if txn_res["success"] else []

    # ── Step 3: Build flow analysis ──────────────────────────────────────────
    counterparties = {}  # code → {name, sent_to, received_from, tx_count}
    total_sent = 0.0
    total_received = 0.0
    high_fraud_txns = []
    channels = {}

    for t in transactions:
        amt = float(t.get("amount", 0))
        fs = float(t.get("fraud_score", 0))
        ch = t.get("channel", "unknown")
        channels[ch] = channels.get(ch, 0) + 1

        # Use user_id comparison (reliable) instead of code string (case issues)
        is_sender = t.get("from_user_id") == user_id
        counterparty_code = t.get("to_code") if is_sender else t.get("from_code")
        counterparty_name = t.get("to_name") if is_sender else t.get("from_name")

        if is_sender:
            total_sent += amt
        else:
            total_received += amt

        cp = counterparties.setdefault(counterparty_code, {
            "name": counterparty_name, "sent_to": 0.0, "received_from": 0.0, "tx_count": 0
        })
        cp["tx_count"] += 1
        if is_sender:
            cp["sent_to"] += amt
        else:
            cp["received_from"] += amt

        if fs >= 60:
            high_fraud_txns.append(t)

    # ── Step 4: Detect cycles ────────────────────────────────────────────────
    cycles = []
    for code, cp in counterparties.items():
        if cp["sent_to"] > 0 and cp["received_from"] > 0 and code != entity_code:
            ratio = min(cp["sent_to"], cp["received_from"]) / max(cp["sent_to"], cp["received_from"])
            if ratio > 0.3:  # money flowed BOTH ways significantly
                cycles.append({
                    "counterparty": code,
                    "name": cp["name"],
                    "sent": cp["sent_to"],
                    "received": cp["received_from"],
                    "ratio": round(ratio, 2)
                })

    # ── Step 5: Build markdown evidence package for LLM ─────────────────────
    txn_table = "| # | Direction | Counterparty | Amount | Channel | Date | Fraud Score |\n"
    txn_table += "|---|-----------|-------------|--------|---------|------|--------------|\n"
    for i, t in enumerate(transactions[:30], 1):
        is_s = t.get("from_user_id") == user_id
        direction = "→ SENT" if is_s else "← RECV"
        cp_code = t.get("to_code") if is_s else t.get("from_code")
        cp_name = t.get("to_name") if is_s else t.get("from_name")
        txn_date = t.get("txn_date") or str(t.get("created_at",""))[:16]
        txn_table += f"| {i} | {direction} | {cp_name} ({cp_code}) | ₹{t.get('amount',0):,.2f} | {t.get('channel','?')} | {txn_date} | {t.get('fraud_score',0)} |\n"

    cp_table = "| Counterparty | Code | Sent To | Received From | Net Flow | # Txns |\n"
    cp_table += "|-------------|------|---------|--------------|----------|--------|\n"
    for code, cp in sorted(counterparties.items(), key=lambda x: -(x[1]["sent_to"]+x[1]["received_from"]))[:15]:
        net = cp["received_from"] - cp["sent_to"]
        net_str = f"+₹{net:,.2f}" if net >= 0 else f"-₹{abs(net):,.2f}"
        cp_table += f"| {cp['name']} | {code} | ₹{cp['sent_to']:,.2f} | ₹{cp['received_from']:,.2f} | {net_str} | {cp['tx_count']} |\n"

    cycle_text = ""
    if cycles:
        cycle_text = "\n### ⚡ CIRCULAR FLOW ALERTS:\n"
        for c in cycles:
            cycle_text += f"- **CYCLE**: {entity_code} ↔ {c['counterparty']} ({c['name']}): sent ₹{c['sent']:,.2f}, received ₹{c['received']:,.2f} (ratio {c['ratio']})\n"

    import datetime as _dt
    def _ts(unix_val):
        try: return _dt.datetime.fromtimestamp(int(unix_val)).strftime('%Y-%m-%d %H:%M')
        except: return str(unix_val)

    evidence_prompt = f"""ACCOUNT UNDER INVESTIGATION: {entity_code}
Name: {account.get('full_name', '?')}
Balance: ₹{account.get('balance', 0):,.2f}
Status: {account.get('status', '?')}
Account #: {account.get('account_number', '?')}
Created: {_ts(account.get('created_at', 0))}
Last Active: {_ts(account.get('last_active', 0))}

FINANCIAL SUMMARY:
- Total transactions analyzed: {len(transactions)}
- Total SENT: ₹{total_sent:,.2f}
- Total RECEIVED: ₹{total_received:,.2f}
- Net: ₹{(total_received - total_sent):,.2f}
- Unique counterparties: {len(counterparties)}
- High fraud-score transactions (≥60): {len(high_fraud_txns)}
- Transaction channels: {dict(channels)}

TRANSACTION LOG (chronological):
{txn_table}

COUNTERPARTY ANALYSIS:
{cp_table}
{cycle_text}
HIGH-FRAUD TRANSACTIONS (fraud_score ≥ 60):
{json.dumps(high_fraud_txns[:10], indent=2, default=str) if high_fraud_txns else "None detected"}

Now write the full forensic investigation report."""

    # ── Step 6: Call LLM for NLP forensic report ────────────────────────────
    llm_res = _call_llm(
        prompt=evidence_prompt,
        system=FORENSIC_SYSTEM_PROMPT,
        backend=backend,
        model=model
    )

    report = llm_res.get("text", "")
    success = llm_res.get("success", False)

    return {
        "success": success,
        "entity_code": entity_code,
        "account": account,
        "report": report,
        "stats": {
            "total_transactions": len(transactions),
            "total_sent": round(total_sent, 2),
            "total_received": round(total_received, 2),
            "net_flow": round(total_received - total_sent, 2),
            "unique_counterparties": len(counterparties),
            "high_fraud_transactions": len(high_fraud_txns),
            "cycles_detected": len(cycles)
        },
        "cycles": cycles,
        "transactions": transactions[:50],
        "counterparties": [
            {"code": k, **v} for k, v in
            sorted(counterparties.items(), key=lambda x: -(x[1]["sent_to"]+x[1]["received_from"]))[:20]
        ],
        "model": llm_res.get("model"),
        "backend": llm_res.get("backend"),
        "error": llm_res.get("error", "")
    }


# ─── SMART CHAT (conversational mode, NOT ReAct/JSON) ────────────────────────

CHAT_SYSTEM_PROMPT = """You are FraudSense, an expert AI fraud analyst at FundTrace Bank. You help officers investigate fraud.

CRITICAL RULES:
1. RESPOND IN NATURAL LANGUAGE ONLY — no JSON, no raw SQL
2. ONLY USE DATA FROM [DATABASE RESULTS] SECTIONS — NEVER invent, guess, or fabricate account names, transaction IDs, amounts, or any numbers
3. If [DATABASE RESULTS] are provided, always present them clearly as a markdown table and explain what they mean
4. If no database results are provided for a data question, say "I don't have that data loaded — try a more specific query" — DO NOT make up fake data
5. Format your responses nicely: use **bold** for key terms, bullet points for lists, and tables for data
6. Be concise and precise — you are an expert, not a chatbot

You can:
- Show and explain real transaction data from the database (when provided)
- Detect fraud patterns in the data
- Explain fraud methodology using general knowledge (clearly mark when speculating)
- Answer questions about FundTrace accounts, alerts, and policies"""

QUERY_KEYWORDS = ["transaction", "account", "balance", "show", "get", "list", "query",
                  "fetch", "find", "first", "top", "recent", "last", "history",
                  "how many", "count", "total", "amount", "transfer", "fraud", "alert",
                  "biggest", "largest", "channel", "circular", "structur", "new account", "repeat",
                  "flagged", "dormant", "balance", "flow", "breakdown", "system"]

def smart_chat(messages: list, entity_code: str = None, backend: str = None, model: str = None) -> dict:
    """
    Conversational chat mode. Returns plain-English reply.
    Auto-queries DB if the user message seems to want data.
    """
    if not messages:
        return {"success": False, "error": "No messages provided", "reply": ""}

    last_user_msg = next((m["content"] for m in reversed(messages) if m.get("role") == "user"), "")
    last_lower = last_user_msg.lower()

    # ── Auto-query DB if message seems data-related ──────────────────────────
    db_context = ""
    needs_data = any(kw in last_lower for kw in QUERY_KEYWORDS)

    if needs_data:
        q = None
        empty_context_msg = None  # Used when query returns 0 rows but we should tell AI why

        lower = last_lower  # alias for readability

        # ── Entity-specific: account transaction history ─────────────────────
        # Only fires when entity_code is set AND the query is clearly about THAT account.
        # Does NOT fire when query has global intent (biggest/largest/all/system/top N etc.)
        _global_intent = ["biggest", "largest", "highest amount", "most expensive", "top 10",
                          "top 5", "all account", "entire", "database", "system", "channel",
                          "breakdown", "total", "list all", "show all", "every account",
                          "top account", "balance", "richest", "repeat", "multiple", "flagged",
                          "alert", "fraud alert", "dormant", "new account", "newly", "recent account"]
        _is_global = any(kw in lower for kw in _global_intent)

        if entity_code and not _is_global and any(kw in lower for kw in ["transaction", "history", "activity", "sent", "received"]):
            q = f"""SELECT t.txn_id, s.full_name AS sender, s.unique_code AS sender_code,
                       r.full_name AS receiver, r.unique_code AS receiver_code,
                       t.amount, t.channel, t.status, t.fraud_score,
                       datetime(t.created_at,'unixepoch') AS date
                FROM transactions t
                LEFT JOIN users s ON t.from_user_id = s.id
                LEFT JOIN users r ON t.to_user_id = r.id
                JOIN users u ON (t.from_user_id = u.id OR t.to_user_id = u.id)
                WHERE UPPER(u.unique_code) = UPPER('{entity_code}')
                ORDER BY t.created_at DESC LIMIT 20"""


        # ── Biggest / largest / highest amount transactions ──────────────────
        elif any(kw in lower for kw in ["biggest", "largest", "highest amount", "most expensive", "largest amount"]):
            limit = 10 if "10" in lower else 5
            q = f"""SELECT t.txn_id, s.full_name AS sender, s.unique_code AS sender_code,
                       r.full_name AS receiver, r.unique_code AS receiver_code,
                       t.amount, t.channel, t.status, t.fraud_score,
                       datetime(t.created_at,'unixepoch') AS date
                FROM transactions t
                LEFT JOIN users s ON t.from_user_id = s.id
                LEFT JOIN users r ON t.to_user_id = r.id
                ORDER BY t.amount DESC LIMIT {limit}"""

        # ── First N transactions ─────────────────────────────────────────────
        elif "first" in lower or ("top 5" in lower and "transaction" in lower) or \
             ("5" in lower and "transaction" in lower and "first" in lower):
            q = """SELECT t.txn_id, s.full_name AS sender, s.unique_code AS sender_code,
                       r.full_name AS receiver, r.unique_code AS receiver_code,
                       t.amount, t.channel, t.status, t.fraud_score,
                       datetime(t.created_at,'unixepoch') AS date
                FROM transactions t
                LEFT JOIN users s ON t.from_user_id = s.id
                LEFT JOIN users r ON t.to_user_id = r.id
                ORDER BY t.id ASC LIMIT 5"""

        # ── High-risk fraud alerts ───────────────────────────────────────────
        elif "high risk" in lower or ("fraud" in lower and "alert" in lower and any(c.isdigit() for c in lower)) \
             or ("score" in lower and "alert" in lower) or ("risk" in lower and "score" in lower and "alert" in lower):
            q = """SELECT fa.alert_id, u.full_name, u.unique_code, fa.risk_score,
                       fa.pattern_type, fa.status,
                       datetime(fa.created_at,'unixepoch') AS created_at
                FROM fraud_alerts fa JOIN users u ON fa.user_id = u.id
                WHERE fa.risk_score >= 70 ORDER BY fa.risk_score DESC LIMIT 10"""
            empty_context_msg = "fraud_alerts table has 0 rows — no fraud alerts have been generated yet. The fraud detection engine creates alerts when suspicious transactions occur."

        # ── Dormant accounts ─────────────────────────────────────────────────
        elif "dormant" in lower:
            q = """SELECT full_name, unique_code, balance,
                datetime(last_active,'unixepoch') AS last_active_date,
                datetime(created_at,'unixepoch') AS created_date
                FROM users WHERE role='client'
                AND last_active < strftime('%s','now','-90 days')
                ORDER BY last_active ASC LIMIT 10"""
            empty_context_msg = "No dormant accounts found (no accounts inactive for 90+ days)."

        # ── Newly / recently created accounts ───────────────────────────────
        elif any(kw in lower for kw in ["new account", "newly created", "recently created",
                                         "new user", "newest account", "registered recently",
                                         "created this month", "created recently", "newest"]) \
             or ("new" in lower and "account" in lower and any(kw in lower for kw in ["last", "recent", "days", "month", "week"])) \
             or ("account" in lower and any(kw in lower for kw in ["last 30", "last 60", "last 90", "last 7", "30 days", "60 days", "90 days", "this month", "this week"])):
            # Extract day count from message (default 30)
            import re as _re
            day_match = _re.search(r'(\d+)\s*day', lower)
            if day_match:
                days = int(day_match.group(1))
            elif "this month" in lower or "30" in lower:
                days = 30
            elif "this week" in lower or "7" in lower:
                days = 7
            elif "60" in lower:
                days = 60
            elif "90" in lower:
                days = 90
            else:
                days = 30
            q = f"""SELECT u.full_name, u.unique_code, u.account_number,
                        ROUND(u.balance, 2) AS balance, u.status,
                        datetime(u.created_at,'unixepoch') AS created_date,
                        COUNT(t.id) AS transaction_count
                FROM users u
                LEFT JOIN transactions t ON (t.from_user_id = u.id OR t.to_user_id = u.id)
                WHERE u.role = 'client'
                  AND u.created_at >= strftime('%s','now','-{days} days')
                GROUP BY u.id
                ORDER BY u.created_at DESC LIMIT 20"""
            empty_context_msg = f"No client accounts were created in the last {days} days."

        # ── All accounts list ────────────────────────────────────────────────
        elif "account" in lower and any(kw in lower for kw in ["list", "all", "show", "every"]):
            q = """SELECT full_name, unique_code, account_number, balance, status,
                datetime(created_at,'unixepoch') AS created_date
                FROM users WHERE role='client' ORDER BY id ASC LIMIT 15"""


        # ── Top N accounts by balance ────────────────────────────────────────
        elif any(kw in lower for kw in ["balance", "top 10", "top account", "richest", "wealthiest"]) \
             and "transaction" not in lower:
            limit = 10 if "10" in lower else 5
            q = f"""SELECT full_name, unique_code, account_number, balance, status
                FROM users WHERE role='client'
                ORDER BY balance DESC LIMIT {limit}"""

        # ── All fraud alerts (recent) ────────────────────────────────────────
        elif "alert" in lower or "fraud" in lower:
            q = """SELECT fa.alert_id, u.full_name, u.unique_code, fa.risk_score,
                       fa.pattern_type, fa.status,
                       datetime(fa.created_at,'unixepoch') AS created_at
                FROM fraud_alerts fa JOIN users u ON fa.user_id = u.id
                ORDER BY fa.created_at DESC LIMIT 10"""
            empty_context_msg = "fraud_alerts table has 0 rows — no fraud alerts have been generated yet. Trigger them by sending suspicious transactions from the client portal."

        # ── Repeat / multiple flagged accounts ───────────────────────────────
        elif "repeat" in lower or "multiple" in lower or "flagged" in lower:
            q = """SELECT u.full_name, u.unique_code, COUNT(fa.id) AS alert_count,
                       MAX(fa.risk_score) AS max_risk_score
                FROM fraud_alerts fa JOIN users u ON fa.user_id = u.id
                GROUP BY fa.user_id ORDER BY alert_count DESC LIMIT 10"""
            empty_context_msg = "fraud_alerts table has 0 rows — no repeat-flagged accounts yet."

        # ── Channel breakdown ────────────────────────────────────────────────
        elif "channel" in lower or "breakdown" in lower:
            q = """SELECT channel, COUNT(*) AS txn_count,
                    ROUND(SUM(amount), 2) AS total_volume,
                    ROUND(AVG(amount), 2) AS avg_amount
                FROM transactions GROUP BY channel ORDER BY txn_count DESC"""

        # ── Total system flow ────────────────────────────────────────────────
        elif "total" in lower or "system" in lower or "flow" in lower:
            q = """SELECT
                    COUNT(*) AS total_transactions,
                    ROUND(SUM(amount), 2) AS total_volume,
                    ROUND(AVG(amount), 2) AS avg_amount,
                    ROUND(MAX(amount), 2) AS largest_transaction,
                    COUNT(CASE WHEN flagged=1 THEN 1 END) AS flagged_count
                FROM transactions"""

        # ── New / recent accounts ─────────────────────────────────────────────
        elif "new" in lower or "recent account" in lower or "latest" in lower:
            q = """SELECT full_name, unique_code, balance, status,
                datetime(created_at,'unixepoch') AS created_date
                FROM users WHERE role='client'
                ORDER BY created_at DESC LIMIT 10"""

        # ── Fallback: recent transactions ordered by amount ───────────────────
        else:
            q = """SELECT t.txn_id, s.full_name AS sender, r.full_name AS receiver,
                       t.amount, t.channel, t.status, t.fraud_score,
                       datetime(t.created_at,'unixepoch') AS date
                FROM transactions t
                LEFT JOIN users s ON t.from_user_id = s.id
                LEFT JOIN users r ON t.to_user_id = r.id
                ORDER BY t.amount DESC LIMIT 10"""

        try:
            result = run_query(q)
            if result["success"] and result["rows"]:
                import csv, io
                rows = result["rows"]
                buf = io.StringIO()
                w = csv.DictWriter(buf, fieldnames=list(rows[0].keys()))
                w.writeheader(); w.writerows(rows)
                db_context = f"\n\n[DATABASE RESULTS — {result['count']} rows]\n{buf.getvalue()}"
            elif empty_context_msg:
                # Inject explicit empty-state so AI can give accurate answer
                db_context = f"\n\n[DATABASE RESULTS — 0 rows]\nNote: {empty_context_msg}"
        except Exception as e:
            db_context = f"\n\n[DB query error: {e}]"


    # ── Build message list for Groq ──────────────────────────────────────────
    groq_messages = [{"role": "system", "content": CHAT_SYSTEM_PROMPT}]

    if entity_code:
        groq_messages[0]["content"] += f"\n\nCurrent entity in focus: {entity_code}"

    # Add history (last 10 turns), inject DB context into the LAST user message
    recent = messages[-10:]
    last_user_idx = len(recent) - 1 - next(
        (i for i, m in enumerate(reversed(recent)) if m.get("role") == "user"), -1
    )
    for i, m in enumerate(recent):
        role = m.get("role", "user")
        content = m.get("content", "").strip()
        if not content:
            continue
        # Inject DB context into the last user message (index-based, not identity)
        if role == "user" and i == last_user_idx and db_context:
            content = content + db_context
        groq_messages.append({"role": role, "content": content})

    # ── Call LLM ─────────────────────────────────────────────────────────────
    from core.llm_client import call_llm as _call_llm
    result = _call_llm(
        prompt=groq_messages[-1]["content"] if groq_messages[-1]["role"] == "user" else "",
        system=groq_messages[0]["content"],
        backend=backend,
        model=model,
        messages=groq_messages[1:]   # pass full conversation history
    )

    return {
        "success": result.get("success", False),
        "reply": result.get("text", ""),
        "error": result.get("error", ""),
        "model": result.get("model"),
        "backend": result.get("backend"),
        "had_db_data": bool(db_context)
    }

# ─── HTTP SERVER ────────────────────────────────────────────────────────────────────

def run_http_server(port: int = 5002):
    """FraudSense HTTP server — /analyze, /chat, /health"""
    from http.server import HTTPServer, BaseHTTPRequestHandler
    from core.llm_client import BACKEND, GROQ_API_KEY, GROQ_MODEL, OLLAMA_MODEL, get_key_pool_status

    print(f"\n\U0001f916 FraudSense Agent starting...")
    print(f"   Backend : {BACKEND.upper()}")
    if BACKEND == "groq":
        pool = get_key_pool_status()
        if not pool["total_keys"]:
            print("\n\u274c  No Groq API keys found — add keys to ai/groq_key.txt (one per line)")
        else:
            print(f"   Model   : {pool['model']}")
            print(f"   Keys    : {pool['total_keys']} key(s) loaded (random rotation enabled)")
            for k in pool["keys"]:
                print(f"             {k}")
    else:
        print(f"   Model   : {OLLAMA_MODEL}")
        print("   Note    : Ollama must be running on http://localhost:11434")


    class Handler(BaseHTTPRequestHandler):
        def log_message(self, format, *args): pass

        def _read_json(self):
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length)
            try:
                return json.loads(body)
            except Exception:
                return {}

        def _send_json(self, obj, status=200):
            response = json.dumps(obj, default=str).encode()
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(response)))
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(response)

        def do_OPTIONS(self):
            self.send_response(204)
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS")
            self.send_header("Access-Control-Allow-Headers", "Content-Type")
            self.end_headers()

        def do_POST(self):
            data = self._read_json()
            try:
                if self.path == "/analyze":
                    result = analyze(
                        task=data.get("task", "Analyze this account for fraud risk"),
                        entity_code=data.get("entity_code"),
                        pattern=data.get("pattern"),
                        alert_id=data.get("alert_id"),
                        user_id=data.get("user_id"),
                        backend=data.get("backend"),
                        model=data.get("model")
                    )
                    self._send_json(result)

                elif self.path == "/chat":
                    result = smart_chat(
                        messages=data.get("messages") or [],
                        entity_code=data.get("entity_code"),
                        backend=data.get("backend"),
                        model=data.get("model")
                    )
                    self._send_json(result)

                elif self.path == "/forensic":
                    entity_code = (data.get("entity_code") or "").strip()
                    if not entity_code:
                        self._send_json({"success": False, "error": "entity_code is required"}, 400)
                    else:
                        result = forensic_analyze(
                            entity_code=entity_code,
                            backend=data.get("backend"),
                            model=data.get("model")
                        )
                        self._send_json(result)

                else:
                    self._send_json({"error": "Not found"}, 404)


            except Exception as e:
                print(f"   \u274c Handler error: {e}")
                import traceback; traceback.print_exc()
                self._send_json({"success": False, "error": str(e)}, 500)

        def do_GET(self):
            if self.path == "/health":
                from core.llm_client import get_key_pool_status
                pool = get_key_pool_status()
                self._send_json({
                    "status": "ok",
                    "agent": "FraudSense",
                    "backend": BACKEND,
                    "groq_key_set": bool(GROQ_API_KEY),
                    "total_keys": pool.get("total_keys", 1),
                    "model": pool.get("model") if BACKEND == "groq" else OLLAMA_MODEL
                })
            else:
                self._send_json({"error": "Not found"}, 404)


    print(f"\n\u2705  Listening on http://localhost:{port}")
    print(f"   POST /analyze  — full ReAct fraud analysis")
    print(f"   POST /chat     — conversational + auto DB queries")
    print(f"   GET  /health\n")
    HTTPServer(("localhost", port), Handler).serve_forever()


# ─── CLI ENTRY ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="FraudSense AI Agent")
    parser.add_argument("--alert-id", help="Fraud alert ID (e.g. ALT-0892)")
    parser.add_argument("--user-id", type=int, help="User ID to analyze")
    parser.add_argument("--entity-code", help="FundTrace ID (e.g. FT-X7K2P9)")
    parser.add_argument("--pattern", help="Pattern type (circular, layering, etc.)")
    parser.add_argument("--task", help="Custom task description")
    parser.add_argument("--http", action="store_true", help="Run as HTTP server")
    parser.add_argument("--port", type=int, default=5002, help="HTTP port (default 5002)")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    args = parser.parse_args()

    if args.http:
        run_http_server(args.port)
    else:
        task = args.task or f"Analyze fraud alert {args.alert_id or 'unknown'} for account {args.entity_code or 'unknown'}"
        result = analyze(
            task=task,
            entity_code=args.entity_code,
            pattern=args.pattern,
            alert_id=args.alert_id,
            user_id=args.user_id,
            verbose=args.verbose
        )
        print("\n" + "="*60)
        print(json.dumps(result, indent=2, default=str))

