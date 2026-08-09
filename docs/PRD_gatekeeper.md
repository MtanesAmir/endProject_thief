# PRD: Gatekeeper & Rate Limiter (`thief_gatekeeper_rate_limiter`)

## 1. Problem Statement
Prevent unbounded message flooding, DOS attacks, and external API quota exhaustion during competitive P2P execution.

## 2. Objectives
- Token Bucket rate limiting ($r=30$ req/min, capacity $C=100$).
- Transient failure retry with exponential backoff.
- Circuit breaker / DOS detection for runaway loops.
