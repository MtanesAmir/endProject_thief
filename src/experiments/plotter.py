"""Experiment Plotter module for visual analysis artifacts."""

import os
from typing import Any, Dict, List

import matplotlib
matplotlib.use("Agg")  # Non-interactive headless backend for CI/tests
import matplotlib.pyplot as plt


class ExperimentPlotter:
    """Plotting engine generating analysis chart artifacts for notebooks and reports."""

    def __init__(self, output_dir: str = "assets"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def plot_scent_decay(self, decay_rate: float = 0.10, turns: int = 20) -> str:
        """Generate and save scent intensity decay curve plot."""
        intensity = 0.9
        values = [intensity]
        for _ in range(1, turns):
            intensity = max(0.0, (1 - decay_rate) * intensity)
            values.append(intensity)

        plt.figure(figsize=(6, 4))
        plt.plot(range(1, turns + 1), values, marker="o", color="purple")
        plt.title(f"Scent Intensity Decay Over Turns (rho = {decay_rate})")
        plt.xlabel("Turn")
        plt.ylabel("Intensity (tau)")
        plt.grid(True)

        filepath = os.path.join(self.output_dir, "scent_decay_plot.png")
        plt.savefig(filepath, dpi=100)
        plt.close()
        return filepath

    def plot_strategy_winrates(self, cop_wins: int = 3, thief_wins: int = 7) -> str:
        """Generate and save Cop vs Thief win-rate bar chart."""
        plt.figure(figsize=(5, 4))
        categories = ["Cop Wins", "Thief Wins"]
        counts = [cop_wins, thief_wins]
        colors = ["blue", "orange"]

        plt.bar(categories, counts, color=colors)
        plt.title("Thief Evasion Simulation Outcomes")
        plt.ylabel("Match Count")

        filepath = os.path.join(self.output_dir, "strategy_winrates.png")
        plt.savefig(filepath, dpi=100)
        plt.close()
        return filepath


def summarize_benchmark(results: Dict[str, Any]) -> str:
    return f"Total Rounds: {results.get('rounds', 0)}, Thief Win Rate: {results.get('thief_win_rate', 0.0):.1%}"
