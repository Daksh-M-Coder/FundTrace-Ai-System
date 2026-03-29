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

## 8. SYSTEM ARCHITECTURE OVERVIEW

### High-Level Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                        FundTrace AI Platform                        │
├─────────────────┬───────────────────────┬───────────────────────────┤
│   CLIENT LAYER  │    SERVER LAYER        │      AI LAYER             │
│                 │                        │                           │
│ ┌─────────────┐ │ ┌────────────────────┐ │ ┌─────────────────────┐  │
│ │ Client App  │ │ │  Node.js + Express │ │ │   FraudSense Agent  │  │
│ │ (HTML/JS)   │ │ │                    │ │ │                     │  │
│ │ ┌─────────┐ │ │ │  ┌──────────────┐ │ │ │ ┌─────────────────┐ │  │
│ │ │ Banking │ │ │ │  │  REST API    │ │ │ │ │ context_builder │ │  │
│ │ │   UI    │ │ │ │  │  Routes      │ │ │ │ │ llm_client      │ │  │
│ │ └─────────┘ │ │ │  └──────────────┘ │ │ │ │ db_tool         │ │  │
│ │             │ │ │  ┌──────────────┐ │ │ │ │ log_reader      │ │  │
│ │ ┌─────────┐ │ │ │  │  fraud.js    │ │ │ │ │ memory_writer   │ │  │
│ │ │ Graph   │ │ │ │  │  Rule Engine │ │ │ │ └─────────────────┘ │  │
│ │ │Renderer │ │ │ │  └──────────────┘ │ │ │                     │  │
│ │ └─────────┘ │ │ │  ┌──────────────┐ │ │ │ ┌─────────────────┐ │  │
│ └─────────────┘ │ │  │  Socket.IO   │ │ │ │ │  Episodic       │ │  │
│                 │ │  │  Real-time   │ │ │ │ │  Memory Store   │ │  │
│ ┌─────────────┐ │ │  └──────────────┘ │ │ │ └─────────────────┘ │  │
│ │ Officer     │ │ │  ┌──────────────┐ │ │ │                     │  │
│ │ Dashboard   │ │ │  │  SQLite DB   │ │ │ │ ┌─────────────────┐ │  │
│ │             │ │ │  │  (banking    │ │ │ │ │   Ollama LLM    │ │  │
│ │ ┌─────────┐ │ │ │  │   data)      │ │ │ │ │  (Local / Free) │ │  │
│ │ │FraudSense│ │ │ │  └──────────────┘ │ │ │ └─────────────────┘ │  │
│ │ │AI Panel │ │ │ │  ┌──────────────┐ │ │ └─────────────────────┘  │
│ │ └─────────┘ │ │ │  │  logger.js   │ │ │                           │
│ └─────────────┘ │ │  │  events.jsonl│ │ │                           │
│                 │ │  └──────────────┘ │ │                           │
└─────────────────┴───────────────────┴───────────────────────────────┘
```

### Data Flow Summary

| Step | From | To | Purpose |
|------|------|----|---------|
| 1 | Client App | Express Server | Banking transaction request |
| 2 | Express Server | SQLite DB | Persist transaction & account state |
| 3 | Express Server | fraud.js | Rule-based fraud scoring |
| 4 | fraud.js | SQLite DB | Fraud alert creation (score > 50) |
| 5 | Express Server | Socket.IO | Real-time event broadcast |
| 6 | Socket.IO | Officer Dashboard | Live alert notification |
| 7 | Officer Dashboard | FraudSense Agent | AI investigation trigger |
| 8 | FraudSense Agent | SQLite DB (read-only) | Live evidence gathering |
| 9 | FraudSense Agent | events.jsonl | Event history reading |
| 10 | FraudSense Agent | Ollama / Groq | LLM reasoning over evidence |
| 11 | FraudSense Agent | Memory Store | Case findings saved |
| 12 | FraudSense Agent | Officer Dashboard | Risk assessment report delivered |

---

## 9. FRAUD DETECTION PATTERNS

### Six Financial Crime Categories Detected

| Pattern | Description | Detection Method |
|---------|-------------|-----------------|
| **Circular Transactions** | Funds leave Account A, pass through B, C, D and return to A — classic money laundering loop | Graph cycle detection (DFS) across transaction graph |
| **Layering** | Multiple rapid hops across accounts to obscure source of funds | Multi-hop path analysis, transaction velocity scoring |
| **Structuring (Smurfing)** | Splitting large amounts into sub-threshold amounts to avoid detection | Aggregation analysis: sum of account's daily transactions vs. threshold |
| **Dormant Account Reactivation** | Inactive account (>90 days) suddenly receives or sends large transactions | Timestamp delta analysis on account's last activity |
| **Profile Mismatch** | Transaction pattern inconsistent with account's declared income/occupation | Statistical deviation from account's baseline behavioral profile |
| **Velocity Spikes** | Unusually high number of transactions within a short time window | Rolling time-window counter with configurable thresholds |

### Rule Engine Scoring Model

```
Fraud Score = Σ(pattern_weight × confidence_factor)

