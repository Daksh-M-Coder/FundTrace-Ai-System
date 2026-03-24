#!/usr/bin/env python3
"""
context_builder.py — Prompt Assembly Engine
============================================
Assembles the full LLM prompt from:
  1. system_prompt.md (semantic - who the AI is)
  2. knowledge_base.md (semantic - what it knows)
  3. episodic_memory.jsonl (relevant past cases)
  4. entity profile (account-specific history)
  5. live DB query results (working memory)
  6. recent event logs (working memory)
  7. current task description

This is the most important file in the AI layer.
"""

import json
import os
import re
from pathlib import Path
from datetime import datetime, timezone

MEMORY_DIR = Path(__file__).parent.parent / "memory"
ENTITIES_DIR = MEMORY_DIR / "entities"
MAX_CONTEXT_CHARS = 20000  # Groq llama-3.3-70b has 32768 token window; 20k chars ~ 5k tokens, well within budget

# ─── LOADERS ─────────────────────────────────────────────────────────────────

def load_system_prompt() -> str:
    path = MEMORY_DIR / "system_prompt.md"
    if path.exists():
        return path.read_text(encoding="utf-8").strip()
    return "You are a fraud detection AI analyst."

def load_knowledge_base() -> str:
    path = MEMORY_DIR / "knowledge_base.md"
    if path.exists():
        content = path.read_text(encoding="utf-8").strip()
        # Truncate if too long — keep first 5000 chars (Groq can handle it)
        return content[:5000]
    return ""

def load_entity_profile(entity_code: str) -> str:
    if not entity_code:
        return ""
    safe_code = re.sub(r'[^A-Z0-9\-]', '', entity_code.upper())
    path = ENTITIES_DIR / f"{safe_code}.md"
    if path.exists():
        return f"\n## Entity Profile: {safe_code}\n" + path.read_text(encoding="utf-8").strip()
    return f"\n## Entity Profile: {safe_code}\nNo prior history on file for this account."

