"""
TEST 07: New Account Query Routing
Tests that "newly created accounts in last N days" queries are correctly routed
to the users table with created_at filtering and transaction count join.

Run from project root: python ai/tests/test_07_new_accounts_query/test.py
"""
import sys, json, time, requests
from pathlib import Path

BASE = "http://localhost:3000"
OFFICER = {"email": "officer@fundtrace.bank", "password": "Officer@123"}

QUERIES = [
    "Show newly created accounts in the last 30 days with their balance and transaction count",
    "Which accounts were created recently in the last 60 days?",
    "List new accounts created this month",
    "Show accounts registered in the last 90 days with balance",
    "Show me the newest accounts in the system",
]

FAKE_WORDS = ["TRX123456", "John Doe", "Jane Smith"]
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

# Test queries
log("\n=== STEP 2: New account queries ===")
for q in QUERIES:
    log(f"\n  Q: {q}")
    payload = {"messages": [{"role": "user", "content": q}], "backend": "groq"}
    try:
        resp = sess.post(f"{BASE}/api/ai/chat", json=payload, timeout=90)
        data = resp.json()
        reply = data.get("reply", "")
        had_db = data.get("had_db_data", False)

        check("HTTP 200", resp.status_code == 200)
        check("success=true", data.get("success", False))
        check("Reply not empty", len(reply) > 20)
        check("had_db_data=True", had_db, "AI used no DB data — still falling through to fallback")
        check("No hallucination", not any(w in reply for w in FAKE_WORDS))
        check("No 'don't have access'", "don't have access" not in reply.lower() and "cannot access" not in reply.lower(),
              "AI said it cannot access account data")

        log(f"  had_db_data: {had_db}")
        log(f"  Reply[:250]: {reply[:250]}")
    except Exception as e:
        log(f"  EXCEPTION: {e}")
        RESULTS.append({"label": q[:50], "status": "ERROR", "note": str(e)})
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
