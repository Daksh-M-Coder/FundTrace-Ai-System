# FundTrace AI — Project Information Document

---

## 1. IDEA TITLE

**FundTrace AI: Intelligent Fund Flow Tracking System for Bank Fraud Detection**

### Proposed Solution

FundTrace AI is a full-stack intelligent banking fraud detection system that maps and visualises the end-to-end movement of funds within a bank across accounts, products, branches, and channels. The system combines a live client banking application with an AI-powered officer investigation portal, using graph analytics and an agentic AI layer to automatically identify suspicious fund flow patterns.

**How it addresses the problem:**
Traditional fraud detection relies on static rule thresholds (e.g., flag anything above ₹10L). FundTrace AI adds three layers on top: a real-time transaction graph that maps fund flows as a network of nodes and edges, a rule-based pattern engine that detects circular flows, layering, structuring, dormant account reactivation, and profile mismatches, and an agentic AI investigator (FraudSense) that reasons over live database data and historical case memory to generate evidence-based risk assessments with human-readable explanations.

**Innovation and uniqueness:**
- The system treats fund flows as a graph problem, not just a list of transactions — enabling detection of multi-hop circular patterns invisible to row-by-row analysis
- The AI agent uses a ReAct (Reason + Act) loop: it queries the database, reads event logs, reasons over the results, and iterates until it can produce a confident conclusion — mimicking how a human investigator thinks
- The agent builds persistent memory across cases using a structured episodic memory system, making it smarter over time as officer outcomes are fed back as labeled training data
- All analysis runs locally using Ollama — no API costs, no data leaving the bank's network

---

## 2. OUTLINE OF UNIQUE & INNOVATIVE SOLUTION

| Feature | Innovation |
|---------|-----------|
| Fund Flow Graph | Real-time D3-based graph visualization of transaction networks |
| Multi-hop Pattern Detection | Detects circular flows across 5+ accounts, not just direct round-trips |
| Agentic AI with Tool Use | LLM actively queries live DB and reads event logs during analysis |
| Episodic Memory | Agent remembers past cases and officer decisions to improve over time |
| Privacy-first AI | Runs on local Ollama — banking data never leaves the machine |
| ML Training Pipeline | Officer decisions automatically accumulate as labeled training data |
| Coupon/Bonus System | Bank officers can issue cryptographic coupon codes to credited accounts |
| Real-time via Socket.IO | Transaction events push instantly to officer dashboard and client app |
| Instagram-style Social | Clients connect via unique FT-XXXXXX IDs, friend-request style |

---

## 3. TECHNICAL APPROACH

### Technologies Used

**Backend:**
- Node.js + Express.js — REST API server
- Socket.IO — real-time bi-directional event streaming
- SQLite (better-sqlite3) — embedded database, zero setup
- bcrypt (12 rounds) — password hashing
- JWT (jsonwebtoken) — stateless authentication with httpOnly cookies
- express-rate-limit — brute force protection

**AI Layer:**
- Python 3.10+ — AI agent, DB tool, log reader
- Ollama — local LLM runtime (runs Llama 3.1, Mistral, Phi-3)
- JSONL — structured event logging format
- Groq API — cloud fallback (free tier)

**Frontend:**
- Vanilla HTML/CSS/JavaScript — no framework, opens in any browser
- D3-style Canvas API — custom interactive fund flow graph renderer
- Socket.IO client — live event reception

### Implementation Flow

```
Client Action
     ↓
Node.js Server (Express)
     ↓
SQLite Database  ←→  logger.js → events.jsonl
     ↓
Rule Engine (fraud.js)
     ↓ (if score > 50)
Fraud Alert Created
     ↓
Socket.IO → Officer Dashboard
     ↓
FraudSense Agent (Python)
  ├─ context_builder.py assembles prompt
  ├─ llm_client.py calls Ollama
  ├─ db_tool.py queries live DB (SELECT only)
  ├─ log_reader.py reads event history
  └─ memory_writer.py saves findings + updates entity profiles
```

---

## 4. FEASIBILITY & VIABILITY

### Feasibility Analysis

**Technical Feasibility:**
- All components use mature, stable open-source libraries
- SQLite handles thousands of transactions per second — sufficient for a bank branch
- Ollama runs on consumer hardware (8GB RAM, no GPU required)
- The entire system runs on a single Windows PC with `node index.js` + `python agent.py`

**Operational Feasibility:**
- No external API dependencies for core banking functions
- Officer workflow mirrors existing bank investigation processes
- FIU report generation matches actual STR filing requirements under PMLA 2002

### Potential Challenges and Risks

| Challenge | Risk Level | Mitigation |
|-----------|-----------|------------|
| LLM hallucination (citing non-existent transactions) | Medium | Agent constrained to cite only data retrieved via db_tool.py |
| Scale (>10,000 accounts) | Medium | SQLite can be replaced with PostgreSQL; graph rendering is already canvas-based |
| Ollama CPU speed (30-60s per analysis) | Low-Medium | Groq free API provides instant responses; Ollama only needed for air-gapped environments |
| Context window overflow as memory grows | Medium | Relevance filtering in memory_reader.py prevents full memory dump into every prompt |
| False positives freezing legitimate accounts | High | Officer confirmation required before any freeze; AI is advisory only |

