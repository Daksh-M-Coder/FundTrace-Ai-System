---
name: chat
description: >
  Agentic free-form chat skill for FundTrace AI — the FraudSense investigator.
  Use this for any open-ended, natural-language investigation question that an
  officer types into the AI Analysis chat box. Triggers on: any question that
  doesn't fit forensic (single account deep dive) or reporting (aggregated stats).
  Examples: "show me newly created accounts in the last 30 days", "which accounts
  have sent money to FT-XXXXX", "explain this alert", "what is unusual about
  this pattern", "who are the top senders this week", "find accounts with no
  friends but high transaction volume", "compare these two accounts". Routes to
  POST /api/ai/agentic-chat and streams SSE events to the dark step-log panel.
  This is the DEFAULT skill — use it whenever the officer just types a question
  and neither forensic.md nor reporting.md is a clear match.
---

# Agentic Chat Skill — FraudSense (FundTrace AI)

## What This Skill Does

Powers the **FraudSense agentic chat interface** — the free-form AI investigator
in the officer portal. The officer types any question in natural language and the
agent autonomously explores the database to answer it.

This is the **primary interface** for unstructured investigation. Unlike forensic
(single account) or reporting (aggregated stats), chat handles anything.

---

## Architecture

```
Officer types question
       ↓
POST /api/ai/agentic-chat  (server/ai.js)
       ↓
Python agent.py (port 5002) → /agentic_chat
       ↓
ai/agentic/loop.py — 8-iteration Groq function-calling loop
       ↓
Groq LLM (llama-3.3-70b) ←→ Tools (list_tables, describe_table, query_db, get_entity)
       ↓
SSE event stream → officer/dashboard.html step-log panel
```

**The LLM writes every SQL query itself. No hardcoded SQL.**

---

## API Endpoint

```
POST /api/ai/agentic-chat
Authorization: Bearer <officer_jwt>
Content-Type: application/json

{
  "message": "Show me accounts that received large transfers in the last 7 days",
  "session_id": "session-abc123"
}
```

Response: `text/event-stream` (SSE)

---

## SSE Event Stream

Events arrive as `data: {...}\n\n`. Each event has a `type` field:

| Event Type | Colour in UI | What It Means |
|------------|-------------|----------------|
| `planning` | 🟣 Purple | Agent is forming its investigation plan |
| `tool_call` | 🟠 Orange | LLM calling a tool — shows exact SQL written |
| `observation` | 🩵 Teal | Tool result — shows data returned from DB |
| `thinking` | 🔵 Blue | LLM intermediate reasoning text |
| `final` | 🟢 Green | Final markdown answer — investigation complete |
| `error` | 🔴 Red | Error detail |

Stream ends with `data: [DONE]`.

**Frontend consumption pattern** (from officer/dashboard.html):
```javascript
let streamDone = false;
while (!streamDone) {
  const { done, value } = await reader.read();
  // parse SSE lines...
  if (raw === '[DONE]') { streamDone = true; break; }
  if (event.type === 'final') { streamDone = true; renderFinalAnswer(event); break; }
}
try { reader.cancel(); } catch(_) {}
```

---

## Agentic Tools Available to the LLM

| Tool | Input Schema | What It Does |
|------|-------------|--------------|
| `list_tables` | `{}` | Lists all tables in fundtrace.db |
| `describe_table` | `{ table_name: string }` | Returns columns + types via PRAGMA |
| `query_db` | `{ sql: string }` | Runs a read-only SELECT (max 200 rows) |
| `get_entity` | `{ unique_code: string }` | Full account profile + transaction stats |

**Safety layer** — `db_tool.py` blocks:
`DROP`, `DELETE`, `UPDATE`, `INSERT`, `ALTER`, `TRUNCATE`, `REPLACE`,
`ATTACH`, `VACUUM`

**Blocked columns**: `password_hash`, `token_hash`
**Blocked tables**: `sessions`, `login_attempts`

---

## Agentic Loop Behaviour

The agent runs up to **8 iterations**:

```
Iteration 1: list_tables()  → learns the schema
Iteration 2: describe_table("relevant_table")  → learns columns
Iteration 3: query_db("SELECT ...")  → gets real data
Iteration 4: (optional) more queries for related data
...
Iteration N: synthesises final answer
```

**Key behaviours:**
- The LLM sees tool results and decides its next action autonomously
- It writes all SQL dynamically based on what it discovers
- It adapts: if a column doesn't exist, it checks PRAGMA first
- It never guesses — it always checks before querying

---

## Persistent Memory System

