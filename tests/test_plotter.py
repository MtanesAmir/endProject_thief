import pytest
from src.experiments.plotter import ExperimentPlotter, summarize_benchmark

def test_plotter(tmp_path):
    ep = ExperimentPlotter(str(tmp_path))
    f1 = ep.plot_scent_decay(turns=5)
    f2 = ep.plot_strategy_winrates(cop_wins=2, thief_wins=8)
    assert f1.endswith(".png")
    assert f2.endswith(".png")
    s = summarize_benchmark({"rounds": 10, "thief_win_rate": 0.8})
    assert "80.0%" in s
