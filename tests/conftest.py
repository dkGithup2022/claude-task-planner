import pytest


@pytest.fixture(autouse=True)
def package_home(tmp_path, monkeypatch):
    """모든 시험은 임시 폴더를 실행 데이터 폴더로 쓴다."""
    home = tmp_path / ".task_plan_manager"
    monkeypatch.setenv("TASK_PLAN_MANAGER_HOME", str(home))
    return home


@pytest.fixture(autouse=True)
def mock_data_dir(tmp_path, monkeypatch):
    """모든 시험은 임시 폴더를 mock 계획 저장소로 쓴다. 저장소의 .mockData/ 를 건드리지 않는다."""
    d = tmp_path / ".mockData"
    monkeypatch.setenv("TASK_PLAN_MANAGER_MOCK_DIR", str(d))
    return d
