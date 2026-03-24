#!/usr/bin/env python3
"""
db_tool.py — Read-Only Database Query Tool for FraudSense AI Agent
==================================================================
Accepts SELECT-only SQL queries. Rejects ALL write operations.
Used by the AI agent to safely inspect live transaction data.

Usage:
  python db_tool.py "SELECT * FROM users LIMIT 5"
  python db_tool.py --http   (starts as HTTP server on port 5001)
"""

import sys
import os
import re
import json
import sqlite3
import argparse
import time
import logging
from datetime import datetime
from pathlib import Path

# ─── CONFIG ──────────────────────────────────────────────────────────────────

ROOT = Path(__file__).parent.parent.parent   # ai/tools/ → ai/ → project_root
DB_PATH = ROOT / "server" / "fundtrace.db"

# Sanity: if still not found, try one level up (running from different cwd)
if not DB_PATH.exists():
    alt = Path(__file__).parent.parent / "server" / "fundtrace.db"
    if alt.exists():
        DB_PATH = alt

AUDIT_LOG = Path(__file__).parent / "logs" / "db_tool_audit.jsonl"
MAX_ROWS = 200
QUERY_TIMEOUT_SECONDS = 5

# Columns that must NEVER be returned (sensitive data firewall)
FORBIDDEN_COLUMNS = {"password_hash", "token_hash"}

# Tables the AI is NOT allowed to query at all
FORBIDDEN_TABLES = {"sessions", "login_attempts"}

# ─── SQL SAFETY ──────────────────────────────────────────────────────────────

# These patterns are forbidden even inside SELECT (subquery injection etc.)
FORBIDDEN_PATTERNS = [
    r"\bINSERT\b",
    r"\bUPDATE\b",
    r"\bDELETE\b",
    r"\bDROP\b",
    r"\bCREATE\b",
    r"\bALTER\b",
    r"\bTRUNCATE\b",
    r"\bREPLACE\b",
    r"\bATTACH\b",
    r"\bDETACH\b",
    r"\bPRAGMA\b",
    r"\bVACUUM\b",
    r"\bANALYZE\b",
    r"\bREINDEX\b",
    r"\bWRITE\b",
    r"--",        # SQL comment injection
    r";.*\S",     # Multiple statements
]

def validate_query(sql: str) -> tuple[bool, str]:
    """Validate a query is safe to execute. Returns (is_safe, reason)."""
    sql_upper = sql.upper().strip()

    # Must start with SELECT
    if not sql_upper.startswith("SELECT"):
        return False, "Only SELECT queries are allowed. Received: " + sql_upper[:20]

    # Check for forbidden operation keywords
    for pattern in FORBIDDEN_PATTERNS:
        if re.search(pattern, sql_upper):
            return False, f"Forbidden pattern detected: {pattern}"

    # Check for forbidden table access
    for table in FORBIDDEN_TABLES:
        if re.search(r'\b' + table.upper() + r'\b', sql_upper):
            return False, f"Access to table '{table}' is not permitted for AI agents"

    return True, "ok"

def sanitize_row(row: dict) -> dict:
    """Remove forbidden columns from a result row."""
    return {k: v for k, v in row.items() if k.lower() not in FORBIDDEN_COLUMNS}

# ─── QUERY EXECUTION ─────────────────────────────────────────────────────────