Base Weights:
  Circular Flow:        +40 points
  Layering:             +30 points  
  Structuring:          +25 points
  Dormant Reactivation: +20 points
  Profile Mismatch:     +20 points
  Velocity Spike:       +15 points

Alert Threshold: Score > 50 → Auto-alert to Officer Dashboard
Investigation Threshold: Score > 75 → FraudSense AI automatically triggered
```

---

## 10. AGENTIC AI — FRAUDSENSE DEEP DIVE

### ReAct Loop Architecture

```
Officer triggers investigation → FraudSense Agent starts
        │
        ▼
[THINK] Analyze available context:
        - Account info, transaction history summary
        - Known fraud patterns in this account's cluster
        - Past similar cases from episodic memory
        │
        ▼
[ACT] Select tool and execute:
        ├── db_tool.py → SELECT query on live SQLite
        ├── log_reader.py → Read recent events.jsonl entries
        └── memory_reader.py → Retrieve similar past cases
        │
        ▼
[OBSERVE] Process tool output:
        - Parse JSON/text result from tool
        - Identify new evidence or gaps
        │
        ▼
[REFLECT] Is the evidence sufficient?
        ├── YES → Generate final risk assessment report
        └── NO  → Loop back to THINK (max 8 iterations)
        │
        ▼
[REPORT] Structured output:
        ├── Risk Level: HIGH / MEDIUM / LOW / CLEAR
        ├── Confidence Score: 0–100%
        ├── Evidence Summary (with cited transaction IDs)
        ├── Pattern Classifications
        ├── Recommended Officer Actions
        └── Open Questions (uncertainties)
        │
        ▼
[MEMORY] Save findings:
        memory_writer.py → episodic_memory.json
        entity_profiles.json → updated account behavioral baseline
```

### FraudSense Capabilities

| Capability | Description |
|------------|-------------|
| Live DB Querying | Reads real-time account, transaction, and alert data (SELECT-only, read-safe) |
| Event Log Reading | Parses structured JSONL event history for temporal patterns |
| Case Memory Recall | Retrieves semantically similar past investigation outcomes |
| Multi-iteration Reasoning | Runs up to 8 Reason-Act-Observe cycles per investigation |
| Confidence Scoring | Outputs 0–100% confidence with explicit uncertainty disclosure |
| Evidence Citation | All claims anchored to specific transaction IDs or log entries |
| Human-readable Reports | Narrative summaries suitable for FIU-IND filing |
| Outcome Learning | Officer decisions fed back as labeled data for continuous improvement |

---

## 11. MULTI-LAYER MEMORY SYSTEM

### Memory Architecture

```
FraudSense Memory Stack
├── Episodic Memory (episodic_memory.json)
│   ├── Case ID, timestamp, account IDs involved
│   ├── Patterns detected, risk level assigned
│   ├── Officer final decision (confirmed/cleared)
│   └── Used for: Similarity search for new investigations
│
├── Entity Profiles (entity_profiles.json)  
│   ├── Per-account behavioral baseline
│   ├── Typical transaction amounts, times, counterparties
│   ├── Profile deviation score
│   └── Used for: Profile mismatch detection calibration
│
└── Skills Cache (skills/)
    ├── Known fraud technique descriptions
    ├── Regulatory definition references (PMLA, FATF)
    └── Used for: Enriching agent reasoning context
```

### Memory-Driven Learning Loop

```
Investigation → Report → Officer Decision → Memory Write
      ↑                                          │
      └──────── Similar Case Retrieval ←─────────┘
                (next new investigation)
