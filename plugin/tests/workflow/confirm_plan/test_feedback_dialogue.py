import json

from task_planner.workflow.confirm_plan.extract_knowledge.feedback_dialogue import feedback_dialogue


def _write(path, rows):
    path.write_text("\n".join(json.dumps(row, ensure_ascii=False) for row in rows), encoding="utf-8")


def _user(at, text):
    return {"type": "user", "timestamp": at, "message": {"content": text}}


def _command(at, args):
    return _user(at, f"<command-name>/task-planner:plan-go</command-name>\n<command-args>{args}</command-args>")


def test_should_cut_from_shown_time_to_last_confirm_command(tmp_path):
    path = tmp_path / "t.jsonl"
    _write(path, [
        _user("2026-11-19T09:00:00.000Z", "보여 주기 전"),
        _user("2026-11-19T10:00:00.000Z", "첫 피드백"),
        _command("2026-11-19T10:05:00.000Z", "7"),
        _user("2026-11-19T10:06:00.000Z", "다시 피드백"),
        _command("2026-11-19T10:10:00.000Z", "7"),
        _user("2026-11-19T10:11:00.000Z", "명령 뒤의 말"),
    ])  # fmt: skip
    texts = [utterance.text for utterance in feedback_dialogue(path, "2026-11-19T10:00:00Z")]
    assert texts == ["첫 피드백", "/task-planner:plan-go 7", "다시 피드백"]


def test_should_read_to_end_when_command_was_in_another_session(tmp_path):
    path = tmp_path / "t.jsonl"
    _write(path, [_user("2026-11-19T10:00:00.000Z", "피드백"), _user("2026-11-19T10:01:00.000Z", "또 피드백")])
    assert [u.text for u in feedback_dialogue(path, "2026-11-19T10:00:00Z")] == ["피드백", "또 피드백"]