def run_query(sql: str) -> dict:
    """Execute a validated SELECT query and return results as dict."""
    start = time.time()

    # Validate
    is_safe, reason = validate_query(sql)
    if not is_safe:
        return {"success": False, "error": reason, "rows": [], "count": 0}

    # Check DB exists
    if not DB_PATH.exists():
        return {"success": False, "error": f"Database not found at {DB_PATH}", "rows": [], "count": 0}

    try:
        # Open read-only connection using URI
        conn = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True, timeout=QUERY_TIMEOUT_SECONDS)
        conn.row_factory = sqlite3.Row
        conn.execute(f"PRAGMA query_timeout = {QUERY_TIMEOUT_SECONDS * 1000}")

        cursor = conn.cursor()

        # Add LIMIT if not present to prevent huge result sets
        sql_check = sql.upper().replace('\n', ' ')
        if 'LIMIT' not in sql_check:
            sql = sql.rstrip().rstrip(';') + f" LIMIT {MAX_ROWS}"

        cursor.execute(sql)
        raw_rows = cursor.fetchmany(MAX_ROWS)
        rows = [sanitize_row(dict(row)) for row in raw_rows]
        conn.close()

        elapsed = round(time.time() - start, 3)

        # Audit log
        log_query(sql, len(rows), elapsed, success=True)

        return {
            "success": True,
            "count": len(rows),
            "rows": rows,
            "elapsed_ms": int(elapsed * 1000),
            "truncated": len(rows) == MAX_ROWS
        }

    except sqlite3.OperationalError as e:
        log_query(sql, 0, time.time() - start, success=False, error=str(e))
        return {"success": False, "error": f"SQL error: {str(e)}", "rows": [], "count": 0}
    except Exception as e:
        log_query(sql, 0, time.time() - start, success=False, error=str(e))
        return {"success": False, "error": f"Unexpected error: {str(e)}", "rows": [], "count": 0}

# ─── AUDIT LOGGING ───────────────────────────────────────────────────────────

def log_query(sql: str, row_count: int, elapsed: float, success: bool, error: str = None):
    """Append every AI query to the audit log. Never deletes."""
    entry = {
        "ts": datetime.utcnow().isoformat() + "Z",
        "sql": sql[:500],  # truncate very long queries
        "row_count": row_count,
        "elapsed_s": round(elapsed, 3),
        "success": success,
        "error": error
    }
    try:
        AUDIT_LOG.parent.mkdir(parents=True, exist_ok=True)
        with open(AUDIT_LOG, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")
    except Exception:
        pass  # Never crash on audit log failure

# ─── HTTP SERVER MODE ─────────────────────────────────────────────────────────

def run_http_server(port: int = 5001):
    """Run as a simple HTTP API so Node.js agent can call it."""
    from http.server import HTTPServer, BaseHTTPRequestHandler

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, format, *args):
            pass  # Suppress default HTTP logs

        def do_POST(self):
            if self.path != "/query":
                self.send_response(404)
                self.end_headers()
                return

            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length)
            try:
                data = json.loads(body)
                sql = data.get("sql", "").strip()
            except Exception:
                sql = ""

            result = run_query(sql) if sql else {"success": False, "error": "No SQL provided", "rows": [], "count": 0}

            response = json.dumps(result).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", len(response))
            self.end_headers()
            self.wfile.write(response)

        def do_GET(self):
            if self.path == "/health":
                resp = json.dumps({"status": "ok", "db_exists": DB_PATH.exists()}).encode()
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(resp)
            else:
                self.send_response(404)
                self.end_headers()

    print(f"🔍 FraudSense DB Tool running on http://localhost:{port}")
    print(f"   Database: {DB_PATH}")
    print(f"   Audit log: {AUDIT_LOG}")
    print(f"   POST /query  {{\"sql\": \"SELECT ...\"}}")
    print(f"   GET  /health")
    HTTPServer(("localhost", port), Handler).serve_forever()

# ─── CLI MODE ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="FraudSense Read-Only DB Tool")
    parser.add_argument("sql", nargs="?", help="SQL SELECT query to execute")
    parser.add_argument("--http", action="store_true", help="Run as HTTP server")
    parser.add_argument("--port", type=int, default=5001, help="HTTP server port")
    args = parser.parse_args()

    if args.http:
        run_http_server(args.port)
    elif args.sql:
        result = run_query(args.sql)
        print(json.dumps(result, indent=2, default=str))
    else:
        parser.print_help()
