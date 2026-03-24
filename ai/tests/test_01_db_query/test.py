"""
TEST 01: DB Query Verification
Confirms DB path is correct and queries return real data.
Run from: ai/ directory
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from tools.db_tool import run_query, DB_PATH

def run():
    lines = []
    def log(s): print(s); lines.append(s)

    log(f"=== TEST 01: DB QUERY VERIFICATION ===")
    log(f"DB path : {DB_PATH}")
    log(f"DB found: {DB_PATH.exists()}")
    assert DB_PATH.exists(), f"FAIL: DB not found at {DB_PATH}"

    # Row counts
    for tbl in ["users", "transactions", "fraud_alerts"]:
        r = run_query(f"SELECT COUNT(*) AS cnt FROM {tbl}")
        cnt = r["rows"][0]["cnt"] if r["success"] and r["rows"] else "ERROR"
        log(f"  {tbl}: {cnt} rows")

    # First 5 txns
    r = run_query("""SELECT t.txn_id, s.full_name AS sender, r.full_name AS receiver,
           t.amount, t.channel, t.status
    FROM transactions t
    LEFT JOIN users s ON t.from_user_id=s.id
    LEFT JOIN users r ON t.to_user_id=r.id
    ORDER BY t.id ASC LIMIT 5""")
    log(f"\nFirst 5 txns (success={r['success']}, count={r['count']}):")
    for row in r.get("rows", []):
        log(f"  {row['txn_id']} | {row['sender']} -> {row['receiver']} | {row['amount']} | {row['status']}")
    assert r["success"] and r["count"] > 0, "FAIL: No txn rows returned"

    # Biggest 10 txns
    r = run_query("""SELECT t.txn_id, s.full_name AS sender, r.full_name AS receiver,
           t.amount, t.status
    FROM transactions t
    LEFT JOIN users s ON t.from_user_id=s.id
    LEFT JOIN users r ON t.to_user_id=r.id
    ORDER BY t.amount DESC LIMIT 10""")
    log(f"\nBiggest 10 txns (count={r['count']}):")
    for row in r.get("rows", []):
        log(f"  {row['txn_id']} | {row['amount']} | {row['status']}")

    # Account lookups
    log("\nAccount lookups (UPPER case-insensitive):")
    for code in ["FT-LA3CK8", "FT-75T37P", "FT-67GMY9"]:
        r = run_query(f"SELECT id, unique_code, full_name, balance FROM users WHERE UPPER(unique_code)=UPPER('{code}')")
        found = r["success"] and r["count"] > 0
        log(f"  {code}: {'FOUND - ' + str(r['rows'][0]) if found else 'NOT FOUND'}")

    # Top balances
    r = run_query("SELECT full_name, unique_code, balance FROM users WHERE role='client' ORDER BY balance DESC LIMIT 10")
    log(f"\nTop balances (count={r['count']}):")
    for row in r.get("rows", []):
        log(f"  {row['unique_code']} | {row['full_name']} | {row['balance']}")

    log("\n=== RESULT: ALL CHECKS PASSED ===")
    Path(__file__).parent.joinpath("result.txt").write_text("\n".join(lines), encoding="utf-8")

if __name__ == "__main__":
    run()
