import json

import pytest

from task_planner.port.local.claude_settings.default_claude_settings_reader import DefaultClaudeSettingsReader
from task_planner.port.local.claude_settings.default_claude_settings_writer import DefaultClaudeSettingsWriter
from task_planner.port.local.claude_settings.dto.statusline_setup import StatuslineSetup

COMMAND = "/plugin/bin/task-planner statusline"


@pytest.fixture(autouse=True)
def work_dir(tmp_path, monkeypatch):
    """작업 폴더 설정은 CLI 를 부른 폴더의 .claude/ 아래, 사용자 설정은 CLAUDE_CONFIG_DIR 아래."""
    (tmp_path / "work").mkdir()
    monkeypatch.chdir(tmp_path / "work")
    monkeypatch.setenv("CLAUDE_CONFIG_DIR", str(tmp_path / "user"))
    return tmp_path / "work"


def local_settings(work_dir):
    return json.loads((work_dir / ".claude" / "settings.local.json").read_text(encoding="utf-8"))


def test_should_create_local_settings_with_statusline(work_dir):
    assert DefaultClaudeSettingsWriter().ensure_statusline(COMMAND, 5) is StatuslineSetup.WRITTEN
    assert local_settings(work_dir) == {"statusLine": {"type": "command", "command": COMMAND, "refreshInterval": 5}}


def test_should_keep_other_keys_and_do_nothing_the_second_time(work_dir):
    (work_dir / ".claude").mkdir()
    (work_dir / ".claude" / "settings.local.json").write_text('{"permissions": {"allow": ["Bash"]}}', encoding="utf-8")
    writer = DefaultClaudeSettingsWriter()
    assert writer.ensure_statusline(COMMAND, 5) is StatuslineSetup.WRITTEN
    assert writer.ensure_statusline(COMMAND, 5) is StatuslineSetup.ALREADY
    assert local_settings(work_dir)["permissions"] == {"allow": ["Bash"]}


@pytest.mark.parametrize("content", ['{"statusLine": {"type": "command", "command": "my-line"}}', "not json"])
def test_should_leave_user_statusline_or_broken_file_alone(work_dir, content):
    (work_dir / ".claude").mkdir()
    path = work_dir / ".claude" / "settings.local.json"
    path.write_text(content, encoding="utf-8")
    assert DefaultClaudeSettingsWriter().ensure_statusline(COMMAND, 5) is StatuslineSetup.LEFT_ALONE
    assert path.read_text(encoding="utf-8") == content


def test_should_replace_our_old_statusline_after_plugin_update(work_dir):
    old = "/plugins/cache/m/task-planner/0.1.0/bin/task-planner statusline"
    new = "/plugins/cache/m/task-planner/0.2.0/bin/task-planner statusline"
    writer = DefaultClaudeSettingsWriter()
    writer.ensure_statusline(old, 5)

    assert writer.ensure_statusline(new, 5) is StatuslineSetup.WRITTEN
    assert local_settings(work_dir)["statusLine"]["command"] == new


def test_should_leave_alone_when_settings_cannot_be_written(work_dir):
    (work_dir / ".claude").write_text("폴더 자리에 파일이 있음", encoding="utf-8")
    assert DefaultClaudeSettingsWriter().ensure_statusline(COMMAND, 5) is StatuslineSetup.LEFT_ALONE


def test_should_read_user_statusline_command(tmp_path):
    reader = DefaultClaudeSettingsReader()
    assert reader.user_statusline_command() is None
    (tmp_path / "user").mkdir()
    (tmp_path / "user" / "settings.json").write_text('{"statusLine": {"command": "orca-line"}}', encoding="utf-8")
    assert reader.user_statusline_command() == "orca-line"