### Strategies for Overcoming Challenges
- Two-person rule: AI recommends, officer confirms — no automated account actions
- Confidence scores and open_questions fields in every AI report make uncertainty explicit
- Episodic memory with officer outcome feedback enables continuous improvement

---

## 5. IMPACT & BENEFITS

### Potential Impact on Target Audience

**Bank Investigators (Officers):**
- Reduces time to investigate a suspicious case from hours to minutes
- Provides evidence packages ready for FIU-IND filing
- Live graph visualization makes fund flow patterns immediately visible

**Bank Customers:**
- Faster fraud detection protects legitimate customers from being unknowingly complicit in money laundering networks
- Transparent freeze notifications with clear next steps

**Regulators (FIU-IND / RBI):**
- Higher quality STRs with AI-generated evidence summaries
- Consistent pattern classification aligned with PMLA 2002 definitions
- Audit trail of every AI analysis for regulatory review

### Benefits

**Social:**
- Reduces money laundering that funds criminal activity
- Protects vulnerable account holders from being used as mules

**Economic:**
- Reduces compliance cost (fewer manual investigations needed)
- Reduces risk of regulatory penalties for missed STR filings
- Fraud losses prevented directly benefit the bank

**Environmental:**
- Local AI (Ollama) vs cloud AI reduces data center energy consumption for routine analysis

---

## 6. BUSINESS MODEL

### Business Model Overview

**Value Proposition:** FundTrace AI provides mid-sized Indian banks and NBFCs with enterprise-grade AML detection at a fraction of the cost of commercial solutions like NICE Actimize or SAS AML, with the added advantage of running on-premise (no data sovereignty concerns).

**Revenue Streams:**
1. **SaaS Licensing:** ₹5–15 lakh/year per bank branch — subscription model
2. **Implementation Services:** One-time setup, data migration, staff training
3. **Custom AI Fine-tuning:** Train the model on the specific bank's historical fraud patterns
4. **Regulatory Reporting Add-on:** Auto-generated STR XML for direct FIU-IND portal submission

**Target Customers:**
- Urban Cooperative Banks (UCBs) — 1,500+ in India, underserved by expensive commercial AML tools
- Small Finance Banks — regulatory pressure, limited compliance budgets
- NBFCs with payment operations — growing RBI scrutiny

**Customer Acquisition:**
- Partner with NABARD and RBI-affiliated banking training institutes
- Direct outreach to compliance officers at Tier-2/3 banks

### Commercialization Potential and Scalability

**Market Size:**
- India has 1,500+ UCBs + 12 Small Finance Banks + 9,500+ NBFCs
- Combined AML software market in India: ₹2,000+ crore, growing at 18% CAGR
- Addressable segment (Tier-2/3 institutions): ₹400 crore

**Scalability Path:**
1. **Phase 1 (Current):** Single-branch SQLite deployment — proof of concept
2. **Phase 2:** PostgreSQL backend + multi-branch consolidation dashboard
3. **Phase 3:** Graph Neural Network replacing rule-based engine (using accumulated labeled data)
4. **Phase 4:** Cloud SaaS with bank-specific model fine-tuning and FIU-IND API integration

**Key Partnerships:**
- Ollama / open-source LLM community — compute independence
- FIU-IND for STR XML format compliance
- CERT-In for security certification

---

## 7. REFERENCES AND RESEARCH

### Regulatory References
- Prevention of Money Laundering Act (PMLA), 2002 — Government of India
- RBI Master Direction on Know Your Customer (KYC), 2016 (updated 2023)
- FIU-IND Suspicious Transaction Report (STR) Guidelines, 2023
- FATF Recommendations on Anti-Money Laundering (2023 edition)

### Technical References
- ReAct: Synergizing Reasoning and Acting in Language Models — Yao et al., 2022 (arXiv:2210.03629)
- Graph Neural Networks for Fraud Detection in Financial Transactions — IEEE, 2022
- Isolation Forest for Anomaly Detection — Liu et al., 2008
- Ollama Documentation — https://ollama.com/docs
- better-sqlite3 — https://github.com/WiseLibs/better-sqlite3
- Socket.IO Documentation — https://socket.io/docs

### One-Page Summary

FundTrace AI is a locally-runnable banking fraud detection system combining a full-stack client/officer web application with an agentic AI investigator. Built with Node.js, SQLite, Python, and local LLMs via Ollama, it requires no cloud subscriptions or API keys. The system detects six categories of financial crime patterns (circular transactions, layering, structuring, dormant account activation, profile mismatches, and velocity spikes) using both rule-based and AI-powered analysis.

The AI agent (FraudSense) uses a ReAct reasoning loop — querying the live database, reading structured event logs, and iterating through evidence — to produce human-readable risk assessments with cited transaction IDs, confidence scores, and recommended officer actions. Its episodic memory system accumulates case outcomes over time, naturally producing labeled training data for future ML model development. The system is designed to operate as an advisory tool, with human officers making all final decisions on account freezes and FIU filings.

The solution targets India's 1,500+ Urban Cooperative Banks and Small Finance Banks that face growing AML compliance requirements but cannot afford commercial solutions costing ₹50+ lakh per year. FundTrace AI provides comparable capability at a fraction of the cost, with the additional advantage of on-premise deployment ensuring complete data sovereignty.

---

*Document version: 1.0 | Generated by FundTrace AI system*