```

This creates a **self-improving feedback loop**: each confirmed fraud case makes the next investigation smarter, reducing false positives over time.

---

## 12. COMPLIANCE & REGULATORY ALIGNMENT

### Regulatory Framework Coverage

| Regulation | Requirement | FundTrace AI Implementation |
|------------|-------------|----------------------------|
| PMLA 2002 | Suspicious Transaction Reporting | Auto-generated STR summaries with evidence |
| PMLA 2002 | Record maintenance for 5 years | Immutable JSONL event log + SQLite archive |
| RBI KYC 2023 | Customer due diligence | Profile mismatch detection flags KYC gaps |
| FATF Rec. 20 | Real-time transaction monitoring | Socket.IO live event streaming |
| FATF Rec. 16 | Wire transfer monitoring | Fund flow graph tracks multi-hop paths |
| FIU-IND STR Guidelines | STR filing format | Report structure aligned to FIU-IND schema |

### Audit Trail Design
- Every transaction is logged to `events.jsonl` with timestamp, actor, and outcome
- Every AI investigation generates a timestamped, versioned report saved to `memory/`
- Officer decisions (confirm/clear) are logged with officer ID and timestamp
- No events are ever deleted — append-only log architecture

---

## 13. COMPETITIVE POSITIONING

### Market Comparison

| Feature | FundTrace AI | NICE Actimize | SAS AML | Oracle FCCM |
|---------|-------------|---------------|---------|-------------|
| Cost (per branch/yr) | ₹5–15 lakh | ₹50–200 lakh | ₹75–300 lakh | ₹100–400 lakh |
| On-premise deployment | ✅ | ✅ | ✅ | ✅ |
| No cloud dependency | ✅ | ❌ | ❌ | ❌ |
| Agentic AI investigator | ✅ | ❌ | ❌ | ❌ |
| Graph visualization | ✅ | ✅ | Partial | ✅ |
| Setup complexity | Single command | Months | Months | Months |
| SMB/UCB accessible | ✅ | ❌ | ❌ | ❌ |
| Open-source core | ✅ | ❌ | ❌ | ❌ |

### Key Differentiators
1. **Agentic AI** — competitors use rules or static ML; FundTrace reasons dynamically
2. **Zero-cost local deployment** — Ollama + SQLite, no vendor lock-in
3. **SMB-first** — designed specifically for India's underserved cooperative banking sector
4. **Explain-ability** — every AI conclusion cites specific evidence (no black box)

---

## 14. TEAM & PROJECT CONTEXT

### Project Origin
- Developed as part of a technology competition/hackathon submission
- Demonstrates full-stack development, AI integration, banking domain knowledge, and regulatory awareness

### Skills Demonstrated
- **Full-Stack Web Development**: Node.js, Express, HTML/CSS/JS, Socket.IO
- **AI/ML Engineering**: ReAct agents, LLM integration, episodic memory, tool-use LLMs
- **Graph Analytics**: Fund flow graph modeling, cycle detection, multi-hop path analysis
- **Security Engineering**: JWT auth, bcrypt hashing, rate limiting, SQL injection prevention
- **Domain Expertise**: PMLA 2002, RBI guidelines, FIU-IND STR format, FATF standards
- **System Design**: Modular architecture, event-driven design, scalability path planning

### Technology Stack Summary

| Layer | Technology | Version | Purpose |
|-------|------------|---------|---------|
| Runtime | Node.js | 18+ | API server |
| Framework | Express.js | 4.x | REST routing |
| Database | SQLite (better-sqlite3) | 3.x | Data persistence |
| Real-time | Socket.IO | 4.x | Live events |
| Auth | JWT + bcrypt | — | Secure sessions |
| AI Runtime | Python | 3.10+ | Agent execution |
| LLM (local) | Ollama | Latest | Privacy-first AI |
| LLM (cloud) | Groq API | Free tier | Fast fallback |
| Frontend | Vanilla HTML/CSS/JS | ES2022 | Zero-dependency UI |
| Graph Render | Canvas API | Native | Fund flow visualization |

---

## 15. PRESENTATION SHOWCASE

### Landing Page Web Application

A dedicated interactive showcase landing page has been built at `landing_pgae_web/index.html` to support the team presentation. It provides:

- **Hero Section**: Full-viewport animated introduction to FundTrace AI
- **Problem Statement**: The crisis of financial fraud in India with live statistical counters
- **Solution Overview**: How FundTrace AI addresses the problem — three-layer approach
- **Technology Stack**: Visual tech stack tour with animated cards
- **System Workflow**: Step-by-step animated flow diagram showing data pipeline
- **Fraud Patterns**: Interactive cards for all six detection categories
- **FraudSense AI**: Deep dive into the ReAct agentic loop with animated diagram
- **Impact & Benefits**: Visualized impact metrics for officers, customers, and regulators
- **Business Model**: Revenue streams, market sizing, scalability path
- **Compliance**: Regulatory alignment matrix
- **Competitive Advantage**: Feature comparison table vs. commercial solutions
- **Call to Action**: Next steps and team credits

### Presentation Strategy

```
PPT Slides → Overview & Headlines (condensed)
Landing Page → Deep dive, live demo, animated explanations
Live Demo → Officer dashboard + client app walkthrough
```

The landing page serves as the extended "digital brochure" that the PPT cannot cover due to slide count limitations — allowing evaluators to explore the full system depth at their own pace.

---

*Document version: 2.0 | Updated with Sections 8–15 | FundTrace AI system*
