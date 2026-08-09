import pytest
from src.domain.scent import ScentTracker

def test_scent_emission_and_decay():
    st = ScentTracker(7)
    st.apply_emission((3, 3), tau_center=0.9)
    assert st.get_scent_level((3, 3)) == pytest.approx(0.9)
    st.apply_decay(rho=0.1)
    assert st.get_scent_level((3, 3)) == pytest.approx(0.81)
    st.reset()
    assert st.get_scent_level((3, 3)) == 0.0
