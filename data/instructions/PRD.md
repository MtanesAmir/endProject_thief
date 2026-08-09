# Product Requirements Document (PRD)
## Distributed Cops-and-Robbers over a Peer-to-Peer Network (Dec-POMDP)

### 1. Overview & System Goal
This project implements an autonomous, decentralized multi-agent system executing a Cops-and-Robbers game on a discrete 7x7 grid over a Peer-to-Peer (P2P) network using the Model Context Protocol (MCP / FastMCP).

The Police agent (Cop) and Robber agent (Thief) operate without a central server or neutral judge. State integrity, turn synchronization, and zero-trust verification are enforced cryptographically via a 4-stage SHA-256 Commit-Reveal protocol.

### 2. Core Objectives
- **Decentralized P2P Architecture**: Run Cop and Thief agents as symmetric FastMCP peers communicating over HTTP/JSON-RPC without a central game server.
- **Cryptographic Fairness**: Non-repudiable move commitment ($H_{commit} = \text{SHA256}(\text{CanonicalJSON}(State, Move, Intent, Nonce))$) ensuring zero cheating.
- **Strategic Intelligence**: Combine distance heuristics (Manhattan), dynamic scent trail decay ($\tau_{ij}(t+1) = \max(0, (1-\rho)\tau_{ij}(t) + \Delta\tau_{ij})$), and Bayesian belief maps ($P(\text{Thief} = s | \text{hints})$).
- **Verifiable Auditability**: Generate signed JSON match report artifacts (`declaration_*.json`, `config_*.json`, `log_*.json`, `result_*.json`) and support replay log integrity verification.

### 3. Functional Requirements
- **FR-01 (Shared Contract)**: Enforce immutable game configuration via `config/game.json` (7x7 grid, 35-step max, 14 max barriers).
- **FR-02 (P2P FastMCP Server)**: Run local FastMCP instance `police_thief_peer` exposing tool handlers for move reception and commitment exchange.
- **FR-03 (Commit-Reveal Protocol)**: 4-stage turn sequence: 1. Commit -> 2. Acknowledge -> 3. Reveal -> 4. Audit.
- **FR-04 (Dual Brain Strategies)**: Provide independent `PoliceBrain` (pursuit) and `ThiefBrain` (evasion & deception).
- **FR-05 (Observability & Heatmap)**: Render live heatmaps (cop local observation $\Omega_i$) and turn state banners ("YOUR TURN" / "LOCKED").
- **FR-06 (Automated Gmail Reporting)**: Transmit signed match JSON summaries to instructor/evaluator via OAuth 2.0 Gmail API.

### 4. Non-Functional Requirements (NFRs)
- **Zero-Trust Separation**: Absolute separation of Cop and Thief state space (`config/police/` vs `config/thief/`).
- **Latency & Performance**: Move decisions calculated in < 50ms per step.
- **Code Coverage**: $\ge 85\%$ test coverage verified via `pytest-cov`.
