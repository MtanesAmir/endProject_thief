# PRD: Stigmergic Scent Tracking (`thief_scent_tracking`)

## 1. Problem Statement
Provide indirect spatial memory of agent movements via synthetic pheromone trails with radial emission and exponential decay.

## 2. Objectives
- 5x5 radial emission field with center intensity tau = 0.90.
- Per-turn decay model: tau_{ij}(t+1) = max(0, (1-rho)tau_{ij}(t)) with rho = 0.10.
- Fast matrix query interface for Bayesian belief assimilation.
