# 🏦 FundTrace AI System — Executive Summary

## 📌 Project Overview
**FundTrace AI** is a production-grade, full-stack banking simulation and state-of-the-art fraud detection platform. It hosts two separate applications—a Customer portal and an Officer investigation suite—running from a unified Node.js/SQLite backend, coupled with a Python-based autonomous AI investigator (FraudSense).

## 🏗️ Architecture & Stack
- **Backend**: Node.js, Express, Socket.IO, `better-sqlite3` (SQLite with WAL mode).
- **Frontend**: Vanilla HTML/JS/CSS web apps (Client and Officer SPAs).
- **AI Agent**: Python 3.10+ orchestrator (ReAct loop) powered by official `groq` SDK (Llama 3.3) and local Ollama, equipped with dynamic multi-key API rotation and full JSON/MD logging.
- **Database**: 8 relational tables (`users`, `transactions`, `fraud_alerts`, `friends`, `sessions`, `notifications`, `login_attempts`, `coupons`) ensuring cross-ecosystem data safety via Foreign Keys and Indexes.

## 🚀 Key Modules & Features

### 1. 🏦 Client Banking App (`client/`)
- Allows users to register, login, and manage their profile securely (`bcrypt` + `HTTP-only JWTs` with server-side revocation).
- **Core actions**: Check balances, view transaction history (with filters), read real-time notifications, and redeem reward coupons.
- **Social System**: Users add connections using a unique ID (`FT-XXXXXX`) via an Instagram-style friend request system.

### 2. 💸 Real-time Transactions & Auth (`server/`)
- Supports money transfers (IMPS, NEFT, RTGS, UPI) wrapped in **atomic SQLite transactions** to guarantee data integrity.
- **Security**: Features brute-force tracking (`login_attempts`), anti-enumeration logic, and two-tier rate-limiting.

### 3. 🚨 Rule-Based Fraud Engine (`server/fraud.js`)
- Every transaction is evaluated synchronously in real time, simulating a GNN + Isolation Forest ensemble.
- Detects pattern anomalies such as **Rapid Layering**, **Circular Transactions**, **Structuring/Smurfing** (below threshold), **Dormant Account Spikes**, **Pass-Through Mules**, and **High-Velocity Receivers**.
- Based on the risk score (0-100), high-risk alerts are broadcast instantly via Socket.IO.

### 4. 👮 Officer Dashboard (`officer/`)
- A secure portal exclusively for investigators featuring a live transaction feed, a graph-based fund flow explorer, and actionable fraud alerts.
- Officers can evaluate alerts, trace circuits, freeze accounts, and trigger the AI agent to conduct comprehensive investigations on-demand.

### 5. 🤖 FraudSense AI Agent (`ai/`)
- A conversational ReAct loop Python agent running on port 5002.
- Capable of triggering tools to dynamically query the live SQLite database, traverse transaction logs, and refer back to generated entity profiles/memories.
- **NLP Forensic Analysis**: It provides human-readable, highly detailed intelligence, explaining account flow histories, flagging cycle alerts, and generating actionable recommendations (freeze, monitor, etc.) without model hallucination.

## 🎯 Bottom Line
FundTrace AI is an end-to-end engineered system that bridges traditional fast, reliable API design with innovative local/cloud LLM tooling to tackle complex financial routing topologies in real time.
