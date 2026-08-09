# Distributed Cops-and-Robbers over a Peer-to-Peer Network (Dec-POMDP) - Thief Peer

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Code style: Ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)
[![Test Coverage: 85%+](https://img.shields.io/badge/coverage-85%25%2B-green.svg)](https://pytest-cov.readthedocs.io/)

Academic multi-agent system executing the **Thief (Robber)** agent in a decentralized, peer-to-peer Cops-and-Robbers pursuit-evasion game over FastMCP.

---

## 1. Mathematical Formalism (Dec-POMDP)
The system is modeled as an 8-tuple Dec-POMDP:
$$\langle n, S, \{A_i\}, P, R, \{\Omega_i\}, O, \gamma \rangle$$
- **$n=2$ Agents**: Police ($i=1$) and Thief ($i=2$).
- **State Space $S$**: Discrete $7\times 7$ grid, agent positions $(r_{cop}, c_{cop})$ and $(r_{thief}, c_{thief})$, active barriers (max 14), and scent field matrix $\tau_{ij}(t)$.
- **Action Space $A_i$**: Orthogonal moves $\{\text{N, S, E, W, STAY}\}$.
- **Transition Function $P(s' | s, a_1, a_2)$**: Deterministic move updates and scent emission/decay.
- **Reward Function $R$**: Asymmetric scoring matrix for capture vs survival.
- **Observation Space $\Omega_i$**: Local observation containing scent traces and verbal hints without direct opponent position access.
- **Observation Function $O$**: Scent kernel $\tau_{center} = 0.90$, decay $\rho = 0.10$.
- **Discount Factor $\gamma$**: Discount factor for temporal planning.

---

## 2. P2P FastMCP & Zero-Trust Synchronization
- Symmetric FastMCP peers communicate over JSON-RPC / HTTP.
- 4-Stage SHA-256 Commit-Reveal protocol prevents cheating and front-running:
  1. **Commit**: $H_{commit} = \text{SHA256}(\text{CanonicalJSON}(State, Move, Intent, Nonce))$
  2. **Acknowledge**: Peer locks commitment before reveal.
  3. **Reveal**: State, Move, and Intent revealed (Nonce withheld).
  4. **Audit**: Nonces revealed post-match for mutual cryptographic verification.

---

## 3. Thief Strategic Intelligence & Evasion
- **Bayesian Belief Map**: Updates probability distribution of Cop position given observed scent trails and verbal declarations.
- **Manhattan Distance Maximization**: Heuristic pathfinding maximizing distance from estimated Cop location while navigating around dynamic barriers.
- **Bluff Generation**: Generates deceptive verbal direction cues to induce false belief priors in the opponent.
- **Resilience**: Integrated Token Bucket Rate Limiter, DOS Detector, and Watchdog deadline tracker.

---

## 4. Quick Start & Execution

### Installation
```bash
uv sync
```

### Running Thief Peer
```bash
uv run python -m src.cli peer --role thief --port 8802
```

### Running Local Simulation Match
```bash
uv run python -m src.cli match --rounds 1
```

### Verifying Match Replay
```bash
uv run python -m src.cli replay --log logs/match_sample.json
```

### Running Test Suite & Coverage
```bash
uv run pytest --cov=src --cov-report=term-missing tests/
```

---

## 5. Partner Police Repository
- [Police Peer Repository](https://github.com/amirmt/project_police)
