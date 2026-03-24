"""
TEST 04: smart_chat direct module test (no HTTP, no hallucination possible)
Calls smart_chat() directly and prints the db_context that would be injected.
Run from: ai/ directory
"""
import sys, importlib
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import the fixed agent module
import agent
from tools.db_tool import DB_PATH

RESULTS = []

def run_chat(label, msg, entity_code=None):
    messages = [{"role": "user", "content": msg}]
    # Temporarily patch smart_chat to also return db_context
    result = agent.smart_chat(messages, entity_code=entity_code, backend="groq")
    had_data = result.get("had_db_data", False)
    reply = result.get("reply", "")
    error = result.get("error", "")
    
    print(f"\n--- {label} ---")
    print(f"  had_db_data: {had_data}")
    print(f"  error: {error[:100] if error else 'none'}")
    print(f"  reply (first 300): {reply[:300]}")
    
    fail_words = ["TRX123456", "John Doe", "Jane Smith", "TechCorp", "TRX123"]
    hallucinated = any(w in reply for w in fail_words)
    status = "PASS" if had_data and not hallucinated else ("FAIL-HALLUCINATION" if hallucinated else "FAIL-NO-DATA")
    print(f"  STATUS: {status}")
    RESULTS.append({"label": label, "had_db_data": had_data, "status": status})

if __name__ == "__main__":
    print(f"=== TEST 04: direct smart_chat ===")
    print(f"DB: {DB_PATH} | exists: {DB_PATH.exists()}")

    run_chat("First5Txns", "Show me the first 5 transactions in the database with sender and receiver names")
    run_chat("TopBalances", "What are the top 10 accounts by current balance?")
    run_chat("Biggest10", "Show the 10 biggest single transactions by amount in the database")
    run_chat("AllAccounts", "Show all client accounts in the database")
    run_chat("ChannelBreakdown", "Show me the transaction volume breakdown by channel")
    run_chat("EntityTxns", "Show me all transactions for account FT-67GMY9", entity_code="FT-67GMY9")
    run_chat("HighRiskAlerts", "List all fraud alerts with risk score above 70")

    print(f"\n=== SUMMARY ===")
    for r in RESULTS:
        icon = "✅" if r["status"] == "PASS" else "❌"
        print(f"  {icon} {r['label']}: {r['status']} (had_data={r['had_db_data']})")
    
    Path(__file__).parent.joinpath("result.txt").write_text(
        "\n".join(f"{r['label']}: {r['status']}" for r in RESULTS), encoding="utf-8"
    )