def load_relevant_episodes(entity_code: str = None, pattern: str = None, limit: int = 4) -> str:
    """Load relevant past episodes from episodic memory."""
    path = MEMORY_DIR / "episodic_memory.jsonl"
    if not path.exists():
        return ""

    episodes = []
    try:
        with open(path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        # Score relevance for each episode
        scored = []
        for line in lines:
            line = line.strip()
            if not line:
                continue
            try:
                ep = json.loads(line)
            except json.JSONDecodeError:
                continue

            if ep.get("id", "").startswith("ep_seed"):
                continue  # Skip seed entries

            score = 0
            ep_str = json.dumps(ep).lower()

            # Same entity = highest priority
            if entity_code and entity_code.lower() in ep_str:
                score += 10

            # Same pattern type
            if pattern and pattern.lower() in ep_str:
                score += 5

            # Recent = slightly higher priority
            ts = ep.get("ts", "")
            if ts:
                score += 1  # newer episodes will be at end of file

            # Outcome known = more valuable
            if ep.get("outcome"):
                score += 3

            if score > 0:
                scored.append((score, ep))

        # Sort by score desc, take top N
        scored.sort(key=lambda x: x[0], reverse=True)
        episodes = [ep for _, ep in scored[:limit]]

    except Exception:
        return ""

    if not episodes:
        return ""

    lines_out = ["\n## Relevant Past Cases (Episodic Memory)"]
    for ep in episodes:
        outcome = ep.get("outcome", "pending")
        score = ep.get("risk_score", "?")
        lines_out.append(
            f"- [{ep.get('ts','?')[:10]}] {ep.get('entity_code','?')} | "
            f"task={ep.get('task','?')} | risk={score} | "
            f"rec={ep.get('recommendation','?')} | outcome={outcome}"
        )
        if ep.get("output_summary"):
            lines_out.append(f"  Summary: {ep['output_summary'][:200]}")

    return "\n".join(lines_out)

# ─── MAIN ASSEMBLER ───────────────────────────────────────────────────────────

def build_prompt(
    task: str,
    entity_code: str = None,
    pattern: str = None,
    db_results: dict = None,
    log_results: dict = None,
    tool_history: list = None,
    output_format_reminder: bool = True
) -> str:
    """
    Assemble the full prompt from all memory sources.

    Args:
        task: The current task description (what to analyze)
        entity_code: FT-XXXXXX of the primary subject account
        pattern: Detected pattern type (circular, layering, etc.)
        db_results: Results from previous DB queries (tool calls)
        log_results: Results from log reader
        tool_history: List of {tool, input, output} dicts from prior tool calls
        output_format_reminder: Whether to append output format guide

    Returns:
        Complete prompt string ready to send to LLM
    """
    parts = []
    total_chars = 0

    def add(section: str, label: str = ""):
        nonlocal total_chars
        if not section:
            return
        total_chars += len(section)
        parts.append(section)

    # 1. System prompt (always included)
    add(load_system_prompt())
    add("\n---\n")

    # 2. Knowledge base (trimmed)
    kb = load_knowledge_base()
    if kb and total_chars < MAX_CONTEXT_CHARS * 0.4:
        add("\n## Knowledge Base (Key Rules)\n" + kb[:2000])
        add("\n---\n")

    # 3. Episodic memory (relevant past cases)
    episodes = load_relevant_episodes(entity_code, pattern)
    if episodes and total_chars < MAX_CONTEXT_CHARS * 0.6:
        add(episodes)
        add("\n---\n")

    # 4. Entity profile (account history)
    profile = load_entity_profile(entity_code) if entity_code else ""
    if profile and total_chars < MAX_CONTEXT_CHARS * 0.7:
        add(profile)
        add("\n---\n")

    # 5. Tool call history (what we've already queried)
    if tool_history:
        add("\n## Tool Results (Data Gathered So Far)")
        for item in tool_history[-5:]:  # Last 5 tool calls
            tool_name = item.get("tool", "?")
            tool_input = str(item.get("input", ""))[:200]
            tool_output = str(item.get("output", ""))[:800]
            add(f"\n### {tool_name}: `{tool_input}`\n```\n{tool_output}\n```")
        add("\n---\n")

    # 6. Current DB results (if pre-loaded)
    if db_results and db_results.get("success"):
        rows = db_results.get("rows", [])
        add(f"\n## Live Database Results ({len(rows)} rows)\n```json\n{json.dumps(rows[:20], indent=2, default=str)}\n```")
        add("\n---\n")

    # 7. Log results (if pre-loaded)
    if log_results and log_results.get("success"):
        summary = log_results.get("summary", "")
        if summary:
            add(f"\n## Recent Event Log\n{summary}")
            add("\n---\n")

    # 8. Current task (always last before format reminder)
    add(f"\n## Current Task\n{task}")

    # 9. Output format reminder
    if output_format_reminder:
        add("""

## Required Response Format
Respond ONLY with valid JSON. No text outside the JSON block.
If you need more data, use a tool. If you have enough, provide final_answer.

```json
{
  "thought": "your step-by-step reasoning here",
  "tool_needed": true or false,
  "tool": "query_db | read_logs | read_entity_profile | none",
  "tool_input": "the query or params string, or null",
  "final_answer": null or {
    "risk_score": 0-100,
    "risk_level": "low | medium | high | critical",
    "patterns_detected": [],
    "evidence": [],
    "reasoning": "clear explanation",
    "recommendation": "monitor | review | freeze | file_str",
    "confidence": 0-100,
    "open_questions": []
  }
}
```""")

    return "\n".join(parts)


if __name__ == "__main__":
    # Test: build a sample prompt
    prompt = build_prompt(
        task="Analyze fraud alert ALT-0892 for account FT-X7K2P9. Pattern: circular. Amount: ₹48.2 Cr.",
        entity_code="FT-X7K2P9",
        pattern="circular"
    )
    print(f"Prompt length: {len(prompt)} chars")
    print("=" * 60)
    print(prompt[:2000])
    print("...")
