"""
TEST 04: smart_chat direct module test - run from ai/ directory
python tests/test_04_direct_chat/run.py
"""
import sys
from pathlib import Path

AI_DIR = Path(__file__).parent.parent.parent  # tests/test_04/ -> tests/ -> ai/
sys.path.insert(0, str(AI_DIR))

import agent
from tools.db_tool import DB_PATH

print(f"=== TEST 04: direct smart_chat ===")
print(f"DB: {DB_PATH} | exists: {DB_PATH.exists()}")

QUERIES = [
    ("First5Txns",     "Show me the first 5 transactions in the database with sender and receiver names", None),
    ("TopBalances",    "What are the top 10 accounts by current balance?", None),
    ("Biggest10",      "Show the 10 biggest single transactions by amount in the database", None),
    ("AllAccounts",    "Show all client accounts in the database", None),
    ("ChannelBreakdown","Show me the transaction volume breakdown by channel", None),
    ("EntityTxns",     "Show me all transactions for account FT-67GMY9", "FT-67GMY9"),
    ("HighRiskAlerts", "List all fraud alerts with risk score above 70", None),
]

FAKE_WORDS = ["TRX123456", "John Doe", "Jane Smith", "TechCorp"]
RESULTS = []

for label, msg, ecode in QUERIES:
    messages = [{"role": "user", "content": msg}]
    print(f"\n--- {label} ---")
    result = agent.smart_chat(messages, entity_code=ecode, backend="groq")
    had_data = result.get("had_db_data", False)
    reply = result.get("reply", "")
    error = result.get("error", "")
    hallucinated = any(w in reply for w in FAKE_WORDS)

    status = "PASS" if had_data and not hallucinated else \
             ("FAIL-HALLUCINATION" if hallucinated else "FAIL-NO-DATA")

    print(f"  had_db_data={had_data}  hallucinated={hallucinated}  status={status}")
    if error: print(f"  error: {error[:120]}")
    print(f"  reply: {reply[:300]}")
    RESULTS.append({"label": label, "status": status, "had_db_data": had_data})

print(f"\n=== SUMMARY ({sum(1 for r in RESULTS if r['status']=='PASS')}/{len(RESULTS)} pass) ===")
for r in RESULTS:
    icon = "PASS" if r["status"] == "PASS" else "FAIL"
    print(f"  [{icon}] {r['label']}: {r['status']}")

Path(__file__).parent.joinpath("result.txt").write_text(
    "\n".join(f"{r['label']}: {r['status']}" for r in RESULTS), encoding="utf-8"
)
print("Saved result.txt")