Every chat session is saved to two locations:

### Session Memory
`ai/memory/sessions/<timestamp>_<session_id>.json`

Full step-by-step record:
```json
{
  "session_id": "session-abc123",
  "question": "Show newly created accounts in last 30 days",
  "iterations": [
    { "type": "tool_call", "tool": "list_tables", "result": [...] },
    { "type": "tool_call", "tool": "describe_table", "input": "users", "result": [...] },
    { "type": "tool_call", "tool": "query_db", "sql": "SELECT ...", "result": [...] },
    { "type": "final", "answer": "..." }
  ],
  "timestamp": "2024-06-10T14:23:00Z"
}
```

### Long-Term Memory
`ai/memory/long_term.jsonl`

One condensed line per session, injected into the system prompt on the next
run. This means:
- After the first run, the agent knows the schema without calling `list_tables`
- Repeated queries get faster and more accurate
- Context about past investigations carries forward

---

## UI Features (officer/dashboard.html — AI Analysis Tab)

### Step-Log Panel
- Events render as expandable cards in a dark panel
- Each card shows type icon + summary header
- Tool call cards show the exact SQL written by the LLM
- Observation cards show a mini data table of results

### Auto-Collapse
- When a **new tool_call** arrives, the previous tool+observation pair collapses
- When **final answer** arrives, all intermediate cards collapse
- Only planning breadcrumb + green final card remain expanded after completion
- Click any card header to manually expand/collapse

### Stop Button
- Cancels the SSE stream mid-run
- Officer can stop a long-running investigation early

### Quick-Query Chips
10 preset investigation questions that fire immediately on click:

| Chip | Question Sent |
|------|--------------|
| 1 | Show newly created accounts in the last 30 days |
| 2 | List accounts with the highest transaction volumes this week |
| 3 | Find round-trip transaction suspects |
| 4 | Show accounts flagged for structuring |
| 5 | List dormant accounts that suddenly became active |
| 6 | Show top 10 high-value transfers today |
| 7 | Find new accounts (< 7 days old) with large transactions |
| 8 | List after-hours transactions (1am–5am) |
| 9 | Show all open high-risk alerts (score > 70) |
| 10 | Find accounts with no social connections but high transaction volume |

---

## Session Management

Each officer chat session has a `session_id`. Best practice:

```javascript
// Generate a fresh session ID per tab/visit
const sessionId = `session-${Date.now()}-${Math.random().toString(36).slice(2)}`;
```

The agent uses `session_id` to:
1. Write the correct session JSON to `ai/memory/sessions/`
2. Keep context within a multi-turn conversation

---

## Legacy Endpoint (non-agentic)

```
POST /api/ai/chat   (legacy — non-agentic, simple chat)
```

This routes to a simpler ReAct-style handler in `ai/agent.py` that does **not**
use the 8-iteration function-calling loop. It exists for backward compatibility.
**Always prefer `/api/ai/agentic-chat` for real investigations.**

---

## Error Scenarios

| Symptom | Cause | Solution |
|---------|-------|----------|
| Cards keep appearing after `[DONE]` | Missing `streamDone` flag in frontend loop | Use `streamDone = true` pattern (see above) |
| 20+ cards flooding screen | Auto-collapse not applied | Ensure collapse logic runs on new `tool_call` and `final` events |
| "Max iterations without answer" | Very complex multi-hop query | Ask a more focused question; repeat (memory helps on next run) |
| Empty observations | Agent tried to query blocked table | Normal — agent adapts and tries another approach |
| Agent returns stale data | Long-term memory has outdated schema | Delete `ai/memory/long_term.jsonl` to reset |

---

## Notes for Claude

- This is the **default skill** for any officer question that is open-ended
  and conversational. If in doubt between chat / forensic / reporting, pick
  this skill — it's the most general.
- The officer portal's AI Analysis tab is the **primary UI surface** for this
  skill. Always route through `/api/ai/agentic-chat`, not the legacy `/api/ai/chat`.
- When crafting prompt guidance for officers, remind them: the more specific
  the question, the faster the agent converges. "Show me round-trip transactions
  involving accounts created this month" is better than "look for fraud".
- The agent has no tools to modify data — it is **read-only**. If an officer
  wants to freeze an account, that must go through:
  `PATCH /api/fraud/accounts/:id/freeze`
- `session_id` is optional but strongly recommended to enable memory persistence
  and to allow multi-turn follow-up questions in the same context.
- If the step-log shows a `planning` card but then hangs, the Groq API may be
  slow. The stop button lets the officer cancel and retry.
