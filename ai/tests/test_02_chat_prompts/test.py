"""
TEST 02: Live Chat API - Sample Prompts
Tests the running agent's /chat endpoint with all the quick-query buttons
and verifies AI returns REAL DB data not hallucinated content.
Run from: ai/ directory with agent running on localhost:5002
"""
import sys, json, time, requests
from pathlib import Path

BASE = "http://localhost:5002"
RESULTS = []

def chat(msg, entity_code=None):
    body = {
        "messages": [{"role": "user", "content": msg}],
        "backend": "groq"
    }
    if entity_code:
        body["entity_code"] = entity_code
    r = requests.post(f"{BASE}/chat", json=body, timeout=40)
    data = r.json()
    return data.get("reply", ""), data.get("had_db_data", False)

def test_prompt(label, msg, must_contain=None, must_not_contain=None, entity_code=None):
    print(f"\n{'='*60}")
    print(f"PROMPT: {msg[:80]}")
    try:
        reply, had_data = chat(msg, entity_code)
        print(f"had_db_data: {had_data}")
        print(f"REPLY (first 400 chars):\n{reply[:400]}")

        result = {"label": label, "prompt": msg, "had_db_data": had_data, "status": "PASS", "notes": []}

        # Hallucination checks
        hallucination_words = ["TRX123456", "John Doe", "Jane Smith", "TechCorp Inc", "USD", "TRX12345"]
        for hw in hallucination_words:
            if hw in reply:
                result["status"] = "FAIL-HALLUCINATION"
                result["notes"].append(f"Contains fake data: '{hw}'")

        if must_contain:
            for word in must_contain:
                if word.lower() not in reply.lower():
                    result["status"] = "FAIL"
                    result["notes"].append(f"Missing expected: '{word}'")

        if must_not_contain:
            for word in must_not_contain:
                if word.lower() in reply.lower():
                    result["status"] = "WARN"
                    result["notes"].append(f"Should not contain: '{word}'")

        print(f"STATUS: {result['status']} | notes: {result['notes']}")
        RESULTS.append(result)

    except Exception as e:
        print(f"ERROR: {e}")
        RESULTS.append({"label": label, "status": "ERROR", "error": str(e)})
    time.sleep(2)  # rate limit

if __name__ == "__main__":
    print("=== TEST 02: LIVE CHAT SAMPLE PROMPTS ===")

    # All quick-query buttons
    test_prompt("Q1 First5Txns",
        "Show me the first 5 transactions in the database with sender and receiver names",
        must_contain=["TXN-"], must_not_contain=["TRX123456","John Doe"])

    test_prompt("Q2 HighRiskAlerts",
        "List all fraud alerts with risk score above 70",
        must_not_contain=["TRX123456"])

    test_prompt("Q3 DormantAccounts",
        "Show all dormant accounts inactive for 90 days",
        must_not_contain=["TRX123456"])

    test_prompt("Q4 TopBalances",
        "What are the top 10 accounts by current balance?",
        must_contain=["FT-"], must_not_contain=["USD","TRX123456"])

    test_prompt("Q5 RecentAlerts",
        "Show all recent fraud alerts",
        must_not_contain=["TRX123456"])

    test_prompt("Q6 CircularFraud",
        "How does circular transaction fraud work? Explain with an example")

    test_prompt("Q7 Biggest10",
        "Show the 10 biggest single transactions by amount in the database",
        must_contain=["TXN-"], must_not_contain=["TRX123456","USD","John Doe"])

    test_prompt("Q8 AllAccounts",
        "Show all client accounts in the database",
        must_contain=["FT-"])

    test_prompt("Q9 ChannelBreakdown",
        "Show me the transaction volume breakdown by channel")

    test_prompt("Q10 SpecificAccount",
        "Show me all transactions for account FT-67GMY9",
        entity_code="FT-67GMY9",
        must_not_contain=["TRX123456"])

    # Summary
    print(f"\n{'='*60}")
    print(f"SUMMARY: {sum(1 for r in RESULTS if r['status']=='PASS')}/{len(RESULTS)} passed")
    for r in RESULTS:
        icon = "✅" if r["status"]=="PASS" else "❌" if "FAIL" in r["status"] else "⚠️" if "WARN" in r["status"] else "💥"
        print(f"  {icon} {r['label']}: {r['status']} {r.get('notes','')}")

    Path(__file__).parent.joinpath("result.txt").write_text(
        json.dumps(RESULTS, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print("\nResults saved to result.txt")
