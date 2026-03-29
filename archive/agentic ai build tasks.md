# FundTrace AI — LangGraph Agentic System Tasks

## Phase 1: Planning
- [x] Analyze existing codebase (agent.py, llm_client.py, db_tool.py, memory tools, skills/)
- [x] Draft implementation plan
- [ ] Get user approval on plan

## Phase 2: Setup & Config
- [ ] Create `/ai/agentic/` folder structure
- [ ] Create `requirements_agentic.txt` with LangGraph + deps
- [ ] Create `config.py` (centralized config: paths, models, temperatures, ports)

## Phase 3: LLM Layer
- [ ] Create `llm/llm_factory.py` — role-aware LLM factory (Planner/Executor/Reflector temps)
- [ ] Create `llm/groq_llm.py` — Groq backend wrapper for LangGraph
- [ ] Create `llm/ollama_llm.py` — Ollama backend wrapper for LangGraph

## Phase 4: Tools
- [ ] Create `tools/db_tools.py` — LangGraph @tool wrappers (query_db, list_tables, describe_table)
- [ ] Create `tools/log_tools.py` — LangGraph @tool wrapper (read_logs)
- [ ] Create `tools/entity_tools.py` — LangGraph @tool wrapper (read_entity_profile)

## Phase 5: Memory System
- [ ] Create `memory/episodic_store.py` — persistent episodic memory (JSONL, loads existing data)
- [ ] Create `memory/vector_store.py` — local vector search (FAISS or TF-IDF fallback)
- [ ] Create `memory/working_memory.py` — in-session scratchpad for the graph state
- [ ] Create `memory/entity_memory.py` — per-entity profile read/write (wraps existing entities/)

## Phase 6: Skills System
- [ ] Create `skills/skill_loader.py` — dynamic skill loader from /skills/*.md files
- [ ] Create `skills/skill_router.py` — choose which skill to activate based on task type

## Phase 7: Graph Agents
- [ ] Create `graph/state.py` — AgentState TypedDict (full graph state definition)
- [ ] Create `graph/planner.py` — Planner node (creates step-by-step plan, temp=0.3)
- [ ] Create `graph/executor.py` — Executor node (runs one step, calls tools, temp=0.1)
- [ ] Create `graph/reflector.py` — Reflector node (critiques, decides next action, temp=0.2)
- [ ] Create `graph/build_graph.py` — assemble the LangGraph StateGraph with edges/conditions

## Phase 8: HTTP Server
- [ ] Create `server.py` — Flask server on port 5003, /analyze /forensic /chat /health endpoints
- [ ] Maintain backward compat with existing /analyze endpoint format

## Phase 9: Verification
- [ ] Create `tests/test_agentic.py` — health check + basic analyze test
- [ ] Verify server starts (python server.py)
- [ ] Verify /analyze endpoint works end-to-end
- [ ] Verify memory persists across restarts
