# 🏦 FundTrace AI — Fund Flow Fraud Detection System

> **A full-stack banking simulation with live fraud detection, a graph-based fund flow explorer, and an autonomous AI investigator.**  
> Built with **Node.js + Express + Socket.IO + SQLite** on the backend and a **Python ReAct agent powered by local Ollama LLM** for intelligent alert analysis.

[![Node.js](https://img.shields.io/badge/Node.js-20.x-green.svg)](https://nodejs.org)
[![Express](https://img.shields.io/badge/Express-4.18-lightgrey.svg)](https://expressjs.com)
[![Socket.IO](https://img.shields.io/badge/Socket.IO-4.7-black.svg)](https://socket.io)
[![SQLite](https://img.shields.io/badge/SQLite-WAL_Mode-blue.svg)](https://sqlite.org)
[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![Ollama](https://img.shields.io/badge/LLM-Ollama_Local-orange.svg)](https://ollama.ai)
[![JWT](https://img.shields.io/badge/Auth-JWT_+_bcrypt-red.svg)](#)
[![Platform](https://img.shields.io/badge/Platform-Windows-blue.svg)](#)

---

## 📋 Table of Contents

- [What Is FundTrace AI?](#-what-is-fundtrace-ai)
- [System Overview](#-system-overview)
- [Architecture Deep Dive](#️-architecture-deep-dive)
- [Project Structure](#-project-structure)
- [Database Schema](#-database-schema)
- [Fraud Detection Engine](#-fraud-detection-engine)
- [FraudSense AI Agent](#-fraudsense-ai-agent)
- [API Reference](#-api-reference)
- [Security Design](#-security-design)
- [Quick Start (Windows)](#-quick-start-windows)
- [Testing the Full Flow](#-testing-the-full-flow)
- [File Overview](#-file-overview)
- [Troubleshooting](#-troubleshooting)

---

## 🎯 What Is FundTrace AI?

FundTrace AI is a **fully functional banking fraud detection simulation** — not a toy demo, but a real system with production-grade patterns throughout.

It provides **two separate web portals** running from a single server:

| Portal | URL | Role |
|--------|-----|------|
| 🏦 **Client Banking App** | `http://localhost:3000/client` | Bank customers — register, login, send money, manage connections |
| 👮 **Officer Investigation Portal** | `http://localhost:3000/officer` | Bank fraud investigators — live alerts, graph explorer, account controls |

The moment a suspicious transaction occurs, a **fraud alert fires in real time** to the officer portal via WebSocket — no polling, no delay. The officer can then trigger **FraudSense**, an autonomous Python AI agent running on a local Ollama LLM, which queries the database, reads logs, recalls past entity profiles, and produces a structured risk report with evidence chain and a recommendation.

> 🏆 **What makes this project exceptional:** It combines a well-engineered Express REST API, stateful WebSocket sessions, a multi-table SQLite schema with WAL mode, a 6-pattern rule-based fraud engine that simulates a GNN + Isolation Forest ensemble, a BFS fund-flow graph traversal, a full social connection system, coupon mechanics, brute-force protection, JWT auth with server-side session revocation, AND a local-LLM-powered ReAct agent — all working together in a coherent, testable system. This is the kind of project that demonstrates real engineering depth.

---

## 🗺️ System Overview

```
┌────────────────────────────────────────────────────────────┐
│                    BROWSER CLIENTS                          │
│                                                            │
│  ┌──────────────────┐        ┌──────────────────────────┐  │
│  │  Client App      │        │  Officer Portal          │  │
│  │  /client/        │        │  /officer/               │  │
│  │  login, dashboard│        │  alerts, graph explorer  │  │
│  │  friends, txns   │        │  accounts, coupons       │  │
│  └────────┬─────────┘        └───────────┬──────────────┘  │
│           │ HTTP + WebSocket              │ HTTP + WebSocket │
└───────────┼──────────────────────────────┼─────────────────┘
            │                              │
┌───────────▼──────────────────────────────▼─────────────────┐
│                   Node.js Server (port 3000)                │
│                                                            │
│   Express REST API          │   Socket.IO                  │
│   ├── /api/auth             │   ├── user_{id} rooms        │
│   ├── /api/transactions     │   ├── officers room          │
│   ├── /api/social           │   └── real-time events:      │
│   ├── /api/fraud            │       txn_received           │
│   └── /api/coupons          │       fraud_alert            │
│                             │       notification           │
│   Middleware Stack:                                         │
│   ├── Rate Limiter (200 req/15min general, 20 auth)        │
│   ├── Cookie Parser + JWT Verify                           │
│   ├── CORS (localhost:3000)                                │
│   └── JSON body parser (10MB limit)                        │
│                                                            │
│   ├── Fraud Engine (scoreFraud — 6 pattern checks)         │
│   └── BFS Graph Traversal (fund flow network)              │
└───────────────────────────┬────────────────────────────────┘
                            │
              ┌─────────────▼──────────────┐
              │  SQLite (fundtrace.db)      │
              │  WAL mode + FK constraints  │
              │  8 tables, 7 indexes        │
              └─────────────┬──────────────┘
                            │
              ┌─────────────▼──────────────┐
              │  FraudSense AI Agent        │
              │  Python / port 5002         │
              │  ReAct loop (max 5 iters)   │
              │  ├── Ollama LLM             │
              │  ├── query_db tool          │
              │  ├── read_logs tool         │
              │  └── read_entity_profile    │
              └────────────────────────────┘
```

---

## 🏗️ Architecture Deep Dive

### 1. Server Layer — `server/index.js`

Single entry point that wires everything together:

- **HTTP server** wraps Express so Socket.IO can share the same port
- **Socket.IO** with JWT-from-cookie authentication: on connection, the JWT is parsed from the cookie to join the right rooms (`user_{id}` for personal events, `officers` for the officer alert feed)
- **Rate limiting**: Two tiers — strict `authLimiter` (20 req/5s in dev) on auth routes, general `generalLimiter` (200 req/15min) on all routes
- **Static serving**: `/client` → `../client/`, `/officer` → `../officer/` — two complete SPAs from a single server
- **AI sidecar**: `fraudModule._io = io` passes the Socket.IO instance to `fraud.js` so it can broadcast real-time alerts without circular imports

### 2. Authentication — `server/auth.js`

A complete, production-patterned auth system with:

| Feature | Implementation |
|---------|---------------|
| Password hashing | `bcrypt` — **12 rounds** (industry standard, ~300ms per hash) |
| Token type | `JWT` signed with `JWT_SECRET`, 7-day expiry |
| Session storage | **Server-side session table** in SQLite — tokens are SHA-256 hashed and stored. Logout truly invalidates the token, unlike pure JWT |
| Cookie security | `httpOnly: true`, `sameSite: 'strict'` — XSS-proof |
| Brute-force protection | Tracks failed login attempts per email in `login_attempts` table; locks after 10 failed attempts in 15 min |
| Password validation | Enforces 8+ chars, uppercase, lowercase, number, special character |
| Login identifier | Accepts both email OR phone number — auto-detects which was provided |
| Account freeze | Frozen accounts are blocked at login with a meaningful error, not just a silent 401 |
| Error messages | Generic `"Invalid email or password"` — never reveals whether the email exists (user enumeration protection) |

**Token lifecycle:**
```
Register/Login → JWT generated → SHA-256(JWT) stored in sessions table
                               → JWT set as httpOnly cookie
Request        → Cookie read → JWT verified → SHA-256 checked against sessions table
Logout         → Session row deleted → token permanently dead (server-side revocation)
```

### 3. Transactions — `server/transactions.js`

Handles money movement with atomic SQLite operations:

```
POST /api/transactions/send
  1. Validate recipient exists (by FT-code, account number, or name search)
  2. Check sender balance ≥ amount
  3. Check sender account is not frozen
  4. BEGIN transaction:
     - Debit sender.balance
     - Credit receiver.balance
     - Insert transactions row (with txn_id, channel, note, flagged flag)
  5. COMMIT
  6. Emit Socket.IO txn_received event to receiver's personal room
  7. Pass completed txn to scoreFraud() → detect patterns
  8. If score > 0: createFraudAlert() → emit to officers room
```

**Payment channels supported:** `IMPS`, `NEFT`, `RTGS`, `UPI`

### 4. Social Connections — `server/social.js`

Instagram-style friend request system:

- Users find each other by **FundTrace ID** (`FT-XXXXXX`) — no email/phone sharing required
- States: `pending → accepted | rejected`
- Accepted connections appear in the "Send Money" recipient picker
- Officers can see the full social graph when investigating a user

### 5. Officer Coupon System — `server/coupons.js`

Officers can create discount/reward coupons (`CP-XXXXXX` codes), clients redeem them for balance credits. Adds a gamification + bank incentive dimension to the simulation.

---

## 📂 Project Structure

```
FundTrace AI system/
│
├── README.md                    ← ⭐ You are here
├── file structure.txt           # Quick structural reference
├── auth delay.md                # Auth flow notes
├── sample accounts.txt          # Test account credentials
├── fund_flow_fraud_detection_system.html  # Concept overview document
│
├── server/                      ← 🟢 Node.js Backend
│   ├── index.js                 # Entry point: Express + Socket.IO bootstrap
│   ├── db.js                    # SQLite schema, migrations, DB helpers
│   ├── auth.js                  # JWT auth, bcrypt, brute-force protection
│   ├── transactions.js          # Money transfer, balance, notifications
│   ├── social.js                # Friend requests, connections, user search
│   ├── fraud.js                 # ⭐ Fraud engine + all officer API routes
│   ├── coupons.js               # Officer coupon creation + client redemption
│   ├── logger.js                # Request/event logging to disk
│   ├── fundtrace.db             # SQLite database (auto-created)
│   └── package.json             # Dependencies
│
├── client/                      ← 🔵 Customer Web App
│   ├── login.html               # Login with email or phone
│   ├── register.html            # Registration with password strength meter
│   ├── dashboard.html           # Balance display, send money, notifications
│   ├── friends.html             # Add by FT-ID, accept/reject requests
│   ├── transactions.html        # Full history with channel/date filters
│   ├── settings.html            # Profile update, password change
│   ├── css/
│   │   └── app.css              # Shared design system (dark theme, components)
│   └── js/
│       └── api.js               # Shared: fetch wrapper, auth guard, Socket.IO, toasts
│
├── officer/                     ← 🔴 Officer Investigation Portal
│   ├── login.html               # Dark-themed officer-only login
│   └── dashboard.html           # Live feed, graph explorer, alerts, accounts
│
└── ai/                          ← 🤖 FraudSense AI Agent (Python)
    ├── agent.py                 # ReAct loop orchestrator
    ├── requirements.txt         # Python dependencies
    ├── ollama_setup.md          # LLM backend setup guide
    ├── core/
    │   ├── context_builder.py   # Builds structured LLM prompt from alert data
    │   ├── llm_client.py        # Ollama HTTP client + JSON response parser
    │   └── memory_writer.py     # Episodic memory + entity profile system
    ├── tools/
    │   ├── db_tool.py           # Safe read-only SQLite query runner
    │   └── log_reader.py        # Event log parser for agent context
    ├── memory/
    │   └── entities/            # Per-account markdown profiles (FT-XXXXXX.md)
    └── logs/                    # Structured event logs for agent consumption
```

---

## 🗄️ Database Schema

FundTrace uses **SQLite with WAL mode** for better concurrent read performance and **foreign key constraints** enforced at the PRAGMA level. The schema is defined and auto-applied in `db.js` — the database is created on first server start with no manual setup.

### Tables

```sql
users               — Bank accounts (clients + officers)
sessions            — Server-side JWT session store
friends             — Social connections with state machine
transactions        — All money movements
fraud_alerts        — Detected fraud events
notifications       — In-app notification inbox
login_attempts      — Brute-force tracking
coupons             — Officer-created reward codes
```

### Schema Detail

#### `users`
| Column | Type | Notes |
|--------|------|-------|
| `id` | INTEGER PK | Auto-increment |
| `unique_code` | TEXT UNIQUE | `FT-XXXXXX` format — public identifier |
| `full_name` | TEXT | |
| `email` | TEXT UNIQUE | Lowercase-normalized on insert |
| `phone` | TEXT UNIQUE (nullable) | Normalized (stripped of `+`, spaces, dashes) |
| `password_hash` | TEXT | bcrypt 12 rounds |
| `role` | TEXT | `'client'` or `'officer'` |
| `balance` | REAL | Default `10000.00` for new clients |
| `account_number` | TEXT UNIQUE | `ACC-{year}-{6-digit}` format |
| `branch` | TEXT | Default `'Mumbai-Main'` |
| `account_type` | TEXT | `'Savings'` / `'Current'` / `'Official'` |
| `status` | TEXT | `'active'` / `'frozen'` / `'dormant'` |
| `last_active` | INTEGER | Unix timestamp |

#### `transactions`
| Column | Type | Notes |
|--------|------|-------|
| `txn_id` | TEXT UNIQUE | `TXN-{5digit}` format |
| `from_user_id` / `to_user_id` | INTEGER FK | References `users(id)` |
| `from_account` / `to_account` | TEXT | Account number strings |
| `amount` | REAL | In INR (₹) |
| `channel` | TEXT | `IMPS / NEFT / RTGS / UPI` |
| `note` | TEXT | Optional memo |
| `flagged` | INTEGER | `0` or `1` |
| `fraud_score` | REAL | Computed by `scoreFraud()` at time of transaction |

#### `fraud_alerts`
| Column | Type | Notes |
|--------|------|-------|
| `alert_id` | TEXT UNIQUE | `ALT-{4digit}` format |
| `pattern_type` | TEXT | `circular / layering / structuring / dormant / profile_mismatch` |
| `risk_score` | REAL | 0–100 |
| `status` | TEXT | `open → reviewing → closed / filed` |
| `assigned_to` | INTEGER FK | Officer assigned for investigation |
| `description` | TEXT | JSON blob with full pattern detail + parties involved |

### Indexes

```sql
idx_transactions_from     ON transactions(from_user_id)
idx_transactions_to       ON transactions(to_user_id)
idx_transactions_time     ON transactions(created_at)
idx_fraud_alerts_user     ON fraud_alerts(user_id)
idx_notifications_user    ON notifications(user_id, read)
idx_coupons_status        ON coupons(status)
idx_coupons_redeemed_by   ON coupons(redeemed_by)
idx_users_phone_unique    UNIQUE ON users(phone) WHERE phone IS NOT NULL
```

The partial unique index on `phone` (`WHERE phone IS NOT NULL`) is a notable design choice — it allows multiple accounts to have no phone number while enforcing uniqueness when one is provided.

---

## 🚨 Fraud Detection Engine

The fraud engine lives in `server/fraud.js` — `scoreFraud()`. It simulates a **GNN + Isolation Forest ensemble model** using deterministic rule-based pattern matching against rolling time windows. Every transaction is scored synchronously before the response returns to the client.

### The 6 Detection Patterns

#### Pattern 1 — Rapid Layering
```
Trigger: ≥ 5 outgoing transactions from same account within 1 hour
Score:   +15 (5–9 txns) / +30 (10+ txns)
Signal:  "Smurfing" money laundering — splitting large amounts into rapid
         small transfers to obscure the trail
```

#### Pattern 2 — Circular Transaction Detection (Graph-based)
```
Trigger: Money flowing A → X → ... → B → A (through intermediate accounts within 72h)
Score:   +35 per circular path detected

Implementation: Two-hop graph query
  - Get all accounts that recently sent money TO the SENDER (within 72h)
  - Get all accounts that the RECEIVER recently sent money TO (within 72h)
  - Overlap → potential intermediate accounts forming a circuit

Direct round-trip: A → B then B → A within 24h
Score: +25
Signal: Classic "boomerang" technique — funds return to origin
         after passing through an intermediary to create distance
```

#### Pattern 3 — Structuring / Smurfing Below Threshold
```
Trigger: Amount between ₹9,00,000–₹9,99,999 (just below ₹10L mandatory reporting)
         AND ≥ 2 such transactions from same sender in 24h
Score:   +30
Signal:  Classic regulatory evasion — breaking large amounts into
         sub-threshold transactions to avoid CTR (Cash Transaction Report) filing
```

#### Pattern 4 — Dormant Account Sudden Activity
```
Trigger: Account had no transactions for 30+ days AND now initiating
         a transfer > ₹50,000
Score:   +20
Signal:  Dormant accounts are commonly used as "mule accounts" —
         opened for legitimate purposes, then reactivated to pass
         through illicit funds in a burst of activity
```

#### Pattern 5 — Profile Mismatch / Pass-Through Behaviour
```
Trigger: Balance before this transaction was 5× higher than current balance
         AND pre-txn balance > ₹1,00,000
Score:   +15
Signal:  Sender received a large unexpected inflow (possibly from a mule
         account), then immediately forwards it out — characteristic of
         pass-through / "middle-man" laundering accounts
```

#### Pattern 6 — High Velocity Receiver (Aggregation Point)
```
Trigger: Recipient received ≥ 8 inbound transfers within 1 hour
Score:   +20
Signal:  Funds converging to a single collection account — a common
         fraud pattern where multiple mule accounts funnel money
         to a central aggregator before final extraction
```

### Risk Score Interpretation

| Score | Risk Level | Default Action |
|-------|-----------|----------------|
| 0–29 | Low | No alert |
| 30–49 | Medium | Alert created, auto-assigned `open` |
| 50–69 | High | Alert flagged high-priority |
| 70–100 | Critical | Officer notified instantly via Socket.IO |

Score is capped at 100 (multiple patterns can stack).

### Real-time Alert Delivery

```javascript
// When score > 0, fraud.js emits to the 'officers' Socket.IO room:
module.exports._io.to('officers').emit('fraud_alert', {
  alert_id, risk_score, pattern,
  amount, sender_name, receiver_name, timestamp
});
```

The officer dashboard receives this event instantly and renders a live alert card with pattern type, risk score and parties involved — no refresh needed.

---

## 🤖 FraudSense AI Agent

The `ai/` folder contains **FraudSense** — an autonomous investigation agent that can be triggered by officers for any fraud alert. It runs as a Python HTTP server on port `5002`.

### ReAct Architecture

FraudSense implements the **ReAct (Reason + Act) loop** pattern:

```
ITERATION LOOP (max 5 cycles):
  1. Build context → call LLM
  2. Parse LLM JSON response:
     ├── tool_needed: true  → run the tool → append result → loop
     └── final_answer: {...} → break, save to memory, return
  3. If max iterations reached → fallback answer (risk=50, confidence=20)
```

### Available Tools

| Tool | Input Format | What It Does |
|------|-------------|-------------|
| `query_db` | SQL string | Executes a read-only SQLite query, returns up to 15 rows as JSON |
| `read_logs` | `account_code=FT-X\|hours=48\|limit=30` | Reads from structured event logs filtered by account and time |
| `read_entity_profile` | FundTrace ID (`FT-XXXXXX`) | Reads the persisted markdown entity profile from past investigations |

### Memory System

FraudSense has **two memory layers**, both written after each investigation:

1. **Episodic memory** (`memory/episodes/`) — timestamped JSON records of every investigation (alert ID, task, risk score, recommendation, evidence chain, open questions)
2. **Entity profiles** (`memory/entities/FT-XXXXXX.md`) — per-account markdown profiles that accumulate over time. On the next investigation involving the same account, the agent reads its own prior analysis, building long-term behavioral context

### Input / Output

**Input (POST `/analyze`)**:
```json
{
  "task": "Analyze fraud alert ALT-0892 for account FT-X7K2P9",
  "entity_code": "FT-X7K2P9",
  "pattern": "circular",
  "alert_id": "ALT-0892",
  "user_id": 42
}
```

**Output**:
```json
{
  "success": true,
  "episode_id": "EP-2026-...",
  "final_answer": {
    "risk_score": 85,
    "risk_level": "critical",
    "patterns_detected": ["circular", "layering"],
    "evidence": ["TXN-88201: ₹50,000 A→B", "TXN-88205: ₹48,000 B→A within 2hr"],
    "reasoning": "Account shows clear round-trip pattern...",
    "recommendation": "freeze",
    "confidence": 87,
    "open_questions": ["Source of funds at T-72h?"]
  },
  "iterations": 3,
  "tool_calls": 2,
  "elapsed_s": 14.2,
  "model": "llama3.2",
  "backend": "ollama"
}
```

### Running the Agent

```bash
# Install dependencies
pip install -r ai/requirements.txt

# Start as HTTP server (so Node.js server can call it)
python ai/agent.py --http --port 5002

# CLI mode — analyze a specific alert
python ai/agent.py --alert-id ALT-0892 --entity-code FT-X7K2P9 --pattern circular --verbose

# Health check
curl http://localhost:5002/health
```

> See `ai/ollama_setup.md` for configuring the local Ollama LLM backend.

---

## 📡 API Reference

All API routes are prefixed with `/api`. Protected routes require the `ft_token` httpOnly cookie set at login.

### Authentication — `/api/auth`

| Method | Route | Auth | Description |
|--------|-------|------|-------------|
| `POST` | `/register` | Public | Create account (email, phone, password, name, branch) |
| `POST` | `/login` | Public | Login with email or phone + password |
| `POST` | `/logout` | 🔒 Client | Invalidate session (deletes server-side session row) |
| `GET` | `/me` | 🔒 Client | Get current user profile |
| `GET` | `/check` | 🔒 Client | Quick auth check (returns role) |
| `PATCH` | `/profile` | 🔒 Client | Update name, phone, or password |

### Transactions — `/api/transactions`

| Method | Route | Auth | Description |
|--------|-------|------|-------------|
| `POST` | `/send` | 🔒 Client | Send money to recipient |
| `GET` | `/history` | 🔒 Client | Transaction history (paginated, with filters) |
| `GET` | `/balance` | 🔒 Client | Current balance |
| `GET` | `/notifications` | 🔒 Client | In-app notification inbox |
| `POST` | `/notifications/read` | 🔒 Client | Mark notifications as read |

### Social — `/api/social`

| Method | Route | Auth | Description |
|--------|-------|------|-------------|
| `POST` | `/request` | 🔒 Client | Send friend request by FT-ID |
| `GET` | `/requests` | 🔒 Client | Incoming pending requests |
| `POST` | `/accept/:id` | 🔒 Client | Accept a friend request |
| `POST` | `/reject/:id` | 🔒 Client | Reject a friend request |
| `GET` | `/connections` | 🔒 Client | Accepted connections list |
| `GET` | `/search?q=` | 🔒 Client | Search users by name or FT-ID |

### Fraud / Officer — `/api/fraud`

| Method | Route | Auth | Description |
|--------|-------|------|-------------|
| `GET` | `/alerts` | 👮 Officer | All fraud alerts (paginated, filterable by status) |
| `GET` | `/alerts/:alertId` | 👮 Officer | Single alert detail + full transaction chain |
| `PATCH` | `/alerts/:alertId` | 👮 Officer | Update alert status (`open → reviewing → closed → filed`) |
| `POST` | `/freeze/:userId` | 👮 Officer | Freeze a client account |
| `POST` | `/unfreeze/:userId` | 👮 Officer | Unfreeze a client account |
| `GET` | `/accounts` | 👮 Officer | All client accounts with status |
| `GET` | `/graph/:userId` | 👮 Officer | BFS fund flow graph (depth + time window configurable) |
| `GET` | `/stats` | 👮 Officer | Dashboard stats (totals, volumes, pattern breakdown) |

### Coupons — `/api/coupons`

| Method | Route | Auth | Description |
|--------|-------|------|-------------|
| `POST` | `/create` | 👮 Officer | Create a reward coupon |
| `GET` | `/list` | 👮 Officer | All coupons with status |
| `POST` | `/redeem` | 🔒 Client | Redeem a coupon code for balance credit |

### Health Check

```
GET /api/health → { "status": "ok", "timestamp": ..., "version": "1.0.0" }
```

---

## 🔒 Security Design

FundTrace was built with real security patterns throughout — not just for show:

| Layer | What's Protected | How |
|-------|-----------------|-----|
| **Passwords** | Brute-force, rainbow tables | bcrypt 12 rounds (~300ms per hash) |
| **Sessions** | Token theft after logout | Server-side session table — logout truly revokes |
| **Cookies** | XSS attacks | `httpOnly: true` — JS cannot read the token |
| **CSRF** | Cross-site requests | `sameSite: 'strict'` cookie policy |
| **Brute-force** | Password guessing | `login_attempts` table — lock after 10 failures in 15 min |
| **Rate limiting** | DoS, scraping | 200 req/15min general; 20 req/15min on auth routes |
| **User enumeration** | Email harvesting | Generic error message on bad login — never reveals if email exists |
| **Account suspension** | Frozen accounts transacting | `status = 'frozen'` blocks both login AND transaction send |
| **Officer separation** | Clients accessing investigation data | `requireOfficer` middleware — role is checked server-side, not just on frontend |
| **Input validation** | SQL injection (via prepared statements), invalid data | All DB queries use `better-sqlite3` prepared statements; explicit field validation on all inputs |

### Production Hardening Checklist

Before deploying outside localhost:

```bash
# 1. Change the JWT secret
JWT_SECRET=your-very-long-random-secret-32chars-minimum node index.js

# 2. Enable HTTPS cookies (auth.js)
secure: true   # in issueToken()

# 3. Restore rate limiter windows to production values (index.js)
windowMs: 15 * 60 * 1000   # 15 minutes (remove the 5-second dev override)

# 4. Add HTTPS/TLS termination (nginx recommended)

# 5. Restrict CORS origins (index.js)
origin: ['https://yourdomain.com']
```

> The bcrypt password hashing is already production-grade. Password strength validation is already enforced server-side (not just client-side). No changes needed there.

---

## 🚀 Quick Start (Windows)

### Prerequisites

| | Required | Notes |
|--|---------|-------|
| **Node.js** | v18+ LTS | Download from nodejs.org — use the green LTS button |
| **npm** | Bundled with Node | No separate install needed |
| **Python** | 3.10+ (optional) | Only needed for the AI agent |
| **Ollama** | Latest (optional) | Only needed for the AI agent |
| **Browser** | Chrome or Edge | Do NOT use Internet Explorer |

### Step 1 — Install Node.js

1. Go to **https://nodejs.org**
2. Download the **LTS version** (green button)
3. Run the installer — click Next through everything, keep all defaults
4. After installation, open **Command Prompt** (`Win+R` → `cmd` → Enter)
5. Verify:
   ```
   node --version   → should show v18.x.x or v20.x.x
   npm --version    → should show a version number
   ```

### Step 2 — Place Project Files

Put the project folder anywhere on your machine. The internal structure must be preserved — do not move files between folders.

### Step 3 — Install Dependencies

```cmd
cd path\to\FundTrace AI system\server
npm install
```

This downloads all packages into `server/node_modules/`. Takes 1–2 minutes on first run.

### Step 4 — Start the Server

Still inside the `server/` folder:

```cmd
node index.js
```

You should see:

```
╔════════════════════════════════════════════╗
║        FundTrace AI — Server Running       ║
╠════════════════════════════════════════════╣
║  Client App : http://localhost:3000/client  ║
║  Officer App: http://localhost:3000/officer ║
║  API        : http://localhost:3000/api     ║
╚════════════════════════════════════════════╝

  Officer login: officer@fundtrace.bank / Officer@123
```

### Step 5 — Open in Browser

- **Client app**: http://localhost:3000/client/login.html
- **Officer portal**: http://localhost:3000/officer/login.html

### Development Mode (Auto-Restart)

```cmd
npm run dev
```

Uses `nodemon` — server auto-restarts when any source file changes.

### Stopping and Restarting

- Stop: `Ctrl + C` in the Command Prompt
- Restart: `node index.js` again
- All data in `fundtrace.db` persists across restarts
- To wipe all data: delete `server/fundtrace.db` and restart — the DB rebuilds automatically

---

## 🧪 Testing the Full Flow

### Default Credentials

**Bank Officer (pre-seeded):**
- Email: `officer@fundtrace.bank`
- Password: `Officer@123`

**Client accounts:**  
Register new accounts at `/client/register.html`. Each new account gets **₹10,000 welcome balance** automatically.

**Password requirements:** 8+ chars, uppercase, lowercase, number, special character  
Example: `Test@1234`

---

### Test Scenario A — Basic Money Transfer

1. **Register 2 client accounts** at `/client/register.html`
   - Alice: `alice@test.com`
   - Bob: `bob@test.com`

2. **Log in as Alice** → go to Dashboard — see ₹10,000 balance

3. **Note Alice's FundTrace ID** (e.g., `FT-X7K2P9`) shown on the dashboard

4. **Log in as Bob** → go to Friends → "Add Connection" tab → enter Alice's FT-ID → Send Request

5. **Switch back to Alice** → Friends → accept Bob's request

6. **As Alice on Dashboard** → search for Bob → enter an amount → select channel → Send

7. **Watch Bob's dashboard** — balance updates live via Socket.IO (no page refresh needed)

---

### Test Scenario B — Triggering Fraud Detection

#### Layering Alert (5 quick transfers)

While logged in as Alice:
1. Send ₹500 to Bob → send again → send again → send again → send again (5 transfers within a minute)
2. Open the **officer portal** in a separate window
3. A `🚨 Fraud Alert` card appears live on the officer dashboard — pattern: `layering`, score: ~30

#### Circular Transaction Alert

1. **Alice sends ₹5,000 to Bob**
2. **Bob immediately sends ₹4,800 back to Alice**
3. Officer portal shows a `circular` alert — direct round-trip detected within 24 hours

#### Structuring Alert

1. As Alice, send **₹920,000** to Bob (just below the ₹10,00,000 threshold)
2. Send **₹950,000** again shortly after
3. A `structuring` alert fires — 2 sub-threshold high-value transactions in 24h

---

### Test Scenario C — Officer Investigation

1. Log into the officer portal at `/officer/login.html`
2. Go to the **Overview** tab → see live transaction feed
3. Go to **Alerts** tab → click any alert → see full detail panel with transaction chain
4. Change an alert status from `open` → `reviewing` → `filed`
5. Go to **Graph Explorer** → enter any User ID from the Accounts tab → click Load → see the BFS fund flow network with color-coded risk nodes

---

### Test Scenario D — FraudSense AI Agent

> Requires Python 3.10+ and Ollama installed. See `ai/ollama_setup.md`.

1. Start the agent server:
   ```bash
   python ai/agent.py --http --port 5002
   ```

2. From officer portal, click **"AI Analyze"** on any open fraud alert
   (or call the API directly):
   ```bash
   curl -X POST http://localhost:5002/analyze \
     -H "Content-Type: application/json" \
     -d "{\"task\": \"Analyze this alert\", \"alert_id\": \"ALT-0892\", \"entity_code\": \"FT-X7K2P9\", \"pattern\": \"circular\"}"
   ```

3. The agent runs its ReAct loop (watch terminal for iteration logs), queries the DB, reads logs, and returns a structured risk report

---

## 📁 File Overview

| File | What It Does |
|------|-------------|
| `server/index.js` | Main server: Express bootstrap, Socket.IO setup, route registration, static serving |
| `server/db.js` | SQLite schema (8 tables), all DB helper functions, data generators for IDs/codes |
| `server/auth.js` | Register, login, logout, JWT issue/verify, bcrypt, brute-force tracking, session table |
| `server/transactions.js` | Send money (atomic balance update), transaction history, balance query, notifications |
| `server/social.js` | Friend requests (send/accept/reject), connections list, user search by name/FT-ID |
| `server/fraud.js` | 6-pattern fraud scoring engine, alert creation, Socket.IO broadcast, all officer API routes |
| `server/coupons.js` | Officer coupon creation (`CP-XXXXXX`), client redemption with balance credit |
| `server/logger.js` | Structured event logging to disk (consumed by AI agent's `read_logs` tool) |
| `client/css/app.css` | Complete shared design system: dark theme, card components, buttons, toasts, animations |
| `client/js/api.js` | Shared JS: authenticated fetch wrapper, auth guard, Socket.IO listener, toast notifications, currency/date formatters |
| `client/login.html` | Client login form — email or phone credential |
| `client/register.html` | Registration with real-time password strength meter |
| `client/dashboard.html` | Main hub: balance widget, send money panel, recent transactions, live notifications |
| `client/friends.html` | Connection management: add by FT-ID, incoming requests, accepted connections list |
| `client/transactions.html` | Full transaction history: paginated, filterable by channel and date range |
| `client/settings.html` | Profile management: update name, phone, change password |
| `officer/login.html` | Dark-themed officer-only login (rejects client credentials) |
| `officer/dashboard.html` | Full investigation suite: live stats, transaction feed, alerts panel, graph explorer, accounts table, coupon tools |
| `ai/agent.py` | FraudSense ReAct loop orchestrator — HTTP server mode + CLI mode |
| `ai/core/context_builder.py` | Builds structured prompt from alert data, entity profile, tool history |
| `ai/core/llm_client.py` | Ollama HTTP client, JSON extraction from LLM raw text, error handling |
| `ai/core/memory_writer.py` | Writes episodic memory records, updates per-entity markdown profiles |
| `ai/tools/db_tool.py` | Safe read-only SQLite runner for the AI agent (same DB as server) |
| `ai/tools/log_reader.py` | Parses structured log files, returns human-readable event summaries |

---

## 🔧 Troubleshooting

**`"node is not recognized as an internal or external command"`**  
→ Node.js wasn't installed or PATH wasn't updated. Restart Command Prompt after installing.

**`"EADDRINUSE: address already in use :::3000"`**  
→ Something else is already running on port 3000. Change the port:
```cmd
set PORT=3001 && node index.js
```
Then access the app at `http://localhost:3001/...`

**`"Cannot find module 'better-sqlite3'"`**  
→ Run `npm install` inside the `server/` folder.

**Page shows "Not authenticated" or keeps redirecting to login**  
→ You must access the app via `http://localhost:3000` (not `file://`). Cookies only work over HTTP/HTTPS.

**Officer login says "Access denied"**  
→ Use exact credentials: `officer@fundtrace.bank` / `Officer@123` (case-sensitive). Client accounts cannot log into the officer portal.

**Fraud alerts not appearing in officer dashboard**  
→ Make sure both the client app and officer portal are open in the **same browser**. The Socket.IO connection uses the auth cookie — different browsers won't share the session.

**AI agent not responding**  
→ Check that Ollama is running (`ollama serve`) and the model is pulled (`ollama pull llama3.2`). See `ai/ollama_setup.md`.

**Balance not updating after a transfer**  
→ The client app uses Socket.IO for live updates. Ensure you're connected via `http://` (not file://). If updates don't arrive, try a manual page refresh.

---

## 💡 Design Decisions & Engineering Notes

### Why SQLite instead of PostgreSQL?

SQLite with WAL mode is **the right choice for a single-node local development system**. WAL mode allows concurrent reads, which is necessary when the Node.js server, the AI agent's `db_tool.py`, and SQLite browser are all reading simultaneously. The entire database is a single portable file — trivial to reset (delete and restart) or inspect (open in DB Browser for SQLite). There's no Docker dependency, no separate database process, no connection pool to manage.

### Why JWT + Server-Side Sessions?

Pure JWT (stateless) cannot support logout — the token is valid until it expires, even if the user logs out. By storing a SHA-256 hash of the JWT in a `sessions` table, FundTrace gets the **best of both worlds**: fast JWT validation (no DB hit for auth check) with the ability to truly revoke any session instantly. The token hash (not the token itself) is stored — even if the sessions table were compromised, the hashes are not reversible to valid tokens.

### Why Socket.IO over Server-Sent Events?

Socket.IO enables **bidirectional** communication — officers can subscribe to the `officers` room by sending a `join_officers` event if the HTTP cookie wasn't parsed at connect time. SSE is unidirectional. The real-time fraud alert delivery and the live transaction feed both benefit from a persistent connection with named event types rather than raw SSE streams.

### Why a Python Sidecar for AI?

The Node.js ecosystem for local LLM integration is immature compared to Python. `ollama` Python SDK, `httpx`, and the standard library provide everything needed. Running the agent as a separate HTTP server on port 5002 means it can be started independently, upgraded, or replaced without touching the Node.js server. The boundary is clean: Node handles all banking operations, Python handles all AI reasoning.

---

## 📊 What Was Built — At a Glance

| Component | Technology | Lines of Code (approx.) |
|-----------|-----------|------------------------|
| Server backbone | Node.js + Express + Socket.IO | ~185 |
| Authentication system | JWT + bcrypt + SQLite sessions | ~340 |
| Transaction engine | SQLite transactions + Socket.IO events | ~310 |
| Social connections | Express REST + SQLite | ~200 |
| Fraud detection engine | Rule-based ML simulation + REST API | ~378 |
| Coupon system | Officer/client REST | ~120 |
| Database schema & helpers | SQLite + better-sqlite3 | ~250 |
| Client web app | HTML + CSS + JS (5 pages) | ~1,400 |
| Officer portal | HTML + CSS + JS (2 pages) | ~700 |
| AI agent orchestrator | Python ReAct loop | ~340 |
| AI agent core (LLM + memory + context) | Python | ~750 |
| AI agent tools | Python | ~250 |

---

*FundTrace AI — Built as a complete banking fraud simulation demonstrating real-world patterns in authentication, real-time event systems, rule-based ML fraud detection, graph traversal, and autonomous AI agents. Version 1.0.0.*
