#!/usr/bin/env python3
"""
memory_writer.py — Memory Persistence Layer
============================================
Saves AI analysis results back to:
  - episodic_memory.jsonl (append-only event log of all analyses)
  - entities/{code}.md (per-account profile, updated after each analysis)

Call this AFTER every successful AI analysis to build up memory over time.
"""

import json
import re
import os
from pathlib import Path
from datetime import datetime, timezone

MEMORY_DIR = Path(__file__).parent.parent / "memory"
ENTITIES_DIR = MEMORY_DIR / "entities"
EPISODIC_FILE = MEMORY_DIR / "episodic_memory.jsonl"

def write_episode(
    entity_code: str,
    task: str,
    trigger: str,
    input_summary: str,
    output_summary: str,
    risk_score: float = None,
    recommendation: str = None,
    patterns: list = None,
    evidence: list = None,
    open_questions: list = None
) -> str:
    """
    Append a new episode to episodic memory.
    Returns the episode ID.
    """
    # Generate episode ID
    ts = datetime.now(timezone.utc)
    ep_id = f"ep_{ts.strftime('%Y%m%d_%H%M%S')}_{entity_code or 'unknown'}"

    episode = {
        "id": ep_id,
        "ts": ts.isoformat().replace("+00:00", "Z"),
        "trigger": trigger,
        "entity_code": entity_code,
        "task": task,
        "input_summary": input_summary[:500],
        "output_summary": output_summary[:500],
        "risk_score": risk_score,
        "recommendation": recommendation,
        "patterns": patterns or [],
        "evidence_count": len(evidence or []),
        "open_questions_count": len(open_questions or []),
        "outcome": None,           # Filled in later by officer action
        "outcome_ts": None,
        "officer_notes": None,
        "correct": None            # Was AI correct? For ML training later
    }

    EPISODIC_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(EPISODIC_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(episode) + "\n")

    return ep_id


def update_episode_outcome(ep_id: str, outcome: str, officer_notes: str = None, correct: bool = None):
    """
    Update an episode's outcome (called when officer acts on a case).
    Since JSONL is append-only, we append an update record.
    """
    ts = datetime.now(timezone.utc)
    update = {
        "id": ep_id + "_update",
        "ts": ts.isoformat().replace("+00:00", "Z"),
        "updates_episode": ep_id,
        "outcome": outcome,
        "outcome_ts": ts.isoformat().replace("+00:00", "Z"),
        "officer_notes": officer_notes,
        "correct": correct
    }
    with open(EPISODIC_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(update) + "\n")


def update_entity_profile(
    entity_code: str,
    analysis_result: dict,
    account_info: dict = None
):
    """
    Update or create an entity profile file.
    These files are running summaries — NOT append-only.
    """
    if not entity_code:
        return

    safe_code = re.sub(r'[^A-Z0-9\-]', '', entity_code.upper())
    profile_path = ENTITIES_DIR / f"{safe_code}.md"
    ENTITIES_DIR.mkdir(parents=True, exist_ok=True)

    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    risk_score = analysis_result.get("risk_score", "?")
    risk_level = analysis_result.get("risk_level", "?")
    patterns = analysis_result.get("patterns_detected", [])
    recommendation = analysis_result.get("recommendation", "?")
    reasoning = analysis_result.get("reasoning", "")[:400]
    evidence = analysis_result.get("evidence", [])[:5]
    open_q = analysis_result.get("open_questions", [])[:3]

    # Build or update profile
    if profile_path.exists():
        existing = profile_path.read_text(encoding="utf-8")
        # Extract existing analysis history section
        history_marker = "## AI Analysis History"
        if history_marker in existing:
            before_history = existing[:existing.index(history_marker)]
            history_section = existing[existing.index(history_marker):]
        else:
            before_history = existing
            history_section = f"\n{history_marker}\n"
    else:
        name = account_info.get("full_name", "Unknown") if account_info else "Unknown"
        branch = account_info.get("branch", "Unknown") if account_info else "Unknown"
        acc_no = account_info.get("account_number", "Unknown") if account_info else "Unknown"
        acct_type = account_info.get("account_type", "Unknown") if account_info else "Unknown"

        before_history = f"""# Entity Profile: {safe_code}

## Identity
- Name: {name}
- Account Number: {acc_no}
- Account Type: {acct_type}
- Branch: {branch}
- First Flagged: {now}
- Profile Created: {now}

## Risk Escalation
- **{now}**: First analysis — risk {risk_score}/100 — recommendation: {recommendation}

## Known Linked Accounts
_(will be updated as network is mapped)_

## Watch Flags
_(patterns to watch for in future transactions)_

"""
        history_section = f"\n## AI Analysis History\n"

    # Append this analysis to history
    new_entry = f"""
### Analysis: {now}
- **Risk Score**: {risk_score}/100 ({risk_level})
- **Patterns**: {', '.join(patterns) if patterns else 'none'}
- **Recommendation**: {recommendation}
- **Reasoning**: {reasoning}
- **Evidence Cited**: {len(evidence)} items
{chr(10).join('  - ' + e for e in evidence[:3])}
- **Open Questions**: {chr(10).join('  - ' + q for q in open_q) if open_q else 'none'}
"""

    final_content = before_history + history_section + new_entry
    profile_path.write_text(final_content, encoding="utf-8")


