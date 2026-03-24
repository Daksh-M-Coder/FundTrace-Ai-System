"""
TEST 08: Global vs Entity-Specific Query Routing
Tests that global queries (biggest N transactions in the database, top accounts, etc.)
are NOT hijacked by the entity-specific route even when entity_code is set in context.

This bug: entity_code is set → "transaction" appears in global query →
entity-specific route fires → returns only 1 account's txns instead of all.

Run from project root: python ai/tests/test_08_global_query_routing/test.py
"""
import sys, json, time, requests
from pathlib import Path

BASE = "http://localhost:3000"
OFFICER = {"email": "officer@fundtrace.bank", "password": "Officer@123"}

# These are GLOBAL queries — should return data across ALL accounts
# even when entity_code is explicitly passed in the request
GLOBAL_QUERIES = [
    ("10 biggest transactions", "Show the 10 biggest single transactions by amount in the database", 3),
    ("top 10 by amount", "Top 10 transactions by amount", 3),
    ("largest transactions", "What are the largest transactions?", 1),
    ("biggest single tx", "Show me the biggest single transaction", 1),
    ("all accounts balance", "What are the top 10 accounts by current balance?", 1),
    ("channel breakdown", "Give me a channel breakdown of all transactions", 1),
    ("total system flow", "What is the total transaction volume in the system?", 1),
]

FAKE_WORDS = ["TRX123456", "John Doe (fake)", "Jane Smith (fake)"]
RESULTS = []

sess = requests.Session()

def log(s): print(s, flush=True)

def check(label, cond, note=""):
    status = "PASS" if cond else "FAIL"
    icon = "✅" if cond else "❌"
    print(f"  {icon} {label}: {status}{(' — '+note) if note else ''}", flush=True)
    RESULTS.append({"label": label, "status": status, "note": note})
    return cond

# Login
log("\n=== STEP 1: Login ===")
r = sess.post(f"{BASE}/api/auth/login", json=OFFICER)
check("Officer login", r.status_code == 200)
if r.status_code != 200:
    log(f"Login failed: {r.text}"); sys.exit(1)

# Test: global queries WITH entity_code set (simulates the officer having an account selected)
log("\n=== STEP 2: Global queries with entity_code=FT-67GMY9 in context ===")
for name, query, min_expected_rows in GLOBAL_QUERIES:
    log(f"\n  [{name}]")
    log(f"  Q: {query}")
    # Crucially: entity_code IS set — this should NOT override global intent
    payload = {
        "messages": [{"role": "user", "content": query}],
        "entity_code": "FT-67GMY9",  # simulates investigator panel having selected an account
        "backend": "groq"
    }
    try:
        resp = sess.post(f"{BASE}/api/ai/chat", json=payload, timeout=90)
        data = resp.json()
        reply = data.get("reply", "")
        had_db = data.get("had_db_data", False)

        check(f"[{name}] HTTP 200", resp.status_code == 200)
        check(f"[{name}] success", data.get("success", False))
        check(f"[{name}] had_db_data", had_db, "no DB data used")
        check(f"[{name}] no hallucination", not any(w in reply for w in FAKE_WORDS))
        # Global query should mention multiple accounts or amounts
        check(f"[{name}] not entity-locked",
              "only transaction" not in reply.lower() and "single transaction" not in reply.lower(),
              "AI returned entity-specific data instead of global")

        log(f"  had_db_data: {had_db}")
        log(f"  Reply[:200]: {reply[:200]}")
    except Exception as e:
        log(f"  EXCEPTION: {e}")
        RESULTS.append({"label": name, "status": "ERROR", "note": str(e)})
    time.sleep(2)

passed = sum(1 for r in RESULTS if r["status"] == "PASS")
failed = sum(1 for r in RESULTS if r["status"] != "PASS")
print(f"\n{'='*60}")
print(f"SUMMARY: {passed}/{len(RESULTS)} passed, {failed} failed")
for r in RESULTS:
    icon = "✅" if r["status"] == "PASS" else "❌"
    print(f"  {icon} {r['label']}: {r['status']}")

Path(__file__).parent.joinpath("result.txt").write_text(
    json.dumps(RESULTS, indent=2, ensure_ascii=False), encoding="utf-8"
)
print("Results saved to result.txt")
sys.exit(0 if failed == 0 else 1)
