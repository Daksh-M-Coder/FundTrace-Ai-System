"""
TEST 06: Investigator Questions → AI Chat Flow
Tests that questions from the Investigator panel correctly:
  1. Pass the selected account's entity_code as context to the AI chat
  2. The AI receives the context and queries the DB for that account
  3. Responses contain real data (not hallucinations) for the account

All questions are sent to /api/ai/chat with entity_code set so the AI can
query the database for that specific account.

Run from: ai/ directory (or anywhere) — requires server+agent running.
"""
import sys, json, requests, time
from pathlib import Path

BASE = "http://localhost:3000"
OFFICER = {"email": "officer@fundtrace.bank", "password": "Officer@123"}

# Subset of investigator questions (one per category)
QUESTIONS = [
    ("Spending Pattern",  "FT-67GMY9", "Has there been a sudden change in spending habits?"),
    ("Fraud Pattern",     "FT-67GMY9", "Is there circular movement of money between accounts?"),
    ("Counterparty",      "FT-67GMY9", "Are funds being transferred to new or recently added beneficiaries?"),
    ("Temporal",          "FT-LA3CK8", "Has the account suddenly become active after a long dormant period?"),
    ("Risk Assessment",   "FT-LA3CK8", "What is the overall fraud risk score for this account?"),
    ("Net Flow",          "FT-75T37P", "Are large deposits followed by immediate withdrawals?"),
]

FAKE_WORDS = ["TRX123456", "John Doe", "Jane Smith", "TechCorp"]
RESULTS = []

sess = requests.Session()

def log(s): print(s, flush=True)

def check(label, cond, note=""):
    status = "PASS" if cond else "FAIL"
    icon = "✅" if cond else "❌"
    print(f"  {icon} {label}: {status}{(' — '+note) if note else ''}", flush=True)
    RESULTS.append({"label": label, "status": status, "note": note})
    return cond

# Step 1: Login
log("\n=== STEP 1: Login ===")
r = sess.post(f"{BASE}/api/auth/login", json=OFFICER)
check("Officer login", r.status_code == 200, f"status={r.status_code}")
if r.status_code != 200:
    log(f"Login failed: {r.text}"); sys.exit(1)

# Step 2: Test each investigator question with entity_code
log("\n=== STEP 2: Investigator questions with entity_code context ===")
for cat, acc_code, question in QUESTIONS:
    log(f"\n  ─── [{cat}] @{acc_code} ───")
    log(f"  Q: {question}")

    # Build the same payload sendQsToAI() would produce:
    # - entity_code is set from the account selector
    # - message is prefixed with [Account: FT-XXXXX]
    full_q = f"[Account: {acc_code}] {question}"
    payload = {
        "messages": [{"role": "user", "content": full_q}],
        "entity_code": acc_code,
        "backend": "groq"
    }

    try:
        resp = sess.post(f"{BASE}/api/ai/chat", json=payload, timeout=90)
        data = resp.json()
        ok = data.get("success", False)
        reply = data.get("reply", "")
        had_db = data.get("had_db_data", False)
        hallucinated = any(w in reply for w in FAKE_WORDS)

        check("HTTP 200", resp.status_code == 200, f"got {resp.status_code}")
        check("success=true", ok)
        check("Reply not empty", len(reply) > 20, f"len={len(reply)}")
        check("No hallucination", not hallucinated, "fake data detected" if hallucinated else "")

        log(f"  had_db_data: {had_db}")
        log(f"  Reply[:300]: {reply[:300]}")

    except Exception as e:
        log(f"  EXCEPTION: {e}")
        RESULTS.append({"label": f"{cat}@{acc_code}", "status": "ERROR", "note": str(e)})

    time.sleep(2)  # rate limit polite gap

# Step 3: Verify entity_code is actually used (AI should mention account code in context)
log("\n=== STEP 3: Verify entity_code context used ===")
mention_q = "[Account: FT-67GMY9] What is the overall fraud risk score for this account?"
r3 = sess.post(f"{BASE}/api/ai/chat", json={
    "messages": [{"role": "user", "content": mention_q}],
    "entity_code": "FT-67GMY9",
    "backend": "groq"
}, timeout=90)
d3 = r3.json()
check("HTTP 200 for risk score Q", r3.status_code == 200)
check("Reply mentions FT-67GMY9 or ABC", 
      "FT-67GMY9" in d3.get("reply","") or "ABC" in d3.get("reply","") or "67" in d3.get("reply",""),
      "AI doesn't reference the account")

# Summary
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
