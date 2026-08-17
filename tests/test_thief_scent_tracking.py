import pytest
from src.domain.scent import ScentTracker

def test_scent_emission_and_decay():
    st = ScentTracker(7)
    # update_scent combines emission + decay in one call
    st.update_scent((3, 3), tau_center=0.9, rho=0.0)
    assert st.get_scent_level((3, 3)) == pytest.approx(0.9, abs=0.01)
    # Apply a second update with decay but no new emission at a different position
    st.update_scent((0, 0), tau_center=0.9, rho=0.1)
    # Center (3,3) should have decayed by 10%
    assert st.get_scent_level((3, 3)) < 0.9
    st.reset()
    assert st.get_scent_level((3, 3)) == 0.0
