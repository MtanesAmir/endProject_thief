# PRD: Bayesian Belief Modeling (`thief_bayesian_belief`)

## 1. Problem Statement
In a Dec-POMDP setting with partial observability, the Thief cannot directly view the Police agent's coordinates. The Thief must construct and maintain a probabilistic belief distribution $b(s)$ across the $7\times 7$ grid.

## 2. Objectives
- Track Cop probability over 49 grid cells.
- Fuse stigmergic scent intensity and verbal declarations.
- Identify highest likelihood target cell $\hat{s} = \arg\max b(s)$.
