# FundTrace AI — LangGraph Agentic System: Implementation Plan

This plan rebuilds the Python AI agent layer from a simple ReAct loop into a proper **LangGraph-based multi-agent system** with persistent memory, dynamic skills, and a clean HTTP API — while keeping full backward compatibility with the existing Node.js server.

---

## Background

**Current state:** [ai/agent.py](file:///c:/Users/daksh/Programmer/Learning/COMP%20TECH%20SKILL/LOW%20CODE%20PROJECTS/FundTrace%20AI%20system/ai/agent.py) runs a manual `while` loop calling the LLM, parsing JSON, calling tools, and looping. All agents (planner, executor, reflector) are baked into one 887-line monolith. Memory is written at the end and never loaded back mid-session.

**Goal:** Rebuild this under `/ai/agentic/` as a proper LangGraph graph with three distinct agent nodes, persistent multi-layer memory, dynamic skill loading, and a Flask HTTP server on port 5003.

---

## User Review Required

> [!IMPORTANT]
> **New port**: The new agentic server runs on **port 5003** (old agent.py runs on 5002). The Node.js server will need a one-line config change to point at 5003. I will NOT touch the Node.js code — you will update that.

> [!NOTE]
> **LangGraph dependency**: This adds `langgraph>=0.2`, `langchain-core>=0.2`, `langchain-groq>=0.2`, `langchain-community>=0.2`, `faiss-cpu>=1.7` (for vector memory), and `flask>=3.0` to requirements. All free/open-source.

> [!NOTE]
> **Old agent.py stays untouched.** The new system is additive — under `/ai/agentic/`. If anything breaks, you can revert to the old server immediately.

---

## Proposed Changes

### Folder Structure (New)

```
ai/
└── agentic/                        ← new root for the LangGraph system
    ├── server.py                   ← Flask HTTP server, port 5003
    ├── config.py                   ← all paths, models, temps, ports
    ├── requirements_agentic.txt    ← new deps: langgraph, flask, faiss-cpu
    │
    ├── llm/
    │   ├── llm_factory.py          ← create role-aware LLMs (planner/executor/reflector)
    │   ├── groq_llm.py             ← Groq backend (reuses existing key pool logic)
    │   └── ollama_llm.py           ← Ollama backend
    │
    ├── tools/
    │   ├── db_tools.py             ← @tool wrappers: query_db, list_tables, describe_table
    │   ├── log_tools.py            ← @tool wrapper: read_logs
    │   └── entity_tools.py         ← @tool wrapper: read_entity_profile
    │
    ├── memory/
    │   ├── episodic_store.py       ← persistent JSONL episodic memory (loads existing ai/memory/)
    │   ├── vector_store.py         ← FAISS-backed semantic search over past episodes
    │   ├── working_memory.py       ← in-graph scratchpad (per-session, held in AgentState)
    │   └── entity_memory.py        ← per-entity profile read/write (wraps existing entities/)
    │
    ├── skills/
    │   ├── skill_loader.py         ← reads /skills/*.md files, parses YAML frontmatter
    │   └── skill_router.py         ← selects correct skill based on task/intent
    │
    ├── graph/
    │   ├── state.py                ← AgentState TypedDict (the single source of truth)
    │   ├── planner.py              ← Planner node: given task → creates ordered plan
    │   ├── executor.py             ← Executor node: executes one plan step, calls tools
    │   ├── reflector.py            ← Reflector node: critiques output, decides next step
    │   └── build_graph.py          ← StateGraph assembly: nodes + edges + conditions
    │
    └── tests/
        └── test_agentic.py         ← integration tests for the new system
```

---

### Component Details

#### [NEW] `ai/agentic/config.py`
Centralized config. Single place for all paths, model names, temperatures, ports. No magic strings elsewhere.
- `PLANNER_TEMP = 0.3`, `EXECUTOR_TEMP = 0.1`, `REFLECTOR_TEMP = 0.2`
- `HTTP_PORT = 5003`
- `DB_PATH`, `SKILLS_DIR`, `MEMORY_DIR`, `ENTITIES_DIR`, `EPISODIC_FILE`
- `BACKEND` env var: `"groq"` or `"ollama"` (toggleable)

---

#### [NEW] `ai/agentic/llm/llm_factory.py`
Creates LLM instances with the correct temperature per role. Respects `BACKEND` env var for Groq vs Ollama.
- `get_planner_llm()` → temp 0.3
- `get_executor_llm()` → temp 0.1
- `get_reflector_llm()` → temp 0.2
- Also exposes `get_chat_llm()` for conversational mode

#### [NEW] `ai/agentic/llm/groq_llm.py`
Thin LangChain-compatible Groq wrapper. Reuses the multi-key pool from [llm_client.py](file:///c:/Users/daksh/Programmer/Learning/COMP%20TECH%20SKILL/LOW%20CODE%20PROJECTS/FundTrace%20AI%20system/ai/core/llm_client.py).

#### [NEW] `ai/agentic/llm/ollama_llm.py`
Thin LangChain-compatible Ollama wrapper. Points at `http://localhost:11434`.

---

#### [NEW] `ai/agentic/tools/db_tools.py`
LangGraph `@tool` decorated functions, wrapping the existing `db_tool.run_query()`:
- `query_db(sql: str)` — validated SELECT only (reuses existing safety layer)
- `list_tables()` — lists all available tables in fundtrace.db
- `describe_table(table_name: str)` — returns column info for a table

#### [NEW] `ai/agentic/tools/log_tools.py`
- [read_logs(account_code, hours, limit)](file:///c:/Users/daksh/Programmer/Learning/COMP%20TECH%20SKILL/LOW%20CODE%20PROJECTS/FundTrace%20AI%20system/ai/tools/log_reader.py#19-108) — wraps existing `log_reader.read_logs()`

#### [NEW] `ai/agentic/tools/entity_tools.py`
- `read_entity_profile(entity_code)` — reads from `ai/memory/entities/{code}.md`

---

#### [NEW] `ai/agentic/memory/episodic_store.py`
- Reads/writes [ai/memory/episodic_memory.jsonl](file:///c:/Users/daksh/Programmer/Learning/COMP%20TECH%20SKILL/LOW%20CODE%20PROJECTS/FundTrace%20AI%20system/ai/memory/episodic_memory.jsonl) (backward compatible with existing data)
- `save_episode(...)` — persists new analysis to disk immediately
- [load_relevant_episodes(entity_code, pattern, limit)](file:///c:/Users/daksh/Programmer/Learning/COMP%20TECH%20SKILL/LOW%20CODE%20PROJECTS/FundTrace%20AI%20system/ai/core/context_builder.py#52-123) — scoring-based retrieval
- **All writes go to disk instantly** — no RAM-only state

#### [NEW] `ai/agentic/memory/vector_store.py`
- FAISS-backed vector index built lazily on first request
- Falls back to TF-IDF keyword matching if FAISS not available
- Index is **saved to disk** at `ai/agentic/memory/vector_index/` after each update
- `search(query, k=5)` — returns top-k similar past episodes

#### [NEW] `ai/agentic/memory/working_memory.py`
- Helpers for managing the in-graph scratchpad (not persisted — lives in AgentState)
- `add_tool_result(state, tool_name, result)` — appends to tool_history
- `get_context_window(state, max_chars)` — trims tool history to fit LLM context budget

#### [NEW] `ai/agentic/memory/entity_memory.py`
- `load_profile(entity_code)` — reads entity .md file
- `update_profile(entity_code, analysis_result)` — wraps existing `memory_writer.update_entity_profile()`

---

#### [NEW] `ai/agentic/skills/skill_loader.py`
- Reads `/skills/*.md` files (the 4 existing ones: forensic, transaction_analysis, reporting, chat)
- Parses YAML frontmatter ([name](file:///c:/Users/daksh/Programmer/Learning/COMP%20TECH%20SKILL/LOW%20CODE%20PROJECTS/FundTrace%20AI%20system/ai/core/llm_client.py#70-73), `description`) using simple regex — no yaml lib needed
- Returns `{name: str, description: str, content: str}` dicts
- Caches loaded skills in memory

#### [NEW] `ai/agentic/skills/skill_router.py`
- `select_skill(task: str, available_skills: list)` → returns best-match skill name
- Strategy: keyword matching first, fallback to LLM-based routing if ambiguous

---

#### [NEW] `ai/agentic/graph/state.py`
```python
class AgentState(TypedDict):
    task: str                    # original user task
    entity_code: str             # target entity (optional)
    pattern: str                 # fraud pattern hint (optional)
    backend: str                 # "groq" or "ollama"
    skill: str                   # active skill name
    plan: list[str]              # ordered list of steps from Planner
    current_step: int            # which plan step we're on
    tool_history: list[dict]     # all tool calls so far {tool, input, output}
    working_notes: str           # Executor's accumulating notes
    reflection: str              # Reflector's latest critique
    final_answer: dict           # structured result when done
    status: str                  # "planning" | "executing" | "reflecting" | "done" | "error"
    error: str                   # last error message
    iterations: int              # total graph iterations (safety limit)
```

#### [NEW] `ai/agentic/graph/planner.py`
**Planner node** (temperature=0.3):
- Receives: task, entity_code, pattern, active skill system prompt, relevant memory
- Outputs: `plan` (ordered list of 3–6 investigation steps)
- Uses low context: only skill prompt + task + 3 most relevant past episodes
- Example output: `["1. Query account profile", "2. Get transaction history", "3. Detect circular flows", "4. Summarize findings"]`

#### [NEW] `ai/agentic/graph/executor.py`
**Executor node** (temperature=0.1):
- Receives: current plan step, tool results so far
- Outputs: tool call result appended to `tool_history`, moves `current_step` forward
- Uses LangGraph's `ToolNode` — tools are bound to the executor LLM
- Context is minimal: only the current step + last 3 tool results

#### [NEW] `ai/agentic/graph/reflector.py`
**Reflector node** (temperature=0.2):
- Receives: full plan, all tool results, working notes
- Outputs: one of: `"continue"` (go to next executor step), `"replan"` (tell planner to revise), `"done"` (produce final answer)
- If `"done"`: synthesizes `final_answer` dict in the output
- Guards: if `iterations >= MAX_ITERATIONS` → force `"done"` with confidence=20

#### [NEW] `ai/agentic/graph/build_graph.py`
```
START → planner → executor → reflector
                     ↑              |
                     |    continue  |
                     └──────────────┘
                                   | done / error
                                   ↓
                                  END
```
- Max iterations safety: 10 graph turns
- Error fallback: any exception → set status="error", route to END

---

#### [NEW] `ai/agentic/server.py`
Flask server on port 5003:
- `POST /analyze` — runs full Planner→Executor→Reflector loop, returns structured result
- `POST /forensic` — forensic deep-dive mode (uses forensic skill)
- `POST /chat` — conversational mode (uses chat skill, single executor turn)
- `GET /health` — returns backend/model/memory status
- `GET /memory/episodes` — list recent episodes (for review)
- `GET /memory/entity/<code>` — get entity profile
- Backward compatible: same request/response format as old `/analyze` and `/forensic` endpoints

---

#### [NEW] `ai/agentic/requirements_agentic.txt`
```
langgraph>=0.2.0
langchain-core>=0.2.0
langchain-groq>=0.2.0
langchain-community>=0.3.0
faiss-cpu>=1.7.4
flask>=3.0.0
groq>=1.1.0
```

---

## Memory Architecture (Persistence Strategy)

| Memory Type | Storage | When Written | When Read |
|-------------|---------|--------------|-----------|
| Episodic | [ai/memory/episodic_memory.jsonl](file:///c:/Users/daksh/Programmer/Learning/COMP%20TECH%20SKILL/LOW%20CODE%20PROJECTS/FundTrace%20AI%20system/ai/memory/episodic_memory.jsonl) | After every analysis completes | At Planner node start |
| Entity Profile | `ai/memory/entities/{code}.md` | After every analysis completes | At Planner node start |
| Vector Index | `ai/agentic/memory/vector_index/` | After every new episode | At Planner node start |
| Working Memory | AgentState (in-memory) | Every executor step | Every executor step |
| AI Call Logs | `ai/logs/json/` + `ai/logs/md/` | Every LLM call | Never (review only) |

**Key principle:** Every write is to disk immediately. No data lost on agent restart.

---

## Verification Plan

### Automated Tests
Run after implementation:
```bash
cd "c:\Users\daksh\Programmer\Learning\COMP TECH SKILL\LOW CODE PROJECTS\FundTrace AI system\ai\agentic"
python -m pytest tests/test_agentic.py -v
```
The test file will cover:
1. `TestConfig` — verify config paths/values are correct
2. `TestTools` — verify each tool works (DB query, list tables, read logs)
3. `TestSkillLoader` — verify skill files are loaded and parseable
4. `TestMemory` — write + read an episode, verify it persists
5. `TestServerHealth` — start server and hit /health endpoint

### Manual Smoke Test (HTTP Server)
1. Start the server: `cd ai\agentic && python server.py`
2. In another terminal, run:
   ```bash
   curl -X POST http://localhost:5003/health
   ```
   Expected: `{"status": "ok", "backend": "groq", ...}`
3. Run an analyze request:
   ```bash
   curl -X POST http://localhost:5003/analyze -H "Content-Type: application/json" -d "{\"task\": \"Is there any suspicious activity in the system?\", \"backend\": \"groq\"}"
   ```
   Expected: JSON with `success:true`, `final_answer.risk_score`, `iterations`, `elapsed_s`

### Memory Persistence Test
1. Run one analyze call (step above)
2. Restart the server: `Ctrl+C` then `python server.py`
3. Run: `curl http://localhost:5003/memory/episodes`
4. Expected: The episode from step 1 appears in the list — proves memory survived restart