def export_training_data(output_path: str = None) -> list:
    """
    Export labeled episodes as training data for future ML model.
    Only includes episodes where outcome is known (officer acted).
    """
    if not EPISODIC_FILE.exists():
        return []

    # Build a map of updates
    episodes = {}
    updates = {}

    with open(EPISODIC_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                ep = json.loads(line)
            except json.JSONDecodeError:
                continue

            if ep.get("updates_episode"):
                updates[ep["updates_episode"]] = ep
            else:
                episodes[ep["id"]] = ep

    # Merge updates into episodes
    labeled = []
    for ep_id, ep in episodes.items():
        if ep_id in updates:
            update = updates[ep_id]
            ep["outcome"] = update.get("outcome")
            ep["outcome_ts"] = update.get("outcome_ts")
            ep["officer_notes"] = update.get("officer_notes")
            ep["correct"] = update.get("correct")

        # Only export if outcome known
        if ep.get("outcome"):
            labeled.append({
                "entity_code": ep.get("entity_code"),
                "task": ep.get("task"),
                "patterns": ep.get("patterns", []),
                "risk_score": ep.get("risk_score"),
                "recommendation": ep.get("recommendation"),
                "outcome": ep.get("outcome"),
                "correct": ep.get("correct"),
                "label": 1 if ep.get("outcome") in ["filed", "freeze"] else 0
            })

    if output_path:
        import csv
        with open(output_path, "w", newline="", encoding="utf-8") as f:
            if labeled:
                writer = csv.DictWriter(f, fieldnames=labeled[0].keys())
                writer.writeheader()
                writer.writerows(labeled)

    return labeled


if __name__ == "__main__":
    # Test: write a sample episode
    ep_id = write_episode(
        entity_code="FT-X7K2P9",
        task="fraud_analysis",
        trigger="fraud_alert",
        input_summary="Circular pattern detected, 5 hops, ₹48.2 Cr in 72h",
        output_summary="Confirmed circular flow. Evidence: TXN-88201 through TXN-89001. Recommend freeze + STR.",
        risk_score=91,
        recommendation="file_str",
        patterns=["circular", "layering"],
        evidence=["TXN-88201: ₹9.85Cr ACC-2847→ACC-0041", "TXN-89001: ₹8.95Cr return to origin"],
        open_questions=["UAE correspondent bank not yet identified"]
    )
    print(f"Written episode: {ep_id}")

    # Test entity profile update
    update_entity_profile(
        "FT-X7K2P9",
        {
            "risk_score": 91, "risk_level": "critical",
            "patterns_detected": ["circular", "layering"],
            "recommendation": "file_str",
            "reasoning": "Funds returned to origin via 5 accounts within 72 hours.",
            "evidence": ["TXN-88201", "TXN-89001"],
            "open_questions": ["Identity of UAE correspondent"]
        },
        account_info={"full_name": "Rajan Enterprises", "branch": "Mumbai-Fort",
                       "account_number": "ACC-2024-499769", "account_type": "Current"}
    )
    print("Entity profile updated.")
