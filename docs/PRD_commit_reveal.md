# PRD: Cryptographic Commit-Reveal Protocol (`thief_commit_reveal_crypto`)

## 1. Problem Statement
In a serverless peer-to-peer game between self-interested agents, moves must be committed before either party reveals their choice, preventing front-running and move tampering.

## 2. Objectives
- Compute SHA-256 commitments over canonical JSON payloads: $(State, Move, Intent, Nonce)$.
- Execute 4-stage turn sequence (Commit -> Ack -> Reveal -> Audit).
- Detect any post-facto tampering with $100\%$ mathematical certainty.
