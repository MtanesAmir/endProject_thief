import pytest
from src.gui.live_gui import LiveGUIController
from src.gui.heatmap import HeatmapRenderer

def test_live_gui():
    gui = LiveGUIController()
    b = gui.update_turn_banner(True)
    assert b == "YOUR TURN"
    b2 = gui.update_turn_banner(False)
    assert b2 == "LOCKED"

def test_heatmap_renderer():
    hr = HeatmapRenderer(3)
    s = hr.format_matrix_ascii([[0.0, 0.5, 0.0], [0.1, 0.9, 0.1], [0.0, 0.2, 0.0]])
    assert "0.90" in s
