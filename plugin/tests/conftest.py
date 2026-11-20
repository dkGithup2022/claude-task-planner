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


@pytest.fixture(autouse=True)
def no_real_claude(monkeypatch):
    """시험이 실제 claude 를 부르지 않게 한다. 가짜 claude 가 필요한 시험은 이 값을 다시 정한다."""
    monkeypatch.setenv("TASK_PLAN_MANAGER_CLAUDE_BIN", "false")


@pytest.fixture(autouse=True)
def outside_claude_code(monkeypatch):
    """시험은 Claude Code 밖에서 도는 것으로 본다. 진행 기록을 남기지 않아 저장소 폴더에 .plan/ 이 생기지 않는다.
    진행 기록을 확인하는 시험은 CLAUDE_CODE_SESSION_ID 를 다시 정한다."""
    monkeypatch.delenv("CLAUDE_CODE_SESSION_ID", raising=False)
