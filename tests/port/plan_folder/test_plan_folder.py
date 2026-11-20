import pytest

from task_plan_manager.model.node_run.node_run import NodeRun
from task_plan_manager.model.node_run.read_input import ReadInput
from task_plan_manager.model.plan.plan_node_status import PlanNodeStatus
from task_plan_manager.port.local.plan_folder.default_plan_folder_reader import DefaultPlanFolderReader
from task_plan_manager.port.local.plan_folder.default_plan_folder_writer import DefaultPlanFolderWriter
from task_plan_manager.port.local.plan_folder.plan_folder_exists_error import PlanFolderExistsError
from task_plan_manager.port.local.plan_folder.plan_folder_missing_error import PlanFolderMissingError


@pytest.fixture(autouse=True)
def work_dir(tmp_path, monkeypatch):
    """계획 폴더는 CLI 를 부른 작업 폴더 아래에 생긴다."""
    monkeypatch.chdir(tmp_path)
    return tmp_path


def test_should_create_plan_folder_and_list_its_id(work_dir):
    reader, writer = DefaultPlanFolderReader(), DefaultPlanFolderWriter()
    assert reader.list_plan_ids() == ()
    writer.create_plan(7, "# 명령")
    writer.create_plan(7, "# 명령")  # 같은 내용이면 그대로
    assert reader.list_plan_ids() == (7,)
    assert reader.read_command(7) == "# 명령"
    assert (work_dir / ".plan" / "7" / "command.md").exists()
    with pytest.raises(PlanFolderExistsError):
        writer.create_plan(7, "# 다른 명령")
    with pytest.raises(PlanFolderMissingError):
        reader.read_command(8)


def test_should_read_prompt_output_and_run_of_a_node(work_dir):
    reader, writer = DefaultPlanFolderReader(), DefaultPlanFolderWriter()
    writer.create_plan(7, "# 명령")
    assert reader.read_prompt(7, 11) is None and reader.read_output(7, 11) is None and reader.read_run(7, 11) is None

    writer.write_prompt(7, 11, "작업 지시")
    target = reader.result_target(7, 11)
    target.result_path.write_text("결과", encoding="utf-8")  # 서브에이전트가 쓰는 자리
    target.files_dir.mkdir()
    (target.files_dir / "a.md").write_text("a", encoding="utf-8")
    saved_run = NodeRun(1, PlanNodeStatus.DONE, read_inputs=(ReadInput(10, 1),))
    writer.save_run(7, 11, saved_run)

    assert reader.read_prompt(7, 11) == "작업 지시"
    output = reader.read_output(7, 11)
    assert output is not None and output.round == 1 and output.files == (target.files_dir / "a.md",)
    assert reader.read_run(7, 11) == saved_run


def test_should_save_and_read_failure_of_a_node(work_dir):
    reader, writer = DefaultPlanFolderReader(), DefaultPlanFolderWriter()
    writer.create_plan(7, "# 명령")
    failed = NodeRun(1, PlanNodeStatus.FAILED, failed_reason="막힘", failed_summary="라이브러리 권한 없음")
    writer.save_run(7, 11, failed)
    assert reader.read_run(7, 11) == failed

    # 실패 이유를 남기기 전의 run.json 도 읽힌다
    run_path = work_dir / ".plan" / "7" / "nodes" / "11" / "run.json"
    run_path.write_text('{"round": 1, "status": "failed"}', encoding="utf-8")
    assert reader.read_run(7, 11) == NodeRun(1, PlanNodeStatus.FAILED)


def test_should_archive_round_and_keep_prompt(work_dir):
    reader, writer = DefaultPlanFolderReader(), DefaultPlanFolderWriter()
    writer.create_plan(7, "# 명령")
    writer.write_prompt(7, 11, "작업 지시")
    reader.result_target(7, 11).result_path.write_text("1 회차 결과", encoding="utf-8")
    writer.save_run(7, 11, NodeRun(1, PlanNodeStatus.FAILED))

    assert writer.archive_round(7, 11) == 2
    archived = work_dir / ".plan" / "7" / "nodes" / "11" / "runs" / "1"
    assert (archived / "result.md").read_text(encoding="utf-8") == "1 회차 결과"
    assert (archived / "prompt.md").exists() and reader.read_prompt(7, 11) == "작업 지시"
    assert reader.read_output(7, 11) is None


def test_should_keep_each_round_when_archiving_twice(work_dir):
    reader, writer = DefaultPlanFolderReader(), DefaultPlanFolderWriter()
    writer.create_plan(7, "# 명령")
    writer.write_prompt(7, 11, "작업 지시")
    target = reader.result_target(7, 11)
    target.result_path.write_text("1 회차", encoding="utf-8")
    assert writer.archive_round(7, 11) == 2
    target.result_path.write_text("2 회차", encoding="utf-8")
    assert writer.archive_round(7, 11) == 3

    runs = work_dir / ".plan" / "7" / "nodes" / "11" / "runs"
    assert (runs / "1" / "result.md").read_text(encoding="utf-8") == "1 회차"
    assert (runs / "2" / "result.md").read_text(encoding="utf-8") == "2 회차"
    current_run = reader.read_run(7, 11)
    assert current_run is not None and current_run.round == 3


def test_should_save_and_read_shown_record(work_dir):
    from task_plan_manager.model.plan.shown_record import ShownRecord

    reader, writer = DefaultPlanFolderReader(), DefaultPlanFolderWriter()
    writer.create_plan(7, "# 명령")
    assert reader.read_shown(7) is None
    writer.save_shown(7, ShownRecord("2026-11-19T10:00:00Z", "/tmp/t.jsonl"))
    writer.save_shown(7, ShownRecord("2026-11-19T11:00:00Z", "/tmp/t.jsonl"))  # 덮어쓴다
    assert reader.read_shown(7) == ShownRecord("2026-11-19T11:00:00Z", "/tmp/t.jsonl")
    assert (work_dir / ".plan" / "7" / "shown.json").exists()


def test_should_save_and_read_stop_mark(work_dir):
    from task_plan_manager.port.local.plan_folder.dto.stop_mark import StopMark

    reader, writer = DefaultPlanFolderReader(), DefaultPlanFolderWriter()
    writer.create_plan(7, "# 명령")
    assert reader.read_stop(7) is None
    mark = StopMark("r_1", "failed_stop", (3,), "노드 3 에서 멈췄습니다.")
    writer.save_stop(7, mark)
    assert reader.read_stop(7) == mark
    assert (work_dir / ".plan" / "7" / "stop.json").exists()


def test_should_write_result_for_confirm_node(work_dir):
    reader, writer = DefaultPlanFolderReader(), DefaultPlanFolderWriter()
    writer.create_plan(7, "# 명령")
    writer.write_result(7, 4, "# 확인")
    output = reader.read_output(7, 4)
    assert output is not None and output.result_path.read_text() == "# 확인"
