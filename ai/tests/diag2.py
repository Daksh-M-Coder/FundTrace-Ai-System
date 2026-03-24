"""Quick diagnostic: check schema and query execution for failing chat queries"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from tools.db_tool import run_query, DB_PATH

print(f"DB: {DB_PATH} | exists: {DB_PATH.exists()}")

# Check transactions table columns
r = run_query("SELECT * FROM transactions LIMIT 1")
if r["success"] and r["rows"]:
    print(f"transactions columns: {list(r['rows'][0].keys())}")
    print(f"sample row: {r['rows'][0]}")

# Check users table columns
r2 = run_query("SELECT * FROM users LIMIT 1")
if r2["success"] and r2["rows"]:
    print(f"\nusers columns: {list(r2['rows'][0].keys())}")

# Test the exact "first 5 txns" query
q = """SELECT t.txn_id, s.full_name AS sender, s.unique_code AS sender_code,
           r.full_name AS receiver, r.unique_code AS receiver_code,
           t.amount, t.channel, t.status, t.fraud_score,
           datetime(t.created_at,'unixepoch') AS date
    FROM transactions t
    LEFT JOIN users s ON t.from_user_id=s.id
    LEFT JOIN users r ON t.to_user_id=r.id
    ORDER BY t.id ASC LIMIT 5"""
r3 = run_query(q)
print(f"\nFirst-5 query: success={r3['success']} count={r3['count']}")
if r3.get("error"): print(f"  ERROR: {r3['error']}")
for row in r3.get("rows", []):
    print(f"  {row}")

# Test entity-specific query for FT-67GMY9
q_entity = """SELECT t.txn_id, s.full_name AS sender, r.full_name AS receiver,
           t.amount, t.channel, t.status
    FROM transactions t
    LEFT JOIN users s ON t.from_user_id=s.id
    LEFT JOIN users r ON t.to_user_id=r.id
    JOIN users u ON (t.from_user_id=u.id OR t.to_user_id=u.id)
    WHERE UPPER(u.unique_code)=UPPER('FT-67GMY9')
    ORDER BY t.created_at DESC LIMIT 20"""
r4 = run_query(q_entity)
print(f"\nEntity FT-67GMY9 query: success={r4['success']} count={r4['count']}")
if r4.get("error"): print(f"  ERROR: {r4['error']}")
for row in r4.get("rows", []):
    print(f"  {row}")

# Check accounts query 
q_acct = """SELECT full_name, unique_code, account_number, balance, status,
    datetime(created_at,'unixepoch') AS created_date
    FROM users WHERE role='client' ORDER BY id ASC LIMIT 15"""
r5 = run_query(q_acct)
print(f"\nAll accounts: success={r5['success']} count={r5['count']}")
for row in r5.get("rows", []):
    print(f"  {row}")

# Channel breakdown
q_ch = """SELECT channel, COUNT(*) AS txn_count,
    ROUND(SUM(amount),2) AS total_volume
    FROM transactions GROUP BY channel ORDER BY txn_count DESC"""
r6 = run_query(q_ch)
print(f"\nChannel breakdown: success={r6['success']} count={r6['count']}")
if r6.get("error"): print(f"  ERROR: {r6['error']}")
for row in r6.get("rows", []):
    print(f"  {row}")
