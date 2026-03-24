"""
TEST 05: Officer Transaction API Endpoints
Tests the two new endpoints added to transactions.js:
  GET /api/transactions/officer/list
  GET /api/transactions/officer/export

Requires:
  - Server running on localhost:3000
  - Officer credentials: officer@fundtrace.bank / Officer@123
Run from: any directory
"""
import requests, json, sys
from pathlib import Path

BASE = "http://localhost:3000"
OFFICER_EMAIL = "officer@fundtrace.bank"
OFFICER_PASS  = "Officer@123"
RESULTS = []

sess = requests.Session()

def log(s): print(s)
def check(label, cond, note=""):
    status = "PASS" if cond else "FAIL"
    icon = "✅" if cond else "❌"
    print(f"  {icon} {label}: {status}{' — '+note if note else ''}")
    RESULTS.append({"label": label, "status": status, "note": note})
    return cond

# ── 1. Login as officer ───────────────────────────────────────────────────────
log("\n=== STEP 1: Officer login ===")
r = sess.post(f"{BASE}/api/auth/login", json={"email": OFFICER_EMAIL, "password": OFFICER_PASS})
check("Login succeeds", r.status_code == 200, f"status={r.status_code}")
if r.status_code != 200:
    log(f"Login failed: {r.text}")
    sys.exit(1)
log(f"  Logged in as: {r.json().get('user', {}).get('full_name')}")

# ── 2. List ALL transactions (no filter) ─────────────────────────────────────
log("\n=== STEP 2: List all transactions ===")
r = sess.get(f"{BASE}/api/transactions/officer/list")
check("Status 200", r.status_code == 200, f"got {r.status_code}")
data = r.json()
check("Has transactions array", isinstance(data.get("transactions"), list))
check("Has accounts for dropdown", isinstance(data.get("accounts"), list) and len(data["accounts"]) > 0)
check("Has total count", isinstance(data.get("total"), int) and data["total"] > 0, f"total={data.get('total')}")
check("Has channels breakdown", isinstance(data.get("channels"), list))
if data.get("transactions"):
    t = data["transactions"][0]
    required_cols = ["txn_id","txn_date","sender_name","sender_code","receiver_name","receiver_code","amount","channel","status","fraud_score"]
    for col in required_cols:
        check(f"Column '{col}' present", col in t)
    log(f"  Sample txn: {t.get('txn_id')} | {t.get('sender_code')} → {t.get('receiver_code')} | {t.get('amount')}")

# ── 3. List transactions filtered by account_code ────────────────────────────
log("\n=== STEP 3: Filter by account FT-67GMY9 ===")
r = sess.get(f"{BASE}/api/transactions/officer/list", params={"account_code": "FT-67GMY9"})
check("Status 200", r.status_code == 200)
data2 = r.json()
check("Returns rows", len(data2.get("transactions", [])) > 0, f"count={len(data2.get('transactions',[]))}")
# Every transaction should involve FT-67GMY9
for t in data2.get("transactions", []):
    ok = (t.get("sender_code") == "FT-67GMY9" or t.get("receiver_code") == "FT-67GMY9")
    if not ok:
        check("All rows involve FT-67GMY9", False, f"rouge txn: {t.get('txn_id')}")
        break
else:
    check("All rows involve FT-67GMY9", True)

# ── 4. Sort by amount DESC ───────────────────────────────────────────────────
log("\n=== STEP 4: Sort by amount DESC ===")
r = sess.get(f"{BASE}/api/transactions/officer/list", params={"sort": "amount_desc"})
check("Status 200", r.status_code == 200)
txns = r.json().get("transactions", [])
if len(txns) >= 2:
    check("Sorted amount DESC", txns[0]["amount"] >= txns[1]["amount"],
          f"{txns[0]['amount']} >= {txns[1]['amount']}")

# ── 5. Invalid account returns 404 ───────────────────────────────────────────
log("\n=== STEP 5: Invalid account returns 404 ===")
r = sess.get(f"{BASE}/api/transactions/officer/list", params={"account_code": "FT-INVALID"})
check("404 for unknown account", r.status_code == 404)

# ── 6. Export CSV ────────────────────────────────────────────────────────────
log("\n=== STEP 6: Export CSV for FT-67GMY9 ===")
r = sess.get(f"{BASE}/api/transactions/officer/export", params={"account_code": "FT-67GMY9", "format": "csv"})
check("Status 200", r.status_code == 200)
check("Content-Type text/csv", "text/csv" in r.headers.get("Content-Type",""))
check("Content-Disposition attachment", "attachment" in r.headers.get("Content-Disposition",""))
check("Filename ends .csv", r.headers.get("Content-Disposition","").endswith(".csv\""))
lines = r.text.strip().split("\r\n")
check("CSV has header row", "txn_id" in lines[0] if lines else False)
check("CSV has data rows", len(lines) >= 2, f"{len(lines)} lines")
log(f"  CSV header: {lines[0][:80]}")
log(f"  CSV rows: {len(lines)-1}")

# ── 7. Export JSON ────────────────────────────────────────────────────────────
log("\n=== STEP 7: Export JSON (all accounts) ===")
r = sess.get(f"{BASE}/api/transactions/officer/export", params={"format": "json"})
check("Status 200", r.status_code == 200)
check("Content-Disposition attachment .json", ".json" in r.headers.get("Content-Disposition",""))
jdata = r.json()
check("Has exported_at", "exported_at" in jdata)
check("Has count", "count" in jdata and jdata["count"] > 0, f"count={jdata.get('count')}")
check("Has transactions array", isinstance(jdata.get("transactions"), list))

# ── 8. Non-officer gets 403 ───────────────────────────────────────────────────
log("\n=== STEP 8: Client login gets 403 on officer endpoint ===")
other = requests.Session()
r2 = other.post(f"{BASE}/api/auth/login", json={"email": "smiley@demo.com", "password": "Client@123"})
if r2.status_code == 200:
    r3 = other.get(f"{BASE}/api/transactions/officer/list")
    check("Client gets 403 on officer endpoint", r3.status_code == 403)
else:
    log("  (skip — no client account to test with)")

# ── Summary ───────────────────────────────────────────────────────────────────
passed = sum(1 for r in RESULTS if r["status"] == "PASS")
failed = sum(1 for r in RESULTS if r["status"] == "FAIL")
print(f"\n{'='*60}")
print(f"SUMMARY: {passed}/{len(RESULTS)} passed, {failed} failed")
for r in RESULTS:
    icon = "✅" if r["status"] == "PASS" else "❌"
    print(f"  {icon} {r['label']}")

Path(__file__).parent.joinpath("result.txt").write_text(
    json.dumps(RESULTS, indent=2, ensure_ascii=False), encoding="utf-8"
)
print("Results saved to result.txt")
sys.exit(0 if failed == 0 else 1)
