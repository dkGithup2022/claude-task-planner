from task_plan_manager.model.node_run.node_run import NodeRun
from task_plan_manager.model.node_run.read_input import ReadInput
from task_plan_manager.model.plan.plan_node_status import PlanNodeStatus


def test_should_return_new_run_on_start_and_finish():
    first_run = NodeRun(1, PlanNodeStatus.TODO)
    started = first_run.start("2026-11-19T10:00:00Z", (ReadInput(11, 2),))
    assert started.status == PlanNodeStatus.RUNNING and started.read_inputs == (ReadInput(11, 2),)
    done = started.finish(PlanNodeStatus.DONE, "2026-11-19T10:06:00Z")
    assert done.status == PlanNodeStatus.DONE and done.finished_at == "2026-11-19T10:06:00Z"
    assert first_run == NodeRun(1, PlanNodeStatus.TODO)
