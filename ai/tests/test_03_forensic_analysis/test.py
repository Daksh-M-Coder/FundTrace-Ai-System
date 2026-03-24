"""
TEST 03: Deep Account Forensic Analysis
Tests the /forensic endpoint for 3 known accounts.
Run from: ai/ directory with agent running on localhost:5002
"""
import sys, json, requests, time
from pathlib import Path

BASE = "http://localhost:5002"

def forensic(entity_code):
    body = {"entity_code": entity_code, "backend": "groq"}
    r = requests.post(f"{BASE}/forensic", json=body, timeout=120)
    return r.json()

def test_account(label, acc_code):
    print(f"\n{'='*60}")
    print(f"FORENSIC: {acc_code} ({label})")
    result = {"account": acc_code, "label": label}
    try:
        data = forensic(acc_code)
        success = data.get("success", False)
        has_report = bool(data.get("report"))
        txn_count = data.get("stats", {}).get("total_transactions", 0)
        error = data.get("error", "")

        print(f"  success     : {success}")
        print(f"  has_report  : {has_report}")
        print(f"  txn_count   : {txn_count}")
        print(f"  error       : {error or 'none'}")
        if data.get("account"):
            a = data["account"]
            print(f"  account     : {a.get('full_name')} | bal={a.get('balance')} | status={a.get('status')}")
        if data.get("stats"):
            print(f"  stats       : {data['stats']}")
        if data.get("report"):
            print(f"  report[:500]:\n{data['report'][:500]}")

        acct_found = success and "not found" not in error.lower()
        status = "PASS" if acct_found and has_report else (
            "FAIL-NOT-FOUND" if "not found" in error.lower() else "FAIL"
        )
        result.update({"success": success, "has_report": has_report,
                        "txn_count": txn_count, "error": error, "status": status})
    except Exception as e:
        print(f"  EXCEPTION: {e}")
        result.update({"status": "ERROR", "error": str(e)})

    print(f"  STATUS: {result['status']}")
    return result

if __name__ == "__main__":
    print("=== TEST 03: FORENSIC ANALYSIS (calls /forensic endpoint) ===")
    RESULTS = []
    for label, code in [("SMILEY", "FT-LA3CK8"), ("DREAM", "FT-75T37P"), ("ABC", "FT-67GMY9")]:
        RESULTS.append(test_account(label, code))
        time.sleep(2)

    print(f"\n{'='*60}")
    print("SUMMARY:")
    passed = sum(1 for r in RESULTS if r.get("status") == "PASS")
    for r in RESULTS:
        icon = "PASS" if r.get("status") == "PASS" else "FAIL"
        print(f"  [{icon}] {r['account']} ({r['label']}): {r['status']} | txns={r.get('txn_count','?')}")

    Path(__file__).parent.joinpath("result.txt").write_text(
        json.dumps(RESULTS, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(f"\n{passed}/{len(RESULTS)} passed. Results saved to result.txt")
