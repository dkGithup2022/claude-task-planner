from task_planner.model.node_run.node_run import NodeRun
from task_planner.model.node_run.read_input import ReadInput
from task_planner.model.plan.plan_node_status import PlanNodeStatus


def test_should_return_new_run_on_start_and_finish():
    first_run = NodeRun(1, PlanNodeStatus.TODO)
    started = first_run.start("2026-11-19T10:00:00Z", (ReadInput(11, 2),))
    assert started.status == PlanNodeStatus.RUNNING and started.read_inputs == (ReadInput(11, 2),)
    done = started.finish(PlanNodeStatus.DONE, "2026-11-19T10:06:00Z")
    assert done.status == PlanNodeStatus.DONE and done.finished_at == "2026-11-19T10:06:00Z"
    assert first_run == NodeRun(1, PlanNodeStatus.TODO)


def test_should_clear_failure_on_start():
    failed = NodeRun(2, PlanNodeStatus.FAILED, failed_reason="막힘", failed_summary="라이브러리 권한 없음")
    started = failed.start("2026-11-19T10:00:00Z", ())
    assert started.failed_reason is None and started.failed_summary is None


def test_should_keep_round_when_back_to_todo():
    started = NodeRun(2, PlanNodeStatus.TODO).start("2026-11-19T10:00:00Z", (ReadInput(11, 1),))
    again = started.back_to_todo()
    assert again == NodeRun(2, PlanNodeStatus.TODO, read_inputs=(ReadInput(11, 1),))
