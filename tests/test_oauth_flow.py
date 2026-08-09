import pytest
from src.automation.oauth_flow import OAuthSetupManager, check_oauth_credentials

def test_oauth_flow(tmp_path):
    cred_file = tmp_path / "credentials.json"
    tok_file = tmp_path / "token.json"

    mgr1 = OAuthSetupManager(str(cred_file), str(tok_file))
    assert mgr1.is_authenticated() is False
    st1 = mgr1.get_auth_status()
    assert st1["mode"] == "MOCK_FALLBACK"
    assert mgr1.run_oauth_flow()["status"] == "MOCK_MODE"

    cred_file.write_text("{}")
    mgr2 = OAuthSetupManager(str(cred_file), str(tok_file))
    st2 = mgr2.get_auth_status()
    assert st2["mode"] == "OAUTH2_PENDING"
    assert mgr2.run_oauth_flow()["status"] == "PENDING_BROWSER_AUTH"

    tok_file.write_text("{}")
    mgr3 = OAuthSetupManager(str(cred_file), str(tok_file))
    assert mgr3.is_authenticated() is True
    st3 = mgr3.get_auth_status()
    assert st3["mode"] == "OAUTH2_ACTIVE"
    assert mgr3.run_oauth_flow()["status"] == "SUCCESS"

    assert check_oauth_credentials(str(tok_file)) is True
