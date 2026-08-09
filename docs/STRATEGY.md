# Thief Evasion Strategy & Mathematical Framework

## 1. Executive Summary
The Thief Agent implements an evasive strategy over a partially observable $7\times 7$ grid. By leveraging stigmergic scent trail inversion and Bayesian belief tracking, the Thief estimates the Police location and calculates optimal orthogonal evasion paths.

## 2. Bayesian Belief Updating
Given the Cop's scent emission field $\tau_{cop}$ and reported verbal hint $h_t$, the Thief updates posterior probability $b_t(s) = P(S_{cop} = s \mid \Omega_t)$:

$$b_{t+1}(s) \propto P(\Omega_{t+1} \mid s) \sum_{s'} P(s \mid s', a_{cop}) b_t(s')$$

## 3. Distance Maximization & Barrier Avoidance
The Thief calculates candidate legal moves $\mathcal{M}(pos_{thief})$ avoiding placed barriers:
$$a^* = \arg\max_{a \in \mathcal{M}} D_{Manhattan}(pos_{thief} + a, \hat{pos}_{cop})$$

where $\hat{pos}_{cop} = \arg\max_s b_t(s)$.

## 4. Verbal Deception (Bluff Generation)
To distort the Cop's belief filter, the Thief issues deceptive orthogonal declarations $h_{thief} \neq a^*$, inducing intentional entropy in the Cop's pursuit trajectory.
