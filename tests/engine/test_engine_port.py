from task_plan_manager.claude_utils.prompt.dto.prompt_call_record import PromptCallRecord
from task_plan_manager.common.paths import home
from task_plan_manager.engine.definition.ref import Ref
from task_plan_manager.engine.definition.task.task_output import TaskOutput
from task_plan_manager.engine.model.history.history_entry import HistoryEntry
from task_plan_manager.engine.model.run_state.flow_run_state import FlowRunState
from task_plan_manager.engine.model.run_state.flow_run_status import FlowRunStatus
from task_plan_manager.engine.model.run_state.node_kind import NodeKind
from task_plan_manager.engine.model.run_state.node_status import NodeStatus
from task_plan_manager.engine.model.run_state.scenario_node import ScenarioNode
from task_plan_manager.engine.model.session.claude_session import ClaudeSession
from task_plan_manager.engine.performer.performed_by import PerformedBy
from task_plan_manager.engine.port.history.default_history_reader import DefaultHistoryReader
from task_plan_manager.engine.port.history.default_history_writer import DefaultHistoryWriter
from task_plan_manager.engine.port.result.default_result_reader import DefaultResultReader
from task_plan_manager.engine.port.result.default_result_writer import DefaultResultWriter
from task_plan_manager.engine.port.run_state.default_run_state_reader import DefaultRunStateReader
from task_plan_manager.engine.port.run_state.default_run_state_writer import DefaultRunStateWriter
from task_plan_manager.engine.port.session.default_session_reader import DefaultSessionReader
from task_plan_manager.engine.port.session.default_session_writer import DefaultSessionWriter
from task_plan_manager.engine.runner.child_run.child_run import ChildRun


def _state() -> FlowRunState:
    alarm = ScenarioNode("a7c2f0e1-1111", "alarm", NodeKind.TASK, performed_by=PerformedBy.MAIN_SESSION_ASK,
                         task=Ref("todo.ask_alarm"))  # fmt: skip
    root = ScenarioNode("c81e0000-2222", "todo", NodeKind.GROUP, child_run=ChildRun.IN_ORDER, children=[alarm])
    return FlowRunState("r_1", "todo", "sess-a", FlowRunStatus.RUNNING, "t0", "t0", root, None)


def test_should_save_files_at_designed_locations():
    # given
    st = _state()
    alarm = st.scenario.children[0]
    # when
    DefaultSessionWriter().save_session(ClaudeSession("sess-a", "/t.jsonl", "r_1", "t0", "t0"))
    DefaultRunStateWriter().save_run(st)
    ref1 = DefaultResultWriter().save_result(st, alarm, "1", TaskOutput({"answer": "10분 전"}))
    ref2 = DefaultResultWriter().save_result(st, alarm, "2", TaskOutput({"answer": "1시간 전"}))
    entry = HistoryEntry(
        "t1", alarm.uuid, alarm.folder_name, "2", NodeStatus.COMPLETED, PerformedBy.MAIN_SESSION_ASK, ref2
    )
    DefaultHistoryWriter().append_history(st, entry)
    call = DefaultResultWriter().save_prompt_call(st, alarm, PromptCallRecord({"user": "u"}, {"ok": True}))
    call2 = DefaultResultWriter().save_prompt_call(st, alarm, PromptCallRecord({"user": "v"}, {"ok": False}))
    # then
    base = home() / "sessions" / "sess-a"
    run = base / "runs" / "r_1"
    files = sorted(str(p.relative_to(base)) for p in base.rglob("*") if p.is_file())
    assert call2 == "alarm_a7c2f0e1/calls/2"
    files = [f for f in files if "/calls/2/" not in f]
    assert files == ["runs/r_1/alarm_a7c2f0e1/calls/1/request.json", "runs/r_1/alarm_a7c2f0e1/calls/1/response.json",
                     "runs/r_1/alarm_a7c2f0e1/result.json", "runs/r_1/history.jsonl", "runs/r_1/state.json",
                     "session.json"]  # fmt: skip
    assert (ref1, ref2, call) == ("alarm_a7c2f0e1/result.json#1", "alarm_a7c2f0e1/result.json#2",
                                  "alarm_a7c2f0e1/calls/1")  # fmt: skip
    assert DefaultResultReader().read_result(st, alarm, "2") == TaskOutput({"answer": "1시간 전"})
    assert DefaultResultReader().read_result(st, alarm, "3") is None
    assert DefaultRunStateReader().load_run("sess-a", "r_1") == st
    assert DefaultSessionReader().load_session("sess-a").active_run_id == "r_1"
    assert DefaultSessionReader().load_session("nobody") is None
    assert [h.item_key for h in DefaultHistoryReader().read_history(st)] == ["2"]
    assert (run / "state.json").exists()


def test_should_keep_first_items_when_fixed_twice():
    st = _state()
    first = DefaultResultWriter().fix_items(st, st.scenario, [{"title": "팀 회의"}])
    again = DefaultResultWriter().fix_items(st, st.scenario, [{"title": "다른 것"}])
    assert again == first and again.items == ({"title": "팀 회의"},)
