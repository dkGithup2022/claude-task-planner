import pytest

from task_plan_manager.common.http.api_choice import api_url, uses_server


def test_should_use_mock_unless_server_is_set(monkeypatch):
    monkeypatch.delenv("TASK_PLAN_MANAGER_API", raising=False)
    assert not uses_server()
    monkeypatch.setenv("TASK_PLAN_MANAGER_API", "server")
    assert uses_server()


def test_should_need_api_url_for_server(monkeypatch):
    monkeypatch.delenv("TASK_PLAN_MANAGER_API_URL", raising=False)
    with pytest.raises(ValueError):
        api_url("/plans")
    monkeypatch.setenv("TASK_PLAN_MANAGER_API_URL", "http://localhost:8000/")
    assert api_url("/plans") == "http://localhost:8000/plans"
